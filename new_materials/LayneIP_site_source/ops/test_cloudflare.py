import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('cloudflare',Path(__file__).with_name('cloudflare.py'))
cf=importlib.util.module_from_spec(spec);spec.loader.exec_module(cf)
DESIRED=json.loads(cf.CONFIG.read_text())

def snapshot(records=None, tech_records=None):
    zones={}
    for name,zone_id,dns in [('layneip.com','a'*32,records),('layneip.tech','b'*32,tech_records)]:
        zones[name]={
            'zone':{'id':zone_id,'name':name,'status':'active'},'dns':dns or [],
            'settings':{key:{'value':'off','editable':True} for key in cf.SETTING_CANDIDATES}
        }
    return {'config_sha256':cf.digest(DESIRED),'zones':zones}

class CloudflarePlanTests(unittest.TestCase):
    def test_no_deletes_or_mail_changes(self):
        plan=cf.make_plan(snapshot([{'type':'MX','name':'layneip.com','content':'mail.example.com'}]),DESIRED)
        self.assertEqual(len(plan['operations']),14)
        self.assertTrue(all(op['kind']=='dns_create' for op in plan['operations']))
        self.assertFalse(any(op['after']['type']=='MX' for op in plan['operations']))

    def test_existing_address_blocks_cutover(self):
        plan=cf.make_plan(snapshot([{'type':'A','name':'layneip.com','content':'192.0.2.10'}]),DESIRED)
        self.assertFalse(any(op['after']['name']=='layneip.com' for op in plan['operations']))
        self.assertTrue(plan['holds'])

    def test_matching_records_are_idempotent(self):
        records={name:[{k:v for k,v in r.items() if k!='zone'} for r in DESIRED['dns'] if r['zone']==name]
                 for name in DESIRED['zones']}
        self.assertEqual(cf.make_plan(snapshot(records['layneip.com'],records['layneip.tech']),DESIRED)['operations'],[])

    def test_conflicting_ipv6_blocks_additive_apex(self):
        plan=cf.make_plan(snapshot([{'type':'AAAA','name':'layneip.com','content':'2001:db8::1'}]),DESIRED)
        self.assertFalse(any(op['zone']=='layneip.com' and op['after']['type']=='A' for op in plan['operations']))

    def test_tech_www_conflict_holds_only_that_host(self):
        tech=[{'type':'CNAME','name':'www.layneip.tech','content':'old.example'}]
        plan=cf.make_plan(snapshot(tech_records=tech),DESIRED)
        self.assertFalse(any(op['after']['name']=='www.layneip.tech' for op in plan['operations']))
        self.assertTrue(any(op['after']['name']=='layneip.tech' for op in plan['operations']))
        self.assertTrue(any('www.layneip.tech' in hold for hold in plan['holds']))

    def test_settings_explicit_and_plan_restrictions(self):
        plan=cf.make_plan(snapshot(),DESIRED,True)
        self.assertEqual(sum(op['kind']=='setting' for op in plan['operations']),6)
        op=next(op for op in plan['operations'] if op['kind']=='setting')
        cf.validate_operation(op,DESIRED)
        bad=copy.deepcopy(op);bad['setting']='ssl';bad['after']='off'
        with self.assertRaises(ValueError):cf.validate_operation(bad,DESIRED)
        bad=copy.deepcopy(op);bad['zone']='unrelated.example'
        with self.assertRaises(ValueError):cf.validate_operation(bad,DESIRED)

    def test_stale_config_stops_plan(self):
        state=snapshot();state['config_sha256']='changed'
        with self.assertRaises(ValueError):cf.make_plan(state,DESIRED)

    def test_partial_audit_is_rejected(self):
        state=snapshot();del state['zones']['layneip.tech']
        with self.assertRaises(ValueError):cf.make_plan(state,DESIRED)

    def test_matching_apex_does_not_hide_conflicting_ipv6(self):
        records=[{k:v for k,v in r.items() if k!='zone'} for r in DESIRED['dns'] if r['zone']=='layneip.com']
        records.append({'type':'AAAA','name':'layneip.com','content':'2001:db8::1'})
        plan=cf.make_plan(snapshot(records),DESIRED)
        self.assertTrue(any('additional address records' in hold for hold in plan['holds']))


class FakeCloudflare:
    def __init__(self, lose_response=False):
        self.state=snapshot([{'id':'mail','type':'MX','name':'layneip.com','content':'mail.example.com'}])
        self.writes=[]
        self.lose_response=lose_response

    def get(self,path):
        if path.startswith('/zones?name='):
            return [copy.deepcopy(self.state['zones'][path.split('=',1)[1]]['zone'])]
        raise AssertionError(path)

    def records(self,zone_id):
        return copy.deepcopy(next(info['dns'] for info in self.state['zones'].values() if info['zone']['id']==zone_id))

    def optional(self,path):
        return {}

    def request(self,method,path,body):
        assert method=='POST' and path.endswith('/dns_records')
        zone_id=path.split('/')[2]
        info=next(info for info in self.state['zones'].values() if info['zone']['id']==zone_id)
        result={**copy.deepcopy(body),'id':str(len(self.writes)+1)}
        info['dns'].append(result)
        self.writes.append((method,path,body))
        if self.lose_response:raise RuntimeError('Response lost after server accepted the record')
        return {'success':True,'result':result}


class CloudflareApplyTests(unittest.TestCase):
    def test_interrupted_journal_replace_preserves_previous_contents(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.json'
            cf.save(path,{'operations':['already confirmed']},exclusive=True)
            before=path.read_bytes()
            with patch.object(cf.os,'replace',side_effect=OSError('simulated disk failure')):
                with self.assertRaises(OSError):cf.save(path,{'operations':['replacement']})
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual(list(Path(folder).iterdir()),[path])

    def test_apply_preserves_mail_and_replanning_is_idempotent(self):
        api=FakeCloudflare()
        plan=cf.make_plan(cf.audit(api,DESIRED),DESIRED)
        with tempfile.TemporaryDirectory() as folder:
            result=cf.apply(api,plan,DESIRED,Path(folder)/'journal.json')
        self.assertEqual(len(api.writes),14)
        self.assertTrue(all(item['status']=='confirmed' for item in result['operations']))
        self.assertEqual(api.state['zones']['layneip.com']['dns'][0]['id'],'mail')
        self.assertEqual(cf.make_plan(cf.audit(api,DESIRED),DESIRED)['operations'],[])

    def test_duplicate_operations_and_existing_journals_prevent_writes(self):
        api=FakeCloudflare()
        plan=cf.make_plan(cf.audit(api,DESIRED),DESIRED)
        duplicate=copy.deepcopy(plan);duplicate['operations'].append(duplicate['operations'][0])
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.json'
            with self.assertRaises(ValueError):cf.apply(api,duplicate,DESIRED,path)
            path.write_text('prior recovery record')
            with self.assertRaises(ValueError):cf.apply(api,plan,DESIRED,path)
            self.assertEqual(path.read_text(),'prior recovery record')
        self.assertEqual(api.writes,[])

    def test_lost_response_stops_and_leaves_an_unconfirmed_journal(self):
        api=FakeCloudflare(lose_response=True)
        plan=cf.make_plan(cf.audit(api,DESIRED),DESIRED)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'journal.json'
            with self.assertRaises(RuntimeError):cf.apply(api,plan,DESIRED,path)
            journal=json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(len(api.writes),1)
        self.assertTrue(journal['operations'][0]['status'].startswith('unconfirmed'))
        self.assertNotIn('completed_at',journal)

if __name__=='__main__':unittest.main()
