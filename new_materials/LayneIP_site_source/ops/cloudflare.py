#!/usr/bin/env python3
"""Scoped Cloudflare inventory and additive launch changes. Python 3.10+, stdlib.

No credentials are read from project files, passed on the command line, or saved.
audit -> plan -> apply are separate operations. Apply rechecks live state and writes
a recovery journal before each mutation. Unknown/competing records are held.
"""
import argparse
import copy
import datetime as dt
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://api.cloudflare.com/client/v4'
ALLOWED_ZONES = {'layneip.com', 'layneip.tech'}
SETTING_CANDIDATES = {'tls_1_3': 'on', 'http2': 'on', 'http3': 'on'}
AUDIT_SETTINGS = [*SETTING_CANDIDATES, 'ssl', 'min_tls_version', 'always_use_https',
                  'security_header', 'browser_cache_ttl', 'cache_level', 'rocket_loader']
CONFIG = Path(__file__).with_name('cloudflare-desired.json')

def utcnow():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def save(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    payload = (json.dumps(value, indent=2) + '\n').encode('utf-8')
    if exclusive:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Unexpected API redirect; credentials were not forwarded.')

class Cloudflare:
    def __init__(self, token):
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, path, body=None):
        if not path.startswith('/zones') or '..' in path:
            raise ValueError('Only zone API paths are supported.')
        headers = {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'}
        req = urllib.request.Request(BASE + path, data=None if body is None else json.dumps(body).encode(), headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=30) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f'Cloudflare returned HTTP {error.code}; verify the scoped token permissions.') from None
        except urllib.error.URLError:
            raise RuntimeError('Cloudflare could not be reached. No automatic retry of writes was attempted.') from None
        if not result.get('success'):
            codes = [e.get('code') for e in result.get('errors', [])]
            raise RuntimeError(f'Cloudflare reported error codes {codes}; request not confirmed.')
        return result

    def get(self, path):
        return self.request('GET', path)['result']

    def records(self, zone_id):
        records, page = [], 1
        while True:
            result = self.request('GET', f'/zones/{zone_id}/dns_records?per_page=100&page={page}')
            records.extend(result['result'])
            if page >= result.get('result_info', {}).get('total_pages', 1):
                return records
            page += 1

    def optional(self, path):
        try:
            return self.get(path)
        except RuntimeError as error:
            return {'unavailable': str(error)}

def audit(api, desired):
    result = {'schema': 1, 'created_at': utcnow(), 'config_sha256': digest(desired), 'zones': {}}
    for name in desired['zones']:
        if name not in ALLOWED_ZONES:
            raise ValueError('Unexpected zone in configuration.')
        candidates = api.get('/zones?name=' + urllib.parse.quote(name))
        exact = [z for z in candidates if z['name'] == name]
        if len(exact) != 1:
            raise RuntimeError(f'Could not uniquely resolve {name}. No changes were made.')
        zone = exact[0]
        prefix = '/zones/' + zone['id']
        result['zones'][name] = {
            'zone': zone, 'dns': api.records(zone['id']),
            'settings': {s: api.optional(prefix + '/settings/' + s) for s in AUDIT_SETTINGS},
            'dnssec': api.optional(prefix + '/dnssec'),
            'rulesets': api.optional(prefix + '/rulesets'),
            'page_rules': api.optional(prefix + '/pagerules'),
            'worker_routes': api.optional(prefix + '/workers/routes'),
            'certificate_packs': api.optional(prefix + '/ssl/certificate_packs')
        }
    return result

def dns_key(record):
    content = record['content']
    if record['type'] == 'CNAME':
        content = content.rstrip('.').lower()
    if record['type'] == 'TXT':
        content = content.strip('"')
    return (record['type'], record['name'].rstrip('.').lower(), content)

