import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codex_plus.access import configured_mcp, mcp_spec
from codex_plus.engine import Engine
from codex_plus.presentation import render_event
from codex_plus.store import Store
from codex_plus.model import ModelAPI
from test_watch_engine import Backend
import test_model as model_fixtures
from test_peers import A, B, OWNER


class InspectionBackend(Backend):
    def __init__(self, binding):
        super().__init__(binding)
        self.enabled = True

    def call(self, method, params, timeout=None):
        if method == 'mcpServerStatus/list':
            self.calls.append((method, copy.deepcopy(params)))
            return {'data': [{'name': 'metrics', 'tools': {'inspect': {}} if self.enabled else {}}], 'nextCursor': None}
        return super().call(method, params, timeout)


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = 100.0
        self.store = Store(Path(self.tmp.name)/'state', clock=lambda: self.now)
        self.binding = {'thread_id': 'owned', 'requested_socket': '/fixture'}
        self.backend = InspectionBackend(self.binding)
        self.engine = Engine(self.store, self.binding, self.backend, monotonic=lambda: self.now)
        self.addCleanup(self.store.close)
        self.addCleanup(self.engine.close)
        self.spec = {'mcp': mcp_spec('metrics', 'inspect', {'run': 'Lantern'}),
                     'interval': 5, 'duration': 120, 'event_limit': 2, 'notify_end': False}

    def tick(self):
        self.engine.tick(receive=False)

    def test_native_inventory_does_not_invoke_tool_or_claim_approval(self):
        result = configured_mcp(self.backend, self.binding, self.spec['mcp'])
        self.assertTrue(result['uses_model_turn'])
        self.assertEqual([method for method, _ in self.backend.calls], ['mcpServerStatus/list'])
        self.backend.enabled = False
        with self.assertRaisesRegex(ValueError, 'unavailable or disabled'):
            configured_mcp(self.backend, self.binding, self.spec['mcp'])

    def test_scheduled_inspection_has_no_direct_rpc_and_no_backlog_while_handling(self):
        job = self.store.create('watch', self.spec)
        self.tick()
        self.assertEqual(self.store.events(job), [])
        self.now = 105; self.tick()
        event = self.store.events(job)[0]
        self.now = 140; self.tick()
        self.assertEqual(len(self.store.events(job)), 1)
        self.assertEqual(self.backend.commands, [])
        self.assertFalse(any(method == 'mcpServer/tool/call' for method, _ in self.backend.calls))
        event = self.store.events(job)[0]
        self.store.turn_completed(event['turn_id'], 'completed')
        self.store.acknowledge(event['id'])
        self.tick()
        self.now = 144; self.tick()
        self.assertEqual(len(self.store.events(job)), 1)
        self.now = 145; self.tick()
        self.assertEqual(len(self.store.events(job)), 2)

    def test_cancel_consumed_inspection_preserves_turn_and_stops_future_checks(self):
        job = self.store.create('watch', self.spec)
        self.tick(); self.now = 105; self.tick(); self.now = 106; self.tick()
        event = self.store.events(job)[0]
        self.assertIsNotNone(event['turn_id'])
        self.store.cancel(job)
        self.now = 107; self.tick()
        self.now = 150; self.tick()
        self.assertEqual(len(self.store.events(job)), 1)
        self.assertNotIn(job, self.engine.inspections)
        self.assertFalse(any(method == 'turn/interrupt' for method, _ in self.backend.calls))

    def test_interruption_is_a_new_later_check_not_replayed_input(self):
        job = self.store.create('watch', self.spec)
        self.tick(); self.now = 105; self.tick(); self.now = 106; self.tick()
        event = self.store.events(job)[0]
        self.store.turn_completed(event['turn_id'], 'interrupted')
        self.tick(); self.now = 111; self.tick()
        events = self.store.events(job)
        self.assertEqual(len(events), 2)
        self.assertNotEqual(events[0]['id'], events[1]['id'])

    def test_unacknowledged_completed_check_is_lost_instead_of_repeated(self):
        job = self.store.create('watch', self.spec)
        self.tick(); self.now = 105; self.tick(); self.now = 106; self.tick()
        self.store.turn_completed(self.store.events(job)[0]['turn_id'], 'completed')
        self.tick(); self.now = 150; self.tick()
        self.assertEqual(len(self.store.events(job)), 1)
        self.assertEqual(self.store.job(job)['source_state'], 'lost')

    def test_disabled_tool_has_lost_source_receipt_and_zero_admission(self):
        self.backend.enabled = False
        job = self.store.create('watch', self.spec)
        self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'lost')
        self.assertEqual(self.store.events(job), [])
        self.assertEqual(self.backend.queue, [])

    def test_recovery_adopts_pending_inspection_without_another_admission(self):
        job = self.store.create('watch', self.spec)
        self.tick(); self.now = 105; self.tick()
        event = self.store.events(job)[0]
        self.engine.inspections.clear()
        self.store.source(job, 'lost', 'fixture restart')
        self.store.request_recovery(job); self.now = 106; self.tick()
        self.assertEqual(self.engine.inspections[job]['event'], event['id'])
        self.now = 110; self.tick()
        self.assertEqual(len(self.store.events(job)), 1)

    def test_source_identity_and_arguments_cannot_change_through_renewal(self):
        job = self.store.create('watch', self.spec)
        self.store.source(job, 'stopped')
        with self.assertRaisesRegex(ValueError, 'cannot change'):
            self.store.request_renewal(job, {**self.spec, 'mcp': mcp_spec('metrics', 'inspect', {'run': 'other'})})
        self.assertEqual(self.store.renewals(), [])

    def test_mixed_or_nonfinite_source_arguments_create_no_job(self):
        with self.assertRaises(ValueError):
            self.store.create('watch', {**self.spec, 'command': ['true']})
        with self.assertRaises(ValueError):
            mcp_spec('metrics', 'inspect', {'value': float('nan')})
        self.assertEqual(self.store.jobs(), [])

    def test_event_is_readable_and_does_not_embed_raw_tool_arguments(self):
        job = self.store.create('watch', self.spec)
        identity = self.store.emit(job, 'scheduled')
        frame = render_event(self.store.event(identity), self.store.job(job))
        self.assertIn('Scheduled inspection:', frame)
        self.assertIn('watch_inspect', frame)
        self.assertNotIn('{"run"', frame)
        self.assertIn('model turn', frame)


class InspectionModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'model'
        self.backend = model_fixtures.Backend()
        for p in (patch('codex_plus.peers.listener_identity', return_value=dict(OWNER)),
                  patch('codex_plus.cli.Client', side_effect=lambda *a, **k: self.backend),
                  patch('codex_plus.cli.ensure_coordinator')):
            p.start(); self.addCleanup(p.stop)
        original = self.backend.call
        def call(method, params, timeout=None):
            if method == 'mcpServerStatus/list':
                self.backend.calls.append((method, params))
                return {'data': [{'name': 'metrics', 'tools': {'inspect': {}}}], 'nextCursor': None}
            return original(method, params, timeout)
        self.backend.call = call

    def api(self):
        return ModelAPI(self.root, OWNER['requested_socket'],
            {'thread_id': A, 'turn_id': model_fixtures.TURN_A},
            client_factory=lambda *a, **k: self.backend)

    def test_inspection_registration_and_cached_exact_arguments(self):
        with self.api() as api:
            text = api.call('watch_start', {'mcp_server': 'metrics', 'mcp_tool': 'inspect',
                'mcp_arguments': {'run': 'Lantern'}, 'followup': 'Report useful changes'})
            self.assertIn('each uses a model turn', text)
            job = api.store.jobs()[0]
            self.assertEqual(job['spec']['interval'], 30)
            detail = api.call('watch_inspect', {'watch': 'w1'})
            self.assertIn('"run": "Lantern"', detail)
            self.assertFalse(any(method == 'mcpServer/tool/call' for method, _ in self.backend.calls))

    def test_current_event_inspection_uses_native_event_binding(self):
        with self.api() as api:
            api.call('watch_start', {'mcp_server': 'metrics', 'mcp_tool': 'inspect',
                'mcp_arguments': {'run': 'Lantern'}, 'followup': 'Report useful changes'})
            job = api.store.jobs()[0]
            event = api.store.emit(job['id'], 'inspection')
            api.store.admitted(event, 'native-event')
            api.store.link_turn(event, model_fixtures.TURN_A)
            self.assertIn('Lantern', api.call('watch_inspect', {}))
            api.call('watch_cancel', {'watch': 'w1'})
            with self.assertRaisesRegex(ValueError, 'cancelled supervision'):
                api.call('watch_renew', {'watch': 'w1'})

    def test_old_coordinator_holds_registration_and_renewal_without_new_intent(self):
        source = {'mcp_server': 'metrics', 'mcp_tool': 'inspect',
                  'followup': 'Report useful changes'}
        with self.api() as api:
            api.call('watch_start', source)
            with patch('codex_plus.cli.coordinator_info', return_value={
                    'runtime_version': '0.1.0-preview.1'}):
                for name, arguments in (('watch_start', source),
                                        ('watch_renew', {'watch': 'w1'})):
                    with self.assertRaisesRegex(ValueError, 'older runtime'):
                        api.call(name, arguments)
            self.assertEqual(len(api.store.jobs()), 1)
            self.assertEqual(api.store.renewals(), [])


if __name__ == '__main__':
    unittest.main()
