import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.engine import Engine
from codex_plus.store import Store
from test_peers import A, B, CHILD, OWNER, ordinary
from test_watch_engine import Backend as QueueBackend


class Backend(QueueBackend):
    def __init__(self, binding):
        super().__init__(binding)
        self.identity = dict(OWNER)
        self.peer = ordinary(B)
        self.peer_loaded = True
        self.peer_goal = None
        self.peer_turns = []

    def call(self, method, params, timeout=None):
        if method == 'thread/loaded/list':
            self.calls.append((method, copy.deepcopy(params)))
            return {'data': [A, B] if self.peer_loaded else [A], 'nextCursor': None}
        if params.get('threadId') == B:
            self.calls.append((method, copy.deepcopy(params)))
            if method == 'thread/read':
                return {'thread': copy.deepcopy(self.peer)}
            if method == 'thread/goal/get':
                return {'goal': copy.deepcopy(self.peer_goal)}
            if method == 'thread/turns/list':
                return {'data': copy.deepcopy(self.peer_turns[:params['limit']]), 'nextCursor': None}
            raise AssertionError('write to observed peer: ' + method)
        result = super().call(method, params, timeout)
        if method == 'thread/read':
            result['thread'].update(source='vscode', parentThreadId=None)
        return result

    def reply(self, text, identity='reply'):
        self.peer_turns = [{'id': 'turn-' + identity, 'status': 'completed', 'items': [
            {'id': identity, 'type': 'agentMessage', 'phase': 'final_answer', 'text': text}]}]


class PeerWatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.now = 100.
        self.store = Store(Path(self.tmp.name) / 'state', clock=lambda: self.now)
        self.binding = {**OWNER, 'thread_id': A}
        self.backend = Backend(self.binding)
        self.patch = patch('codex_plus.peers.listener_identity', return_value=dict(OWNER))
        self.patch.start(); self.addCleanup(self.patch.stop)
        self.engine = Engine(self.store, self.binding, self.backend, monotonic=lambda: self.now)
        self.spec = {'peer': {**OWNER, 'thread_id': B}, 'interval': 5, 'duration': 120,
                     'event_limit': 2, 'signals': ['reply'], 'quiet_initial': True}

    def tearDown(self):
        self.engine.close(); self.store.close(); self.tmp.cleanup()

    def tick(self):
        self.engine.tick(receive=False)

    def watch(self):
        job = self.store.create('watch', self.spec)
        self.tick(); self.tick()
        return job

    def advance(self, seconds=5):
        self.now += seconds; self.tick()

    def test_quiet_baseline_material_reply_and_cancel_never_write_to_peer(self):
        job = self.watch()
        self.assertEqual(self.store.events(job), [])
        self.assertTrue(self.store.job(job)['baseline'])
        self.backend.peer['updatedAt'] += 10
        self.advance()
        self.assertEqual(self.store.events(job), [])
        self.backend.reply('done')
        self.advance()
        events = self.store.events(job)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['delivery'], 'native_queued')
        self.store.cancel(job); self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'stopped')
        self.assertEqual(self.backend.commands, [])
        peer_calls = {method for method, params in self.backend.calls if params.get('threadId') == B}
        self.assertTrue(peer_calls <= {'thread/read', 'thread/turns/list', 'thread/goal/get'})
        before = len(self.backend.calls)
        self.advance()
        self.assertFalse(any(params.get('threadId') == B for _, params in self.backend.calls[before:]))

    def test_busy_and_goal_held_destination_do_not_stop_observation_or_change_peer(self):
        job = self.watch()
        self.backend.runtime = {'type': 'active', 'activeFlags': []}
        self.backend.reply('one'); self.advance()
        event = self.store.events(job)[0]
        self.assertEqual(event['delivery'], 'native_queued')
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))
        self.backend.goal = {'threadId': A, 'status': 'paused'}
        self.backend.reply('two', 'reply-two'); self.advance()
        self.assertEqual(self.store.events(job)[1]['delivery'], 'pending')
        self.assertEqual(self.store.job(job)['source_state'], 'running')
        self.assertFalse(any(method == 'thread/goal/set' for method, _ in self.backend.calls))

    def test_unavailable_peer_requires_explicit_recovery_with_gap_and_same_identity(self):
        job = self.watch()
        self.backend.peer_loaded = False; self.advance()
        self.assertEqual(self.store.job(job)['source_state'], 'lost')
        baseline = self.store.job(job)['baseline']
        self.backend.peer_loaded = True; self.backend.reply('after gap')
        self.advance()
        self.assertEqual(self.store.job(job)['baseline'], baseline)
        self.store.request_recovery(job); self.tick(); self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'running')
        self.assertIn('"observation_gap":true', self.store.events(job)[0]['observation'])
        self.assertEqual(self.store.job(job)['spec']['peer'], self.spec['peer'])

    def test_no_peer_write_or_implicit_recovery_after_provenance_changes(self):
        job = self.watch()
        self.backend.peer.update(source={'subAgent': 'review'}, parentThreadId=A)
        self.advance()
        self.assertEqual(self.store.job(job)['source_state'], 'lost')
        self.assertEqual(self.store.events(job), [])
        self.backend.peer = ordinary(B); self.advance()
        self.assertEqual(self.store.job(job)['source_state'], 'lost')

    def test_renewal_preserves_peer_identity_and_one_reader(self):
        parent = self.watch()
        with self.assertRaises(ValueError):
            self.store.request_renewal(parent, {**self.spec, 'peer': {**OWNER, 'thread_id': CHILD}})
        child = self.store.request_renewal(parent, self.spec)
        self.tick(); self.tick()
        self.assertEqual(self.store.job(parent)['intent'], 'replaced')
        self.assertEqual(list(self.engine.peer_polls), [child])
        self.store.cancel(parent); self.tick()
        self.assertEqual(self.engine.peer_polls, {})
        self.assertEqual(self.store.job(child)['intent'], 'cancelled')

    def test_cancellation_during_native_read_prevents_event_admission(self):
        job = self.watch(); self.backend.reply('race')
        original = self.backend.call
        def call(method, params, timeout=None):
            result = original(method, params, timeout)
            if method == 'thread/turns/list':
                self.store.cancel(job)
            return result
        self.backend.call = call; self.advance()
        self.assertEqual(self.store.events(job), [])
        self.assertEqual(self.store.job(job)['intent'], 'cancelled')
        self.assertEqual(self.engine.peer_polls, {})

    def test_monotonic_expiry_after_read_prevents_late_event(self):
        job = self.watch(); self.backend.reply('late')
        original = self.backend.call
        def call(method, params, timeout=None):
            result = original(method, params, timeout)
            if method == 'thread/turns/list':
                self.now += 121
            return result
        self.backend.call = call
        self.tick()
        self.advance()
        self.assertEqual(self.store.events(job), [])
        # RPC deadline failure can mark loss first; next tick must settle expiry.
        self.tick()
        self.assertEqual(self.store.job(job)['intent'], 'expired')

    def test_same_session_and_foreign_owner_are_refused_without_peer_reads(self):
        for peer in ({**OWNER, 'thread_id': A}, {**OWNER, 'pid': 101, 'thread_id': B}):
            job = self.store.create('watch', {**self.spec, 'peer': peer})
            self.tick()
            self.assertEqual(self.store.job(job)['source_state'], 'error')
        self.assertFalse(any(params.get('threadId') == B for _, params in self.backend.calls))

    def test_initial_satisfied_reply_can_emit_and_event_limit_stops_only_adapter(self):
        self.backend.reply('already present')
        job = self.store.create('watch', {**self.spec, 'quiet_initial': False, 'event_limit': 1})
        self.tick(); self.tick(); self.tick()
        self.assertEqual(len(self.store.events(job)), 1)
        self.assertEqual(self.store.job(job)['source_state'], 'stopped')
        self.assertEqual(self.engine.peer_polls, {})
        self.assertTrue(self.backend.peer_loaded)

    def test_coordinator_loss_preserves_baseline_and_requires_explicit_recovery(self):
        job = self.watch()
        baseline = self.store.job(job)['baseline']
        self.engine._disconnect('fixture connection lost')
        self.assertEqual(self.engine.peer_polls, {})
        self.assertEqual(self.store.job(job)['source_state'], 'lost')
        self.assertEqual(self.store.job(job)['baseline'], baseline)
        self.backend = Backend(self.binding)
        self.engine = Engine(self.store, self.binding, self.backend, monotonic=lambda: self.now)
        self.tick()
        self.assertEqual(self.engine.peer_polls, {})
        self.store.request_recovery(job); self.tick(); self.tick()
        self.assertEqual(len(self.engine.peer_polls), 1)

    def test_message_registration_is_single_admission_and_has_native_correlation(self):
        with self.store.transaction():
            job = self.store.create('message', {'prompt': 'hello', 'followup': 'hello'})
            event = self.store.emit(job, 'hello', 'message')
        self.assertIsNone(self.store.emit(job, 'again', 'message'))
        self.tick(); self.advance(1); self.advance(1)
        self.assertEqual(len([method for method, _ in self.backend.calls if method == 'thread/queue/add']), 1)
        self.assertEqual(self.store.event(event)['turn_id'], 'turn-' + event)
        self.assertEqual(self.store.job(job)['kind'], 'message')

    def test_peer_spec_validation_and_existing_journal_reopen_preserve_receipts(self):
        for changes in ({'interval': 0}, {'turn_limit': 11}, {'signals': ['reply', 'reply']},
                        {'signals': ['bad']}, {'command': ['fixture']}, {'peer': {'thread_id': B}}):
            with self.assertRaises(ValueError):
                self.store.create('watch', {**self.spec, **changes})
        job = self.watch()
        baseline = self.store.job(job)['baseline']
        self.engine.close(); self.store.close()
        self.store = Store(Path(self.tmp.name) / 'state', clock=lambda: self.now)
        self.assertEqual(self.store.job(job)['baseline'], baseline)
        self.assertEqual(self.store.job(job)['spec']['peer'], self.spec['peer'])

    def test_message_provenance_change_holds_start_and_never_reenqueues(self):
        job = self.store.create('message', {'prompt': 'information'})
        event = self.store.emit(job, 'information', 'message')
        self.backend.runtime = {'type': 'active', 'activeFlags': []}
        self.tick()
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')
        original = self.backend.call
        def call(method, params, timeout=None):
            result = original(method, params, timeout)
            if method == 'thread/read' and params.get('threadId') == A:
                result['thread']['source'] = {'subAgent': 'review'}
            return result
        self.backend.call = call
        self.backend.runtime = {'type': 'idle'}; self.advance(1)
        self.assertEqual(self.store.event(event)['start_state'], 'pending')
        self.assertEqual(self.store.job(job)['control_reason'], 'peer_provenance_unavailable')
        self.assertEqual(len([method for method, _ in self.backend.calls if method == 'thread/queue/add']), 1)
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))


if __name__ == '__main__':
    unittest.main()