def make_plan(snapshot, desired, include_settings=False):
    if snapshot.get('config_sha256') != digest(desired):
        raise ValueError('The desired configuration changed; take a new audit.')
    if set(snapshot.get('zones', {})) != set(desired['zones']):
        raise ValueError('The audit must contain every configured zone exactly once.')
    plan = {'schema': 1, 'created_at': utcnow(), 'config_sha256': digest(desired),
            'operations': [], 'holds': [], 'manual_review': desired['manual_review']}
    for name, info in snapshot['zones'].items():
        if name not in ALLOWED_ZONES:
            raise ValueError('Unexpected zone in snapshot.')
        zid = info['zone']['id']
        if info['zone'].get('status') != 'active':
            plan['holds'].append(f'{name}: zone is not active; no changes planned.')
            continue
        wanted = [r for r in desired['dns'] if r['zone'] == name]
        for record in wanted:
            same_name = [r for r in info['dns'] if r['name'].rstrip('.').lower() == record['name']]
            exact = [r for r in same_name if dns_key(r) == dns_key(record)]
            wanted_keys = {dns_key(r) for r in wanted if r['name'] == record['name']}
            if exact:
                if any(r.get('proxied') for r in exact):
                    plan['holds'].append(f"{record['name']}: existing target is proxied; review Sites routing before changing proxy state.")
                if record['type'] in ('A', 'CNAME') and any(
                    r['type'] in ('A', 'AAAA', 'CNAME') and dns_key(r) not in wanted_keys for r in same_name
                ):
                    plan['holds'].append(f"{record['name']}: additional address records compete with the hosting target; review the complete record set.")
                continue
            if record['type'] == 'TXT':
                conflict = any(r['type'] == 'CNAME' or (r['type'] == 'TXT' and dns_key(r) not in wanted_keys) for r in same_name)
            elif record['type'] == 'CNAME':
                conflict = bool(same_name)
            else:
                conflict = any(r['type'] in ('A', 'AAAA', 'CNAME') and (dns_key(r) not in wanted_keys or r.get('proxied')) for r in same_name)
            if conflict:
                plan['holds'].append(f"{record['name']} {record['type']}: competing existing record; no overwrite or deletion planned.")
                continue
            body = {k: v for k, v in record.items() if k != 'zone'}
            plan['operations'].append({'kind': 'dns_create', 'zone': name, 'zone_id': zid, 'after': body})
        if include_settings:
            for setting, value in SETTING_CANDIDATES.items():
                current = info['settings'].get(setting, {})
                if current.get('value') == value:
                    continue
                if current.get('editable') is not True or 'value' not in current:
                    plan['holds'].append(f'{name}: {setting} unavailable or not editable on this plan.')
                    continue
                plan['operations'].append({'kind': 'setting', 'zone': name, 'zone_id': zid,
                                           'setting': setting, 'before': current['value'], 'after': value})
    plan['holds'] = sorted(set(plan['holds']))
    return plan

def validate_operation(op, desired):
    if op.get('zone') not in ALLOWED_ZONES or not re.fullmatch('[0-9a-f]{32}', op.get('zone_id', '')):
        raise ValueError('Invalid zone in plan.')
    if op.get('kind') == 'setting':
        if op.get('setting') not in SETTING_CANDIDATES or op.get('after') != SETTING_CANDIDATES[op['setting']]:
            raise ValueError('Setting change outside this tool’s scope.')
    elif op.get('kind') == 'dns_create':
        allowed = [{k: v for k, v in r.items() if k != 'zone'} for r in desired['dns'] if r['zone'] == op['zone']]
        if op.get('after') not in allowed:
            raise ValueError('DNS change outside the prepared hosting records.')
    else:
        raise ValueError('Unsupported operation. Deletion is never automated.')

