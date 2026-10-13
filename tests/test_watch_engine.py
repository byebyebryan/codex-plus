import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.engine import Engine
from codex_plus.native import RpcError, Client
from codex_plus.store import Store
from codex_plus.access import resolve as source_permissions


class Backend:
    def __init__(self, binding):
        self.binding = binding
        self.events, self.responses, self.process_ids, self.queue = [], {}, set(), []
        self.sequence = 0
        self.commands, self.calls, self.closed = [], [], False
        self.goal = None
        self.runtime = {'type': 'idle'}
        self.add_error = None
        self.start_error = None
        self.source_sandbox = {'type': 'dangerFullAccess'}
        self.source_cwd = '/'

    def bind(self, thread, timeout=None):
        return self.binding

    def submit(self, method, params):
        self.sequence += 1
        self.commands.append((self.sequence, params))
        self.process_ids.add(params['processId'])
        return self.sequence

    def call(self, method, params, timeout=None):
        self.calls.append((method, params))
        if method == 'thread/resume':
            return {'thread': {'id': self.binding['thread_id']}, 'sandbox': self.source_sandbox,
                    'cwd': self.source_cwd, 'activePermissionProfile': None}
        if method == 'thread/read':
            return {'thread': {'id': self.binding['thread_id'], 'canAcceptDirectInput': True, 'status': self.runtime}}
        if method == 'thread/goal/get':
            return {'goal': self.goal}
        if method == 'thread/queue/add':
            if self.add_error:
                raise self.add_error
            row = {'id': 'native-' + params['clientUserMessageId'],
                   'clientUserMessageId': params['clientUserMessageId'], 'input': params['input']}
            self.queue.append(row)
            return {'queuedSubmission': row}
        if method == 'thread/queue/list':
            start = int(params.get('cursor', 0))
            end = start + params['limit']
            return {'data': list(self.queue[start:end]), 'nextCursor': str(end) if end < len(self.queue) else None}
        if method == 'thread/queue/start':
            if self.start_error:
                raise self.start_error
            row = next(row for row in self.queue if row['id'] == params['queuedSubmissionId'])
            self.queue.remove(row)
            return {'turn': {'id': 'turn-' + row['clientUserMessageId']}}
        if method == 'thread/queue/delete':
            self.queue = [row for row in self.queue if row['id'] != params['queuedSubmissionId']]
            return {'deleted': True}
        if method == 'command/exec/terminate':
            for rid, command in self.commands:
                if command['processId'] == params['processId']:
                    self.responses[rid] = {'exitCode': 137}
            return {}
        raise AssertionError(method)

    def result(self, rid):
        return self.responses.pop(rid)

    def close(self):
        self.closed = True

    def receive(self, timeout):
        raise TimeoutError('no fake input')

    def output(self, process, data, *, cap=False):
        self.events.append({'method': 'command/exec/outputDelta', 'params': {
            'processId': process, 'stream': 'stdout', 'deltaBase64': base64.b64encode(data).decode(),
            'capReached': cap}})


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = 100.0
        self.store = Store(self.root / 'state', clock=lambda: self.now)
        self.binding = {'thread_id': 'fixture-thread', 'requested_socket': '/fixture/socket'}
        self.backend = Backend(self.binding)
        self.engine = Engine(self.store, self.binding, self.backend, monotonic=lambda: self.now)
        self.spec = {'command': ['rtk', 'proxy', 'fixture-reader'], 'cwd': str(self.root),
                     'duration': 120, 'event_limit': 2}

    def tearDown(self):
        self.engine.close()
        self.store.close()
        self.tmp.cleanup()

    def tick(self):
        self.engine.tick(receive=False)

    def source(self):
        job = self.store.create('watch', self.spec)
        self.tick()
        return job, self.backend.commands[-1][1]['processId']

    def test_paused_goal_holds_delivery_without_stopping_source(self):
        job, process = self.source()
        self.backend.goal = {'threadId': 'fixture-thread', 'status': 'paused'}
        self.backend.output(process, b'useful\n')
        self.now += 1; self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'running')
        self.assertEqual(self.store.events(job)[0]['delivery'], 'pending')
        self.assertFalse(any(method == 'thread/queue/add' for method, _ in self.backend.calls))
        self.backend.goal['status'] = 'active'
        self.now += 1; self.tick()
        self.assertEqual(self.store.events(job)[0]['delivery'], 'native_queued')
        self.assertFalse(any(method == 'thread/goal/set' for method, _ in self.backend.calls))

    def test_interruption_receipt_does_not_cancel_observation(self):
        job, process = self.source()
        self.backend.events.append({'method': 'turn/completed', 'params': {
            'threadId': 'fixture-thread', 'turn': {'id': 'ordinary-turn', 'status': 'interrupted'}}})
        self.tick()
        self.assertEqual(self.store.job(job)['intent'], 'active')
        self.assertEqual(self.store.job(job)['source_state'], 'starting')

    def test_source_start_receipt_requires_native_output(self):
        job, process = self.source()
        self.assertEqual(self.store.job(job)['source_state'], 'starting')
        self.backend.output(process, b'\n')
        self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'running')
        self.assertEqual(self.store.events(job), [])

    def test_command_exec_uses_resolved_native_permission_request(self):
        self.backend.source_cwd = str(self.root)
        grant = source_permissions(self.backend, self.binding, str(self.root), 'read_only', 'required')
        job = self.store.create('watch', {**self.spec, 'execution': grant})
        self.tick()
        self.assertEqual(self.backend.commands[-1][1]['sandboxPolicy'],
                         {'type': 'readOnly', 'networkAccess': True})
        self.assertEqual(self.store.job(job)['source_state'], 'starting')

    def test_revoked_grant_before_start_holds_only_that_source(self):
        self.backend.source_cwd = str(self.root)
        grant = source_permissions(self.backend, self.binding, str(self.root))
        job = self.store.create('watch', {**self.spec, 'execution': grant})
        self.backend.source_sandbox = {'type': 'readOnly', 'networkAccess': False}
        self.tick()
        self.assertEqual(self.backend.commands, [])
        self.assertEqual(self.store.job(job)['source_state'], 'lost')
        self.assertFalse(self.backend.closed)

    def test_permission_change_stops_source_and_ignores_late_output(self):
        self.backend.source_cwd = str(self.root)
        grant = source_permissions(self.backend, self.binding, str(self.root))
        job = self.store.create('watch', {**self.spec, 'execution': grant})
        self.tick()
        process = self.backend.commands[-1][1]['processId']
        self.backend.events.append({'method': 'thread/settings/updated', 'params': {
            'threadId': self.binding['thread_id'], 'threadSettings': {
                'sandboxPolicy': {'type': 'readOnly', 'networkAccess': False},
                'cwd': str(self.root), 'activePermissionProfile': None}}})
        self.backend.output(process, b'late observation\n')
        self.tick()
        self.assertEqual(self.store.events(job), [])
        self.assertTrue(any(method == 'command/exec/terminate' for method, _ in self.backend.calls))
        self.assertFalse(any(method == 'turn/interrupt' for method, _ in self.backend.calls))

    def test_output_truncation_terminates_source_explicitly(self):
        job, process = self.source()
        self.backend.output(process, b'partial', cap=True)
        self.tick()
        self.assertTrue(any(method == 'command/exec/terminate' for method, _ in self.backend.calls))
        self.assertEqual(self.store.job(job)['source_state'], 'error')
        self.assertEqual(self.store.events(job), [])

    def test_cancel_inflight_native_admission_preserves_truth(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        original = self.backend.call
        def call(method, params, **kwargs):
            result = original(method, params, **kwargs)
            if method == 'thread/queue/add':
                self.store.cancel(job)
            return result
        self.backend.call = call
        self.tick()
        self.assertEqual(self.store.job(job)['intent'], 'cancelled')
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['start_state'], 'withdrawn')
        self.assertEqual(self.backend.queue, [])

    def test_source_error_is_not_watched_job_failure(self):
        job = self.store.create('watch', {**self.spec, 'notify_end': True})
        self.tick()
        rid = self.backend.commands[-1][0]
        self.backend.responses[rid] = {'exitCode': 2}
        self.now += 1; self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'error')
        notice = self.store.events(job)[0]
        self.assertEqual(notice['kind'], 'lifecycle')
        self.assertEqual(json.loads(notice['observation'])['watched_job_outcome'], 'unknown')

    def test_periodic_command_waits_between_runs_and_preserves_snapshot_baseline(self):
        job = self.store.create('watch', {**self.spec, 'command_interval': 5,
            'quiet_initial': True, 'snapshot_fields': ['progress'], 'notify_end': True})
        self.tick()
        first_id, first = self.backend.commands[-1]
        self.backend.output(first['processId'], b'{"progress":0,"revision":0}\n')
        self.backend.responses[first_id] = {'exitCode': 0}
        self.tick()
        self.assertEqual(self.store.events(job), [])
        self.assertEqual(self.store.job(job)['source_state'], 'running')
        self.now = 104; self.tick()
        self.assertEqual(len(self.backend.commands), 1)
        self.now = 105; self.tick()
        second_id, second = self.backend.commands[-1]
        self.assertNotEqual(first['processId'], second['processId'])
        self.backend.output(second['processId'], b'{"progress":1,"revision":1}\n')
        self.backend.responses[second_id] = {'exitCode': 0}
        self.tick()
        self.assertEqual(len(self.store.events(job)), 1)
        self.assertEqual(self.store.events(job)[0]['kind'], 'source')
        self.store.cancel(job); self.now = 110; self.tick()
        self.assertEqual(len(self.backend.commands), 2)

    def test_periodic_command_failure_stops_without_retry_or_model_poll(self):
        job = self.store.create('watch', {**self.spec, 'command_interval': 5})
        self.tick()
        rid = self.backend.commands[-1][0]
        self.backend.responses[rid] = {'exitCode': 1}
        self.tick(); self.now = 110; self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'error')
        self.assertEqual(len(self.backend.commands), 1)

    def test_timeout_after_submission_is_uncertain_and_not_replayed(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.backend.add_error = TimeoutError('lost reply')
        self.tick()
        self.assertEqual(self.store.event(event)['delivery'], 'uncertain')
        self.assertTrue(self.backend.closed)
        replacement = Backend(self.binding)
        self.engine.client = replacement
        self.now += 1; self.tick()
        self.assertFalse(any(method == 'thread/queue/add' for method, _ in replacement.calls))

    def test_uncertain_start_keeps_known_admission(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        self.backend.start_error = TimeoutError('start reply lost')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')
        self.assertEqual(self.store.event(event)['start_state'], 'unknown')

    def test_busy_start_refusal_and_earlier_user_input_are_preserved(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.backend.queue.append({'id': 'human-first', 'clientUserMessageId': 'human', 'input': []})
        self.tick(); self.now += 1; self.tick()
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))
        self.backend.queue.pop(0)
        self.backend.start_error = RpcError('thread already has an active or pending turn')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['start_state'], 'pending')
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')

    def test_live_correlation_does_not_claim_acknowledgement(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        self.backend.events.extend([
            {'method': 'item/started', 'params': {'threadId': 'fixture-thread', 'turnId': 'turn',
                'item': {'type': 'userMessage', 'clientId': event}}},
            {'method': 'turn/completed', 'params': {'threadId': 'fixture-thread',
                'turn': {'id': 'turn', 'status': 'completed'}}}])
        self.tick()
        receipt = self.store.event(event)
        self.assertEqual(receipt['turn_outcome'], 'completed')
        self.assertFalse(receipt['acknowledged'])

    def test_source_renewal_has_no_overlap(self):
        parent, process = self.source()
        child = self.store.request_renewal(parent, self.spec)
        self.now += 1; self.tick()
        self.now += 1; self.tick()
        self.assertEqual(self.store.job(parent)['source_state'], 'stopped')
        self.assertEqual(self.store.job(child)['source_state'], 'pending')
        self.now += 1; self.tick()
        self.assertEqual(len(self.engine.sources), 1)
        self.assertIn(child, self.engine.sources)

    def test_cancel_during_queue_inspection_prevents_start(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        original = self.backend.call
        def call(method, params, **kwargs):
            result = original(method, params, **kwargs)
            if method == 'thread/queue/list':
                self.store.cancel(job)
            return result
        self.backend.call = call
        self.now += 1; self.tick()
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))
        self.assertEqual(self.store.event(event)['start_state'], 'withdrawn')

    def test_expired_admission_is_withdrawn_without_losing_receipt(self):
        timer = self.store.create('wake', {'after': 0, 'duration': 2, 'prompt': 'fixture'})
        self.tick()
        event = self.store.events(timer)[0]
        self.now += 3; self.tick()
        receipt = self.store.event(event['id'])
        self.assertEqual(receipt['delivery'], 'native_queued')
        self.assertEqual(receipt['start_state'], 'withdrawn')
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))

    def test_pending_notice_expires_without_native_connection(self):
        job = self.store.create('watch', {**self.spec, 'notify_end': True})
        event = self.store.notice(job, 'source_error')
        self.engine.client = None
        self.engine.next_connect = self.now + 1000
        self.now += 31; self.tick()
        self.assertEqual(self.store.event(event)['delivery'], 'expired')

    def test_registration_during_native_receive_gets_a_deadline(self):
        created = []
        def receive(timeout):
            created.append(self.store.create('watch', self.spec))
            raise TimeoutError('fixture receive timeout')
        self.backend.receive = receive
        self.engine.tick()
        self.assertEqual(self.store.job(created[0])['source_state'], 'starting')
        self.assertIn(created[0], self.engine.sources)
        self.assertFalse(self.backend.closed)

    def test_cancel_unknown_start_withdraws_owned_pending_input(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        self.backend.start_error = TimeoutError('start reply lost')
        self.now += 1; self.tick()
        queued = list(self.backend.queue)
        self.store.cancel(job)
        self.backend = Backend(self.binding)
        self.backend.queue = queued
        self.engine.client = self.backend
        self.now += 1; self.tick()
        self.assertEqual(self.backend.queue, [])
        self.assertEqual(self.store.event(event)['start_state'], 'withdrawn')

    def test_renewal_deadline_settles_even_without_native_connection(self):
        parent = self.store.create('watch', self.spec)
        child = self.store.request_renewal(parent, self.spec)
        self.engine.client = None
        self.engine.next_connect = self.now + 1000
        self.tick(); self.now += 11; self.tick()
        self.assertEqual(self.store.renewal(child)['state'], 'expired')
        self.assertEqual(self.store.job(parent)['intent'], 'active')

    def test_clock_rollback_does_not_extend_renewal_handshake(self):
        parent = self.store.create('watch', self.spec)
        child = self.store.request_renewal(parent, self.spec)
        self.engine.client = None; self.engine.next_connect = self.now + 1000
        self.tick()
        self.store.clock = lambda: 50
        self.now += 11; self.tick()
        self.assertEqual(self.store.renewal(child)['state'], 'expired')

    def cancelled_admission(self, *, unknown=True):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        if unknown:
            self.store.db.execute("UPDATE events SET start_state='unknown' WHERE id=?", (event,))
        self.store.cancel(job)
        return job, event

    def test_owned_entry_beyond_first_page_is_withdrawn_and_foreign_entries_stay(self):
        _, event = self.cancelled_admission()
        foreign = [{'id': 'human-' + str(n), 'clientUserMessageId': 'foreign-' + str(n)} for n in range(101)]
        self.backend.queue = foreign + self.backend.queue
        self.now += 1; self.tick()
        self.assertEqual(self.backend.queue, foreign)
        self.assertEqual(self.store.event(event)['withdraw_state'], 'withdrawn')
        self.assertTrue(any(method == 'thread/queue/list' and 'cursor' in params for method, params in self.backend.calls))

    def test_later_owned_entry_is_not_started_past_human_input(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.backend.queue = [{'id': 'human-' + str(n), 'clientUserMessageId': 'human'} for n in range(101)]
        self.tick(); self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['start_state'], 'pending')
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))

    def test_absent_input_keeps_start_uncertainty_and_admission(self):
        _, event = self.cancelled_admission()
        self.backend.queue = []
        self.now += 1; self.tick()
        receipt = self.store.event(event)
        self.assertEqual(receipt['delivery'], 'native_queued')
        self.assertEqual(receipt['start_state'], 'unknown')
        self.assertEqual(receipt['withdraw_state'], 'not_pending')
        self.assertIsNone(receipt['turn_outcome'])

    def test_known_consumed_turn_is_preserved_during_cancel(self):
        _, event = self.cancelled_admission()
        self.store.link_turn(event, 'owned-running-turn')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'consumed')
        self.assertFalse(any(method == 'thread/queue/delete' for method, _ in self.backend.calls))
        self.assertFalse(any(method == 'turn/interrupt' for method, _ in self.backend.calls))

    def test_incomplete_queue_scan_stays_unknown_without_deletion(self):
        _, event = self.cancelled_admission()
        original = self.backend.call
        def call(method, params, **kwargs):
            if method == 'thread/queue/list': return {'data': [], 'nextCursor': 'repeated'}
            return original(method, params, **kwargs)
        self.backend.call = call
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'unknown')
        self.assertEqual(self.store.event(event)['start_state'], 'unknown')
        self.assertFalse(any(method == 'thread/queue/delete' for method, _ in self.backend.calls))

    def test_changed_binding_refuses_withdrawal(self):
        _, event = self.cancelled_admission()
        self.backend.binding = {**self.binding, 'owner': 'different'}
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'unknown')
        self.assertFalse(any(method == 'thread/queue/delete' for method, _ in self.backend.calls))

    def test_delete_consume_race_does_not_claim_withdrawal(self):
        _, event = self.cancelled_admission()
        original = self.backend.call
        def call(method, params, **kwargs):
            if method == 'thread/queue/delete':
                self.backend.queue = []
                return {'deleted': False}
            return original(method, params, **kwargs)
        self.backend.call = call
        self.now += 1; self.tick()
        receipt = self.store.event(event)
        self.assertEqual(receipt['withdraw_state'], 'unknown')
        self.assertEqual(receipt['start_state'], 'unknown')

    def test_shutdown_withdraws_owned_input_and_preserves_foreign_queue(self):
        _, event = self.cancelled_admission()
        foreign = {'id': 'human', 'clientUserMessageId': 'other'}
        self.backend.queue.insert(0, foreign)
        self.engine.close()
        self.assertEqual(self.backend.queue, [foreign])
        self.assertEqual(self.store.event(event)['withdraw_state'], 'withdrawn')
        self.assertTrue(self.backend.closed)

    def test_offline_cleanup_connects_without_resuming_or_starting_sources(self):
        _, event = self.cancelled_admission()
        self.engine.client = None
        with patch('codex_plus.engine.Client', return_value=self.backend) as connect:
            self.engine.close()
        connect.assert_called_once()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'withdrawn')
        self.assertFalse(any(method in ('thread/resume', 'thread/queue/start', 'thread/goal/set') for method, _ in self.backend.calls))

    def test_shutdown_budget_is_shared_across_events(self):
        job = self.store.create('watch', self.spec)
        first = self.store.emit(job, 'first'); second = self.store.emit(job, 'second')
        self.tick(); self.store.cancel(job)
        original = self.backend.call
        attempts = []
        def call(method, params, **kwargs):
            if method == 'thread/queue/list':
                attempts.append(kwargs['timeout']); self.now += kwargs['timeout']
                raise TimeoutError('native reply absent')
            return original(method, params, **kwargs)
        self.backend.call = call
        self.engine.close()
        self.assertEqual(len(attempts), 1)
        self.assertLessEqual(attempts[0], 5)
        self.assertEqual(self.store.event(first)['withdraw_state'], 'unknown')
        self.assertEqual(self.store.event(second)['withdraw_state'], 'unknown')

    def test_protocol_heartbeats_do_not_extend_receive_deadline(self):
        client = Client.__new__(Client)
        client.sock = Mock()
        client.buffer = b'\x89\x00' * 10
        client.fragments = bytearray()
        with patch('codex_plus.native.time.monotonic', side_effect=[0, .1, .5, 1.1]):
            with self.assertRaises(TimeoutError): client.receive(1)
        self.assertEqual(client.sock.sendall.call_count, 2)

    def test_queue_timeout_and_foreign_same_native_id_are_not_retracted(self):
        _, event = self.cancelled_admission()
        self.backend.queue[0]['clientUserMessageId'] = 'foreign'
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'not_pending')
        self.assertTrue(self.backend.queue)
        original = self.backend.call
        def call(method, params, **kwargs):
            if method == 'thread/queue/list': raise TimeoutError('queue read timed out')
            return original(method, params, **kwargs)
        self.backend.call = call
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'unknown')
        self.assertFalse(any(method == 'thread/queue/delete' for method, _ in self.backend.calls))

    def test_queue_page_bound_is_unknown_and_does_not_delete(self):
        _, event = self.cancelled_admission()
        foreign = [{'id': 'foreign-' + str(n), 'clientUserMessageId': 'foreign'} for n in range(2000)]
        self.backend.queue = foreign + self.backend.queue
        self.now += 1; self.tick()
        receipt = self.store.event(event)
        self.assertEqual(receipt['withdraw_state'], 'unknown')
        self.assertIn('bound', receipt['withdraw_detail'])
        self.assertFalse(any(method == 'thread/queue/delete' for method, _ in self.backend.calls))

    def test_stop_reply_after_monotonic_deadline_cannot_create_child(self):
        parent, _ = self.source()
        child = self.store.request_renewal(parent, self.spec)
        original = self.backend.call
        def call(method, params, **kwargs):
            result = original(method, params, **kwargs)
            if method == 'command/exec/terminate':
                self.now += 11
                self.store.clock = lambda: 100  # Wall clock did not advance.
            return result
        self.backend.call = call
        self.tick()
        self.assertEqual(self.store.renewal(child)['state'], 'expired')
        with self.assertRaises(ValueError): self.store.job(child)

    def test_registration_expired_during_receive_does_not_start_a_source(self):
        created = []
        def receive(timeout):
            created.append(self.store.create('watch', {**self.spec, 'duration': 1}))
            self.now += 2
            raise TimeoutError('fixture receive delayed')
        self.backend.receive = receive
        self.engine.tick()
        self.assertEqual(self.store.job(created[0])['intent'], 'expired')
        self.assertEqual(self.backend.commands, [])

    def test_offline_known_consumed_receipt_needs_no_native_connection(self):
        _, event = self.cancelled_admission()
        self.store.link_turn(event, 'already-consumed')
        self.engine._disconnect('fixture owner stopped')
        with patch('codex_plus.engine.Client') as connect:
            self.engine.close()
        connect.assert_not_called()
        self.assertEqual(self.store.event(event)['withdraw_state'], 'consumed')

    def test_slow_rpc_send_does_not_reset_response_deadline(self):
        now = [100.0]
        class SlowPeer:
            def settimeout(self, value): self.timeout = value
            def sendall(self, data): now[0] += 3
            def recv(self, count):
                delay = 3
                if self.timeout < delay:
                    now[0] += self.timeout
                    raise TimeoutError('response exceeded remaining budget')
                now[0] += delay
                payload = b'{"id":1,"result":{}}'
                return b'\x81' + bytes([len(payload)]) + payload
        client = Client.__new__(Client)
        client.sock = SlowPeer(); client.sequence = 0
        client.buffer = b''; client.fragments = bytearray()
        client.responses = {}; client.events = []; client.process_ids = set(); client.thread_id = None
        with patch('codex_plus.native.time.monotonic', side_effect=lambda:now[0]):
            with self.assertRaises(TimeoutError): client.call('fixture', {}, timeout=5)
        self.assertLessEqual(now[0] - 100, 5)


if __name__ == '__main__':
    unittest.main()
