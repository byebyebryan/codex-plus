"""Configured completion transport, independent of any attached terminal."""

from __future__ import annotations

import json
import os
from pathlib import Path
import selectors
import signal
import stat
import subprocess
import time
import tomllib

from .native import Client, listener_identity
from .notification_inspect import default_socket, source_identity
from .notification_protocol import event_id, metadata, native_id, validate
from .notifications import completion_body

MAX_EVENT = 16384
MAX_REPLY = 1024


def config_path():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'codex-plus/notify.toml'


def load_config(path):
    path = Path(path).expanduser()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise ValueError('notification config must be an owned regular file without group/world write')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            raw = stream.read(32769)
        if len(raw) > 32768:
            raise ValueError('notification config exceeds bound')
        result = tomllib.loads(raw.decode())
        if type(result.get('v')) is not int or result['v'] != 1:
            raise ValueError('unsupported notification config')
        return result
    finally:
        os.close(fd)


def command(value, *, placeholders=False):
    if (not isinstance(value, list) or not 1 <= len(value) <= 32
            or any(not isinstance(arg, str) or not arg or '\0' in arg or len(arg.encode()) > 2048 for arg in value)
            or sum(len(arg.encode()) for arg in value) > 8192
            or not Path(value[0]).is_absolute()):
        raise ValueError('notification command requires bounded argv and an absolute executable')
    for arg in value:
        if ('{' in arg or '}' in arg) and (not placeholders or arg != '{thread}'):
            raise ValueError('only a complete {thread} argument is supported')
    return value


def eligible_thread(socket_path, thread_id, *, client_factory=Client, identity=listener_identity):
    # Internal title/model work can invoke legacy notify too, without a local
    # index row. Require positive native user-thread evidence, never a title or
    # the absence of a child marker. This read does not load/resume any thread.
    try:
        with client_factory(socket_path, experimental=True, timeout=2) as client:
            thread = client.call('thread/read', {'threadId': thread_id, 'includeTurns': False}, timeout=2)['thread']
            return (isinstance(thread, dict) and thread.get('id') == thread_id
                    and thread.get('threadSource') == 'user' and not thread.get('parentThreadId')
                    and thread.get('source') in ('cli', 'vscode', 'appServer')
                    and identity(socket_path) == client.identity)
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, TimeoutError):
        return False


def envelope(payload, socket_path):
    body = completion_body(payload)
    if body is None:
        return None
    thread, turn = native_id(payload.get('thread-id')), native_id(payload.get('turn-id'))
    if not eligible_thread(socket_path, thread):
        return None
    host, instance = source_identity(socket_path)
    value = {'v': 1, 'metadata': metadata(host, instance, thread, turn),
             'title': 'Codex', 'body': body}
    return validate_event(value)


def validate_event(value):
    if (not isinstance(value, dict) or set(value) != {'v', 'metadata', 'title', 'body'}
            or type(value['v']) is not int or value['v'] != 1 or value['title'] != 'Codex'
            or not isinstance(value['body'], str) or not 1 <= len(value['body'].encode()) <= 2048
            or any(c != '\n' and (ord(c) < 32 or 127 <= ord(c) < 160) for c in value['body'])):
        raise ValueError('invalid notification event')
    validate(value['metadata'])
    if value['metadata']['body_format'] != 'markdown':
        raise ValueError('unsupported completion body format')
    return value


def encode_event(value):
    raw = json.dumps(validate_event(value), separators=(',', ':'), ensure_ascii=True).encode() + b'\n'
    if len(raw) > MAX_EVENT:
        raise ValueError('notification event exceeds bound')
    return raw


def read_event(stream):
    raw = stream.read(MAX_EVENT + 1)
    if len(raw) > MAX_EVENT:
        raise ValueError('notification event exceeds bound')
    def unique(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError('duplicate notification field')
            result[key] = item
        return result
    return validate_event(json.loads(raw, object_pairs_hook=unique))


def read_line(stream, deadline, *, limit=MAX_REPLY):
    """Read one bounded line without buffering later action bytes."""
    data = bytearray()
    with selectors.DefaultSelector() as selector:
        selector.register(stream, selectors.EVENT_READ)
        while len(data) <= limit:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise TimeoutError('notification response timed out')
            chunk = os.read(stream.fileno(), 1)
            if not chunk:
                raise ValueError('notification response ended early')
            if chunk == b'\n':
                return bytes(data)
            data += chunk
    raise ValueError('notification response exceeds bound')


def stop(process, *, group=True):
    # Every transport/worker owns a fresh process group. Never signal a native owner.
    if process.returncode is not None:
        return
    try:
        if group:
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass
    process.wait()


def write_input(process, data, deadline):
    os.set_blocking(process.stdin.fileno(), False)
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdin, selectors.EVENT_WRITE)
        while data:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise TimeoutError('notification transport input timed out')
            try:
                size = os.write(process.stdin.fileno(), data)
            except BlockingIOError:
                continue
            data = data[size:]
    process.stdin.close()


def check_reply(value, event):
    if (not isinstance(value, dict) or set(value) != {'v', 'event', 'status', 'desktop_id'}
            or type(value['v']) is not int or value['v'] != 1
            or value['event'] != event_id(event['metadata'])
            or value['status'] not in ('delivered', 'duplicate', 'uncertain')
            or type(value['desktop_id']) is not int or not 0 <= value['desktop_id'] <= 0xffffffff
            or (value['status'] != 'uncertain' and value['desktop_id'] == 0)):
        raise ValueError('invalid notification delivery reply')
    return value


def forward(event, argv, *, timeout=8):
    argv = command(argv)
    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.monotonic() + timeout
        write_input(process, encode_event(event), deadline)
        result = check_reply(json.loads(read_line(process.stdout, deadline)), event)
        process.wait(timeout=max(.01, deadline - time.monotonic()))
        if process.returncode != 0:
            raise ValueError('notification transport failed')
        return result
    finally:
        stop(process)
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()


def hook(payload, config):
    path = config.get('socket', default_socket())
    if not isinstance(path, str) or not Path(path).is_absolute():
        raise ValueError('notification source socket must be absolute')
    event = envelope(payload, path)
    return forward(event, config.get('command')) if event is not None else None
