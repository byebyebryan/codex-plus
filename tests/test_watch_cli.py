from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.cli import main, shutdown_preview
from codex_plus.store import Store
from test_peers import A, B, OWNER


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.state = self.root / 'state'
        self.store = Store(self.state)
        (self.state / 'binding.json').write_text(json.dumps({'thread_id': 'fixture-thread'}))
        self.spec = {'command': ['rtk', 'proxy', 'true'], 'cwd': str(self.root), 'duration': 120}
        grant = {'native': {'sandbox': {'type': 'readOnly', 'networkAccess': False},
                 'profile': None, 'cwd': str(self.root)},
                 'request': {'sandboxPolicy': {'type': 'readOnly', 'networkAccess': False}},
                 'source_access': 'session', 'network_access': 'inherit'}
        for p in (patch('codex_plus.cli.source_permissions', return_value=grant),
                  patch('codex_plus.cli.Client')):
            p.start(); self.addCleanup(p.stop)

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

    def test_early_acknowledgement_keeps_a_consumed_callback_until_completion(self):
        from codex_plus import cli
        for outcome in ('completed', 'failed', 'interrupted'):
            with self.subTest(outcome=outcome):
                watch = self.store.create('watch', self.spec)
                event = self.store.emit(watch, 'synthetic callback')
                self.store.admitted(event, 'synthetic-native-id')
                self.store.link_turn(event, 'synthetic-' + outcome)
                self.store.acknowledge(event)
                self.store.cancel(watch)
                ticks = [0]
                class CallbackEngine:
                    def __init__(inner, store, frozen):
                        inner.store = store
                        inner.generation = 'synthetic-generation'
                        inner.successor = None
                        inner.sources, inner.peer_polls = {}, {}
                        inner.inspections, inner.command_due = {}, {}
                        inner.client = object()
                    def tick(inner):
                        ticks[0] += 1
                        if ticks[0] == 20:
                            inner.store.turn_completed('synthetic-' + outcome, outcome)
                        if ticks[0] > 40:
                            raise AssertionError('coordinator did not settle')
                    def awaiting_receipts(inner):
                        return ticks[0] < 20
                    def close(inner): pass
                with patch('codex_plus.cli.Engine', CallbackEngine), \
                     patch('codex_plus.cli.time.monotonic', side_effect=lambda: float(ticks[0])):
                    cli._serve_once(self.state)
                self.assertEqual(self.store.event(event)['turn_outcome'], outcome)
                self.assertGreaterEqual(ticks[0], 20)

    def test_reminder_cli_default_expiry_covers_requested_delay_before_admission(self):
        with patch('codex_plus.cli.validate_binding'), patch('codex_plus.cli.ensure_coordinator'):
            code, result = self.run_cli(['wake_schedule', '--after', '600', '--prompt', 'Reassess fixture.'])
            self.assertEqual(code, 0)
            self.assertEqual(result['duration'], 720)
            self.assertAlmostEqual(self.store.job(result['id'])['expires'] - self.store.job(result['id'])['due'], 120)
            with self.assertRaises(ValueError):
                self.run_cli(['wake_schedule', '--after', '86400', '--prompt', 'Invalid.'])
            self.assertEqual(len(self.store.jobs()), 1)

    def test_compact_ack_requires_unique_known_native_admission(self):
        job = self.store.create('message', {'prompt': 'hello'})
        event = self.store.emit(job, 'hello', 'message')
        with self.assertRaises(ValueError):
            self.run_cli(['ack', 'e-' + event[:8]])
        self.assertFalse(self.store.event(event)['acknowledged'])
        self.store.admitted(event, 'native-exact')
        with patch('codex_plus.cli.Client') as native:
            code, result = self.run_cli(['ack', 'e-' + event[:8]])
        self.assertEqual(code, 0)
        self.assertEqual(result['id'], event)
        self.assertTrue(result['acknowledged'])
        native.assert_not_called()

    def test_ambiguous_compact_ack_changes_no_receipt(self):
        ids = ['01234567-1111-4111-8111-111111111111', '01234567-2222-4222-8222-222222222222']
        for identity in ids:
            job = self.store.create('message', {'prompt': 'hello'})
            event = self.store.emit(job, 'hello', 'message')
            self.store.db.execute('UPDATE events SET id=? WHERE id=?', (identity, event))
            self.store.admitted(identity, 'native-' + identity)
        with self.assertRaises(ValueError):
            self.run_cli(['ack', 'e-01234567'])
        self.assertFalse(any(event['acknowledged'] for event in self.store.events()))

    def test_registration_reports_actual_read_only_bounds(self):
        with patch('codex_plus.cli.validate_binding'), patch('codex_plus.cli.ensure_coordinator'):
            code, result = self.run_cli(['watch_start', '--cwd', str(self.root), '--duration', '90',
                '--limit', '1', '--', 'rtk', 'proxy', 'true'])
        self.assertEqual(code, 0)
        self.assertEqual(result['effective_bounds']['duration'], 90)
        self.assertEqual(result['effective_bounds']['source_events'], 1)
        self.assertEqual(result['source_policy'], {'sandboxPolicy': {'type': 'readOnly', 'networkAccess': False}})

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

    def test_recovery_reconciles_offline_source_before_requesting_restart(self):
        watch = self.store.create('watch', self.spec)
        self.store.source(watch, 'running')
        def restarted(root):
            self.store.reconcile()
        with patch('codex_plus.cli.validate_binding'), patch('codex_plus.cli.ensure_coordinator', side_effect=restarted):
            code, result = self.run_cli(['recover', watch])
        self.assertEqual(code, 0)
        self.assertTrue(result['observation_gap'])
        self.assertTrue(self.store.job(watch)['recover_requested'])

    def test_pending_and_failed_replacement_ids_have_cached_receipts(self):
        parent = self.store.create('watch', self.spec)
        self.store.source(parent, 'running')
        child = self.store.request_renewal(parent, self.spec)
        with patch('codex_plus.cli.Client') as native, patch('codex_plus.cli.ensure_coordinator') as start:
            _, pending = self.run_cli(['status', child])
            self.store.reconcile()
            _, failed = self.run_cli(['status', child])
        self.assertEqual(pending['renewals'][0]['state'], 'pending')
        self.assertEqual(failed['renewals'][0]['state'], 'interrupted')
        self.assertEqual(failed['registrations'][0]['id'], parent)
        native.assert_not_called(); start.assert_not_called()

    def test_renewal_reconciles_offline_owner_before_acceptance(self):
        parent = self.store.create('watch', self.spec)
        self.store.source(parent, 'running')
        with patch('codex_plus.cli.validate_binding'), patch('codex_plus.cli.ensure_coordinator', side_effect=lambda root:self.store.reconcile()):
            with self.assertRaisesRegex(ValueError, 'lost'):
                self.run_cli(['renew', '--id', parent, '--', 'rtk', 'proxy', 'true'])
        self.assertEqual(self.store.job(parent)['intent'], 'active')
        self.assertEqual(self.store.renewals(), [])

    def test_offline_cancel_requests_cleanup_without_starting_coordinator(self):
        parent = self.store.create('watch', self.spec)
        with patch('codex_plus.cli.coordinator_info', return_value=None), patch('codex_plus.cli.Engine') as engine, patch('codex_plus.cli.ensure_coordinator') as start:
            _, result = self.run_cli(['cancel', parent])
        self.assertEqual(result['cancelled'], [parent])
        engine.return_value.close.assert_called_once()
        start.assert_not_called()

    def test_peer_watch_reports_distinct_frozen_source_and_destination(self):
        frozen = {**OWNER, 'thread_id': A}
        peer = {**OWNER, 'thread_id': B}
        (self.state / 'binding.json').write_text(json.dumps(frozen))
        with patch('codex_plus.cli.validate_binding', return_value=frozen), \
                patch('codex_plus.cli.Client'), patch('codex_plus.cli.PeerReader') as reader, \
                patch('codex_plus.cli.ensure_coordinator'):
            reader.return_value.resolve.return_value = peer
            _, result = self.run_cli(['watch_start', '--peer', B, '--signals', 'reply,goal',
                                     '--interval', '7', '--quiet-initial'])
        self.assertEqual(result['destination'], frozen)
        self.assertEqual(result['source_policy']['observed_peer'], peer)
        self.assertFalse(result['source_policy']['resumes_peer'])
        self.assertEqual(self.store.job(result['id'])['spec']['interval'], 7)

    def test_foreign_peer_owner_is_refused_before_any_registration(self):
        frozen = {**OWNER, 'thread_id': A}
        with patch('codex_plus.cli.validate_binding', return_value=frozen), \
                patch('codex_plus.cli.Client'), patch('codex_plus.cli.PeerReader') as reader, \
                patch('codex_plus.cli.ensure_coordinator') as start:
            reader.return_value.resolve.return_value = {**OWNER, 'pid': 101, 'thread_id': B}
            with self.assertRaises(ValueError):
                self.run_cli(['watch_start', '--peer', B])
        self.assertEqual(self.store.jobs(), [])
        start.assert_not_called()

    def test_message_startup_failure_returns_durable_ids_without_claiming_delivery(self):
        frozen = {**OWNER, 'thread_id': B}
        with patch('codex_plus.cli.validate_binding', return_value=frozen), \
                patch('codex_plus.cli.Client'), patch('codex_plus.cli.PeerReader'), \
                patch('codex_plus.cli.ensure_coordinator', side_effect=TimeoutError('startup unknown')):
            _, result = self.run_cli(['peer_send', '--message', 'information'])
        self.assertEqual(result['state'], 'registered_coordinator_unavailable')
        self.assertEqual(self.store.event(result['event_id'])['delivery'], 'pending')
        self.assertEqual(len(self.store.events(result['id'])), 1)
        self.assertTrue(result['admission_is_not_handling'])

    def test_rtk_supervisor_log_is_outside_legacy_and_incarnation_journal_boundaries(self):
        from codex_plus import cli
        from codex_plus.owner_recovery import _open_state_processes

        probe = self.root / 'coordinator_probe.py'
        probe.write_text('''\
import os
from pathlib import Path
import sys
import time

journal, ready, release, closed, finish = map(Path, sys.argv[1:])
fd = os.open(journal, os.O_CREAT | os.O_RDWR, 0o600)
for descriptor in (1, 2):
    try:
        os.close(descriptor)
    except OSError:
        pass
temporary = ready.with_name(ready.name + '.tmp')
temporary.write_text(str(os.getpid()))
temporary.replace(ready)
while not release.exists():
    time.sleep(0.02)
os.close(fd)
temporary = closed.with_name(closed.name + '.tmp')
temporary.write_text('closed')
temporary.replace(closed)
while not finish.exists():
    time.sleep(0.02)
''')
        real_popen = subprocess.Popen

        layouts = (
            ('legacy', self.root / 'legacy-state', None),
            ('incarnation', self.root / 'native-state' / A / 'incarnations' / 'epoch-1',
             self.root / 'native-state' / A),
        )
        for label, state, stable_container in layouts:
            with self.subTest(layout=label):
                state.mkdir(mode=0o700, parents=True)
                journal = state / 'journal.sqlite3'
                journal.touch(mode=0o600)
                ready = self.root / (label + '.ready')
                release = self.root / (label + '.release')
                closed = self.root / (label + '.closed')
                finish = self.root / (label + '.finish')
                supervisor = None
                probe_pid = None
                probe_identity = None

                def launch(arguments, **kwargs):
                    nonlocal supervisor
                    self.assertEqual(arguments[:2], ['rtk', 'proxy'])
                    replacement = ['rtk', 'proxy', sys.executable, '-B', str(probe),
                                   str(journal), str(ready), str(release), str(closed), str(finish)]
                    supervisor = real_popen(replacement, **kwargs)
                    return supervisor

                def fake_coordinator_info(root):
                    if Path(root) != state or not ready.is_file():
                        return None
                    try:
                        return {'pid': int(ready.read_text())}
                    except (OSError, ValueError):
                        return None

                def wait_for(path):
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        if path.is_file():
                            return
                        time.sleep(0.02)
                    self.fail(f'probe marker was not created: {path.name}')

                try:
                    with patch('codex_plus.cli.coordinator_info', side_effect=fake_coordinator_info), \
                            patch('codex_plus.cli.subprocess.Popen', side_effect=launch):
                        cli.ensure_coordinator(state)

                    probe_pid = int(ready.read_text())
                    probe_identity = cli.process_identity(probe_pid)
                    self.assertIsNotNone(probe_identity)
                    self.assertEqual(_open_state_processes(state)['holder'], str(probe_pid),
                                     'an actual journal FD must remain a positive holder')

                    log_path = cli.coordinator_log_path(state)
                    boundary = stable_container or state
                    self.assertFalse(log_path.is_relative_to(boundary.resolve()))
                    self.assertEqual(stat.S_IMODE(log_path.parent.stat().st_mode), 0o700)
                    self.assertEqual(stat.S_IMODE(log_path.stat().st_mode), 0o600)

                    # The probe releases its journal as a coordinator would on
                    # handoff, but stays alive with stdio closed so only RTK's
                    # retained supervisor descriptors can hold the state tree.
                    release.touch()
                    wait_for(closed)
                    self.assertIsNone(supervisor.poll(), 'RTK must still supervise the gated probe')
                    self.assertIsNone(_open_state_processes(state)['holder'])
                    if stable_container:
                        self.assertIsNone(_open_state_processes(stable_container)['holder'])
                finally:
                    release.touch(exist_ok=True)
                    finish.touch(exist_ok=True)
                    if supervisor is not None:
                        try:
                            return_code = supervisor.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            if (probe_pid and probe_identity
                                    and cli.process_identity(probe_pid) == probe_identity):
                                os.kill(probe_pid, signal.SIGTERM)
                            if supervisor.poll() is None:
                                supervisor.terminate()
                            return_code = supervisor.wait(timeout=5)
                        self.assertEqual(return_code, 0)
                    if probe_pid and probe_identity:
                        self.assertNotEqual(cli.process_identity(probe_pid), probe_identity,
                                            'the exact bounded probe process must be gone')

    def test_coordinator_log_directory_symlink_is_refused_before_launch(self):
        from codex_plus import cli

        state = self.root / 'linked-log-state'
        state.mkdir(mode=0o700)
        outside = self.root / 'outside-log-target'
        outside.mkdir(mode=0o700)
        namespace = self.root / '.coordinator-logs'
        namespace.symlink_to(outside, target_is_directory=True)
        with patch('codex_plus.cli.subprocess.Popen') as launch:
            with self.assertRaises(ValueError):
                cli.ensure_coordinator(state)
        launch.assert_not_called()
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
