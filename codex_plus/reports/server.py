"""Plain HTTP hosting with explicit, owned tmux session controls."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys
import time
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import build_opener, ProxyHandler
import uuid

from . import VERSION
from .config import absolute_path, config_path, load
from .store import Store, canonical, no_links, owned_directory, process_birth

SESSION = "codex-report-server"
OWNER_OPTION = "@codex_report_server_owner"


def settings(config):
    if not config.base_url or urlsplit(config.base_url).scheme != "http":
        raise ValueError("the built-in server needs a configured HTTP base_url; HTTPS can use an external server")
    url = urlsplit(config.base_url)
    return config.server_bind or url.hostname, url.port or 80, unquote(url.path).rstrip('/') + '/'


def fingerprint(config):
    return hashlib.sha256(canonical({'data_root': str(config.data_root), 'base_url': config.base_url,
                                     'server_bind': config.server_bind})).hexdigest()


def probe_url(config):
    bind, port, prefix = settings(config)
    host = '127.0.0.1' if bind == '0.0.0.0' else '::1' if bind == '::' else bind
    authority = f'[{host}]:{port}' if ':' in host else f'{host}:{port}'
    return urlunsplit(('http', authority, quote(prefix, safe='/') + '_server-health', '', ''))


def health(config):
    with build_opener(ProxyHandler({})).open(probe_url(config), timeout=1) as response:
        data = response.read(4097)
        if response.status != 200 or len(data) > 4096:
            raise ValueError('unexpected report server health response')
    value = json.loads(data)
    if not isinstance(value, dict) or value.get('component') != SESSION or value.get('fingerprint') != fingerprint(config):
        raise ValueError('the endpoint does not identify this report server configuration')
    return value


def make_server(config, *, port=None, instance=None):
    bind, configured_port, prefix = settings(config)
    root = config.data_root / 'public'
    token = instance or uuid.uuid4().hex
    if not re.fullmatch('[0-9a-f]{32}', token):
        raise ValueError('invalid report server instance')

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def setup(self):
            super().setup()
            self.connection.settimeout(15)

        def translate_path(self, path):
            decoded = unquote(urlsplit(path).path, errors='strict')
            if not decoded.startswith(prefix) or '\\' in decoded:
                raise ValueError('outside report URL prefix')
            parts = decoded[len(prefix):].rstrip('/').split('/') if decoded != prefix else []
            if any(not p or p in ('.', '..') or p.startswith('.write-') or any(ord(c) < 32 for c in p) for p in parts):
                raise ValueError('invalid report path')
            target = root.joinpath(*parts)
            no_links(target)
            return str(target)

        def send_head(self):
            try:
                path = unquote(urlsplit(self.path).path, errors='strict')
            except (ValueError, UnicodeError):
                self.send_error(404, 'Report not found'); return None
            if path == prefix.rstrip('/') and prefix != '/':
                self.send_response(301); self.send_header('Location', quote(prefix, safe='/'))
                self.send_header('Content-Length', '0'); self.end_headers(); return None
            if path == prefix + '_server-health':
                value = {'schema': 1, 'component': SESSION, 'version': VERSION,
                         'instance': token, 'fingerprint': fingerprint(config)}
                data = canonical(value)
                self.send_response(200); self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data))); self.send_header('Cache-Control', 'no-store')
                self.end_headers(); return io.BytesIO(data)
            try:
                self.translate_path(self.path)
                return super().send_head()
            except (ValueError, OSError, UnicodeError):
                self.send_error(404, 'Report not found'); return None

        def list_directory(self, path):
            self.send_error(404, 'Directory listing is disabled'); return None

        def end_headers(self):
            self.send_header('X-Content-Type-Options', 'nosniff')
            super().end_headers()

    server_type = ThreadingHTTPServer
    if ':' in bind:
        class IPv6Server(ThreadingHTTPServer):
            address_family = socket.AF_INET6
        server_type = IPv6Server
    server = server_type((bind, configured_port if port is None else port), Handler)
    try:
        store = Store(config)
        with store.locked():
            store.rebuild()
    except BaseException:
        server.server_close(); raise
    return server


class Controller:
    def __init__(self, config, path, *, socket_path=None):
        self.config, self.path = config, absolute_path(path)
        self.command = ['tmux'] + (['-S', str(absolute_path(socket_path)), '-f', '/dev/null'] if socket_path else [])

    def tmux(self, *args, optional=False):
        result = subprocess.run([*self.command, *map(str, args)], capture_output=True, text=True, timeout=5)
        if result.returncode:
            if optional: return None
            raise ValueError('tmux: ' + result.stderr.strip()[:1024])
        return result.stdout.strip()

    @contextmanager
    def locked(self):
        parent = self.config.data_root.parent
        owned_directory(parent, create=True)
        fd = os.open(parent / '.codex-report-server.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            s = os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid():
                raise ValueError('unsafe report server control lock')
            fcntl.flock(fd, fcntl.LOCK_EX); yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN); os.close(fd)

    def owned(self):
        inventory = self.tmux('list-sessions', '-F', '#{session_name}\t#{session_id}', optional=True)
        sid = next((line.split('\t', 1)[1] for line in (inventory or '').splitlines()
                    if line.startswith(SESSION + '\t')), None)
        if sid is None: return None
        raw = self.tmux('show-options', '-qv', '-t', sid, OWNER_OPTION)
        if not raw or len(raw) > 16384:
            raise ValueError('the existing codex-report-server session is not owned by this launcher')
        owner = json.loads(raw)
        if (owner.get('schema') != 1 or owner.get('component') != SESSION
                or owner.get('fingerprint') != fingerprint(self.config)
                or not re.fullmatch('[0-9a-f]{32}', owner.get('instance', ''))):
            raise ValueError('the existing report session belongs to another configuration')
        panes = self.tmux('list-panes', '-s', '-t', sid, '-F', '#{pane_pid}\t#{pane_dead}').splitlines()
        if len(panes) != 1:
            raise ValueError('the report session has additional panes; refusing to manage them')
        pid, dead = panes[0].split('\t')
        if dead != '1':
            actual = (Path('/proc') / pid / 'cmdline').read_bytes().rstrip(b'\0').split(b'\0')
            if actual != [arg.encode() for arg in owner.get('argv', [])]:
                raise ValueError('the report pane now runs a different process; no action was taken')
        return {**owner, 'session_id': sid, 'pid': int(pid), 'dead': dead == '1'}

    def status(self):
        owner = self.owned()
        if owner is None: return {'state': 'stopped', 'session': SESSION, 'url': self.config.base_url}
        result = {'state': 'unhealthy', 'session': SESSION, 'session_id': owner['session_id'],
                  'pid': owner['pid'], 'url': self.config.base_url}
        if owner['dead']: return {**result, 'detail': 'the HTTP server process has exited'}
        try:
            value = health(self.config)
            if value.get('instance') != owner['instance']: raise ValueError('the endpoint instance differs')
            return {**result, 'state': 'running', 'version': value['version']}
        except (OSError, ValueError) as error:
            return {**result, 'detail': str(error)[:1024]}

    def stop_owned(self):
        owner = self.owned()
        if owner is not None:
            birth = process_birth(owner['pid'])
            self.tmux('kill-session', '-t', owner['session_id'])
            deadline = time.monotonic() + 3
            while birth is not None and process_birth(owner['pid']) == birth:
                if time.monotonic() >= deadline: raise ValueError('the owned HTTP process did not exit after stopping its session')
                time.sleep(0.02)
        return {'state': 'stopped', 'session': SESSION, 'url': self.config.base_url}

    def start(self, *, restart=False):
        settings(self.config)
        with self.locked():
            owner = self.owned()
            if owner is not None:
                if not restart:
                    result = self.status()
                    if result['state'] != 'running': raise ValueError('the owned server is unhealthy; use restart or attach to inspect it')
                    return {**result, 'reused': True}
                self.stop_owned()
            store = Store(self.config)
            with store.locked(): store.rebuild()
            token = uuid.uuid4().hex
            script = Path(__file__).resolve().parents[2] / 'scripts/codex-report-server'
            argv = [sys.executable, '-B', str(script), '--config', str(self.path), 'serve', '--instance', token]
            sid = self.tmux('new-session', '-d', '-P', '-F', '#{session_id}', '-s', SESSION, '-n', 'http', *argv)
            marker = {'schema': 1, 'component': SESSION, 'fingerprint': fingerprint(self.config), 'instance': token, 'argv': argv}
            self.tmux('set-option', '-t', sid, OWNER_OPTION, json.dumps(marker))
            self.tmux('set-option', '-t', sid, 'remain-on-exit', 'on')
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                try:
                    result = self.status()
                except (OSError, ValueError):
                    time.sleep(0.05); continue
                if result['state'] == 'running': return {**result, 'reused': False}
                time.sleep(0.05)
            raise ValueError('HTTP server did not become ready; attach to codex-report-server to inspect its output')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=config_path())
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--tmux-socket', type=Path, help='Separate tmux socket for isolated checks')
    commands = parser.add_subparsers(dest='action', required=True)
    for action in ('start', 'stop', 'restart', 'status', 'attach'): commands.add_parser(action)
    serve = commands.add_parser('serve'); serve.add_argument('--instance')
    args = parser.parse_args(argv)
    try:
        config = load(args.config)
        if args.action == 'serve':
            with make_server(config, instance=args.instance) as server:
                print(f'{SESSION}: serving {config.base_url} from {config.data_root / "public"}', flush=True)
                server.serve_forever()
            return 0
        controller = Controller(config, args.config, socket_path=args.tmux_socket)
        if args.action == 'start' or args.action == 'restart': result = controller.start(restart=args.action == 'restart')
        elif args.action == 'stop':
            with controller.locked(): result = controller.stop_owned()
        elif args.action == 'attach':
            owner = controller.owned()
            if owner is None: raise ValueError('the report server is not running')
            os.execvp('tmux', [*controller.command, 'attach-session', '-t', owner['session_id']])
        else: result = controller.status()
        print(json.dumps(result) if args.json else f'{SESSION}: {result["state"]}\n{result.get("url") or "Hosting is unconfigured."}')
        return 0 if result['state'] != 'unhealthy' else 1
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({'error': str(error)[:1024]}) if args.json else 'Report server error: ' + str(error), file=sys.stderr)
        return 1
