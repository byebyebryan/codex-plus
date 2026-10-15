"""Observe bounded metadata from an explicitly routed native client connection."""

from __future__ import annotations

from collections import OrderedDict
import json
import struct

from .notification_protocol import label, metadata, native_id

MAX_MESSAGE = 256 * 1024
MAX_THREADS = 32
MAX_REQUESTS = 128
MAX_FINALS = 64


class Messages:
    """An observer only: all bytes continue through the independently owned relay."""

    def __init__(self, *, max_message=MAX_MESSAGE):
        self.maximum = max_message
        self.buffer = bytearray()
        self.fragments = bytearray()
        self.http = True
        self.skip = 0
        self.discard_fragment = False
        self.disabled = False
        self.skipped = 0

    def feed(self, data):
        if self.disabled:
            return []
        if self.skip:
            count = min(len(data), self.skip)
            data = data[count:]
            self.skip -= count
        self.buffer.extend(data)
        if self.http:
            boundary = self.buffer.find(b'\r\n\r\n')
            if boundary < 0:
                if len(self.buffer) > 16384:
                    self.buffer.clear()
                    self.disabled = True
                return []
            if boundary > 16384:
                self.buffer.clear()
                self.disabled = True
                return []
            del self.buffer[:boundary + 4]
            self.http = False
        output = []
        while len(self.buffer) >= 2:
            first, second = self.buffer[:2]
            length, offset = second & 127, 2
            if length == 126:
                if len(self.buffer) < 4:
                    break
                length, offset = struct.unpack('!H', self.buffer[2:4])[0], 4
            elif length == 127:
                if len(self.buffer) < 10:
                    break
                length, offset = struct.unpack('!Q', self.buffer[2:10])[0], 10
            offset += 4 if second & 128 else 0
            opcode, final = first & 15, bool(first & 128)
            if length > self.maximum:
                total = offset + length
                count = min(total, len(self.buffer))
                del self.buffer[:count]
                self.skip = total - count
                self.fragments.clear()
                self.discard_fragment = not final
                self.skipped += 1
                if self.skip:
                    break
                continue
            if len(self.buffer) < offset + length:
                break
            mask = self.buffer[offset - 4:offset] if second & 128 else None
            payload = bytes(self.buffer[offset:offset + length])
            del self.buffer[:offset + length]
            if mask:
                payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
            if opcode in (8, 9, 10):
                continue
            if opcode not in (0, 1) or first & 112:
                self.fragments.clear()
                self.discard_fragment = not final
                continue
            if opcode == 1:
                self.fragments.clear()
                self.discard_fragment = False
            if self.discard_fragment:
                if final:
                    self.discard_fragment = False
                continue
            self.fragments.extend(payload)
            if len(self.fragments) > self.maximum:
                self.fragments.clear()
                self.discard_fragment = not final
                self.skipped += 1
                continue
            if final:
                try:
                    value = json.loads(self.fragments)
                    if isinstance(value, dict):
                        output.append(value)
                except (ValueError, UnicodeError, RecursionError):
                    pass
                self.fragments.clear()
        return output


def bounded_put(mapping, key, value, limit):
    mapping.pop(key, None)
    mapping[key] = value
    while len(mapping) > limit:
        mapping.popitem(last=False)


def eligible(thread):
    return (thread.get('threadSource') == 'user' and not thread.get('parentThreadId')
            and thread.get('source') in ('cli', 'vscode', 'appServer'))


class Notices:
    """Bind only explicit native start/resume requests; rosters cannot grant a route."""

    def __init__(self, host, instance):
        self.host, self.instance = label(host, 63), label(instance, 128)
        self.requests = OrderedDict()
        self.threads = OrderedDict()
        self.finals = OrderedDict()
        self.sent = OrderedDict()

    def forget(self, thread):
        self.threads.pop(thread, None)
        for key in tuple(self.finals):
            if key[0] == thread:
                self.finals.pop(key, None)

    def client(self, value):
        identifier, method = value.get('id'), value.get('method')
        if (method in ('thread/start', 'thread/resume', 'thread/unsubscribe', 'thread/archive')
                and isinstance(identifier, (str, int)) and not isinstance(identifier, bool)):
            params = value.get('params')
            target = params.get('threadId') if isinstance(params, dict) else None
            canonical = False
            if method != 'thread/start':
                try:
                    target = native_id(target)
                    canonical = True
                except (ValueError, TypeError):
                    if (method != 'thread/resume' or not isinstance(target, str)
                            or not target or len(target) > 256 or any(ord(c) < 32 for c in target)):
                        return
            bounded_put(self.requests, identifier, (method, target, canonical), MAX_REQUESTS)

    def server(self, value):
        identifier = value.get('id')
        if isinstance(identifier, (str, int)) and not isinstance(identifier, bool) and identifier in self.requests:
            method, target, canonical = self.requests.pop(identifier)
            result = value.get('result')
            if method in ('thread/unsubscribe', 'thread/archive'):
                if isinstance(result, dict) and 'error' not in value:
                    if method == 'thread/archive' or result.get('status') in ('unsubscribed', 'notSubscribed', 'notLoaded'):
                        self.forget(target)
                return None
            thread = result.get('thread') if isinstance(result, dict) else None
            if isinstance(thread, dict):
                try:
                    tid = native_id(thread.get('id'))
                except (ValueError, TypeError, AttributeError):
                    return None
                if method == 'thread/resume' and canonical and tid != target:
                    return None
                if not eligible(thread):
                    self.forget(tid)
                    return None
                name = thread.get('name')
                bounded_put(self.threads, tid, name[:256] if isinstance(name, str) else '', MAX_THREADS)
            return None
        params = value.get('params')
        if not isinstance(params, dict):
            return None
        tid = params.get('threadId')
        if not isinstance(tid, str) or tid not in self.threads:
            return None
        method = value.get('method')
        if method in ('thread/closed', 'thread/archived'):
            self.forget(tid)
        elif method == 'thread/name/updated':
            name = params.get('threadName')
            if isinstance(name, str):
                self.threads[tid] = name[:256]
        elif method == 'item/completed':
            item = params.get('item')
            turn = params.get('turnId')
            if (isinstance(item, dict) and item.get('type') == 'agentMessage'
                    and item.get('phase') in (None, 'final_answer') and isinstance(item.get('text'), str)
                    and isinstance(turn, str)):
                bounded_put(self.finals, (tid, turn), item['text'][:8192], MAX_FINALS)
        elif method == 'turn/completed':
            turn = params.get('turn')
            if not isinstance(turn, dict) or turn.get('status') != 'completed':
                return None
            try:
                native_id(turn.get('id'))
            except (ValueError, TypeError, AttributeError):
                return None
            key = tid, turn['id']
            if key in self.sent:
                return None
            bounded_put(self.sent, key, True, MAX_FINALS)
            text = self.finals.pop(key, '')
            rich = metadata(self.host, self.instance, tid, turn['id'], markdown=bool(text))
            return {'metadata': rich, 'title': self.threads[tid] or 'Codex',
                    'body': text or 'Turn complete.'}
        return None
