import base64
import json
import struct
import unittest
from unittest.mock import patch

from codex_plus.notification_protocol import decode, encode, event_id, metadata
from codex_plus.notification_stream import Messages, Notices
from codex_plus.notification_inspect import inspect, relation, source_identity
from codex_plus.notification_run import packet

THREAD = '11111111-1111-4111-8111-111111111111'
OLD = 'ffffffff-ffff-4fff-8fff-ffffffffffff'
NEW = '00000000-0000-4000-8000-000000000000'


def frame(payload, opcode=1, final=True, mask=False):
    if isinstance(payload, dict):
        payload = json.dumps(payload).encode()
    n = len(payload)
    size = bytes([n]) if n < 126 else b'\x7e' + struct.pack('!H', n) if n < 65536 else b'\x7f' + struct.pack('!Q', n)
    if mask:
        size = bytes([size[0] | 128]) + size[1:] + b'abcd'
        payload = bytes(c ^ b'abcd'[i % 4] for i, c in enumerate(payload))
    return bytes([opcode | (128 if final else 0)]) + size + payload


class Rich(unittest.TestCase):
    def test_category_is_canonical_and_strict(self):
        value = metadata('host', 'native', THREAD, OLD)
        self.assertEqual(decode(encode(value)), value)
        for bad in ('garbage', encode(value) + '=', encode(value).replace('.v1.', '.v2.')):
            with self.assertRaises(ValueError):
                decode(bad)
        with self.assertRaises(ValueError):
            encode(dict(value, extra=1))
        with self.assertRaises(ValueError):
            metadata('host\nother', 'native', THREAD, OLD)

    def test_stream_skip_large_frame_and_resume_with_constant_buffer(self):
        parser = Messages(max_message=128)
        payload = b'HTTP/1.1 101 Switching\r\n\r\n' + frame(b'x' * 1000000) + frame({'method': 'done'}, mask=True)
        result = []
        for at in range(0, len(payload), 73):
            result += parser.feed(payload[at:at + 73])
            self.assertLess(len(parser.buffer), 256)
        self.assertEqual(result, [{'method': 'done'}])
        self.assertEqual(parser.skipped, 1)

    def test_fragmented_message_with_ping_and_bounded_overflow(self):
        parser = Messages(max_message=64)
        data = (b'GET / HTTP/1.1\r\n\r\n' + frame(b'{"x":', final=False)
                + frame(b'ping', opcode=9) + frame(b'1}', opcode=0)
                + frame(b'x' * 50, final=False) + frame(b'y' * 50, opcode=0)
                + frame({'x': 2}))
        self.assertEqual(parser.feed(data), [{'x': 1}, {'x': 2}])

    def bound(self):
        observer = Notices('host', 'native')
        observer.client({'id': 7, 'method': 'thread/resume', 'params': {'threadId': THREAD}})
        observer.server({'id': 7, 'result': {'thread': {'id': THREAD, 'name': 'My thread',
                                                   'source': 'cli', 'threadSource': 'user'}}})
        return observer

    def complete(self, observer, turn=OLD):
        return observer.server({'method': 'turn/completed', 'params': {
            'threadId': THREAD, 'turn': {'id': turn, 'status': 'completed'}}})

    def test_roster_does_not_grant_route_and_completion_is_deduplicated(self):
        observer = Notices('host', 'native')
        observer.server({'id': 1, 'result': {'thread': {'id': THREAD}}})
        self.assertIsNone(self.complete(observer))
        observer = self.bound()
        observer.server({'method': 'item/completed', 'params': {'threadId': THREAD, 'turnId': OLD,
            'item': {'type': 'agentMessage', 'phase': 'final_answer', 'text': '**Ready**'}}})
        notice = self.complete(observer)
        self.assertEqual(notice['body'], '**Ready**')
        self.assertIsNone(self.complete(observer))
        wire = packet(notice)
        type_field = wire.split(b':t=')[1].split(b':')[0]
        self.assertEqual(decode(base64.b64decode(type_field).decode()), notice['metadata'])
        self.assertIn(event_id(notice['metadata']).encode(), wire)

    def test_system_and_children_have_no_route(self):
        for origin in ({}, {'source': 'cli'}, {'threadSource': 'user'},
                       {'threadSource': 'thread_title'}, {'parentThreadId': NEW}, {'source': {'subagent': {}}}):
            observer = Notices('host', 'native')
            observer.client({'id': 7, 'method': 'thread/start'})
            observer.server({'id': 7, 'result': {'thread': {'id': THREAD, **origin}}})
            self.assertIsNone(self.complete(observer))

    def test_mismatched_resume_and_unsubscribe_revoke_no_unrelated_route(self):
        observer = self.bound()
        observer.client({'id': 8, 'method': 'thread/resume', 'params': {'threadId': NEW}})
        observer.server({'id': 8, 'result': {'thread': {'id': THREAD, 'source': 'cli', 'threadSource': 'user'}}})
        self.assertIsNotNone(self.complete(observer))
        observer = self.bound()
        observer.client({'id': 9, 'method': 'thread/unsubscribe', 'params': {'threadId': THREAD}})
        observer.server({'id': 9, 'error': {'code': -1}})
        self.assertIsNotNone(self.complete(observer))
        observer.server({'method': 'thread/closed', 'params': {'threadId': THREAD}})
        self.assertIsNone(self.complete(observer, NEW))
        observer = self.bound()
        observer.client({'id': 10, 'method': 'thread/unsubscribe', 'params': {'threadId': THREAD}})
        observer.server({'id': 10, 'result': {'status': 'unsubscribed'}})
        self.assertIsNone(self.complete(observer))

    def test_viewers_have_distinct_kitty_actions_and_same_episode(self):
        notice = self.complete(self.bound())
        first, second = packet(notice, route='a'), packet(notice, route='b')
        self.assertNotEqual(first.split(b':', 1)[0], second.split(b':', 1)[0])
        self.assertIn(b':f=Q29kZXg=', first)
        for wire in (first, second):
            tag = wire.split(b':t=')[1].split(b':')[0]
            self.assertEqual(decode(base64.b64decode(tag).decode()), notice['metadata'])

    def test_successful_native_resume_alias_binds_the_returned_exact_id(self):
        observer = Notices('host', 'native')
        observer.client({'id': 1, 'method': 'thread/resume', 'params': {'threadId': 'my-session-name'}})
        observer.server({'id': 1, 'result': {'thread': {'id': THREAD, 'source': 'cli', 'threadSource': 'user'}}})
        self.assertIsNotNone(self.complete(observer))

    def test_malformed_values_do_not_break_observer(self):
        observer = self.bound()
        for params in ({'threadId': []}, {'threadId': THREAD, 'item': {'phase': []}}, {'threadId': THREAD, 'turn': []}):
            observer.server({'method': 'item/completed', 'params': params})
        observer.client({'id': 8, 'method': 'thread/start'})
        observer.server({'id': 8, 'result': []})
        self.assertIsNotNone(self.complete(observer))

    def test_relation_uses_native_order_and_requires_original_completed_turn(self):
        page = {'data': [{'id': NEW, 'status': 'inProgress'}, {'id': OLD, 'status': 'completed'}]}
        self.assertEqual(relation(page, OLD), 'superseded')
        page['data'][0]['status'] = 'completed'
        self.assertEqual(relation(page, OLD), 'superseded')
        self.assertEqual(relation(page, NEW), 'current')
        self.assertEqual(relation({'data': [page['data'][0]]}, OLD), 'unknown')
        self.assertEqual(relation({'data': [page['data'][1]] * 2}, OLD), 'unknown')

    def test_inspector_only_reads_requested_threads_and_rechecks_owner(self):
        host, instance = source_identity('/tmp/native.sock')
        card = metadata(host, instance, THREAD, OLD)
        calls = []
        class Client:
            identity = 'same'
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def remaining(self, deadline): return 1
            def call(self, method, params, **kwargs):
                calls.append((method, params))
                return {'data': [{'id': NEW, 'status': 'completed'}, {'id': OLD, 'status': 'completed'}]}
        request = {'v': 1, 'nonce': 'a' * 32, 'cards': [card]}
        result = inspect(request, '/tmp/native.sock', client_factory=Client, identity=lambda _: 'same')
        self.assertEqual(result['results'][event_id(card)], 'superseded')
        self.assertEqual([c[0] for c in calls], ['thread/turns/list'])
        result = inspect(request, '/tmp/native.sock', client_factory=Client, identity=lambda _: 'changed')
        self.assertEqual(result['results'][event_id(card)], 'unknown')


if __name__ == '__main__':
    unittest.main()
