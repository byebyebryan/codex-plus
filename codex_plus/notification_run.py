"""Explicit native TUI route; relays bytes without replacing its UI or daemon."""

from __future__ import annotations

import asyncio
import base64
import os
from pathlib import Path
import signal
import sys
import tempfile

from .native import listener_identity
from .notification_inspect import source_identity
from .notification_protocol import encode, event_id
from .notification_stream import Messages, Notices
from .notifications import notification, terminal


def packet(notice, *, only_when='unfocused'):
    # Reuse legacy text normalization and UTF-8 truncation before adding metadata.
    body_packet = notification({'type': 'agent-turn-complete', 'last-assistant-message': notice['body']})
    encoded_body = body_packet.split(b';')[-1].removesuffix(b'\x07')
    title = ''.join(c if ord(c) >= 32 and not 127 <= ord(c) < 160 else ' ' for c in notice['title'])
    b64 = lambda text: base64.b64encode(text.encode(errors='replace')).decode()
    identifier = event_id(notice['metadata'])
    return (f'\x1b]99;i={identifier}:o={only_when}:t={b64(encode(notice["metadata"]))}:e=1:d=0;{b64(title[:128])}\x07'
            f'\x1b]99;i={identifier}:p=body:e=1:d=1;').encode() + encoded_body + b'\x07'


def publish(fd, data, tmux):
    if tmux:
        data = b'\x1bPtmux;' + data.replace(b'\x1b', b'\x1b\x1b') + b'\x1b\\'
    # Small packet, nonblocking writes: a broken display must not stop the native relay.
    try:
        while data:
            size = os.write(fd, data)
            if not size:
                break
            data = data[size:]
    except OSError:
        pass


async def run(path, arguments, executable='codex', *, only_when='unfocused'):
    if any(arg in ('--remote', '--no-daemon') or arg.startswith('--remote=') for arg in arguments):
        raise ValueError('run owns its native socket route; use --socket before --')
    # Only native interactive entry points are qualified. Other CLI commands stay direct.
    if any(arg in ('exec', 'app-server', 'login', 'logout', 'review', 'mcp', 'mcp-server', 'fork') for arg in arguments):
        raise ValueError('run supports interactive TUI launches only')
    identity = listener_identity(path)  # Existing user-owned daemon only; never starts one.
    target = terminal()
    if target is None:
        raise ValueError('run requires an attached Kitty terminal (direct or tmux)')
    tty, tmux = target
    fd = os.open(tty, os.O_WRONLY | os.O_NOCTTY | os.O_NONBLOCK)
    # /dev/tty itself is a root-owned device node for this process's controlling
    # terminal. An explicit tmux /dev/pts/N route additionally needs UID validation.
    if not os.isatty(fd) or (tmux and os.fstat(fd).st_uid != os.getuid()):
        os.close(fd)
        raise ValueError('notification route must be an owned terminal')
    host, instance = source_identity(path)
    connections = set()
    async def accept(reader, writer):
        task = asyncio.current_task()
        connections.add(task)
        backend = None
        try:
            if listener_identity(path) != identity:
                return
            upstream, backend = await asyncio.open_unix_connection(identity['resolved_socket'])
            notices = Notices(host, instance)
            async def pump(source, destination, client):
                observer = Messages()
                while data := await source.read(65536):
                    # Forward first. Observation never edits or reconstructs native bytes.
                    destination.write(data)
                    await destination.drain()
                    try:
                        for value in observer.feed(data):
                            if client:
                                notices.client(value)
                            elif notice := notices.server(value):
                                publish(fd, packet(notice, only_when=only_when), tmux)
                    except Exception:
                        observer.disabled = True
                        print('codex-notify: metadata observation unavailable on this connection', file=sys.stderr)
            pumps = [asyncio.create_task(pump(reader, backend, True)),
                     asyncio.create_task(pump(upstream, writer, False))]
            try:
                await asyncio.wait(pumps, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for pending in pumps:
                    pending.cancel()
                await asyncio.gather(*pumps, return_exceptions=True)
        except (OSError, RuntimeError):
            pass
        finally:
            writer.close()
            if backend is not None:
                backend.close()
            connections.discard(task)
    process = None
    try:
        # Short path, private directory and socket. No long-lived service or persistent log.
        with tempfile.TemporaryDirectory(prefix='codex-notify-', dir='/tmp') as directory:
            proxy = str(Path(directory) / 'client.sock')
            server = await asyncio.start_unix_server(accept, path=proxy)
            os.chmod(proxy, 0o600)
            try:
                # Ctrl-C remains native TUI input/lifecycle; do not cancel its parent.
                asyncio.get_running_loop().add_signal_handler(signal.SIGINT, lambda: None)
                process = await asyncio.create_subprocess_exec(executable, '--remote', 'unix://' + proxy,
                    '-c', 'notify=[]', '-c', 'tui.notifications=["approval-requested"]', *arguments)
                loop = asyncio.get_running_loop()
                for sig in (signal.SIGTERM, signal.SIGHUP):
                    loop.add_signal_handler(sig, lambda sig=sig: process.send_signal(sig) if process.returncode is None else None)
                return await process.wait()
            finally:
                server.close()
                await server.wait_closed()
                if process is not None and process.returncode is None:
                    process.terminate()
                    await process.wait()
                for task in tuple(connections):
                    task.cancel()
                await asyncio.gather(*connections, return_exceptions=True)
    finally:
        os.close(fd)
