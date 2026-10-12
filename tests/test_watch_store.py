import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.store import Store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = 100.0
        self.store = Store(self.root / 'state', clock=lambda: self.now)
        self.spec = {'command': ['rtk', 'proxy', 'true'], 'cwd': str(self.root),
                     'duration': 120, 'event_limit': 2}

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_occurrences_are_distinct_and_bounded(self):
        watch = self.store.create('watch', self.spec)
        one = self.store.emit(watch, 'same')
        two = self.store.emit(watch, 'same')
        self.assertNotEqual(one, two)
        self.assertIsNone(self.store.emit(watch, 'same'))
        self.assertEqual(len(self.store.events(watch)), 2)

    def test_snapshot_noise_and_initially_satisfied_option(self):
        spec = {**self.spec, 'snapshot_fields': ['status', 'progress'], 'quiet_initial': True}
        watch = self.store.create('watch', spec)
        self.assertIsNone(self.store.emit(watch, json.dumps({'status': 'running', 'progress': 0, 'revision': 1})))
        self.assertIsNone(self.store.emit(watch, json.dumps({'status': 'running', 'progress': 0, 'revision': 2})))
        self.assertIsNotNone(self.store.emit(watch, json.dumps({'status': 'completed', 'progress': 100})))
        immediate = self.store.create('watch', {**spec, 'quiet_initial': False})
        self.assertIsNotNone(self.store.emit(immediate, json.dumps({'status': 'completed', 'progress': 100})))

    def test_baseline_and_event_rollback_together(self):
        watch = self.store.create('watch', {**self.spec, 'snapshot_fields': ['progress']})
        self.store.db.execute("CREATE TRIGGER reject_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT,'fault'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.emit(watch, '{"progress":1}')
        self.assertIsNone(self.store.job(watch)['baseline'])
        self.assertEqual(self.store.job(watch)['event_count'], 0)
        self.assertEqual(self.store.events(watch), [])

    def test_invalid_projection_never_changes_baseline(self):
        watch = self.store.create('watch', {**self.spec, 'snapshot_fields': ['progress']})
        for raw in ('[]', '{}', '{"progress":NaN}', '{"progress":Infinity}', 'not json'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.store.emit(watch, raw)
        self.assertIsNone(self.store.job(watch)['baseline'])

    def test_cancel_before_reservation_and_inflight_admission(self):
        watch = self.store.create('watch', self.spec)
        pending = self.store.emit(watch, 'first')
        inflight = self.store.emit(watch, 'second')
        self.assertTrue(self.store.reserve(inflight))
        self.store.cancel(watch)
        self.assertFalse(self.store.reserve(pending))
        self.store.admitted(inflight, 'native-input')
        self.assertEqual(self.store.job(watch)['intent'], 'cancelled')
        self.assertEqual(self.store.event(pending)['delivery'], 'cancelled')
        self.assertEqual(self.store.event(inflight)['delivery'], 'native_queued')
        self.assertIsNone(self.store.emit(watch, 'later'))

    def test_expiry_and_one_shot_restore(self):
        timer = self.store.create('wake', {'after': 10, 'duration': 20, 'prompt': 'check'})
        event = self.store.emit(timer, 'check', 'wake')
        self.assertIsNone(self.store.emit(timer, 'check', 'wake'))
        self.now += 21
        self.store.expire(timer)
        self.assertEqual(self.store.event(event)['delivery'], 'expired')
        self.assertIsNone(self.store.emit(timer, 'check', 'wake'))

    def test_expiry_notice_is_bounded_and_cancel_has_no_notice(self):
        watch = self.store.create('watch', {**self.spec, 'notify_end': True})
        self.now += 121
        self.store.expire(watch)
        events = self.store.events(watch)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['kind'], 'lifecycle')
        self.assertTrue(self.store.reserve(events[0]['id']))
        self.assertIsNone(self.store.notice(watch, 'again'))
        other = self.store.create('watch', {**self.spec, 'notify_end': True})
        self.store.cancel(other)
        self.assertIsNone(self.store.notice(other, 'cancelled'))

    def test_unknown_admission_survives_reopen_without_replay(self):
        watch = self.store.create('watch', self.spec)
        event = self.store.emit(watch, 'fixture')
        self.store.reserve(event)
        self.store.close()
        self.store = Store(self.root / 'state', clock=lambda: self.now)
        self.store.reconcile()
        self.assertEqual(self.store.event(event)['delivery'], 'uncertain')
        self.assertFalse(self.store.reserve(event))

    def test_live_turn_receipt_can_arrive_before_link(self):
        watch = self.store.create('watch', self.spec)
        event = self.store.emit(watch, 'fixture')
        self.store.reserve(event)
        self.store.turn_completed('turn', 'completed')
        self.store.link_turn(event, 'turn')
        receipt = self.store.event(event)
        self.assertEqual(receipt['delivery'], 'native_queued')
        self.assertEqual(receipt['turn_outcome'], 'completed')
        self.assertFalse(receipt['acknowledged'])
        self.assertTrue(self.store.acknowledge(event)['acknowledged'])

    def test_acknowledgement_requires_known_admission_and_truthful_id(self):
        watch = self.store.create('watch', self.spec)
        event = self.store.emit(watch, 'fixture')
        for identifier in ('missing', event):
            with self.assertRaises(ValueError):
                self.store.acknowledge(identifier)
        self.store.reserve(event)
        self.store.uncertain(event, 'unknown')
        with self.assertRaises(ValueError):
            self.store.acknowledge(event)

    def test_renewal_waits_for_stop_and_cancel_covers_lineage(self):
        watch = self.store.create('watch', self.spec)
        self.store.source(watch, 'running')
        new_id = self.store.request_renewal(watch, self.spec)
        self.assertIsNone(self.store.finish_renewal(watch))
        with self.assertRaises(ValueError):
            self.store.job(new_id)
        self.store.source(watch, 'stopped', 'replacement')
        self.assertEqual(self.store.finish_renewal(watch), new_id)
        self.assertEqual(self.store.job(new_id)['parent_id'], watch)
        cancelled = self.store.cancel(watch)
        self.assertEqual(set(cancelled['cancelled']), {watch, new_id})
        with self.assertRaises(ValueError):
            self.store.request_renewal(new_id, self.spec)

    def test_cancel_wins_while_replacement_is_pending(self):
        watch = self.store.create('watch', self.spec)
        new_id = self.store.request_renewal(watch, self.spec)
        self.store.cancel(watch)
        self.store.source(watch, 'stopped', 'cancelled')
        self.assertIsNone(self.store.finish_renewal(watch))
        with self.assertRaises(ValueError):
            self.store.job(new_id)

    def test_restart_does_not_silently_relaunch_source(self):
        watch = self.store.create('watch', self.spec)
        self.store.source(watch, 'running')
        self.store.reconcile()
        self.assertEqual(self.store.job(watch)['source_state'], 'lost')
        self.assertFalse(self.store.job(watch)['recover_requested'])
        self.store.request_recovery(watch)
        self.assertTrue(self.store.job(watch)['recover_requested'])
        self.store.cancel(watch)
        with self.assertRaises(ValueError):
            self.store.request_recovery(watch)

    def test_private_state_rejects_shared_directory(self):
        public = self.root / 'public'
        public.mkdir(mode=0o755)
        public.chmod(0o755)  # Independent of the CLI's process-wide private umask.
        with self.assertRaises(ValueError):
            Store(public)
        self.assertEqual((self.root / 'state/journal.sqlite3').stat().st_mode & 0o777, 0o600)

    def test_queue_start_reservation_rechecks_intent_and_expiry(self):
        for stopped in ('cancel', 'expiry'):
            with self.subTest(stopped=stopped):
                watch = self.store.create('watch', self.spec)
                event = self.store.emit(watch, 'fixture')
                self.store.reserve(event)
                self.store.admitted(event, 'native-input')
                if stopped == 'cancel':
                    self.store.cancel(watch)
                else:
                    self.now += 121
                self.assertFalse(self.store.reserve_start(event))
                self.assertEqual(self.store.event(event)['delivery'], 'native_queued')

    def test_lost_source_renewal_is_rejected_without_changing_intent(self):
        watch = self.store.create('watch', self.spec)
        self.store.source(watch, 'lost')
        with self.assertRaisesRegex(ValueError, 'lost'):
            self.store.request_renewal(watch, self.spec)
        self.assertEqual(self.store.job(watch)['intent'], 'active')
        self.store.request_recovery(watch)
        self.assertTrue(self.store.job(watch)['recover_requested'])

    def test_owner_loss_interrupts_attempt_and_leaves_parent_recoverable(self):
        parent = self.store.create('watch', self.spec)
        self.store.source(parent, 'running')
        first = self.store.request_renewal(parent, self.spec)
        self.store.reconcile()
        self.assertEqual(self.store.renewal(first)['state'], 'interrupted')
        self.assertEqual(self.store.job(parent)['intent'], 'active')
        self.assertEqual(self.store.job(parent)['source_state'], 'lost')
        self.store.request_recovery(parent)
        self.store.source(parent, 'running')
        second = self.store.request_renewal(parent, self.spec)
        self.store.source(parent, 'stopped')
        self.assertEqual(self.store.finish_renewal(parent), second)
        self.assertEqual(self.store.renewal(first)['state'], 'interrupted')
        self.assertEqual(self.store.renewal(second)['state'], 'done')
        self.assertEqual(len([j for j in self.store.jobs() if j['parent_id'] == parent]), 1)

    def test_late_stop_cannot_create_successor_after_handshake_deadline(self):
        parent = self.store.create('watch', self.spec)
        child = self.store.request_renewal(parent, self.spec)
        self.now += 11
        self.store.source(parent, 'stopped')
        self.assertIsNone(self.store.finish_renewal(parent))
        self.assertEqual(self.store.renewal(child)['state'], 'expired')
        self.assertEqual(self.store.job(parent)['intent'], 'active')
        with self.assertRaises(ValueError): self.store.job(child)

    def test_short_parent_lease_bounds_renewal_and_cancel_preserves_failed_history(self):
        parent = self.store.create('watch', {**self.spec, 'duration': 3})
        child = self.store.request_renewal(parent, self.spec)
        self.assertEqual(self.store.renewal(child)['deadline'], self.now + 3)
        self.now += 4; self.store.expire_renewals()
        self.assertEqual(self.store.job(parent)['intent'], 'expired')
        self.store.cancel(child)
        self.assertEqual(self.store.renewal(child)['state'], 'expired')
        self.assertEqual(self.store.job(parent)['intent'], 'cancelled')

    def test_confirmed_finished_source_can_renew_after_its_old_lease(self):
        parent = self.store.create('watch', self.spec)
        self.store.source(parent, 'completed')
        self.now += 130; self.store.expire(parent)
        child = self.store.request_renewal(parent, self.spec)
        self.assertEqual(self.store.renewal(child)['state'], 'done')
        self.assertEqual(self.store.job(child)['expires'], self.now + 120)

    def legacy_renewal_table(self, rows):
        self.store.db.execute('DROP TABLE renewals')
        self.store.db.execute('''CREATE TABLE renewals (parent_id TEXT PRIMARY KEY REFERENCES jobs(id),
            new_id TEXT NOT NULL,spec TEXT NOT NULL,state TEXT NOT NULL,detail TEXT NOT NULL DEFAULT '')''')
        self.store.db.executemany('INSERT INTO renewals VALUES (?,?,?,?,?)', rows)

    def test_legacy_journal_migration_preserves_identity_baseline_and_uncertainty(self):
        parent = self.store.create('watch', {**self.spec, 'snapshot_fields': ['progress']})
        event = self.store.emit(parent, '{"progress":20}')
        self.store.reserve(event); self.store.uncertain(event, 'legacy reply missing')
        self.store.source(parent, 'running')
        before = self.store.job(parent)
        self.store.db.execute('ALTER TABLE events DROP COLUMN withdraw_state')
        self.store.db.execute('ALTER TABLE events DROP COLUMN withdraw_detail')
        self.legacy_renewal_table([(parent, 'legacy-child', json.dumps(self.spec), 'pending', 'legacy detail')])
        self.store.close(); self.store = Store(self.root / 'state', clock=lambda: self.now)
        self.assertEqual(self.store.job(parent), before)
        self.assertEqual(self.store.event(event)['delivery'], 'uncertain')
        self.assertEqual(self.store.event(event)['withdraw_state'], 'none')
        attempt = self.store.renewal('legacy-child')
        self.assertIsNone(attempt['created'])
        self.assertEqual(attempt['deadline'], self.now + 10)
        self.assertEqual(attempt['detail'], 'legacy detail')
        self.store.close(); self.store = Store(self.root / 'state', clock=lambda: self.now + 50)
        self.assertEqual(self.store.renewal('legacy-child'), attempt)
        self.store.reconcile()
        self.assertEqual(self.store.renewal('legacy-child')['state'], 'interrupted')
        self.assertFalse(self.store.reserve(event))

    def test_migration_failure_rolls_back_legacy_table(self):
        first = self.store.create('watch', self.spec); second = self.store.create('watch', self.spec)
        self.legacy_renewal_table([(p, 'colliding-id', json.dumps(self.spec), 'pending', '') for p in (first, second)])
        self.store.close()
        with self.assertRaises(sqlite3.IntegrityError): Store(self.root / 'state')
        db = sqlite3.connect(self.root / 'state/journal.sqlite3')
        self.assertEqual(db.execute('SELECT COUNT(*) FROM renewals').fetchone()[0], 2)
        self.assertNotIn('deadline', [r[1] for r in db.execute('PRAGMA table_info(renewals)')])
        self.assertFalse(db.execute("SELECT name FROM sqlite_master WHERE name='renewals_next'").fetchall())
        db.execute('DELETE FROM renewals'); db.commit(); db.close()
        self.store = Store(self.root / 'state', clock=lambda: self.now)


if __name__ == '__main__':
    unittest.main()
