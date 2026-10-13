import copy
from contextlib import closing
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codex_plus.model import MODEL_GUIDANCE, ModelAPI, native_context, tool_definitions, validate_arguments
from codex_plus.model_server import Server
from codex_plus.store import Store
from test_peers import A, B, CHILD, OWNER, ordinary


TURN_A = 'aaaaaaaa-1111-4111-8111-111111111111'
TURN_B = 'bbbbbbbb-1111-4111-8111-111111111111'


def meta(thread=A, turn=TURN_A):
    return {'threadId': thread, 'sessionId': thread, 'x-codex-turn-metadata': {
        'thread_id': thread, 'session_id': thread, 'turn_id': turn}}


class Backend:
    def __init__(self):
        self.identity = dict(OWNER)
        self.rows = {A: ordinary(A, name='coordinator'), B: ordinary(B, name='opaque beta')}
        self.rows[A]['status'] = {'type': 'active', 'activeFlags': []}
        self.turns = {A: [{'id': TURN_A, 'status': 'inProgress', 'items': []}],
                      B: [{'id': TURN_B, 'status': 'completed', 'items': [
                          {'id': 'context', 'type': 'agentMessage', 'phase': 'final_answer',
                           'text': 'I am validating the redwood samples.'}]}]}
        self.calls = []

    def bind(self, identity, timeout=None):
        if identity not in self.rows: raise ValueError('target not loaded')
        return {**OWNER, 'thread_id': identity}

    def call(self, method, params, timeout=None):
        self.calls.append((method, copy.deepcopy(params)))
        if method == 'thread/loaded/list': return {'data': list(self.rows), 'nextCursor': None}
        identity = params['threadId']
        if method == 'thread/read': return {'thread': copy.deepcopy(self.rows[identity])}
        if method == 'thread/goal/get': return {'goal': None}
        if method == 'thread/turns/list': return {'data': copy.deepcopy(self.turns.get(identity, [])[:params['limit']]), 'nextCursor': None}
        raise AssertionError('model reader wrote native state: ' + method)

    def remaining(self, deadline):
        from codex_plus.native import Client
        return Client.remaining(deadline)

    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


