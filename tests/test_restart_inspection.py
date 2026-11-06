import json
import unittest

from codex_plus import owner_recovery as owners
from codex_plus.store import Store
import test_owner_recovery as recovery_tests
from test_owner_recovery import A, B, binding


class RestartInspectionTests(unittest.TestCase):
    setUp = recovery_tests.OwnerRecoveryTests.setUp
    tearDown = recovery_tests.OwnerRecoveryTests.tearDown
    legacy_state = recovery_tests.OwnerRecoveryTests.legacy_state
    make_recovery = recovery_tests.OwnerRecoveryTests.make_recovery
    recover_clean = recovery_tests.OwnerRecoveryTests.recover_clean
    recipient_message = recovery_tests.OwnerRecoveryTests.recipient_message

    @staticmethod
    def watch_spec(label):
        return {'command': ['true'], 'cwd': '/', 'duration': 100, 'event_limit': 3,
                'followup': 'fixture follow-up', 'label': label}

    def watch_records(self, *, duplicate_label=False):
        old = binding(A, pid=2147483001, start='12', executable='/fixture/old-codex')
        state = self.legacy_state(A, old, refs=())
        store = Store(state)
        try:
            first = store.create('watch', self.watch_spec('shared label' if duplicate_label else 'first watch'))
            second = store.create('watch', self.watch_spec('shared label' if duplicate_label else 'second watch'))
            store.db.executemany('INSERT INTO model_refs VALUES (?,?,?,?,?)', (
                ('watch', 'w7', first, None, 'shared label' if duplicate_label else 'first watch'),
                ('watch', 'w8', second, None, 'shared label' if duplicate_label else 'second watch')))
        finally:
            store.close()
        return old, first, second, state

    def test_watch_inspect_selects_exact_current_reference_and_is_read_only(self):
        _old, first, second, state = self.watch_records()
        before = owners._tree_manifest(state)
        with self.make_recovery() as api:
            text = api.cached_inspection('watch_inspect', {'watch': 'w7'})
        self.assertIn('Cached watch reference from the selected journal', text)
        self.assertIn(first, text)
        self.assertNotIn(second, text)
        self.assertEqual(owners._tree_manifest(state), before)

    def test_watch_inspect_reports_unavailable_ambiguous_and_unselected_records_honestly(self):
        _old, first, second, _state = self.watch_records(duplicate_label=True)
        with self.make_recovery() as api:
            missing = api.cached_inspection('watch_inspect', {'watch': 'w99'})
            ambiguous = api.cached_inspection('watch_inspect', {'watch': 'shared label'})
            unselected = api.cached_inspection('watch_inspect', {})
        self.assertIn('reference is unavailable', missing)
        self.assertNotIn(first, missing)
        self.assertNotIn(second, missing)
        self.assertIn('ambiguous', ambiguous)
        self.assertNotIn(first, ambiguous)
        self.assertNotIn(second, ambiguous)
        self.assertIn('No exact watch reference was selected', unselected)
        self.assertNotIn(first, unselected)

    def test_ref_shaped_watch_label_is_used_when_no_exact_reference_exists(self):
        _old, first, second, state = self.watch_records()
        store = Store(state)
        try:
            store.db.execute("UPDATE model_refs SET label='w99' WHERE ref='w8'")
        finally:
            store.close()
        with self.make_recovery() as api:
            text = api.cached_inspection('watch_inspect', {'watch': 'w99'})
        self.assertIn(second, text)
        self.assertNotIn(first, text)
        self.assertNotIn('reference is unavailable', text)

    def test_archived_watch_reference_uses_immutable_history(self):
        old, first, _second, _state = self.watch_records()
        store = Store(_state)
        try:
            store.cancel(first)
            store.cancel(_second)
        finally:
            store.close()
        with self.make_recovery() as api:
            self.recover_clean(api)
        with self.make_recovery() as api:
            text = api.cached_inspection('watch_inspect', {'watch': 'w7'})
        self.assertIn('Archived immutable reference', text)
        self.assertIn('"historical": true', text)
        self.assertIn(first, text)

    def test_exact_message_status_reads_current_and_archived_receipts(self):
        old = binding(A, pid=2147483002, start='13', executable='/fixture/old-codex')
        event = self.recipient_message(B, binding(B), old)
        state = self.legacy_state(A, old, refs=(
            ('message', 'm7', event, json.dumps(binding(B)), 'fixture recipient'),))
        before = owners._tree_manifest(state)
        with self.make_recovery() as api:
            current = api.cached_inspection('message_status', {'message': 'm7'})
        self.assertIn('Exact cached outgoing message m7', current)
        self.assertIn('Stored fixture purpose', current)
        self.assertEqual(owners._tree_manifest(state), before)

        with self.make_recovery() as api:
            self.recover_clean(api)
        archive = owners.archive_entries(self.root, A)[0][1]
        archive_before = owners._tree_manifest(archive)
        with self.make_recovery() as api:
            archived = api.cached_inspection('message_status', {'message': 'm7'})
        self.assertIn('verified immutable archive', archived)
        self.assertIn('Stored fixture purpose', archived)
        self.assertEqual(owners._tree_manifest(archive), archive_before)

    def test_message_status_missing_and_unscoped_results_are_truthful_and_bounded(self):
        old = binding(A, pid=2147483003, start='14', executable='/fixture/old-codex')
        state = self.legacy_state(A, old, refs=(
            ('message', 'm7', 'missing-event-1', json.dumps(binding(B)), 'first recipient'),
            ('message', 'm8', 'missing-event-2', json.dumps(binding(B)), 'second recipient')))
        before = owners._tree_manifest(state)
        with self.make_recovery() as api:
            missing = api.cached_inspection('message_status', {'message': 'm99'})
            listing = api.cached_inspection('message_status', {'limit': 1})
        self.assertIn('Exact outgoing message receipt unavailable', missing)
        self.assertIn('do not resend', missing)
        self.assertNotIn('first recipient', missing)
        self.assertIn('selected journal and verified archives', listing)
        self.assertIn('Showing 1 of 2 cached outgoing references', listing)
        self.assertIn('second recipient', listing)
        self.assertNotIn('first recipient', listing)
        self.assertEqual(owners._tree_manifest(state), before)

    def test_unscoped_watch_lists_disclose_unfiltered_selected_journal_scope(self):
        _old, _first, _second, state = self.watch_records()
        with self.make_recovery() as api:
            text = api.cached_inspection('watch_list', {'scope': 'current', 'limit': 1})
        self.assertIn('requested scope=current', text)
        self.assertIn('unfiltered and omits archived journals', text)
        self.assertIn('Showing 1 of 2 selected-journal records', text)
        self.assertIn('current source state', text)


if __name__ == '__main__':
    unittest.main()
