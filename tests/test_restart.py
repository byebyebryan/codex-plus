import json
import fcntl
import os
import signal
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codex_plus import owner_recovery as owners, restart
from codex_plus import cli
from codex_plus.model import ModelAPI
from codex_plus.model_server import Server
from codex_plus.engine import Engine
from codex_plus.store import Store, validate_spec
import test_owner_recovery as recovery_tests
from test_owner_recovery import binding, A, B
from test_model import meta
from test_watch_engine import Backend as EngineBackend


class RestartTests(unittest.TestCase):
    setUp = recovery_tests.OwnerRecoveryTests.setUp
    tearDown = recovery_tests.OwnerRecoveryTests.tearDown
    legacy_state = recovery_tests.OwnerRecoveryTests.legacy_state
    make_recovery = recovery_tests.OwnerRecoveryTests.make_recovery

    def watch(self, *, peer=True, **changes):
        old = binding(A, pid=2147483000, start='12', executable='/fixture/old-codex')
        state = self.root / A
        if not state.exists():
            self.legacy_state(A, old)
        spec = {'duration': 100, 'event_limit': 3, 'quiet_initial': True}
        spec.update({'peer': {**old, 'thread_id': B}} if peer else {'command': ['true'], 'cwd': '/'})
        spec.update(changes)
        store = Store(state, clock=lambda: 100)
        job = store.create('watch', spec)
        return old, store, job

    def planned(self, store, old, *, now=110):
        return restart.plan(store.db, old, binding(A), self.backend, now=now, preview='fixture-preview')

    def recover(self, api, mode):
        status = api.status(mode=mode)
        token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
        return token, json.loads(api.recover(expected_preview=token, confirm=True, mode=mode))

    def test_quarantine_preserves_expired_lost_source_and_restores_fresh_control(self):
        old, store, job = self.watch(peer=False)
        store.source(job, 'lost', 'fixture missing final command receipt')
        store.expire(job)
        store.db.execute('INSERT INTO model_refs VALUES (?,?,?,?,?)', ('watch', 'w7', job, None, 'fixture source'))
        store.close()
        original = (self.root / A / 'journal.sqlite3').read_bytes()
        with self.make_recovery() as api:
            self.assertIn('rollover_refused', api.status())
            token, receipt = self.recover(api, 'quarantine')
            self.assertEqual(json.loads(api.recover(expected_preview=token, confirm=True, mode='quarantine')), receipt)
        self.assertFalse(receipt['intent_migrated'])
        self.assertFalse(receipt['native_input_submitted'])
        self.assertFalse(receipt['sources_started'])
        self.assertIn('unresolved_source_owner', receipt['quarantined_blockers'])
        archive = owners.archive_entries(self.root, A)[0][1]
        self.assertEqual((archive / 'source/journal.sqlite3').read_bytes(), original)
        self.assertEqual((self.root / A / 'journal.sqlite3').read_bytes(), original)
        self.assertIn('surviving external effects remain unknown', owners.history_summary(self.root, A))
        context = {'thread_id': A, 'turn_id': recovery_tests.TURN_A}
        with ModelAPI(self.root, '/fixture/control', context, client_factory=lambda *a, **kw: self.backend) as api:
            self.assertIn('0 total in history', api.call('watch_list', {}))
            with self.assertRaisesRegex(ValueError, 'historical|archived'):
                api.call('watch_cancel', {'watch': 'w7'})

    def test_resume_uses_fresh_refs_and_original_lease(self):
        old, store, job = self.watch()
        store.source(job, 'lost', 'fixture daemon ended')
        store.db.execute('INSERT INTO model_refs VALUES (?,?,?,?,?)', ('watch', 'w7', job, None, 'fixture peer'))
        store.close()
        with patch('codex_plus.owner_recovery.time.time', return_value=110), self.make_recovery() as api:
            token, receipt = self.recover(api, 'resume')
            self.assertEqual(json.loads(api.recover(expected_preview=token, confirm=True, mode='resume')), receipt)
        self.assertEqual(receipt['continued_registrations'], 1)
        self.assertFalse(receipt['sources_started'])
        state = owners.selected_state(self.root / A)[0]
        fresh = Store(state)
        try:
            new = fresh.jobs()[0]
            self.assertNotEqual(new['id'], job)
            self.assertEqual(new['expires'], 200)
            self.assertEqual(new['spec']['peer'], binding(B))
            self.assertEqual(fresh.events(), [])
        finally:
            fresh.close()
        with ModelAPI(self.root, '/fixture/control', {'thread_id': A, 'turn_id': recovery_tests.TURN_A},
                      client_factory=lambda *a, **kw: self.backend) as api:
            self.assertIn('w8:', api.call('watch_list', {}))
            with self.assertRaisesRegex(ValueError, 'historical|archived'):
                api.call('watch_renew', {'watch': 'w7'})

    def test_quarantine_and_resume_cannot_bypass_owner_writer_scope_or_queue_proofs(self):
        old, store, job = self.watch(peer=False)
        store.source(job, 'lost', 'fixture unknown'); store.close()
        for proof in (False, None):
            for mode in ('quarantine', 'resume'):
                with self.subTest(proof=proof, mode=mode), patch('codex_plus.owner_recovery._process_proof', return_value=proof), self.make_recovery() as api:
                    text = api.status(mode=mode)
                    self.assertIn('state=rollover_refused', text)
                    token = next(line.split('=', 1)[1] for line in text.splitlines() if line.startswith('expected_preview='))
                    with self.assertRaisesRegex(ValueError, 'refused'):
                        api.recover(expected_preview=token, confirm=True, mode=mode)
        self.backend.queues[A] = [{'id': 'foreign queue input'}]
        with self.make_recovery() as api:
            self.assertIn('native_queue_not_empty', api.status(mode='quarantine'))
        self.backend.queues[A] = []
        with (self.root / A / 'owner.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with self.make_recovery() as api:
                self.assertIn('coordinator_or_helper_lock_held', api.status(mode='resume'))
        changed = {**self.backend.identity, 'host': 'different fixture host'}
        self.backend.identity = changed
        self.listener.stop()
        with patch('codex_plus.peers.listener_identity', return_value=changed), self.make_recovery() as api:
            self.assertIn('logical_scope_changed', api.status(mode='quarantine'))

    def test_resume_retry_after_preselection_crash_rejects_modified_staging(self):
        old, store, _job = self.watch(); store.close()
        with patch('codex_plus.owner_recovery.time.time', return_value=110), self.make_recovery() as api:
            status = api.status(mode='resume')
            token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
            with patch.object(owners.Recovery, '_commit_selection', side_effect=RuntimeError('fixture crash')):
                with self.assertRaisesRegex(RuntimeError, 'fixture crash'):
                    api.recover(expected_preview=token, confirm=True, mode='resume')
            self.assertEqual(owners.selected_state(self.root / A)[2], old)
            staged = next((self.root / A / 'incarnations').iterdir())
            changed = Store(staged)
            changed.db.execute('UPDATE jobs SET event_count=event_count+1')
            changed.close()
            with self.assertRaisesRegex(ValueError, 'prepared restart bounds changed'):
                api.recover(expected_preview=token, confirm=True, mode='resume')
            self.assertEqual(owners.selected_state(self.root / A)[2], old)

    def test_stale_watch_inspection_returns_cached_state_without_writes(self):
        old, store, job = self.watch(peer=False)
        store.source(job, 'lost', 'fixture source is unknown'); store.close()
        before = owners._tree_manifest(self.root / A)
        factory = lambda root, socket, context, **kw: ModelAPI(root, socket, context, client_factory=lambda *a, **k: self.backend)
        recovery = lambda root, socket, context: owners.Recovery(root, socket, context, client_factory=lambda *a, **k: self.backend)
        server = Server(self.root, '/fixture/control', api_factory=factory, recovery_factory=recovery)
        with patch('codex_plus.model_server.existing_socket', return_value='/fixture/control'):
            response = server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                'params': {'name': 'watch_list', 'arguments': {}, '_meta': meta()}})['result']
        self.assertFalse(response['isError'])
        self.assertTrue(response['structuredContent']['cached_previous_owner'])
        self.assertIn('fixture source is unknown', response['content'][0]['text'])
        self.assertEqual(owners._tree_manifest(self.root / A), before)
        self.assertFalse(any(method.startswith(('command/', 'turn/', 'thread/resume', 'thread/queue/add')) for method, *_ in self.backend.calls))

    def test_coordinator_releases_writer_and_metadata_before_handoff(self):
        old, store, _job = self.watch(); store.close()
        state = self.root / A
        class FixtureEngine:
            def __init__(self, *args):
                self.generation = 'fixture generation'
                self.successor = binding(A)
            def tick(self): pass
            def close(self): pass
        class FixtureRecovery:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def handoff(inner):
                self.assertFalse((state / 'coordinator.json').exists())
                with (state / 'owner.lock').open('a') as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return {'continued_registrations': 0}
        with patch('codex_plus.cli.Engine', FixtureEngine), patch('codex_plus.owner_recovery.Recovery', FixtureRecovery), \
             patch('codex_plus.cli.signal.signal'), patch('codex_plus.cli.process_identity', return_value={'pid': os.getpid(), 'start_ticks': 'fixture', 'executable': '/fixture/python'}):
            cli.serve(state)
        self.assertEqual(owners.selected_state(state)[2], old)

    def test_delayed_historical_launcher_cannot_reopen_old_journal(self):
        _old, store, job = self.watch(peer=False)
        store.source(job, 'lost', 'fixture uncertain command'); store.expire(job); store.close()
        with self.make_recovery() as api:
            self.recover(api, 'quarantine')
        before = owners._tree_manifest(self.root / A)
        with patch('codex_plus.cli.Store', side_effect=AssertionError('historical Store opened')):
            self.assertIsNone(cli._serve_once(self.root / A))
        self.assertEqual(owners._tree_manifest(self.root / A), before)

    def test_handoff_reenters_same_release_for_each_selected_epoch(self):
        selected = self.root / A / 'incarnations' / 'e-fixture'
        selected.mkdir(parents=True, mode=0o700)
        changed = binding(A)
        class Recovery:
            def __init__(inner, *args, **kwargs): pass
            def __enter__(inner): return inner
            def __exit__(inner, *args): pass
            def handoff(inner): return {'continued_registrations': 1}
        for original, successor in ((self.root / A, selected),
                                    (selected, selected.with_name('e-next'))):
            with self.subTest(state=original.name), \
                 patch('codex_plus.cli._serve_once', side_effect=[changed, None]) as run, \
                 patch('codex_plus.owner_recovery.Recovery', Recovery), \
                 patch('codex_plus.owner_recovery.selected_state', return_value=(successor, None, None, None)), \
                 patch('codex_plus.cli.os.execv') as execute:
                cli.serve(original)
            execute.assert_called_once_with(cli.sys.executable, [cli.sys.executable, '-B',
                str(Path(cli.__file__).resolve().parents[1] / 'scripts/codex-plus-watch'),
                '--state', str(successor), 'serve'])
            self.assertEqual(run.call_count, 1)

    def test_failed_reentry_never_runs_the_selected_epoch_with_old_arguments(self):
        changed = binding(A)
        original = self.root / A
        selected = original / 'incarnations' / 'e-fixture'
        class Recovery:
            def __init__(inner, *args, **kwargs): pass
            def __enter__(inner): return inner
            def __exit__(inner, *args): pass
            def handoff(inner): return {'continued_registrations': 1}
        with patch('codex_plus.cli._serve_once', side_effect=[changed, None]) as run, \
             patch('codex_plus.owner_recovery.Recovery', Recovery), \
             patch('codex_plus.owner_recovery.selected_state', return_value=(selected, None, None, None)), \
             patch('codex_plus.cli.os.execv', side_effect=OSError('synthetic exec refusal')), \
             patch('codex_plus.cli.time.sleep'), patch('sys.stderr'):
            cli.serve(original)
        self.assertEqual([call.args[0] for call in run.call_args_list], [original, original])

    def test_writer_transition_is_separate_from_model_lock_and_exclusive(self):
        with owners.thread_locks(self.root, [A]):
            with owners.writer_transition(self.root, A):
                with self.assertRaises(TimeoutError):
                    with owners.writer_transition(self.root, A, timeout=0):
                        self.fail('second writer transition was admitted')

    def test_explicit_resume_requests_coordinator_after_selection_only(self):
        _old, store, _job = self.watch(); store.close()
        calls = []
        def accepted(state, result):
            self.assertEqual(owners.selected_state(self.root / A)[0], state)
            calls.append(state)
            return {**result, 'state': 'coordinator_requested'}
        with patch('codex_plus.owner_recovery.time.time', return_value=110), self.make_recovery() as api:
            _token, receipt = self.recover(api, 'resume')
            self.assertEqual(calls, [])
            with patch('codex_plus.cli.accepted_coordinator', side_effect=accepted):
                requested = api.start_continuations(receipt)
                self.assertEqual(requested['continuation_coordinator']['state'], 'coordinator_requested')
                self.assertEqual(len(calls), 1)
                api.start_continuations({'mode': 'quarantine', 'continued_registrations': 0})
                self.assertEqual(len(calls), 1)

    def test_monotonic_lease_and_reminder_due_survive_wall_clock_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source'; source.mkdir(mode=0o700)
            wall, mono = [100.0], [0.0]
            store = Store(source, clock=lambda: wall[0], monotonic=lambda: mono[0])
            old = binding(A, pid=2147483000)
            watch = store.create('watch', {'duration': 100, 'peer': {**old, 'thread_id': B}})
            wake = store.create('wake', {'duration': 100, 'after': 50, 'prompt': 'fixture'})
            wall[0], mono[0] = 20.0, 80.0
            prepared = restart.plan(store.db, old, binding(A), self.backend, now=wall[0],
                                    monotonic=mono[0], preview='fixture rollback')
            store.close()
            target = Path(tmp) / 'fresh'; target.mkdir(mode=0o700)
            restart.seed(target, prepared)
            fresh = Store(target, clock=lambda: wall[0], monotonic=lambda: mono[0])
            engine = Engine(fresh, binding(A), EngineBackend(binding(A)), monotonic=lambda: mono[0])
            try:
                with patch.object(engine, '_connect', return_value=False):
                    engine.tick(receive=False)
                    self.assertTrue(all(value == 100 for value in engine.deadlines.values()))
                    self.assertEqual(list(engine.wake_due.values()), [50])
                    mono[0] = 100
                    engine.tick(receive=False)
                self.assertTrue(all(job['intent'] == 'expired' for job in fresh.jobs()))
                self.assertEqual(fresh.events(), [])
            finally:
                engine.close(); fresh.close()

    def test_legacy_missing_or_elapsed_monotonic_anchor_is_quarantined(self):
        old, store, job = self.watch()
        try:
            store.db.execute('UPDATE jobs SET lease_deadline=? WHERE id=?', (10, job))
            prepared = restart.plan(store.db, old, binding(A), self.backend, now=110,
                                    monotonic=11, preview='fixture expired anchor')
            self.assertEqual(prepared['registrations'][0]['reason'], 'original_monotonic_lease_expired')
            store.db.execute('UPDATE jobs SET lease_boot=NULL,lease_deadline=NULL WHERE id=?', (job,))
            self.assertEqual(self.planned(store, old)['registrations'][0]['reason'], 'original_monotonic_lease_unavailable')
            self.assertEqual(self.planned(store, old)['continuations'], [])
        finally:
            store.close()

    def test_resume_retry_rejects_lowered_reference_highwater(self):
        _old, store, job = self.watch()
        store.db.execute('INSERT INTO model_refs VALUES (?,?,?,?,?)', ('watch', 'w7', job, None, 'fixture source'))
        store.close()
        with patch('codex_plus.owner_recovery.time.time', return_value=110), self.make_recovery() as api:
            status = api.status(mode='resume')
            token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
            with patch.object(owners.Recovery, '_commit_selection', side_effect=RuntimeError('fixture crash')):
                with self.assertRaisesRegex(RuntimeError, 'fixture crash'):
                    api.recover(expected_preview=token, confirm=True, mode='resume')
            staged = next((self.root / A / 'incarnations').iterdir())
            changed = Store(staged)
            changed.db.execute("UPDATE model_ref_counters SET next_value=0 WHERE kind='watch'")
            changed.close()
            with self.assertRaisesRegex(ValueError, 'reference high-water counters changed'):
                api.recover(expected_preview=token, confirm=True, mode='resume')

    def test_unmodified_resume_preparation_retries_once_without_event_replay(self):
        _old, store, job = self.watch(); store.close()
        with patch('codex_plus.owner_recovery.time.time', return_value=110), self.make_recovery() as api:
            status = api.status(mode='resume')
            token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
            with patch.object(owners.Recovery, '_commit_selection', side_effect=RuntimeError('fixture crash')):
                with self.assertRaisesRegex(RuntimeError, 'fixture crash'):
                    api.recover(expected_preview=token, confirm=True, mode='resume')
            first = json.loads(api.recover(expected_preview=token, confirm=True, mode='resume'))
            second = json.loads(api.recover(expected_preview=token, confirm=True, mode='resume'))
            self.assertEqual(first, second)
        state = owners.selected_state(self.root / A)[0]
        with owners._state_snapshot(state) as connection:
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM jobs').fetchone()[0], 1)
            self.assertEqual(connection.execute('SELECT COUNT(*) FROM events').fetchone()[0], 0)
        self.assertFalse(any(method.startswith(('command/', 'turn/', 'thread/resume', 'thread/queue/add')) for method, *_ in self.backend.calls))

    def test_stop_during_handoff_does_not_start_a_successor_coordinator(self):
        _old, store, _job = self.watch(); store.close()
        handlers = {}
        def install(sig, handler):
            handlers[sig] = handler
            return signal.SIG_DFL
        class Recovery:
            def __init__(inner, *args, **kwargs): pass
            def __enter__(inner): return inner
            def __exit__(inner, *args): pass
            def handoff(inner):
                handlers[signal.SIGTERM](signal.SIGTERM, None)
                return {'continued_registrations': 1}
        with patch('codex_plus.cli.signal.signal', side_effect=install), \
             patch('codex_plus.cli._serve_once', return_value=binding(A)) as run, \
             patch('codex_plus.owner_recovery.Recovery', Recovery):
            cli.serve(self.root / A)
        self.assertEqual(run.call_count, 1)

    def test_peer_continuation_has_fresh_identity_original_bounds_and_no_event_copy(self):
        old, store, job = self.watch()
        try:
            store.db.execute('UPDATE jobs SET event_count=1,baseline=? WHERE id=?', ('fixture baseline', job))
            plan = self.planned(store, old)
            new = plan['continuations'][0]
            self.assertNotEqual(new['id'], job)
            self.assertEqual(new['expires'], 200)
            self.assertEqual(new['spec']['peer'], binding(B))
            self.assertEqual(plan, self.planned(store, old))
            target = self.root / 'fresh'; target.mkdir(mode=0o700)
            restart.seed(target, plan)
            fresh = Store(target)
            try:
                row = fresh.job(new['id'])
                self.assertEqual((row['created'], row['expires'], row['event_count'], row['baseline']),
                                 (100, 200, 1, 'fixture baseline'))
                self.assertEqual(fresh.events(), [])
                self.assertEqual(row['root_id'], new['id'])
            finally:
                fresh.close()
        finally:
            store.close()
        self.assertFalse(any(method.startswith(('command/', 'turn/', 'thread/resume', 'thread/queue'))
                             for method, *_ in self.backend.calls))

    def test_command_requires_original_resume_policy(self):
        old, store, job = self.watch(peer=False)
        try:
            self.assertEqual(self.planned(store, old)['continuations'], [])
            spec = store.job(job)['spec']; spec['restart'] = 'resume'
            store.db.execute('UPDATE jobs SET spec=? WHERE id=?', (json.dumps(spec), job))
            self.assertEqual(len(self.planned(store, old)['continuations']), 1)
        finally:
            store.close()

    def test_expired_cancelled_exhausted_and_unresolved_lineages_do_not_resume(self):
        for variant in ('expired', 'cancelled', 'exhausted', 'uncertain', 'acknowledged_unknown', 'pending', 'renewal', 'stopped'):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as tmp:
                state = Path(tmp); store = Store(state, clock=lambda: 100)
                old = binding(A, pid=2147483000)
                job = store.create('watch', {'duration': 100, 'event_limit': 2, 'peer': {**old, 'thread_id': B}})
                try:
                    if variant == 'expired':
                        store.expire(job)
                    elif variant == 'cancelled':
                        store.cancel(job)
                    elif variant == 'exhausted':
                        store.db.execute('UPDATE jobs SET event_count=2 WHERE id=?', (job,))
                    elif variant == 'stopped':
                        store.source(job, 'stopped')
                    elif variant == 'renewal':
                        store.request_renewal(job, store.job(job)['spec'])
                    else:
                        event = store.emit(job, json.dumps({key: 'fixture' for key in store.job(job)['spec']['snapshot_fields']}))
                        if variant == 'uncertain':
                            store.uncertain(event, 'fixture lost admission')
                        elif variant == 'acknowledged_unknown':
                            store.admitted(event, 'fixture queue')
                            store.acknowledge(event)
                    self.assertEqual(self.planned(store, old)['continuations'], [])
                finally:
                    store.close()

    def test_unloaded_or_changed_peer_does_not_cold_resume(self):
        old, store, _job = self.watch()
        try:
            del self.backend.rows[B]
            plan = self.planned(store, old)
            self.assertEqual(plan['continuations'], [])
            self.assertIn('peer_not_positively', plan['registrations'][0]['reason'])
            self.assertFalse(any(method == 'thread/resume' for method, *_ in self.backend.calls))
        finally:
            store.close()

    def test_restart_policy_validation(self):
        for value in ('force', True, None):
            with self.assertRaises(ValueError):
                validate_spec('watch', {'command': ['true'], 'cwd': '/', 'restart': value})
        with self.assertRaises(ValueError):
            validate_spec('wake', {'after': 1, 'prompt': 'fixture', 'restart': 'resume'})

    def test_restarted_command_waits_cadence_and_rechecks_native_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock = [0.0]
            store = Store(Path(tmp), clock=lambda: 100, monotonic=lambda: clock[0])
            frozen = binding(A)
            backend = EngineBackend(frozen)
            grant = {'native': {'sandbox': {'type': 'readOnly', 'networkAccess': False},
                                'profile': None, 'cwd': '/'},
                     'request': {'sandboxPolicy': {'type': 'readOnly', 'networkAccess': False}},
                     'source_access': 'session', 'network_access': 'inherit'}
            job = store.create('watch', {'duration': 100, 'command': ['true'], 'cwd': '/',
                'command_interval': 5, 'restart': 'resume', 'execution': grant})
            store.control(job, 'daemon_restart_observation_gap')
            engine = Engine(store, frozen, backend, monotonic=lambda: clock[0])
            try:
                engine.tick(receive=False)
                self.assertEqual(backend.commands, [])
                clock[0] = 4
                engine.tick(receive=False)
                self.assertEqual(backend.commands, [])
                clock[0] = 5
                engine.tick(receive=False)
                self.assertEqual(backend.commands, [])
                self.assertEqual(store.job(job)['source_state'], 'lost')
                self.assertIn('permissions changed', store.job(job)['source_detail'])
            finally:
                engine.close(); store.close()


if __name__ == '__main__':
    unittest.main()