def apply(api, plan, desired, journal_path):
    if Path(journal_path).exists():
        raise ValueError('Recovery journal already exists. Keep it and choose a new --journal path.')
    if plan.get('config_sha256') != digest(desired):
        raise ValueError('Configuration changed; audit and plan again.')
    operations = plan.get('operations', [])
    if len({digest(op) for op in operations}) != len(operations):
        raise ValueError('Plan contains duplicate operations. Audit and plan again.')
    age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(plan['created_at'])
    if not dt.timedelta(0) <= age <= dt.timedelta(hours=24):
        raise ValueError('Plan must be less than 24 hours old. Audit and plan again.')
    # Resolve account state again; an edited/stale file cannot redirect writes to another zone.
    fresh = audit(api, desired)
    fresh_plan = make_plan(fresh, desired, include_settings=True)
    for op in plan['operations']:
        validate_operation(op, desired)
        if op not in fresh_plan['operations']:
            raise RuntimeError('Live state has changed or an operation is no longer safe. Audit and plan again.')
    journal = {'schema': 1, 'started_at': utcnow(), 'before': fresh, 'operations': []}
    save(journal_path, journal, exclusive=True)
    working_dns = {name: copy.deepcopy(info['dns']) for name, info in fresh['zones'].items()}
    for op in plan['operations']:
        entry = {'operation': op, 'status': 'pending'}
        journal['operations'].append(entry)
        save(journal_path, journal)
        prefix = '/zones/' + op['zone_id']
        try:
            if op['kind'] == 'dns_create':
                # Recheck all records at the owner name immediately before creating anything.
                live = api.records(op['zone_id'])
                baseline = working_dns[op['zone']]
                owner = op['after']['name']
                fields = ('id', 'type', 'name', 'content', 'ttl', 'proxied', 'priority')
                fingerprint = lambda records: sorted(digest({k:r.get(k) for k in fields}) for r in records if r['name'] == owner)
                if fingerprint(live) != fingerprint(baseline):
                    raise RuntimeError('DNS owner changed during apply; stopped before the next write.')
                result = api.request('POST', prefix + '/dns_records', op['after'])['result']
                baseline.append(result)
                entry['record_id'] = result['id']
            else:
                live = api.get(prefix + '/settings/' + op['setting'])
                if live.get('value') != op['before'] or live.get('editable') is not True:
                    raise RuntimeError('Setting changed during apply; stopped before the next write.')
                result = api.request('PATCH', prefix + '/settings/' + op['setting'], {'value': op['after']})['result']
            entry['status'] = 'confirmed'
            entry['result'] = result
        except Exception:
            entry['status'] = 'unconfirmed — inspect live state before retrying'
            save(journal_path, journal)
            raise
        save(journal_path, journal)
    journal['completed_at'] = utcnow()
    save(journal_path, journal)
    return journal

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    a = sub.add_parser('audit'); a.add_argument('--out', default='.cloudflare-audit/audit.json')
    p = sub.add_parser('plan'); p.add_argument('audit'); p.add_argument('--include-settings', action='store_true'); p.add_argument('--out', default='.cloudflare-audit/plan.json')
    a = sub.add_parser('apply'); a.add_argument('plan'); a.add_argument('--journal', default='.cloudflare-audit/apply-journal.json')
    args = parser.parse_args()
    desired = json.loads(CONFIG.read_text())
    if args.command == 'plan':
        result = make_plan(json.loads(Path(args.audit).read_text()), desired, args.include_settings)
        save(args.out, result)
        print(f"Prepared {len(result['operations'])} operations; {len(result['holds'])} holds. Review {args.out}. No changes made.")
        return
    if not sys.stdin.isatty():
        raise RuntimeError('Run in an interactive terminal for the hidden token prompt.')
    token = getpass.getpass('Scoped Cloudflare API token (input hidden; never saved): ').strip()
    if not token:
        raise RuntimeError('No token supplied. No changes made.')
    api = Cloudflare(token)
    if args.command == 'audit':
        result = audit(api, desired); save(args.out, result)
        print(f'Read-only inventory saved to {args.out}. No changes made.')
    else:
        result = apply(api, json.loads(Path(args.plan).read_text()), desired, args.journal)
        print(f"Confirmed {len(result['operations'])} operations. Recovery journal: {args.journal}")

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