class ModelTests(unittest.TestCase):
    def test_annotations_distinguish_passive_reads_from_job_and_message_effects(self):
        tools = {t['name']: t for t in tool_definitions()}
        for name in ('peer_list', 'peer_inspect', 'watch_list', 'message_status', 'wake_list'):
            self.assertTrue(tools[name]['annotations']['readOnlyHint'])
            self.assertFalse(tools[name]['annotations']['destructiveHint'])
        for name in ('watch_start', 'watch_renew', 'watch_cancel', 'watch_recover', 'peer_send', 'event_ack', 'wake_schedule', 'wake_cancel'):
            self.assertFalse(tools[name]['annotations']['readOnlyHint'])
        self.assertTrue(tools['peer_send']['annotations']['destructiveHint'])
        self.assertTrue(tools['watch_cancel']['annotations']['destructiveHint'])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'model'
        self.backend = Backend()
        self.patches = [patch('codex_plus.peers.listener_identity', return_value=dict(OWNER)),
                        patch('codex_plus.cli.Client', side_effect=lambda *a, **k: self.backend),
                        patch('codex_plus.cli.ensure_coordinator')]
        for p in self.patches: p.start(); self.addCleanup(p.stop)

    def tearDown(self): self.tmp.cleanup()

    def api(self, thread=A, turn=TURN_A, **kwargs):
        return ModelAPI(self.root, OWNER['requested_socket'], {'thread_id': thread, 'turn_id': turn},
                        client_factory=lambda *a, **k: self.backend, **kwargs)

    def discover(self, api, display='validation'):
        text = api.call('peer_list', {})
        row = api.store.db.execute("SELECT * FROM model_refs WHERE kind='peer' AND identity=?", (B,)).fetchone()
        if display: api._remember('peer', B, {**OWNER, 'thread_id': B}, display)
        return row['ref'], text

    def test_contextual_discovery_has_agent_context_without_user_prompts_or_ordinary_child_refs(self):
        self.backend.rows[CHILD] = ordinary(CHILD, name='validation')
        self.backend.rows[CHILD].update(source={'subAgent': 'review'}, parentThreadId=B)
        self.backend.turns[B][0]['items'] += [{'id': 'private', 'type': 'userMessage', 'content': [{'text': 'private human input'}]}]
        with self.api() as api:
            ref, text = self.discover(api)
            self.assertIn('redwood samples', text)
            self.assertIn('Delegated children excluded from ordinary peers: 1', text)
            self.assertNotIn('private human input', text)
            self.assertNotIn(B, text)
            self.assertEqual(api.store.db.execute("SELECT COUNT(*) FROM model_refs WHERE identity=?", (CHILD,)).fetchone()[0], 0)
            self.assertIn('redwood samples', api.call('peer_inspect', {'peer': ref}))
        self.assertTrue(all(method in ('thread/loaded/list', 'thread/read', 'thread/turns/list', 'thread/goal/get') for method, _ in self.backend.calls))

    def test_alias_is_persistent_and_never_retargets_after_name_reuse(self):
        with self.api() as api:
            self.discover(api)
        self.backend.rows[CHILD] = ordinary(CHILD, name='opaque beta')
        del self.backend.rows[B]
        with self.api() as api:
            with self.assertRaises(Exception): api.call('watch_start', {'peer': 'validation', 'followup': 'tell me when needed'})
            self.assertEqual(api.store.jobs(), [])
            row = api._reference('peer', 'validation')
            self.assertEqual(json.loads(row['binding'])['thread_id'], B)

    def test_ambiguous_alias_and_unclassified_peer_are_not_selected(self):
        self.backend.rows[CHILD] = ordinary(CHILD, name='second peer')
        with self.api() as api:
            self.discover(api)
            api._remember('peer', CHILD, {**OWNER, 'thread_id': CHILD}, 'validation')
            with self.assertRaises(ValueError): api.call('peer_send', {'peer': 'validation', 'message': 'hello'})
            self.backend.rows[B]['source'] = 'unknown-origin'
            with self.assertRaises(Exception): api.call('peer_inspect', {'peer': 'p1'})
            self.assertEqual(api.store.jobs(), [])

    def test_native_owner_change_refuses_existing_state(self):
        with self.api(): pass
        with patch.object(self.backend, 'bind', return_value={**OWNER, 'pid': 101, 'thread_id': A}):
            with self.assertRaises(Exception): self.api()

    def test_unapproved_caller_does_not_connect_or_create_private_state(self):
        with self.assertRaises(ValueError): self.api(allowed={B})
        self.assertFalse(self.root.exists())
        self.assertEqual(self.backend.calls, [])

    def test_completed_or_changed_calling_turn_cannot_create_intent(self):
        self.backend.turns[A][0]['status'] = 'completed'
        with self.assertRaises(ValueError): self.api()
        self.backend.turns[A][0]['status'] = 'inProgress'
        with self.api() as api:
            self.discover(api)
            self.backend.turns[A][0]['status'] = 'interrupted'
            with self.assertRaises(ValueError): api.call('watch_start', {'peer': 'validation', 'followup': 'watch it'})
            self.assertEqual(api.store.jobs(), [])

    def test_registration_defaults_respect_configured_bounds_and_preserve_peer_identity(self):
        with self.api(max_duration=40, max_events=1) as api:
            self.discover(api)
            text = api.call('watch_start', {'peer': 'validation', 'followup': 'tell me when needed'})
            self.assertIn('Registered w1', text)
            job = api.store.jobs()[0]
            self.assertEqual(job['spec']['duration'], 40)
            self.assertEqual(job['spec']['event_limit'], 1)
            self.assertEqual(job['spec']['peer']['thread_id'], B)
            self.assertTrue(job['spec']['quiet_initial'])
            self.assertNotIn(B, text)
            with self.assertRaises(ValueError): api.call('watch_start', {'peer': 'validation', 'followup': 'watch', 'duration': 41})
            self.assertEqual(len(api.store.jobs()), 1)

    def test_read_only_trial_peer_cannot_receive_a_message(self):
        with self.api(allowed={A}) as api:
            self.discover(api)
            with self.assertRaises(ValueError): api.call('peer_send', {'peer': 'validation', 'message': 'hello'})
        self.assertFalse((self.root / B).exists())

    def test_scoped_request_is_attributed_to_native_caller_and_handler_outcome_is_separate(self):
        with self.api(allowed={A, B}) as api:
            self.discover(api)
            text = api.call('peer_send', {'peer': 'validation', 'message': 'Use smaller batches.', 'kind': 'request'})
            self.assertIn('Registered m1', text)
        with closing(Store(self.root / B)) as recipient:
            event = recipient.events()[0]
            job = recipient.job(event['job_id'])
            self.assertEqual(job['spec']['sender']['thread_id'], A)
            self.assertEqual(job['spec']['message_kind'], 'request')
            self.assertFalse(event['acknowledged'])
            recipient.admitted(event['id'], 'native-message')
        self.backend.rows[B]['status'] = {'type': 'active', 'activeFlags': []}
        self.backend.turns[B] = [{'id': TURN_B, 'status': 'inProgress', 'items': [
            {'id': 'native-user', 'type': 'userMessage', 'clientId': event['id']}]}]
        with self.api(B, TURN_B, allowed={A, B}) as recipient:
            text = recipient.call('event_ack', {'outcome': 'declined', 'detail': 'Outside my direct task.'})
            self.assertIn('declined', text)
            self.assertEqual(recipient.store.event(event['id'])['turn_id'], TURN_B)
            self.assertTrue(recipient.store.event(event['id'])['acknowledged'])
            with self.assertRaises(ValueError): recipient.call('event_ack', {'outcome': 'accepted', 'detail': 'different claim'})
        with self.api() as sender:
            receipt = sender.call('message_status', {'message': 'm1'})
            self.assertIn('recipient declined', receipt)
            self.assertIn('not yet known', receipt)
            self.assertIn('does not prove an external effect', receipt)

    def test_human_or_unadmitted_turn_cannot_forge_event_handling(self):
        with self.api() as api:
            with self.assertRaises(ValueError): api.call('event_ack', {})
            job = api.store.create('message', {'prompt': 'hello'})
            event = api.store.emit(job, 'hello', 'message')
            self.backend.turns[A][0]['items'] = [{'type': 'userMessage', 'clientId': event}]
            with self.assertRaises(ValueError): api.call('event_ack', {})
            self.assertIsNone(api.store.event(event)['turn_id'])
            self.assertFalse(api.store.event(event)['acknowledged'])

    def test_known_consumed_turn_receipt_cannot_be_overwritten_by_replayed_input(self):
        with self.api() as api:
            job = api.store.create('message', {'prompt': 'hello'})
            event = api.store.emit(job, 'hello', 'message')
            api.store.admitted(event, 'native-message')
            api.store.link_turn(event, TURN_B)
            self.backend.turns[A][0]['items'] = [{'type': 'userMessage', 'clientId': event}]
            with self.assertRaises(ValueError): api.call('event_ack', {})
            self.assertEqual(api.store.event(event)['turn_id'], TURN_B)

    def test_cancelled_auto_update_cannot_register_fresh_watch_or_send(self):
        with self.api() as api:
            self.discover(api)
            api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
            job = api.store.jobs()[0]
            snapshot = {'peer_id': B, 'coverage': {}, 'task_outcome': 'unknown',
                        'reply': [], 'needs_input': [], 'goal': None}
            api.store.emit(job['id'], json.dumps(snapshot))
            snapshot['reply'] = [{'text': 'update'}]
            event = api.store.emit(job['id'], json.dumps(snapshot))
            api.store.admitted(event, 'native-event')
            api.store.link_turn(event, TURN_A)
            api.store.cancel(job['id'])
            with self.assertRaises(ValueError): api.call('watch_start', {'peer': 'validation', 'followup': 'restart'})
            with self.assertRaises(ValueError): api.call('peer_send', {'peer': 'validation', 'message': 'work'})
            self.assertEqual(len(api.store.jobs()), 1)

    def test_cancel_pending_renewal_reference_cancels_exact_lineage(self):
        with self.api() as api:
            self.discover(api)
            api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
            parent = api.store.jobs()[0]
            child = api.store.request_renewal(parent['id'], parent['spec'])
            api._remember('watch', child)
            with patch('codex_plus.cli.coordinator_info', return_value={'pid': 1}):
                api.call('watch_cancel', {'watch': 'w2'})
            self.assertEqual(api.store.job(parent['id'])['intent'], 'cancelled')
            self.assertEqual(api.store.renewal(child)['state'], 'cancelled')

    def test_model_cannot_supply_caller_or_nonfinite_options(self):
        with self.api() as api:
            for args in ({'caller': B}, {'limit': True}, {'limit': 2.5}, {'limit': float('inf')}):
                with self.assertRaises(ValueError): api.call('peer_list', args)
            self.assertEqual(api.store.jobs(), [])

    def test_one_shot_reminder_is_inspectable_and_exactly_cancellable(self):
        with self.api() as api:
            text = api.call('wake_schedule', {'after': 20, 'prompt': 'Reassess the existing fixture.'})
            self.assertIn('t1', text)
            with patch('codex_plus.cli.ensure_coordinator') as start:
                self.assertIn('Reassess the existing fixture', api.call('wake_list', {}))
                start.assert_not_called()
            api.call('wake_cancel', {'wake': 't1'})
            self.assertEqual(api.store.jobs()[0]['intent'], 'cancelled')
            self.assertEqual(api.store.events(), [])

    def test_cancelled_reminder_callback_cannot_create_a_replacement(self):
        with self.api() as api:
            api.call('wake_schedule', {'after': 1, 'prompt': 'Reassess.'})
            job = api.store.jobs()[0]
            event = api.store.emit(job['id'], 'Reassess.', 'wake')
            api.store.admitted(event, 'native-event'); api.store.link_turn(event, TURN_A)
            api.store.cancel(job['id'])
            with self.assertRaises(ValueError): api.call('wake_schedule', {'after': 1, 'prompt': 'Again.'})
            self.assertEqual(len(api.store.jobs()), 1)

    def test_calling_turn_is_rechecked_after_native_validation_before_intent_write(self):
        with self.api() as api:
            with patch('codex_plus.cli.validate_binding', side_effect=lambda root:self.backend.turns[A][0].update(status='interrupted')):
                with self.assertRaises(ValueError): api.call('wake_schedule', {'after': 1, 'prompt': 'Reassess.'})
            self.assertEqual(api.store.jobs(), [])

    def test_lost_watch_requires_explicit_recovery_and_preserves_source_and_gap(self):
        with self.api() as api:
            self.discover(api)
            api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
            job = api.store.jobs()[0]
            api.store.source(job['id'], 'lost')
            with self.assertRaises(ValueError): api.call('watch_renew', {'watch': 'w1'})
            text = api.call('watch_recover', {'watch': 'w1'})
            self.assertIn('gap', text)
            current = api.store.job(job['id'])
            self.assertTrue(current['recover_requested'])
            self.assertEqual(current['spec']['peer']['thread_id'], B)
            self.assertEqual(len(api.store.jobs()), 1)

    def test_coordinator_startup_failure_keeps_one_durable_watch_and_reminder_reference(self):
        with self.api() as api:
            self.discover(api)
            with patch('codex_plus.cli.ensure_coordinator', side_effect=TimeoutError('startup unknown')):
                watch = api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
                wake = api.call('wake_schedule', {'after': 20, 'prompt': 'Reassess.'})
            for text in (watch, wake): self.assertIn('Do not repeat registration', text)
            self.assertIn('w1', api.call('watch_list', {}))
            self.assertIn('t1', api.call('wake_list', {}))
            self.assertEqual(len(api.store.jobs()), 2)


