from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from reference_suite.cli import main


class ConsolidatedCliTests(unittest.TestCase):
    def call(self, root, *arguments):
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(['--root', str(root), *map(str, arguments)])
        self.assertEqual(code, 0, errors.getvalue())
        return json.loads(output.getvalue())

    def test_api_snapshot_import_show_and_diff_share_the_selected_data_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'api.json'
            old = {'openapi': '3.0.3', 'info': {'title': 'Local API fixture', 'version': '1'},
                   'paths': {'/works': {'get': {'summary': 'List works', 'responses': {'200': {'description': 'OK'}}}}}}
            source.write_text(json.dumps(old), encoding='utf-8')
            first = self.call(root, 'spec-import', source)
            self.assertEqual(first['endpoint_count'], 1)
            self.assertTrue(Path(first['snapshot_path']).is_relative_to(root / 'out' / 'specifications'))
            shown = self.call(root, 'spec-show', first['snapshot_path'])
            self.assertEqual(shown['endpoints'][0]['id'], 'GET /works')
            old['paths']['/works']['get']['summary'] = 'List searchable works'
            old['paths']['/works/{id}'] = {'get': {'responses': {'200': {'description': 'OK'}}}}
            source.write_text(json.dumps(old), encoding='utf-8')
            second = self.call(root, 'spec-import', source)
            diff = self.call(root, 'spec-diff', first['snapshot_path'], second['snapshot_path'])
            self.assertEqual(diff['counts']['added'], 1)
            self.assertEqual(diff['counts']['changed'], 1)
            self.assertEqual(diff['counts']['removed'], 0)

    def test_preset_revision_preview_and_explicit_local_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'selected.txt'
            source.write_text('A local fixture with no external request.', encoding='utf-8')
            job_file = root / 'job.json'
            job = {'provider': 'local', 'operation': 'ingest', 'value': str(source), 'dataset': 'first'}
            job_file.write_text(json.dumps(job), encoding='utf-8')
            first = self.call(root, 'preset-save', 'local-source', job_file, '--reason', 'Use selected local fixture')
            self.assertEqual(first['revision'], 1)
            job['dataset'] = 'second'
            job_file.write_text(json.dumps(job), encoding='utf-8')
            self.call(root, 'preset-save', 'local-source', job_file, '--reason', 'Separate destination dataset')
            self.assertEqual(len(self.call(root, 'preset-history', 'local-source')), 2)
            self.assertEqual(self.call(root, 'preset-list')[0]['revision'], 2)
            self.assertEqual(self.call(root, 'preset-show', 'local-source', '--revision', 1)['job']['dataset'], 'first')
            planned = self.call(root, 'preset-plan', 'local-source', '--revision', 1)
            self.assertEqual(planned['job']['dataset'], 'first')
            self.assertEqual(planned['requests'], [])
            self.assertFalse((root / 'out').exists())
            completed = self.call(root, 'preset-run', 'local-source', '--revision', 1)
            self.assertEqual(completed['status'], 'complete')
            self.assertEqual(completed['preset']['revision'], 1)
            self.assertTrue(Path(completed['run_dir']).is_relative_to(root / 'out' / 'local' / 'first'))

    def test_malformed_job_file_is_rejected_before_planning_or_running(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            job = root / 'bad.json'
            job.write_text(json.dumps({'provider': 'openalex', 'operation': 'search', 'value': 'public fixture',
                                       'max_results': True}), encoding='utf-8')
            output, errors = StringIO(), StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                code = main(['--root', str(root), 'plan', '--job-file', str(job)])
            self.assertEqual(code, 2)
            self.assertIn('must be an integer', errors.getvalue())
            self.assertFalse((root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
