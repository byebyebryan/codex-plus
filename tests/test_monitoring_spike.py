"""Offline acceptance checks for the study's framing and recording boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'spikes/monitoring'))
from native import Client
from simulator import step
from spike import Journal, Lines, NotSubmitted


class FramingTests(unittest.TestCase):
    def test_utf8_chunks_occurrences_and_final_record(self):
        lines = Lines()
        encoded = 'café\nsame\nsame\nlast'.encode()
        out = []
        for byte in encoded:
            out.extend(lines.feed(bytes([byte])))
        out.extend(lines.feed(b'', eof=True))
        self.assertEqual(out, ['café', 'same', 'same', 'last'])

    def test_malformed_and_unterminated_oversized_output(self):
        with self.assertRaises(UnicodeDecodeError):
            Lines().feed(b'\xff\n')
        with self.assertRaises(ValueError):
            Lines(4).feed(b'abcde')
        with self.assertRaises(ValueError):
            Lines(4).feed(b'abcde\n')

    def test_native_partial_frame_survives_read_timeout(self):
        client = Client.__new__(Client)
        client.sock, peer = socket.socketpair()
        client.buffer = b''
        client.fragments = bytearray()
        client.responses, client.events, client.process_ids = {}, [], set()
        client.thread_id = None
        message = json.dumps({'id': 7, 'result': {'ok': True}}).encode()
        frame = bytes([0x81, len(message)]) + message
        try:
            peer.sendall(frame[:5])
            with self.assertRaises(socket.timeout):
                client.receive(0.01)
            peer.sendall(frame[5:])
            self.assertEqual(client.receive()['result'], {'ok': True})
        finally:
            client.close()
            peer.close()


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = 100.0
        self.path = self.root / 'journal.sqlite'
        self.journal = Journal(self.path, lambda: self.now)
        self.job = self.journal.create('watch', {})

    def tearDown(self):
        self.journal.db.close()
        self.tmp.cleanup()

    def test_fixture_noise_projection_and_terminal_states(self):
        run = self.root / 'run'
        initial = step(run, 'init')
        projection = lambda state: json.dumps({k: state[k] for k in ['status', 'progress', 'errors']}, sort_keys=True)
        self.assertIsNotNone(self.journal.emit(self.job, 'initial', baseline=projection(initial)))
        noisy = step(run, 'noise')
        self.assertNotEqual(initial['revision'], noisy['revision'])
        self.assertIsNone(self.journal.emit(self.job, 'noise', baseline=projection(noisy)))
        self.assertEqual(step(run, 'stall')['throughput'], 0)
        self.assertEqual(step(run, 'recover')['throughput'], 10)
        self.assertEqual(step(run, 'complete')['remaining'], 0)
        with self.assertRaises(ValueError):
            step(run, 'advance')
        self.assertEqual(step(run, 'fail')['status'], 'failed')

    def test_repeated_occurrences_are_distinct_and_bounded(self):
        first = self.journal.emit(self.job, 'same')
        second = self.journal.emit(self.job, 'same')
        self.assertNotEqual(first, second)
        self.assertIsNone(self.journal.emit(self.job, 'third'))
        self.assertEqual(len(self.journal.events(self.job)), 2)

    def test_cancel_before_dispatch_and_inflight_receipt(self):
        event = self.journal.emit(self.job, 'pending')
        self.journal.cancel(self.job)
        called = []
        self.journal.dispatch(event, lambda e: called.append(e))
        self.assertEqual(called, [])
        self.assertIsNone(self.journal.emit(self.job, 'after cancel'))
        other = self.journal.create('watch', {})
        event = self.journal.emit(other, 'in flight')
        def sink(e):
            self.assertEqual(self.journal.cancel(other)[0]['state'], 'dispatching')
            return 'native-id'
        self.journal.dispatch(event, sink)
        self.assertEqual(self.journal.job(other)['state'], 'cancelled')
        self.assertEqual(self.journal.events(other)[0]['state'], 'native_queued')

    def test_unknown_cancel_does_not_claim_a_receipt(self):
        with self.assertRaises(ValueError):
            self.journal.cancel('unknown')

    def test_cancel_remains_authoritative_after_inflight_failure(self):
        event = self.journal.emit(self.job, 'in flight')
        def sink(e):
            self.journal.cancel(self.job)
            raise TimeoutError('submission outcome unknown')
        self.journal.dispatch(event, sink)
        self.journal.state(self.job, 'completed')
        self.assertEqual(self.journal.job(self.job)['state'], 'cancelled')
        self.assertEqual(self.journal.events(self.job)[0]['state'], 'uncertain')

    def test_expiry_and_one_shot_replacement(self):
        old = self.journal.create('wake', {'prompt': 'old'}, after=10)
        self.assertIsNone(self.journal.wake_due(old))
        self.journal.cancel(old)
        new = self.journal.create('wake', {'prompt': 'new'}, after=20)
        self.now = 121
        self.assertIsNone(self.journal.wake_due(old))
        self.assertIsNotNone(self.journal.wake_due(new))
        self.assertIsNone(self.journal.wake_due(new))
        self.now = 221
        self.assertIsNone(self.journal.emit(self.job, 'expired'))
        self.assertFalse(self.journal.live(self.job))
        self.assertEqual(self.journal.job(self.job)['state'], 'expired')

    def test_baseline_and_pending_event_rollback_together(self):
        self.journal.db.execute("CREATE TRIGGER fail_event BEFORE INSERT ON events BEGIN SELECT RAISE(ABORT, 'fault'); END")
        with self.assertRaises(Exception):
            self.journal.emit(self.job, 'material change', baseline='new baseline')
        self.assertIsNone(self.journal.job(self.job)['baseline'])
        self.assertEqual(self.journal.events(self.job), [])

    def test_uncertain_delivery_is_not_replayed(self):
        event = self.journal.emit(self.job, 'maybe admitted')
        calls = []
        def sink(e):
            calls.append(e['id'])
            raise TimeoutError('transport failed after possible admission')
        self.journal.dispatch(event, sink)
        self.journal.dispatch(event, sink)
        self.assertEqual(calls, [event])
        self.assertEqual(self.journal.events(self.job)[0]['state'], 'uncertain')
        self.assertEqual(self.journal.job(self.job)['state'], 'suspended')

    def test_known_preflight_failure_is_not_uncertain_submission(self):
        event = self.journal.emit(self.job, 'blocked')
        def sink(e):
            raise NotSubmitted('owner unavailable before queue command')
        self.journal.dispatch(event, sink)
        self.assertEqual(self.journal.events(self.job)[0]['state'], 'not_submitted')

    def test_crash_after_reservation_preserves_uncertainty(self):
        class Crash(BaseException):
            pass
        event = self.journal.emit(self.job, 'reserved')
        with self.assertRaises(Crash):
            self.journal.dispatch(event, lambda e: (_ for _ in ()).throw(Crash()))
        self.journal.db.close()
        self.journal = Journal(self.path, lambda: self.now)
        self.journal.reconcile_crash()
        self.assertEqual(self.journal.events(self.job)[0]['state'], 'uncertain')


if __name__ == '__main__':
    unittest.main()
