"""Bounded, local-only app-server client for the monitoring study.

This is spike code, not an installed client or destination-discovery API.
It connects to an existing Unix listener and never starts an app server.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import time
from typing import Any


class RpcError(RuntimeError):
    pass


def listener_identity(requested: str) -> dict[str, Any]:
    resolved = Path(requested).resolve(strict=True)
    rows = [line.split() for line in Path('/proc/net/unix').read_text().splitlines()[1:]]
    inodes = {row[6] for row in rows if len(row) >= 8 and row[7] == str(resolved)
              and row[3] == '00010000'}
    owners = []
    for process in Path('/proc').iterdir():
        if not process.name.isdecimal():
            continue
        try:
            owned = False
            for fd in (process / 'fd').iterdir():
                try:
                    owned |= os.readlink(fd) in {'socket:[' + i + ']' for i in inodes}
                except OSError:
                    continue
            if owned:
                # Start ticks distinguish PID reuse; executable alone does not.
                stat_tail = (process / 'stat').read_text().rsplit(')', 1)[1].split()
                owners.append({'pid': int(process.name), 'start_ticks': stat_tail[19],
                               'executable': os.readlink(process / 'exe')})
        except OSError:
            continue
    if len(inodes) != 1 or len(owners) != 1:
        raise RpcError('listener ownership is unavailable or ambiguous')
    return {'host': socket.gethostname(), 'requested_socket': requested,
            'resolved_socket': str(resolved), **owners[0]}


class Client:
    def __init__(self, requested: str, *, experimental: bool = False):
        self.identity = listener_identity(requested)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.buffer = b''
        self.fragments = bytearray()
        self.responses: dict[int, dict] = {}
        self.events: list[dict] = []
        self.sequence = 0
        self.thread_id: str | None = None
        self.process_ids: set[str] = set()
        try:
            self.sock.connect(self.identity['resolved_socket'])
            key = base64.b64encode(os.urandom(16)).decode()
            self.sock.sendall(('GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n'
                               'Connection: Upgrade\r\nSec-WebSocket-Key: ' + key +
                               '\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
            while b'\r\n\r\n' not in self.buffer:
                if len(self.buffer) > 16384:
                    raise RpcError('oversized upgrade response')
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise RpcError('EOF during upgrade')
                self.buffer += chunk
            header, self.buffer = self.buffer.split(b'\r\n\r\n', 1)
            expected = base64.b64encode(hashlib.sha1(
                (key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
            headers = dict(line.split(b':', 1) for line in header.split(b'\r\n')[1:])
            headers = {k.lower(): v.strip() for k, v in headers.items()}
            if not header.startswith(b'HTTP/1.1 101 ') or headers.get(b'sec-websocket-accept') != expected:
                raise RpcError('WebSocket upgrade rejected')
            self.call('initialize', {'clientInfo': {'name': 'codex_plus_spike',
                                                   'version': '0.1.0'},
                                     'capabilities': {'experimentalApi': experimental}})
            self.send({'method': 'initialized'})
        except BaseException:
            self.sock.close()
            raise

    def close(self) -> None:
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def send(self, message: dict | bytes, opcode: int = 1) -> None:
        payload = message if isinstance(message, bytes) else json.dumps(message).encode()
        mask = os.urandom(4)
        length = len(payload)
        size = (bytes([0x80 | length]) if length < 126 else
                bytes([0x80 | 126]) + struct.pack('!H', length) if length < 65536 else
                bytes([0x80 | 127]) + struct.pack('!Q', length))
        encoded = bytes(value ^ mask[i % 4] for i, value in enumerate(payload))
        self.sock.sendall(bytes([0x80 | opcode]) + size + mask + encoded)

    def submit(self, method: str, params: dict) -> int:
        self.sequence += 1
        if method == 'command/exec' and params.get('processId'):
            self.process_ids.add(params['processId'])
        self.send({'id': self.sequence, 'method': method, 'params': params})
        return self.sequence

    def _fill(self, count: int, deadline: float) -> None:
        while len(self.buffer) < count:
            self.sock.settimeout(max(0.001, deadline - time.monotonic()))
            chunk = self.sock.recv(max(4096, count - len(self.buffer)))
            if not chunk:
                raise RpcError('transport EOF')
            self.buffer += chunk

    def receive(self, timeout: float = 10) -> dict:
        deadline = time.monotonic() + timeout
        while True:
            self._fill(2, deadline)
            a, b = self.buffer[:2]
            length = b & 127
            offset = 2
            if length == 126:
                self._fill(4, deadline)
                length = struct.unpack('!H', self.buffer[2:4])[0]
                offset = 4
            elif length == 127:
                self._fill(10, deadline)
                length = struct.unpack('!Q', self.buffer[2:10])[0]
                offset = 10
            if length > 2 * 1024 * 1024 or len(self.fragments) + length > 2 * 1024 * 1024:
                raise RpcError('oversized protocol frame')
            header_size = offset + (4 if b & 128 else 0)
            self._fill(header_size + length, deadline)
            mask = self.buffer[offset:header_size] if b & 128 else None
            payload = self.buffer[header_size:header_size + length]
            self.buffer = self.buffer[header_size + length:]
            if mask:
                payload = bytes(value ^ mask[i % 4] for i, value in enumerate(payload))
            opcode = a & 15
            if opcode == 8:
                raise RpcError('WebSocket closed')
            if opcode == 9:
                self.send(payload, 10)
                continue
            if opcode == 10:
                continue
            if opcode not in (0, 1):
                raise RpcError('unexpected WebSocket frame')
            self.fragments.extend(payload)
            if a & 128:
                message = json.loads(self.fragments)
                self.fragments.clear()
                if 'id' in message and ('result' in message or 'error' in message):
                    self.responses[message['id']] = message
                else:
                    params = message.get('params', {})
                    if (self.thread_id and params.get('threadId') == self.thread_id or
                            params.get('processId') in self.process_ids):
                        self.events.append(message)
                return message

    def result(self, request_id: int, timeout: float = 10) -> dict:
        deadline = time.monotonic() + timeout
        while request_id not in self.responses:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('RPC outcome unknown after deadline')
            self.receive(remaining)
        response = self.responses.pop(request_id)
        if 'error' in response:
            raise RpcError(json.dumps(response['error']))
        return response['result']

    def call(self, method: str, params: dict, timeout: float = 10) -> dict:
        return self.result(self.submit(method, params), timeout)

    def bind(self, thread_id: str) -> dict:
        if listener_identity(self.identity['requested_socket']) != self.identity:
            raise RpcError('listener owner changed')
        cursor = None
        for _ in range(20):
            params = {'limit': 100}
            if cursor:
                params['cursor'] = cursor
            page = self.call('thread/loaded/list', params)
            if thread_id in page['data']:
                self.thread_id = thread_id
                return {**self.identity, 'thread_id': thread_id}
            cursor = page.get('nextCursor')
            if not cursor:
                break
        raise RpcError('target not positively present in loaded inventory')

    def wait_turn(self, turn_id: str, timeout: float = 60) -> dict:
        deadline = time.monotonic() + timeout
        while True:
            for event in self.events:
                if (event.get('method') == 'turn/completed' and
                        event['params']['turn']['id'] == turn_id):
                    return event['params']['turn']
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('turn not completed before deadline')
            self.receive(remaining)
