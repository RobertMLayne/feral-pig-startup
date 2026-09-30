#!/usr/bin/env python3
"""Read-only public DNS and HTTP checks for the four Layne IP website hosts.

Uses Cloudflare's public resolver and requests each website without following
redirects. Requires no account credential. Results are observations,
not an inventory of hidden Cloudflare origin records or account settings.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import subprocess
import urllib.error
import urllib.parse
import urllib.request

CONFIG = Path(__file__).with_name('cloudflare-desired.json')
HOSTS = ('layneip.com', 'www.layneip.com', 'layneip.tech', 'www.layneip.tech')
CANONICAL = 'layneip.com'
PROBE_PATH = '/services/patent-preparation.html?source=domain-check'
TYPES = {'A': 1, 'CNAME': 5, 'TXT': 16, 'AAAA': 28}
MAX_BODY = 65536


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def normalized_value(kind, value):
    if kind == 'CNAME':
        return value.lower().rstrip('.')
    if kind == 'TXT':
        # DNS JSON represents TXT RDATA as one or more quoted character strings.
        return ''.join(shlex.split(value)) if value.startswith('"') else value
    return value


def assess_dns(name, kind, expected, payload):
    code = payload.get('Status')
    result = {'name': name, 'type': kind, 'expected': sorted(expected),
              'dns_status': code, 'authenticated_data': payload.get('AD')}
    if code not in (0, 3):
        return {**result, 'status': 'resolver_error', 'observed': [], 'error': payload.get('error')}
    observed = sorted({normalized_value(kind, a['data']) for a in payload.get('Answer', [])
                       if a.get('type') == TYPES[kind]
                       and a.get('name', '').lower().rstrip('.') == name.lower().rstrip('.')})
    matches = set(expected).issubset(observed) if kind == 'TXT' else set(expected) == set(observed)
    status = 'match' if matches else ('different_answers' if observed else 'missing')
    result.update(status=status, observed=observed)
    if kind in ('A', 'AAAA', 'CNAME') and status != 'match':
        result['note'] = 'Public answers can hide customer-proxied origins or flattened CNAMEs; inspect the zone before changing records.'
    return result


def dns_check(item, timeout):
    (name, kind), expected = item
    url = 'https://cloudflare-dns.com/dns-query?' + urllib.parse.urlencode({'name': name, 'type': kind})
    request = urllib.request.Request(url, headers={'Accept': 'application/dns-json', 'User-Agent': 'LayneIP-DomainCheck/1'})
    try:
        if os.name == 'nt':
            # Use Windows' resolver without changing TLS verification or trust stores.
            command = ['powershell.exe', '-NoProfile', '-NonInteractive', '-File',
                       str(Path(__file__).with_name('query_dns.ps1')),
                       '-QueryName', name, '-QueryType', kind]
            completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=True)
            result = assess_dns(name, kind, expected, json.loads(completed.stdout))
            result['transport'] = 'Windows Resolve-DnsName to 1.1.1.1'
            return result
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            raw = response.read(MAX_BODY + 1)
        if len(raw) > MAX_BODY:
            raise ValueError('DNS response exceeds the check limit')
        result = assess_dns(name, kind, expected, json.loads(raw))
        result['transport'] = 'DNS over HTTPS'
        return result
    except (OSError, ValueError, urllib.error.URLError, subprocess.SubprocessError) as error:
        return {'name': name, 'type': kind, 'expected': sorted(expected),
                'status': 'transport_error', 'error': str(error), 'observed': []}


def assess_http(url, status, location=None, body=''):
    parts = urllib.parse.urlsplit(url)
    expected = urllib.parse.urlunsplit(('https', CANONICAL, parts.path, parts.query, ''))
    result = {'url': url, 'http_status': status, 'location': location,
              'expected_canonical_url': expected}
    if status in (301, 302, 303, 307, 308) and location:
        target = urllib.parse.urlsplit(urllib.parse.urljoin(url, location))
        same_path = target.path == parts.path
        same_query = target.query == parts.query
        canonical = (target.scheme == 'https' and target.netloc.lower() == CANONICAL
                     and not target.fragment)
        result.update(path_preserved=same_path, query_preserved=same_query)
        if parts.scheme == 'https' and parts.netloc == CANONICAL and target.geturl() == url:
            result['status'] = 'redirect_loop'
        elif canonical and same_path and same_query:
            result['status'] = 'canonical_redirect'
        else:
            result['status'] = 'other_redirect'
    elif status == 200:
        result['status'] = 'canonical_page' if parts.scheme == 'https' and parts.netloc == CANONICAL else 'served_without_canonical_redirect'
    elif status in (401, 403):
        result['status'] = 'access_restricted_or_host_error'
        if '1014' in body:
            result['cloudflare_error'] = '1014'
    else:
        result['status'] = 'http_error'
    return result


def http_check(url, timeout):
    request = urllib.request.Request(url, headers={'User-Agent': 'LayneIP-DomainCheck/1'})
    try:
        try:
            response = urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            result = assess_http(url, response.code, response.headers.get('Location'),
                                 response.read(MAX_BODY).decode('utf-8', errors='replace'))
        result['https_response_received'] = url.startswith('https:')
        return result
    except (OSError, ValueError, urllib.error.URLError) as error:
        return {'url': url, 'status': 'transport_error', 'error': str(error),
                'https_response_received': False}


def check(desired, timeout=15):
    groups = {}
    for record in desired['dns']:
        name = record['name']
        if not any(name == zone or name.endswith('.' + zone) for zone in ('layneip.com', 'layneip.tech')):
            raise ValueError('Unexpected domain in desired DNS records')
        groups.setdefault((name, record['type']), set()).add(normalized_value(record['type'], record['content']))
    # A stale independent IPv6 destination can bypass otherwise-correct IPv4 routing.
    for apex in ('layneip.com', 'layneip.tech'):
        groups.setdefault((apex, 'AAAA'), set())
    with ThreadPoolExecutor(max_workers=6) as pool:
        dns = list(pool.map(lambda item: dns_check(item, timeout), sorted(groups.items())))
        urls = [scheme + '://' + host + PROBE_PATH for host in HOSTS for scheme in ('http', 'https')]
        http = list(pool.map(lambda url: http_check(url, timeout), urls))
    ready = all(item['status'] == 'match' for item in dns) and all(
        item['status'] in ('canonical_page', 'canonical_redirect') for item in http)
    return {'schema': 1, 'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'resolver': '1.1.1.1' if os.name == 'nt' else 'https://cloudflare-dns.com/dns-query', 'dns': dns, 'http': http,
            'public_launch_checks_pass': ready,
            'scope': 'Public resolver and HTTP observations only. Redirects are not followed. Account records, mail delivery, website content approval, and certificate renewal configuration require separate review.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='.cloudflare-audit/public-domain-check.json')
    parser.add_argument('--timeout', type=float, default=15)
    parser.add_argument('--require-ready', action='store_true', help='Return a failing exit code when public launch checks do not pass')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 60:
        parser.error('--timeout must be between 1 and 60 seconds')
    result = check(json.loads(CONFIG.read_text(encoding='utf-8')), args.timeout)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    for item in result['dns']:
        print(f"DNS {item['name']} {item['type']}: {item['status']}")
    for item in result['http']:
        print(f"HTTP {item['url']}: {item['status']} ({item.get('http_status', 'no response')})")
    print(f'Report: {target.resolve()}')
    return 1 if args.require_ready and not result['public_launch_checks_pass'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
