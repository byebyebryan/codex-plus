import copy
from contextlib import closing
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import uuid
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

    def test_reminder_default_covers_delay_and_delivery_window_within_limit(self):
        with self.api(max_duration=1000) as api:
            for after, duration in ((0, 120), (120, 240), (600, 720), (999, 1000)):
                text = api.call('wake_schedule', {'after': after, 'prompt': 'Reassess the fixture.'})
                job = api.store.jobs()[-1]
                self.assertEqual(job['spec']['duration'], duration)
                self.assertAlmostEqual(job['expires'] - job['due'], duration - after)
                self.assertIn('delivery window', text)
            api.call('wake_schedule', {'after': 600, 'duration': 650, 'prompt': 'Explicit window.'})
            self.assertEqual(api.store.jobs()[-1]['spec']['duration'], 650)
            before = len(api.store.jobs())
            for args in ({'after': 1000}, {'after': 600, 'duration': 600},
                         {'after': 600, 'duration': 1001}, {'after': -1}):
                with self.assertRaises(ValueError):
                    api.call('wake_schedule', {**args, 'prompt': 'Invalid.'})
            self.assertEqual(len(api.store.jobs()), before)

    def test_reminder_recap_bounds_settled_history_without_scanning_all_jobs_or_events(self):
        with self.api() as api:
            for number in range(400):
                identity = api.store.create('wake', {'after': 10, 'duration': 20,
                    'prompt': 'Settled synthetic check ' + str(number)})
                api.store.cancel(identity)
            active = api.store.create('wake', {'after': 600, 'duration': 720,
                'prompt': 'Check the pending build'})
            with (patch.object(api.store, 'jobs', side_effect=AssertionError('unbounded jobs')),
                 patch.object(api.store, 'events', side_effect=AssertionError('unbounded events')),
                 patch('codex_plus.cli.ensure_coordinator') as start):
                text = api.call('wake_list', {})
                start.assert_not_called()
            self.assertIn('Check the pending build', text)
            self.assertNotIn('Settled synthetic check', text)
            self.assertIn('Showing 1 of 1 current reminders; 401 total', text)
            self.assertIn('scope=history', text)
            self.assertLess(len(text.encode()), 2500)
            ref = api.store.db.execute("SELECT ref FROM model_refs WHERE kind='wake' AND identity=?", (active,)).fetchone()[0]
        with self.api() as api:
            self.assertIn(ref, api.call('wake_list', {}))
            api.call('wake_cancel', {'wake': ref})
            self.assertEqual(api.store.job(active)['intent'], 'cancelled')

    def test_reminder_pages_cover_history_and_refuse_watch_or_other_scope_cursors(self):
        with self.api() as api:
            api.store.clock = lambda: 100
            identities = set()
            for number in range(7):
                identity = api.store.create('wake', {'after': 10, 'duration': 20, 'prompt': str(number)})
                identities.add(identity)
                if number % 2: api.store.cancel(identity)
            cursor = None
            seen = []
            while True:
                page = api.store.registration_page('wake', scope='history', limit=2, cursor=cursor)
                seen.extend(job['id'] for job in page['registrations'])
                cursor = page['next_cursor']
                if cursor is None: break
            self.assertEqual(set(seen), identities)
            self.assertEqual(len(seen), len(identities))
            page = api.store.registration_page('wake', scope='history', limit=2)
            self.assertIn('next_cursor:', api.call('wake_list', {'scope': 'history', 'limit': 2}))
            with self.assertRaises(ValueError): api.store.watch_page(scope='history', cursor=page['next_cursor'])
            with self.assertRaises(ValueError): api.call('wake_list', {'cursor': page['next_cursor']})
            for options in ({'limit': 0}, {'limit': 51}, {'cursor': 'invalid'}):
                with self.assertRaises(ValueError): api.call('wake_list', options)

    def test_reminder_recap_exposes_overdue_stale_and_uncertain_receipts_without_mutation(self):
        with self.api() as api:
            api.store.clock = lambda: 100
            identity = api.store.create('wake', {'after': 10, 'duration': 20, 'prompt': 'Recheck the build'})
            event = api.store.emit(identity, 'Recheck the build', 'wake')
            api.store.reserve(event)
            api.store.uncertain(event, 'admission reply missing')
            api.store.clock = lambda: 140
            before = api.store.job(identity), api.store.event(event)
            text = api.call('wake_list', {})
            self.assertIn('may be stale', text)
            self.assertIn('due 30.0 seconds ago', text)
            self.assertIn('lease expired 20.0 seconds ago', text)
            self.assertIn('Delivery uncertain', text)
            self.assertIn('admission reply missing', text)
            self.assertIn('not acknowledged', text)
            self.assertEqual(before, (api.store.job(identity), api.store.event(event)))

    def _acknowledged_reminder(self, api, prompt):
        identity = api.store.create('wake', {'after': 0, 'duration': 120, 'prompt': prompt})
        event = api.store.emit(identity, prompt, 'wake')
        turn = str(uuid.uuid4())
        api.store.admitted(event, 'native-' + event)
        api.store.link_turn(event, turn)
        api.store.acknowledge(event)
        api.store.settle(identity)
        return identity, event, turn

    def test_acknowledged_reminder_followups_remain_current_until_native_completion(self):
        with self.api() as api:
            expected = set()
            for outcome in (None, 'completed', 'failed', 'interrupted'):
                identity, event, turn = self._acknowledged_reminder(api, 'Callback ' + str(outcome))
                self.assertEqual(api.store.job(identity)['intent'], 'completed')
                if outcome is not None: api.store.turn_completed(turn, outcome)
                if outcome != 'completed': expected.add(identity)
            before = api.store.jobs(), api.store.events()
            with patch('codex_plus.cli.ensure_coordinator') as start:
                text = api.call('wake_list', {})
                start.assert_not_called()
            for outcome in ('None', 'failed', 'interrupted'):
                self.assertIn('Callback ' + outcome, text)
            self.assertNotIn('Callback completed', text)
            self.assertIn('Follow-up turn pending or outcome unknown', text)
            self.assertIn('Follow-up needs attention: failed', text)
            self.assertIn('Follow-up needs attention: interrupted', text)
            self.assertIn('Showing 3 of 3 current reminders; 4 total', text)
            seen, cursor = [], None
            while True:
                page = api.store.registration_page('wake', limit=2, cursor=cursor)
                seen.extend(job['id'] for job in page['registrations'])
                cursor = page['next_cursor']
                if cursor is None: break
            self.assertEqual(set(seen), expected)
            self.assertEqual(len(seen), len(expected))
            self.assertIn('Callback completed', api.call('wake_list', {'scope': 'history'}))
            self.assertEqual(before, (api.store.jobs(), api.store.events()))

    def test_cancelling_failed_reminder_followups_closes_attention_and_retains_receipts(self):
        with self.api() as api:
            for outcome in ('failed', 'interrupted'):
                with self.subTest(outcome=outcome):
                    prompt = 'Resolve callback ' + outcome
                    identity, event, turn = self._acknowledged_reminder(api, prompt)
                    api.store.turn_completed(turn, outcome, {'message': 'Synthetic callback failure'})
                    self.assertIn(prompt, api.call('wake_list', {}))
                    ref = api._remember('wake', identity)
                    api.call('wake_cancel', {'wake': ref})
                    self.assertNotIn(prompt, api.call('wake_list', {}))
                    history = api.call('wake_list', {'scope': 'history'})
                    for expected in (prompt, 'turn ' + outcome, 'handling acknowledged',
                                     'cached intent cancelled', 'Synthetic callback failure'):
                        self.assertIn(expected, history)
                    self.assertEqual(api.store.event(event)['withdraw_state'], 'consumed')
            self.assertEqual(len(api.store.jobs()), 2)
            self.assertEqual(len(api.store.events()), 2)
            self.assertEqual(api.store.renewals(), [])

    def test_cancelled_consumed_reminder_stays_current_until_its_turn_outcome_is_known(self):
        with self.api() as api:
            identity, event, turn = self._acknowledged_reminder(api, 'Already running callback')
            ref = api._remember('wake', identity)
            api.call('wake_cancel', {'wake': ref})
            text = api.call('wake_list', {})
            self.assertIn('Already running callback', text)
            self.assertIn('cached intent cancelled', text)
            self.assertIn('Follow-up turn pending or outcome unknown', text)
            self.assertEqual(api.store.event(event)['withdraw_state'], 'consumed')
            api.store.turn_completed(turn, 'interrupted')
            self.assertNotIn('Already running callback', api.call('wake_list', {}))
            self.assertIn('turn interrupted', api.call('wake_list', {'scope': 'history'}))
            self.assertEqual(len(api.store.jobs()), 1)
            self.assertTrue(all(method in ('thread/loaded/list', 'thread/read', 'thread/turns/list', 'thread/goal/get')
                                for method, _ in self.backend.calls), self.backend.calls)

    def test_watch_reads_share_freshness_failure_and_handling_receipts_without_source_work(self):
        with self.api() as api:
            self.discover(api)
            api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
            job = api.store.jobs()[0]
            api.store.source(job['id'], 'running', 'HTTP 401 from synthetic endpoint')
            api.store.control(job['id'], 'native control state unavailable')
            event = api.store.notice(job['id'], 'synthetic failure')
            api.store.db.execute("UPDATE events SET delivery='uncertain',detail='admission reply lost' WHERE id=?", (event,))
            with patch('codex_plus.cli.coordinator_info', return_value=None), patch('codex_plus.cli.ensure_coordinator') as start:
                for operation, args in (('watch_list', {}), ('watch_inspect', {'watch': 'w1'})):
                    text = api.call(operation, args)
                    for expected in ('source unknown', 'Last source receipt: running', 'HTTP 401',
                                     'control state unavailable', 'Delivery uncertain', 'not acknowledged', 'admission reply lost'):
                        self.assertIn(expected, text)
                    self.assertNotIn('| source running', text)
                start.assert_not_called()

    def test_watch_history_is_bounded_active_first_and_explicitly_pageable(self):
        with self.api() as api:
            self.discover(api)
            api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
            active = api.store.jobs()[0]
            for index in range(200):
                identity = api.store.create('watch', {**active['spec'], 'label': 'ended-' + str(index)})
                api.store.cancel(identity)
            uncertain = api.store.create('watch', {**active['spec'], 'label': 'unresolved fixture'})
            event = api.store.notice(uncertain, 'synthetic failure')
            api.store.cancel(uncertain)
            api.store.db.execute("UPDATE events SET delivery='uncertain' WHERE id=?", (event,))
            current = api.call('watch_list', {})
            self.assertIn('w1:', current)
            self.assertIn('unresolved fixture', current)
            self.assertNotIn('ended-', current)
            self.assertIn('2 current watches; 202 total', current)
            self.assertLess(len(current), 2000)
            seen, cursor = set(), None
            while True:
                page = api.store.watch_page(scope='history', limit=17, cursor=cursor)
                identities = {row['id'] for row in page['registrations']}
                self.assertFalse(seen & identities)
                seen.update(identities)
                cursor = page['next_cursor']
                if cursor is None: break
            self.assertEqual(len(seen), 202)
            history = api.call('watch_list', {'scope': 'history', 'limit': 5})
            self.assertIn('Showing 5 of 202', history)
            self.assertIn('next_cursor:', history)
            self.assertLess(history.index('w1:'), history.index('ended-'))
            with self.assertRaises(ValueError): api.call('watch_list', {'cursor': 'invalid'})
            with self.assertRaises(ValueError): api.call('watch_list', {'limit': 51})

    def test_renewal_reference_can_be_inspected_before_child_is_created(self):
        with self.api() as api:
            self.discover(api)
            api.call('watch_start', {'peer': 'validation', 'followup': 'watch'})
            parent = api.store.jobs()[0]
            child = api.store.request_renewal(parent['id'], parent['spec'])
            ref = api._remember('watch', child)
            self.assertIn('renewal pending', api.call('watch_inspect', {'watch': ref}))

    def test_sender_cancels_only_its_outgoing_intent_and_retains_handling_receipts(self):
        with self.api(allowed={A,B}) as api:
            self.discover(api)
            api.call('peer_send', {'peer':'validation','message':'Updated fixture.'})
            self.assertIn('Cancellation requested',api.call('message_cancel',{'message':'m1'}))
            self.assertIn('intent cancelled',api.call('message_status',{'message':'m1'}))
            with closing(Store(self.root/B)) as recipient:
                self.assertEqual(recipient.jobs()[0]['intent'],'cancelled')
                self.assertEqual(recipient.events()[0]['delivery'],'cancelled')

    def test_outgoing_cancel_refuses_forged_sender_ownership(self):
        with self.api(allowed={A,B}) as api:
            self.discover(api)
            api.call('peer_send',{'peer':'validation','message':'Updated fixture.'})
            with closing(Store(self.root/B)) as recipient:
                job=recipient.jobs()[0];spec=job['spec'];spec['sender']['thread_id']=CHILD
                recipient.db.execute('UPDATE jobs SET spec=? WHERE id=?',(json.dumps(spec),job['id']))
            with self.assertRaises(ValueError):api.call('message_cancel',{'message':'m1'})
            with self.assertRaises(ValueError):api.call('message_status',{'message':'m1'})
            self.assertIn('this caller does not own', api.call('message_status', {}))
            with closing(Store(self.root/B)) as recipient:self.assertEqual(recipient.jobs()[0]['intent'],'active')

    def test_outgoing_receipts_are_rediscoverable_after_context_loss_and_paginated_without_sends(self):
        with self.api(allowed={A, B}) as api:
            self.discover(api)
            for number in range(23):
                api.call('peer_send', {'peer': 'validation', 'message': 'Synthetic checksum ' + str(number)})
        with closing(Store(self.root / B)) as recipient:
            before = recipient.jobs(), recipient.events()
        with self.api() as api:
            text = api.call('message_status', {})
            self.assertIn('m23: intent', text)
            self.assertIn('m4: intent', text)
            self.assertNotIn('m3: intent', text)
            self.assertIn('Showing 20 of 23', text)
            self.assertIn('next_cursor: m4', text)
            older = api.call('message_status', {'cursor': 'm4'})
            self.assertIn('m3: intent', older)
            self.assertIn('m1: intent', older)
            self.assertNotIn('next_cursor:', older)
            self.assertIn('m1: intent', api.call('message_status', {'message': 'm1'}))
            self.assertEqual(api.store.jobs(), [])
        with closing(Store(self.root / B)) as recipient:
            self.assertEqual(before, (recipient.jobs(), recipient.events()))

    def test_outgoing_discovery_is_scoped_to_its_sender_and_validates_pagination(self):
        with self.api(allowed={A, B}) as api:
            self.discover(api)
            api.call('peer_send', {'peer': 'validation', 'message': 'Synthetic checksum'})
            for args in ({'cursor': 'missing'}, {'limit': 0}, {'limit': 51},
                         {'message': 'm1', 'cursor': 'm1'}):
                with self.assertRaises(ValueError): api.call('message_status', args)
        self.backend.rows[B]['status'] = {'type': 'active', 'activeFlags': []}
        self.backend.turns[B][0]['status'] = 'inProgress'
        with self.api(B, TURN_B) as api:
            self.assertIn('Showing 0 of 0', api.call('message_status', {}))
            with self.assertRaises(ValueError): api.call('message_status', {'message': 'm1'})

    def test_missing_recipient_receipts_remain_unknown_without_recreating_state_or_resending(self):
        with self.api(allowed={A, B}) as api:
            self.discover(api)
            api.call('peer_send', {'peer': 'validation', 'message': 'Synthetic checksum'})
        shutil.rmtree(self.root / B)
        with self.api() as api:
            text = api.call('message_status', {})
            self.assertIn('m1: receipt unavailable', text)
            self.assertIn('Delivery/handling unknown; do not resend', text)
            with self.assertRaises(ValueError): api.call('message_status', {'message': 'm1'})
            self.assertFalse((self.root / B).exists())
            self.assertEqual(api.store.jobs(), [])

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
        for tool in tools:
            self.assertNotIn('caller', tool['inputSchema']['properties'])

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
