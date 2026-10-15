"""Explicit native TUI route; relays bytes without replacing its UI or daemon."""

from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
import os
import secrets
import signal
import sys
import tempfile

from .native import listener_identity
from .notification_inspect import source_identity
from .notification_launcher import preflight
from .notification_protocol import encode, event_id
from .notification_stream import Messages, Notices
from .notifications import notification, terminal


def packet(notice, *, only_when='unfocused', route=''):
    body_packet = notification({'type': 'agent-turn-complete', 'last-assistant-message': notice['body']})
    encoded_body = body_packet.split(b';')[-1].removesuffix(b'\x07')
    title = ''.join(c if ord(c) >= 32 and not 127 <= ord(c) < 160 else ' ' for c in notice['title'])
    title = (title[:128] or 'Codex') + ' @ ' + notice['metadata']['host']
    b64 = lambda text: base64.b64encode(text.encode(errors='replace')).decode()
    # Kitty identifiers are local to its process, not per terminal window. Give
    # independent viewers distinct action targets while preserving episode metadata.
    identifier = event_id(notice['metadata']) + ('-' + route if route else '')
    return (f'\x1b]99;i={identifier}:f={b64("Codex")}:o={only_when}:w=30000:'
            f't={b64(encode(notice["metadata"]))}:e=1:d=0;{b64(title)}\x07'
            f'\x1b]99;i={identifier}:p=body:e=1:d=1;').encode() + encoded_body + b'\x07'


def publish(fd, data, tmux):
    if tmux:
        data = b'\x1bPtmux;' + data.replace(b'\x1b', b'\x1b\x1b') + b'\x1b\\'
    try:
        while data:
            size = os.write(fd, data)
            if not size:
                return False
            data = data[size:]
    except OSError:
        return False
    return True


@dataclass
class Prepared:
    owner: dict
    fd: int
    tmux: bool
    overrides: list[str]
    route: str


def prepare(path, arguments, executable):
    target = terminal()
    if target is None:
        raise ValueError('rich notifications require an attached Kitty terminal')
    tty, tmux = target
    fd = os.open(tty, os.O_WRONLY | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        if not os.isatty(fd) or (tmux and os.fstat(fd).st_uid != os.getuid()):
            raise ValueError('notification route must be an owned terminal')
        owner, overrides = preflight(path, arguments, executable)
        return Prepared(owner, fd, tmux, overrides, secrets.token_hex(8))
    except BaseException:
        os.close(fd)
        raise


def degraded_notice(prepared):
    title = base64.b64encode(b'Rich Codex notifications paused').decode()
    body = base64.b64encode(b'Your native session continues. This window may miss completion alerts; '
                            b'use a fresh native launch to restore basic notifications.').decode()
    identifier = 'codex-notify-status-' + prepared.route
    publish(prepared.fd, (f'\x1b]99;i={identifier}:f=Q29kZXg=:o=unfocused:w=30000:e=1:d=0;{title}\x07'
                         f'\x1b]99;i={identifier}:p=body:e=1:d=1;{body}\x07').encode(), prepared.tmux)


async def run(path, arguments, executable='/usr/bin/codex', *, only_when='unfocused', prepared=None):
    prepared = prepared or prepare(path, arguments, executable)
    identity, fd, tmux = prepared.owner, prepared.fd, prepared.tmux
    host, instance = source_identity(path)
    connections = set()
    warned = False

    def degrade():
        nonlocal warned
        if not warned:
            warned = True
            print('codex-notify: rich notification observation unavailable; native session continues', file=sys.stderr)
            degraded_notice(prepared)

    async def accept(reader, writer):
        task = asyncio.current_task()
        if len(connections) >= 4:
            writer.close()
            return
        connections.add(task)
        backend = None
        try:
            if listener_identity(path) != identity:
                degrade()
                return
            upstream, backend = await asyncio.open_unix_connection(identity['resolved_socket'])
            notices = Notices(host, instance)
            observing = True

            async def pump(source, destination, client):
                nonlocal observing
                observer = Messages()
                while data := await source.read(65536):
                    destination.write(data)
                    await destination.drain()
                    if not observing:
                        continue
                    try:
                        values = observer.feed(data)
                        if observer.disabled:
                            raise ValueError('unsupported native framing')
                        for value in values:
                            if client:
                                notices.client(value)
                            elif notice := notices.server(value):
                                if not publish(fd, packet(notice, only_when=only_when, route=prepared.route), tmux):
                                    raise OSError('terminal notification write failed')
                    except Exception:
                        observing = False
                        degrade()

            pumps = [asyncio.create_task(pump(reader, backend, True)),
                     asyncio.create_task(pump(upstream, writer, False))]
            try:
                completed, _ = await asyncio.wait(pumps, return_when=asyncio.FIRST_COMPLETED)
                if any(task.exception() is not None for task in completed):
                    degrade()
            finally:
                for pending in pumps:
                    pending.cancel()
                await asyncio.gather(*pumps, return_exceptions=True)
        except (OSError, RuntimeError):
            degrade()
        finally:
            writer.close()
            if backend is not None:
                backend.close()
            connections.discard(task)

    process = None
    loop = asyncio.get_running_loop()
    signals = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    try:
        with tempfile.TemporaryDirectory(prefix='codex-notify-', dir='/tmp') as directory:
            proxy = directory + '/client.sock'
            server = await asyncio.start_unix_server(accept, path=proxy)
            os.chmod(proxy, 0o600)
            try:
                loop.add_signal_handler(signal.SIGINT, lambda: None)
                process = await asyncio.create_subprocess_exec(executable, '--remote', 'unix://' + proxy,
                    *prepared.overrides, *arguments)
                for sig in (signal.SIGTERM, signal.SIGHUP):
                    loop.add_signal_handler(sig, lambda sig=sig: process.send_signal(sig) if process.returncode is None else None)
                return await process.wait()
            finally:
                server.close()
                await server.wait_closed()
                if process is not None and process.returncode is None:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), 4)
                    except TimeoutError:
                        process.kill()
                        await process.wait()
                for task in tuple(connections):
                    task.cancel()
                await asyncio.gather(*connections, return_exceptions=True)
    finally:
        for sig, previous in signals.items():
            loop.remove_signal_handler(sig)
            signal.signal(sig, previous)
        os.close(fd)