class ProtocolTests(unittest.TestCase):
    def test_native_context_refuses_missing_conflicting_or_body_supplied_identity(self):
        self.assertEqual(native_context(meta()), {'thread_id': A, 'turn_id': TURN_A})
        for value in (None, {}, {**meta(), 'threadId': B}, {**meta(), 'sessionId': B},
                      {**meta(), 'x-codex-turn-metadata': {'thread_id': A, 'session_id': A}}):
            with self.assertRaises(ValueError): native_context(value)

    def test_tools_are_generic_and_protocol_does_not_create_a_native_client_for_discovery(self):
        def forbidden(*args, **kwargs): raise AssertionError('tools/list connected to native runtime')
        server = Server('/private/model', '/private/socket', max_duration=120, max_events=2, api_factory=forbidden)
        output = io.StringIO()
        requests = [ {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
                     {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
                     {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'} ]
        server.serve(io.StringIO('\n'.join(json.dumps(r) for r in requests)), output)
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(replies), 2)
        self.assertEqual(replies[0]['result']['instructions'], MODEL_GUIDANCE)
        tools = replies[1]['result']['tools']
        watch = next(t for t in tools if t['name'] == 'watch_start')
        self.assertEqual(watch['inputSchema']['properties']['duration']['maximum'], 120)
        self.assertNotIn('caller', json.dumps(tools))

    def test_bad_tool_metadata_returns_readable_error_without_native_access(self):
        def forbidden(*args, **kwargs): raise AssertionError('invalid metadata reached native API')
        server = Server('/private/model', '/private/socket', api_factory=forbidden)
        result = server.handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'peer_list', 'arguments': {}}})
        self.assertTrue(result['result']['isError'])
        self.assertEqual(result['result']['content'][0]['type'], 'text')

    def test_oversized_and_malformed_packets_do_not_break_later_protocol_requests(self):
        server = Server('/private/model', '/private/socket')
        output = io.StringIO()
        source = io.StringIO('bad JSON\n' + 'x' * (256 * 1024 + 20) + '\n' + json.dumps({'jsonrpc': '2.0', 'id': 3, 'method': 'ping'}) + '\n')
        server.serve(source, output)
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r.get('error', {}).get('code') for r in replies[:2]], [-32700, -32600])
        self.assertEqual(replies[-1]['result'], {})


if __name__ == '__main__': unittest.main()
