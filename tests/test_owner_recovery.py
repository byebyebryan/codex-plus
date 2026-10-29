import fcntl
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import uuid

from codex_plus import owner_recovery as owners
from codex_plus.store import Store
from test_peers import A, B, OWNER


TURN_A = 'aaaaaaaa-1111-4111-8111-111111111111'
TURN_B = 'bbbbbbbb-1111-4111-8111-111111111111'
TURN_OLD = 'cccccccc-1111-4111-8111-111111111111'
EVENT_OLD = 'dddddddd-1111-4111-8111-111111111111'
OTHER = '00000000-0000-4000-8000-000000000009'


def binding(thread, *, pid=900000, start='900', executable='/fixture/new-codex'):
    return {**OWNER, 'uid': os.getuid(), 'pid': pid, 'start_ticks': start,
            'executable': executable, 'thread_id': thread}


def independent(thread):
    return {'id': thread, 'source': 'vscode', 'threadSource': 'user',
            'parentThreadId': None, 'forkedFromId': None, 'name': 'fixture ' + thread[-1],
            'cwd': '/fixture', 'canAcceptDirectInput': True,
            'status': {'type': 'active', 'activeFlags': []}, 'updatedAt': 100}


class Backend:
    def __init__(self):
        self.identity = {key: value for key, value in binding(A).items() if key != 'thread_id'}
        self.rows = {A: independent(A), B: independent(B)}
        self.turns = {
            A: [{'id': TURN_A, 'status': 'inProgress', 'items': []}],
            B: [{'id': TURN_B, 'status': 'inProgress', 'items': []}],
        }
        self.queues = {A: [], B: []}
        self.queue_error = None
        self.calls = []

    def bind(self, thread, timeout=None):
        if thread not in self.rows:
            raise ValueError('thread is not positively loaded')
        return {**self.identity, 'thread_id': thread}

    def call(self, method, params, timeout=None):
        self.calls.append((method, dict(params), timeout))
        thread = params.get('threadId')
        if method == 'thread/loaded/list':
            return {'data': list(self.rows), 'nextCursor': None}
        if method == 'thread/read':
            return {'thread': dict(self.rows[thread])}
        if method == 'thread/turns/list':
            return {'data': list(self.turns.get(thread, []))[:params['limit']], 'nextCursor': None}
        if method == 'thread/queue/list':
            if self.queue_error:
                raise self.queue_error
            return {'data': list(self.queues.get(thread, [])), 'nextCursor': None}
        raise AssertionError('unexpected native operation: ' + method)

    def close(self):
        pass


class OwnerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'model'
        self.root.mkdir(mode=0o700)
        self.backend = Backend()
        self.listener = patch('codex_plus.peers.listener_identity', return_value=self.backend.identity)
        self.listener.start()
        self.addCleanup(self.listener.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def legacy_state(self, thread, frozen, *, refs=(), with_refs=True):
        state = self.root / thread
        state.mkdir(mode=0o700)
        (state / 'binding.json').write_text(json.dumps(frozen, sort_keys=True) + '\n')
        (state / 'binding.json').chmod(0o600)
        store = Store(state)
        try:
            if with_refs:
                store.db.executescript('''
                    CREATE TABLE model_refs (
                        kind TEXT NOT NULL, ref TEXT NOT NULL, identity TEXT NOT NULL,
                        binding TEXT, label TEXT NOT NULL DEFAULT '',
                        PRIMARY KEY(kind,ref), UNIQUE(kind,identity));
                    CREATE TABLE model_responses (
                        event_id TEXT PRIMARY KEY REFERENCES events(id),
                        turn_id TEXT NOT NULL, outcome TEXT NOT NULL, detail TEXT NOT NULL);
                ''')
                for row in refs:
                    store.db.execute('INSERT INTO model_refs(kind,ref,identity,binding,label) VALUES (?,?,?,?,?)', row)
        finally:
            store.close()
        return state

    def make_recovery(self, thread=A, turn=TURN_A):
        return owners.Recovery(self.root, '/fixture/control', {'thread_id': thread, 'turn_id': turn},
            client_factory=lambda *args, **kwargs: self.backend)

    def recipient_message(self, thread, recipient, sender, *, event_id=None,
                          delivery='native_queued', acknowledged=1, withdrawal='none',
                          turn_id=None, turn_outcome=None, intent='completed'):
        state = self.legacy_state(thread, recipient, with_refs=False)
        store = Store(state)
        try:
            job = store.create('message', {'prompt': 'Stored fixture purpose', 'sender': sender,
                'sender_label': 'fixture sender', 'message_kind': 'request', 'duration': 20})
            actual = store.emit(job, 'Stored fixture purpose', 'message')
            if event_id and event_id != actual:
                store.db.execute('UPDATE events SET id=? WHERE id=?', (event_id, actual))
                actual = event_id
            if delivery == 'native_queued':
                store.admitted(actual, 'fixture-native-queue-id')
            store.db.execute('''UPDATE events SET delivery=?,acknowledged=?,withdraw_state=?,
                turn_id=?,turn_outcome=? WHERE id=?''',
                (delivery, acknowledged, withdrawal, turn_id, turn_outcome, actual))
            store.db.execute('UPDATE jobs SET intent=? WHERE id=?', (intent, job))
        finally:
            store.close()
        return actual

    def recover_clean(self, api):
        status = api.status()
        self.assertIn('state=clean_rollover_available', status)
        token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
        receipt = json.loads(api.recover(expected_preview=token, confirm=True))
        return token, receipt

    def test_clean_rollover_archives_immutable_legacy_and_seeds_ref_highwater(self):
        old = binding(A, pid=2147483000, start='12', executable='/fixture/old-codex')
        self.recipient_message(B, binding(B), old, event_id=EVENT_OLD, turn_id=TURN_OLD)
        self.legacy_state(A, old, refs=(
            ('peer', 'p7', B, json.dumps(binding(B)), 'old-peer'),
            ('watch', 'w2', 'job-2', None, 'old-watch'),
            ('message', 'm3', EVENT_OLD, json.dumps(binding(B)), 'old-message'),
            ('wake', 't5', 'wake-5', None, 'old-wake'),
        ))
        with self.make_recovery() as api:
            token, receipt = self.recover_clean(api)
            self.assertEqual(json.loads(api.recover(expected_preview=token, confirm=True)), receipt)
        selected, epoch, current, marker = owners.selected_state(self.root / A)
        self.assertEqual(current, binding(A))
        self.assertEqual(epoch, receipt['selected_epoch'])
        self.assertTrue((self.root / A / 'binding.json').read_text().find(owners.SELECTION_FORMAT) >= 0)
        archive_epoch, archive, manifest = owners.archive_entries(self.root, A)[0]
        self.assertEqual(manifest['binding'], old)
        self.assertEqual(json.loads((archive / 'source' / 'binding.json').read_text()), old)
        self.assertEqual((archive / 'source' / 'binding.json').stat().st_mode & 0o777, 0o600)
        self.assertEqual(owners.reference_highwater(self.root, A),
                         {'peer': 7, 'watch': 2, 'message': 3, 'wake': 5})
        with self.assertRaisesRegex(ValueError, 'exceed one bounded page'):
            owners.historical_refs(self.root, A, limit=2)
        page_one = owners.historical_refs(self.root, A, limit=2, page=True)
        page_two = owners.historical_refs(self.root, A, limit=2, offset=2, page=True)
        self.assertEqual(len(page_one), 2)
        self.assertEqual(len(page_two), 2)
        with self.assertRaises(ValueError):
            owners.historical_refs(self.root, A, limit=1, offset=100001, page=True)
        store = Store(selected)
        try:
            with store.transaction():
                self.assertEqual(owners.allocate_reference(store.db, 'peer'), 'p8')
                self.assertEqual(owners.allocate_reference(store.db, 'watch'), 'w3')
                self.assertEqual(owners.allocate_reference(store.db, 'message'), 'm4')
                self.assertEqual(owners.allocate_reference(store.db, 'wake'), 't6')
        finally:
            store.close()
        self.assertIn('1 owner incarnation(s)', owners.history_summary(self.root, A))
        self.assertTrue(marker['archives'][0]['manifest_sha256'])
        self.assertTrue(archive_epoch.startswith('legacy-'))
        self.backend.identity.update(pid=900001, start_ticks='901', executable='/fixture/next-codex')
        with self.make_recovery() as api:
            _second_token, second_receipt = self.recover_clean(api)
        self.assertEqual(second_receipt['previous_epoch'], epoch)
        self.assertEqual(len(owners.archive_entries(self.root, A)), 2)
        self.assertEqual(owners.reference_highwater(self.root, A),
                         {'peer': 8, 'watch': 3, 'message': 4, 'wake': 6})

    def test_cli_only_state_without_model_refs_can_be_inspected_and_recovered(self):
        self.legacy_state(A, binding(A, pid=2147483001), with_refs=False)
        with self.make_recovery() as api:
            token, receipt = self.recover_clean(api)
        selected, _, _, _ = owners.selected_state(self.root / A)
        with owners._state_snapshot(selected) as db:
            self.assertTrue(owners._has_table(db, 'model_refs'))
        self.assertEqual(owners.historical_refs(self.root, A, 'peer'), [])
        self.assertEqual(receipt['state'], 'recovered')
        self.assertTrue(token.startswith('owner-preview:'))

    def test_boot_change_overrides_a_reused_exact_process_tuple(self):
        first_boot = '11111111-1111-4111-8111-111111111111'
        second_boot = '22222222-2222-4222-8222-222222222222'
        self.legacy_state(A, binding(A, pid=2147483012))
        with patch('codex_plus.owner_recovery.kernel_boot_id', return_value=first_boot):
            with self.make_recovery() as api:
                self.recover_clean(api)
        with patch('codex_plus.owner_recovery.kernel_boot_id', return_value=second_boot), \
             patch('codex_plus.owner_recovery._process_proof', return_value=False):
            with self.make_recovery() as api:
                status = api.status()
                self.assertIn('exact saved process tuple appears reused after a kernel reboot', status)
                self.assertIn('state=clean_rollover_available', status)
                _token, receipt = self.recover_clean(api)
                selected, _epoch, frozen, _marker = owners.selected_state(self.root / A,
                    expected_binding=binding(A))
        self.assertEqual(frozen, binding(A))
        self.assertEqual(receipt['boot_id'], second_boot)

    def test_corrupt_or_mismatched_boot_identity_cannot_prove_old_owner_gone(self):
        self.legacy_state(A, binding(A, pid=2147483013))
        with self.make_recovery() as api:
            self.recover_clean(api)
        thread_root = self.root / A
        selected, _epoch, _binding, marker = owners.selected_state(thread_root)
        epoch_path = selected / 'owner-epoch.json'
        epoch = json.loads(epoch_path.read_text())
        marker_path = thread_root / 'binding.json'
        marker_value = json.loads(marker_path.read_text())
        original_epoch = epoch_path.read_bytes()

        # Even if the process proof says the exact old tuple is alive, malformed
        # persisted boot metadata must not turn it into evidence of a reboot.
        invalid = 'corrupt-but-nonempty'
        epoch['boot_id'] = invalid
        marker_value['boot_id'] = invalid
        owners._atomic_json(epoch_path, epoch)
        owners._atomic_json(marker_path, marker_value)
        corrupt_marker = marker_path.read_bytes()
        corrupt_epoch = epoch_path.read_bytes()
        self.backend.identity.update(pid=900001, start_ticks='901', executable='/fixture/third-codex')
        with patch('codex_plus.owner_recovery._process_proof', return_value=False):
            with self.make_recovery() as api:
                status = api.status()
                self.assertIn('state=corrupt_or_incomplete', status)
                with self.assertRaisesRegex(ValueError, 'canonical nonzero UUID'):
                    api.recover(expected_preview='owner-preview:' + 'a' * 64, confirm=True)
        self.assertEqual(marker_path.read_bytes(), corrupt_marker)
        self.assertEqual(epoch_path.read_bytes(), corrupt_epoch)

        # A valid UUID is still insufficient when the stable selector and epoch
        # disagree about which boot owns the selected state.
        marker_value['boot_id'] = '33333333-3333-4333-8333-333333333333'
        epoch['boot_id'] = json.loads(original_epoch)['boot_id']
        owners._atomic_json(epoch_path, epoch)
        owners._atomic_json(marker_path, marker_value)
        with self.make_recovery() as api:
            status = api.status()
        self.assertIn('state=corrupt_or_incomplete', status)
        self.assertIn('selected owner boot identity differs from the stable owner marker', status)

    def test_acknowledged_event_with_unknown_turn_outcome_is_preserved_and_does_not_block(self):
        old = binding(A, pid=2147483002)
        event = self.recipient_message(B, binding(B), old, turn_id=TURN_OLD)
        self.legacy_state(A, old, refs=(('message', 'm1', event, json.dumps(binding(B)), 'fixture message'),))
        with self.make_recovery() as api:
            status = api.status()
            self.assertIn('state=clean_rollover_available', status)
            self.assertIn('outgoing_message_receipts=1; classified=1; acknowledged_unknown_turn_outcomes=1', status)
            self.assertIn('remain unknown and are preserved', status)
            _token, receipt = self.recover_clean(api)
        self.assertTrue(receipt['history_retained_read_only'])
        self.assertEqual(owners.historical_refs(self.root, A, 'message')[0]['ref'], 'm1')

    def test_active_work_queue_and_held_lock_fail_closed(self):
        old = binding(A, pid=2147483003)
        state = self.legacy_state(A, old)
        store = Store(state)
        job = store.create('wake', {'after': 2, 'duration': 20, 'prompt': 'unfinished fixture'})
        store.close()
        with self.make_recovery() as api:
            self.assertIn('active_or_replacing_registration', api.status())
            self.backend.queues[A] = [{'id': 'unresolved-fixture'}]
            self.assertIn('native_queue_not_empty', api.status())
            self.backend.queues[A] = []
            lock = state / 'owner.lock'
            lock.touch(mode=0o600)
            fd = os.open(lock, os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                self.assertIn('coordinator_or_helper_lock_held', api.status())
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
        self.assertTrue(job)

    def test_event_and_renewal_uncertainty_matrix_refuses_rollover(self):
        cases = (
            ('pending', 0, 'none', 'unresolved_admission'),
            ('dispatching', 0, 'none', 'unresolved_admission'),
            ('uncertain', 0, 'none', 'unresolved_admission'),
            ('native_queued', 0, 'none', 'unacknowledged_queued_input'),
            ('native_queued', 1, 'unknown', 'unresolved_withdrawal'),
            ('unclassified', 1, 'none', 'unclassified_event_state'),
        )
        for index, (delivery, acknowledged, withdrawal, blocker) in enumerate(cases):
            with self.subTest(delivery=delivery, acknowledged=acknowledged, withdrawal=withdrawal):
                self.root = Path(self.tmp.name) / ('event-case-' + str(index))
                self.root.mkdir(mode=0o700)
                state = self.legacy_state(A, binding(A, pid=2147483020 + index))
                store = Store(state)
                try:
                    job = store.create('message', {'prompt': 'fixture', 'sender': binding(B),
                        'message_kind': 'request', 'duration': 20})
                    event = store.emit(job, 'fixture', 'message')
                    store.db.execute("UPDATE jobs SET intent='completed' WHERE id=?", (job,))
                    store.db.execute('UPDATE events SET delivery=?,acknowledged=?,withdraw_state=? WHERE id=?',
                        (delivery, acknowledged, withdrawal, event))
                finally:
                    store.close()
                with self.make_recovery() as api:
                    status = api.status()
                self.assertIn(blocker, status)

        self.root = Path(self.tmp.name) / 'pending-renewal-case'
        self.root.mkdir(mode=0o700)
        state = self.legacy_state(A, binding(A, pid=2147483030))
        store = Store(state)
        try:
            parent = store.create('watch', {'command': ['/bin/true'], 'cwd': '/tmp',
                'duration': 20, 'event_limit': 1, 'followup': 'fixture'})
            store.db.execute('UPDATE jobs SET intent=? WHERE id=?', ('cancelled', parent))
            store.db.execute('''INSERT INTO renewals(parent_id,new_id,spec,state,created,deadline)
                VALUES (?,?,?,?,?,?)''', (parent, str(uuid.uuid4()), '{}', 'pending', 1, 2))
        finally:
            store.close()
        with self.make_recovery() as api:
            self.assertIn('pending_renewal', api.status())

        for index, source_state in enumerate(('starting', 'running', 'stop_requested', 'lost')):
            with self.subTest(source_state=source_state):
                self.root = Path(self.tmp.name) / ('source-state-' + str(index))
                self.root.mkdir(mode=0o700)
                state = self.legacy_state(A, binding(A, pid=2147483035 + index))
                store = Store(state)
                try:
                    job = store.create('watch', {'command': ['/bin/true'], 'cwd': '/tmp',
                        'duration': 20, 'event_limit': 1, 'followup': 'fixture'})
                    store.db.execute("UPDATE jobs SET intent='cancelled',source_state=? WHERE id=?",
                        (source_state, job))
                finally:
                    store.close()
                with self.make_recovery() as api:
                    status = api.status()
                self.assertIn('unresolved_source_owner', status)

    def test_event_start_and_turn_outcomes_are_classified_but_null_remains_allowed(self):
        cases = (
            ('settled_unknown_turn_outcome', 'started', None, True),
            ('unclassified_turn_outcome', 'started', 'future_unclassified', False),
            ('unclassified_start_state', 'future_unclassified', None, False),
        )
        for index, (name, start_state, turn_outcome, clean) in enumerate(cases):
            with self.subTest(case=name):
                self.root = Path(self.tmp.name) / ('event-classification-' + str(index))
                self.root.mkdir(mode=0o700)
                state = self.legacy_state(A, binding(A, pid=2147483060 + index))
                store = Store(state)
                try:
                    job = store.create('message', {'prompt': 'fixture', 'sender': binding(B),
                        'message_kind': 'request', 'duration': 20})
                    event = store.emit(job, 'fixture', 'message')
                    store.db.execute("UPDATE jobs SET intent='completed' WHERE id=?", (job,))
                    store.db.execute('''UPDATE events SET delivery='native_queued',acknowledged=1,
                        withdraw_state='none',start_state=?,turn_id=?,turn_outcome=? WHERE id=?''',
                        (start_state, TURN_OLD, turn_outcome, event))
                finally:
                    store.close()
                with self.make_recovery() as api:
                    status = api.status()
                    token = next(line.split('=', 1)[1] for line in status.splitlines()
                                 if line.startswith('expected_preview='))
                    if clean:
                        self.assertIn('state=clean_rollover_available', status)
                        receipt = json.loads(api.recover(expected_preview=token, confirm=True))
                        self.assertEqual(receipt['state'], 'recovered')
                    else:
                        self.assertIn('unclassified_event_state', status)
                        self.assertIn('state=rollover_refused', status)
                        with self.assertRaisesRegex(ValueError, 'clean rollover is refused'):
                            api.recover(expected_preview=token, confirm=True)

    def test_outgoing_receipts_require_exact_settled_recipient_evidence(self):
        cases = (
            ('pending', 0, 'none', 'outgoing_unresolved_admission'),
            ('dispatching', 0, 'none', 'outgoing_unresolved_admission'),
            ('uncertain', 0, 'none', 'outgoing_unresolved_admission'),
            ('native_queued', 0, 'none', 'outgoing_unacknowledged_queued_input'),
            ('native_queued', 1, 'unknown', 'outgoing_unresolved_withdrawal'),
        )
        old = binding(A, pid=2147483031)
        for index, (delivery, acknowledged, withdrawal, blocker) in enumerate(cases):
            with self.subTest(delivery=delivery, acknowledged=acknowledged, withdrawal=withdrawal):
                self.root = Path(self.tmp.name) / ('outgoing-case-' + str(index))
                self.root.mkdir(mode=0o700)
                event = self.recipient_message(B, binding(B), old, delivery=delivery,
                    acknowledged=acknowledged, withdrawal=withdrawal)
                self.legacy_state(A, old, refs=(
                    ('message', 'm1', event, json.dumps(binding(B)), 'fixture recipient'),))
                with self.make_recovery() as api:
                    status = api.status()
                self.assertIn(blocker, status)
                self.assertIn('state=rollover_refused', status)

        self.root = Path(self.tmp.name) / 'outgoing-missing'
        self.root.mkdir(mode=0o700)
        self.legacy_state(A, old, refs=(
            ('message', 'm1', EVENT_OLD, json.dumps(binding(B)), 'fixture recipient'),))
        with self.make_recovery() as api:
            status = api.status()
        self.assertIn('outgoing_receipt_unknown', status)
        self.assertIn('state=rollover_refused', status)

    def test_outgoing_active_or_replacing_intent_refuses_even_after_acknowledgement(self):
        old = binding(A, pid=2147483032)
        for intent in ('active', 'replacing'):
            with self.subTest(intent=intent):
                self.root = Path(self.tmp.name) / ('outgoing-' + intent)
                self.root.mkdir(mode=0o700)
                event = self.recipient_message(B, binding(B), old, intent=intent)
                self.legacy_state(A, old, refs=(
                    ('message', 'm1', event, json.dumps(binding(B)), 'fixture recipient'),))
                with self.make_recovery() as api:
                    status = api.status()
                self.assertIn('outgoing_active_or_replacing_registration', status)
                self.assertIn('state=rollover_refused', status)

    def test_settled_cached_outgoing_receipt_does_not_require_loading_closed_peer(self):
        old = binding(A, pid=2147483033)
        event = self.recipient_message(B, binding(B), old)
        self.legacy_state(A, old, refs=(
            ('message', 'm1', event, json.dumps(binding(B)), 'closed fixture recipient'),))
        del self.backend.rows[B]
        with self.make_recovery() as api:
            _token, receipt = self.recover_clean(api)
        self.assertEqual(receipt['state'], 'recovered')
        self.assertTrue(all(method != 'thread/resume' for method, _, _ in self.backend.calls))

    def test_missing_and_tampered_archives_never_recreate_or_hide_history(self):
        self.legacy_state(A, binding(A, pid=2147483034))
        with self.make_recovery() as api:
            self.recover_clean(api)
            _epoch, archive, _manifest = owners.archive_entries(self.root, A)[0]
            snapshot = archive / 'journal.snapshot.sqlite3'
            saved = snapshot.read_bytes()
            snapshot.chmod(0o600)  # Deliberate corruption by the archive owner.
            snapshot.write_bytes(b'tampered fixture')
            snapshot.chmod(0o400)
            with self.assertRaisesRegex(ValueError, 'checksum'):
                owners.archive_entries(self.root, A)
            with self.assertRaisesRegex(ValueError, 'archived history unavailable'):
                api.status(category='events')
            snapshot.chmod(0o600)
            snapshot.write_bytes(saved)
            snapshot.chmod(0o400)
            moved = archive.with_name('missing-fixture-archive')
            archive.rename(moved)
            with self.assertRaises((ValueError, OSError)):
                owners.archive_entries(self.root, A)
            self.assertFalse(archive.exists())
            self.assertIn('incomplete or unavailable', owners.history_summary(self.root, A))

    def test_changed_logical_realm_and_unloaded_peer_refuse(self):
        changes = (('host', 'previous-host'), ('uid', os.getuid() + 1),
                   ('pid_namespace', 'pid:[previous]'), ('requested_socket', '/previous/requested'),
                   ('resolved_socket', '/previous/resolved'))
        for index, (key, value) in enumerate(changes):
            with self.subTest(field=key):
                self.root = Path(self.tmp.name) / ('realm-' + str(index))
                self.root.mkdir(mode=0o700)
                old = binding(A, pid=2147483040 + index)
                old[key] = value
                self.legacy_state(A, old)
                with self.make_recovery() as api:
                    self.assertIn('logical_scope_changed', api.status())
        self.root = Path(self.tmp.name) / 'realm-thread'
        self.root.mkdir(mode=0o700)
        old = binding(A, pid=2147483050)
        old['thread_id'] = B
        self.legacy_state(A, old)
        with self.make_recovery() as api:
            self.assertIn('state=corrupt_or_incomplete', api.status())
        self.root = Path(self.tmp.name) / 'unloaded-peer'
        self.root.mkdir(mode=0o700)
        self.legacy_state(A, binding(A), refs=(('peer', 'p1', B, json.dumps(binding(B)), 'beta'),))
        self.backend.rows.pop(B)
        with self.make_recovery() as api:
            with self.assertRaisesRegex(ValueError, 'not positively loaded'):
                api.status(peer='p1')

    def test_active_turn_interruption_at_selection_commit_leaves_retryable_prep(self):
        state = self.legacy_state(A, binding(A, pid=2147483051))
        with self.make_recovery() as api:
            status = api.status()
            token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
            original = owners._atomic_json
            def interrupt_turn(path, value, **kwargs):
                if Path(path) == state / 'binding.json' and value.get('format') == owners.SELECTION_FORMAT:
                    self.backend.turns[A][0]['status'] = 'completed'
                return original(path, value, **kwargs)
            with patch.object(owners, '_atomic_json', side_effect=interrupt_turn):
                with self.assertRaisesRegex(ValueError, 'exact active native caller turn'):
                    api.recover(expected_preview=token, confirm=True)
            self.assertEqual(json.loads((state / 'binding.json').read_text()), binding(A, pid=2147483051))
            self.backend.turns[A][0]['status'] = 'inProgress'
            receipt = json.loads(api.recover(expected_preview=token, confirm=True))
        self.assertEqual(receipt['state'], 'recovered')

    def test_stale_preview_and_incomplete_queue_refuse_without_rewriting_source(self):
        state = self.legacy_state(A, binding(A, pid=2147483004))
        before = (state / 'binding.json').read_bytes()
        with self.make_recovery() as api:
            status = api.status()
            token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
            (state / 'extra.json').write_text('{}\n')
            (state / 'extra.json').chmod(0o600)
            with self.assertRaisesRegex(ValueError, 'preview is stale'):
                api.recover(expected_preview=token, confirm=True)
            self.assertEqual((state / 'binding.json').read_bytes(), before)
            self.backend.queue_error = TimeoutError('fixture queue timeout')
            self.assertIn('native_queue_scan_incomplete', api.status())

    def test_marker_last_preparation_can_be_verified_and_retried(self):
        state = self.legacy_state(A, binding(A, pid=2147483005))
        with self.make_recovery() as api:
            status = api.status()
            token = next(line.split('=', 1)[1] for line in status.splitlines() if line.startswith('expected_preview='))
            atomic_json = owners._atomic_json
            def fail_selection(path, value, **kwargs):
                if Path(path) == state / 'binding.json' and value.get('format') == owners.SELECTION_FORMAT:
                    raise OSError('fixture crash before marker commit')
                return atomic_json(path, value, **kwargs)
            with patch.object(owners, '_atomic_json', side_effect=fail_selection):
                with self.assertRaisesRegex(OSError, 'fixture crash'):
                    api.recover(expected_preview=token, confirm=True)
            self.assertEqual(json.loads((state / 'binding.json').read_text()), binding(A, pid=2147483005))
            retry_status = api.status()
            self.assertIn('state=clean_rollover_available', retry_status)
            self.assertIn(token, retry_status)
            receipt = json.loads(api.recover(expected_preview=token, confirm=True))
        self.assertEqual(receipt['state'], 'recovered')
        self.assertEqual(len(owners.archive_entries(self.root, A)), 1)

    def test_prepared_epoch_boot_is_rechecked_before_marker_commit(self):
        state = self.legacy_state(A, binding(A, pid=2147483052))
        original_binding = (state / 'binding.json').read_bytes()
        with self.make_recovery() as api:
            status = api.status()
            token = next(line.split('=', 1)[1] for line in status.splitlines()
                         if line.startswith('expected_preview='))
            verify_tree = owners._verify_tree_unchanged
            tampered = []

            def alter_prepared_epoch(source, expected, **kwargs):
                result = verify_tree(source, expected, **kwargs)
                if kwargs.get('ignore_paths') and not tampered:
                    candidates = list((state / 'incarnations').iterdir())
                    self.assertEqual(len(candidates), 1)
                    epoch_path = candidates[0] / 'owner-epoch.json'
                    epoch = json.loads(epoch_path.read_text())
                    epoch['boot_id'] = '44444444-4444-4444-8444-444444444444'
                    owners._atomic_json(epoch_path, epoch)
                    tampered.append(True)
                return result

            with patch.object(owners, '_verify_tree_unchanged', side_effect=alter_prepared_epoch):
                with self.assertRaisesRegex(ValueError, 'captured current boot'):
                    api.recover(expected_preview=token, confirm=True)
        self.assertTrue(tampered)
        self.assertEqual((state / 'binding.json').read_bytes(), original_binding)

    def test_partial_unrelated_process_fd_census_is_reported_but_not_a_gate(self):
        self.legacy_state(A, binding(A, pid=2147483009))
        partial = {'holder': None, 'partial': True, 'unreadable_processes': 1,
                   'reasons': ['fixture_unrelated_process']}
        with patch('codex_plus.owner_recovery._open_state_processes', return_value=partial):
            with self.make_recovery() as api:
                status = api.status()
        self.assertIn('process_fd_scan=partial', status)
        self.assertIn('state=clean_rollover_available', status)

    def test_tracked_coordinator_metadata_must_be_exact_and_resolved(self):
        state = self.legacy_state(A, binding(A, pid=2147483010))
        good = {'pid': os.getpid(),
                'start_ticks': Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19],
                'executable': os.readlink('/proc/self/exe'), 'generation': str(uuid.uuid4()),
                'state': str(state.resolve())}
        owners._atomic_json(state / 'coordinator.json', good)
        with self.make_recovery() as api:
            self.assertIn('tracked_coordinator_alive', api.status())
        bad = dict(good, state=str(self.root / 'other-state'))
        owners._atomic_json(state / 'coordinator.json', bad)
        with self.make_recovery() as api:
            self.assertIn('tracked_coordinator_metadata_invalid', api.status())

    def test_unknown_tracked_coordinator_liveness_refuses_rollover(self):
        state = self.legacy_state(A, binding(A, pid=2147483011))
        record = {'pid': 4242, 'start_ticks': '100', 'executable': '/fixture/coordinator',
                  'generation': str(uuid.uuid4()), 'state': str(state.resolve())}
        owners._atomic_json(state / 'coordinator.json', record)
        with patch('codex_plus.owner_recovery._process_proof', return_value=None):
            with self.make_recovery() as api:
                status = api.status()
        self.assertIn('tracked_coordinator_liveness_unknown', status)
        self.assertIn('state=rollover_refused', status)

    def test_intermediate_managed_symlink_and_oversized_json_are_rejected(self):
        thread_root = self.root / A
        thread_root.mkdir(mode=0o700)
        epoch = 'e-' + 'a' * 32
        marker = {'format': owners.SELECTION_FORMAT, 'thread_id': A, 'epoch': epoch,
            'selected': 'incarnations/' + epoch, 'binding': binding(A),
            'boot_id': '11111111-1111-4111-8111-111111111111',
            'archives': [], 'last_recovery': None}
        owners._atomic_json(thread_root / 'binding.json', marker)
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir(mode=0o700)
        (thread_root / 'incarnations').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'must not be a symlink'):
            owners.selected_state(thread_root)
        large = self.root / 'too-large.json'
        large.write_bytes(b' ' * (owners.MAX_JSON_BYTES + 1))
        large.chmod(0o600)
        with self.assertRaisesRegex(ValueError, 'size bound'):
            owners._read_json(large)

    def test_pid_reuse_is_distinguished_from_the_exact_saved_process(self):
        old_binding = binding(A, pid=4242, start='100', executable='/fixture/old')
        with tempfile.TemporaryDirectory() as proc_dir:
            root = Path(proc_dir)
            stat_line = '4242 (fixture process) ' + ' '.join(['S'] + ['0'] * 18 + ['200'])
            (root / 'stat').write_text(stat_line)
            (root / 'stat').chmod(0o600)
            fake_path_type = type(Path('/'))
            real_path = Path
            class ProcPath(fake_path_type):
                def stat(self, *args, **kwargs):
                    if str(self) == '/proc/4242':
                        return (root / 'stat').stat()
                    return super().stat(*args, **kwargs)
                def read_text(self, *args, **kwargs):
                    if str(self) == '/proc/4242/stat':
                        return (root / 'stat').read_text()
                    return super().read_text(*args, **kwargs)
            original_readlink = os.readlink
            def readlink(path, *args, **kwargs):
                if str(path) == '/proc/4242/exe':
                    return '/fixture/new'
                return original_readlink(path, *args, **kwargs)
            with patch.object(owners, 'Path', ProcPath), patch.object(owners.os, 'readlink', side_effect=readlink):
                self.assertTrue(owners._process_proof(old_binding))
                old_binding['start_ticks'] = '200'
                old_binding['executable'] = '/fixture/new'
                self.assertFalse(owners._process_proof(old_binding))

    def test_current_sender_receipt_resolves_archived_recipient_and_fences_forgery(self):
        sender = binding(A)
        old_recipient = binding(B, pid=2147483006, start='22', executable='/fixture/old-recipient')
        recipient_state = self.legacy_state(B, old_recipient, with_refs=False)
        store = Store(recipient_state)
        try:
            store.db.execute('''CREATE TABLE model_responses (
                event_id TEXT PRIMARY KEY REFERENCES events(id), turn_id TEXT NOT NULL,
                outcome TEXT NOT NULL, detail TEXT NOT NULL)''')
            job = store.create('message', {'prompt': 'Stored confidential purpose', 'sender': binding(OTHER),
                'sender_label': 'fixture sender', 'message_kind': 'request', 'duration': 20})
            event = store.emit(job, 'Stored confidential purpose', 'message')
            store.admitted(event, 'native-input-fixture')
            store.acknowledge(event)
            store.db.execute("UPDATE jobs SET intent='completed' WHERE id=?", (job,))
            store.db.execute('INSERT INTO model_responses VALUES (?,?,?,?)',
                (event, TURN_OLD, 'accepted', 'Reviewed within the stated scope.'))
        finally:
            store.close()
            event_id = event
        sender_state = self.legacy_state(A, sender, refs=(
            ('message', 'm1', event_id, json.dumps(old_recipient), 'fixture recipient'),))
        with self.make_recovery(B, TURN_B) as api:
            _token, receipt = self.recover_clean(api)
        outgoing = {'kind': 'message', 'ref': 'm1', 'identity': event_id,
                    'binding': json.dumps(old_recipient), 'label': 'fixture recipient'}
        with self.assertRaisesRegex(ValueError, 'this caller does not own') as caught:
            owners.historical_message_receipt(self.root, A, outgoing)
        self.assertNotIn('Stored confidential purpose', str(caught.exception))

    def test_current_sender_receipt_resolves_historical_recipient(self):
        sender = binding(A)
        old_recipient = binding(B, pid=2147483008, start='23', executable='/fixture/old-recipient')
        recipient_state = self.legacy_state(B, old_recipient, with_refs=False)
        store = Store(recipient_state)
        try:
            store.db.execute('''CREATE TABLE model_responses (
                event_id TEXT PRIMARY KEY REFERENCES events(id), turn_id TEXT NOT NULL,
                outcome TEXT NOT NULL, detail TEXT NOT NULL)''')
            job = store.create('message', {'prompt': 'Stored confidential purpose', 'sender': sender,
                'sender_label': 'fixture sender', 'message_kind': 'request', 'duration': 20})
            event = store.emit(job, 'Stored confidential purpose', 'message')
            store.admitted(event, 'native-input-fixture')
            store.acknowledge(event)
            store.db.execute("UPDATE jobs SET intent='completed' WHERE id=?", (job,))
            store.db.execute('INSERT INTO model_responses VALUES (?,?,?,?)',
                (event, TURN_OLD, 'accepted', 'Reviewed within the stated scope.'))
        finally:
            store.close()
        sender_state = self.legacy_state(A, sender, refs=(
            ('message', 'm1', event, json.dumps(old_recipient), 'fixture recipient'),))
        with self.make_recovery(B, TURN_B) as api:
            _token, receipt = self.recover_clean(api)
        outgoing = {'kind': 'message', 'ref': 'm1', 'identity': event,
                    'binding': json.dumps(old_recipient), 'label': 'fixture recipient'}
        text = owners.historical_message_receipt(self.root, A, outgoing)
        self.assertIn('recipient accepted', text)
        self.assertIn('Stored confidential purpose', text)
        self.assertIn('does not prove an external effect', text)
        self.assertEqual(receipt['state'], 'recovered')
        self.assertTrue(sender_state.is_dir())

    def test_historical_incoming_checks_both_event_and_turn_identity(self):
        old = binding(A, pid=2147483007)
        state = self.legacy_state(A, old, with_refs=False)
        store = Store(state)
        try:
            job = store.create('message', {'prompt': 'old', 'sender': binding(B),
                'message_kind': 'request', 'duration': 20})
            event = store.emit(job, 'old', 'message')
            store.admitted(event, 'fixture')
            store.link_turn(event, TURN_OLD)
            store.acknowledge(event)
            store.db.execute("UPDATE jobs SET intent='completed' WHERE id=?", (job,))
        finally:
            store.close()
        with self.make_recovery() as api:
            token, _receipt = self.recover_clean(api)
            self.backend.turns[A][0]['items'] = [{'type': 'userMessage', 'clientId': event}]
            status = api.status()
            self.assertIn('already_current', status)
            self.assertIn('active_turn_is_archived_callback=true', status)
            with self.assertRaisesRegex(ValueError, 'archived event'):
                api.recover(expected_preview=token, confirm=True)
        self.assertTrue(owners.historical_incoming(self.root, A, [], TURN_OLD))


if __name__ == '__main__':
    unittest.main()
