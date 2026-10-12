from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.cli import main, shutdown_preview
from codex_plus.store import Store


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / 'state'
        self.store = Store(self.state)
        (self.state / 'binding.json').write_text(json.dumps({'thread_id': 'fixture-thread'}))
        self.spec = {'command': ['rtk', 'proxy', 'true'], 'cwd': str(self.root), 'duration': 120}

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def run_cli(self, args):
        output = io.StringIO()
        with redirect_stdout(output):
            result = main(['--state', str(self.state), *args])
        return result, json.loads(output.getvalue())

    def test_shutdown_without_confirmation_is_only_a_preview(self):
        watch = self.store.create('watch', self.spec)
        with patch('codex_plus.cli.os.kill') as kill:
            code, result = self.run_cli(['shutdown'])
        self.assertEqual(code, 2)
        self.assertTrue(result['needs_confirmation'])
        self.assertEqual(self.store.job(watch)['intent'], 'active')
        kill.assert_not_called()

    def test_confirmed_shutdown_cancels_owned_work_without_native_rpc(self):
        watch = self.store.create('watch', self.spec)
        with patch('codex_plus.cli.coordinator_info', return_value=None), patch('codex_plus.cli.Client') as native:
            code, result = self.run_cli(['shutdown', '--confirm'])
        self.assertEqual(code, 0)
        self.assertTrue(result['native_owner_preserved'])
        self.assertEqual(self.store.job(watch)['intent'], 'cancelled')
        native.assert_not_called()

    def test_cached_status_does_not_start_or_refresh_native_runtime(self):
        watch = self.store.create('watch', self.spec)
        with patch('codex_plus.cli.Client') as native, patch('codex_plus.cli.ensure_coordinator') as start:
            code, result = self.run_cli(['status', watch])
        self.assertEqual(code, 0)
        self.assertEqual(result['coordinator']['state'], 'offline')
        self.assertTrue(result['source_receipts_may_be_stale'])
        native.assert_not_called(); start.assert_not_called()

    def test_registration_reports_actual_read_only_bounds(self):
        with patch('codex_plus.cli.validate_binding'), patch('codex_plus.cli.ensure_coordinator'):
            code, result = self.run_cli(['watch_start', '--cwd', str(self.root), '--duration', '90',
                '--limit', '1', '--', 'rtk', 'proxy', 'true'])
        self.assertEqual(code, 0)
        self.assertEqual(result['effective_bounds']['duration'], 90)
        self.assertEqual(result['effective_bounds']['source_events'], 1)
        self.assertEqual(result['source_policy'], {'type': 'readOnly', 'networkAccess': False})

    def test_renew_options_are_not_swallowed_as_source_argv(self):
        watch = self.store.create('watch', self.spec)
        with patch('codex_plus.cli.validate_binding'), patch('codex_plus.cli.ensure_coordinator'):
            code, result = self.run_cli(['renew', '--id', watch, '--cwd', str(self.root),
                '--duration', '45', '--limit', '1', '--', 'rtk', 'proxy', 'replacement'])
        self.assertEqual(code, 0)
        row = self.store.db.execute('SELECT spec FROM renewals WHERE parent_id=?', (watch,)).fetchone()
        spec = json.loads(row[0])
        self.assertEqual(spec['command'], ['rtk', 'proxy', 'replacement'])
        self.assertEqual(spec['duration'], 45)

    def test_offline_source_health_is_unknown_without_destroying_last_receipt(self):
        watch = self.store.create('watch', self.spec)
        self.store.source(watch, 'running')
        code, result = self.run_cli(['status', watch])
        job = result['registrations'][0]
        self.assertEqual(job['source_state'], 'unknown')
        self.assertEqual(job['last_source_state'], 'running')
        self.assertEqual(self.store.job(watch)['source_state'], 'running')


if __name__ == '__main__':
    unittest.main()
