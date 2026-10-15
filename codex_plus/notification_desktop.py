"""Finite desktop delivery and optional exact-thread resume actions."""

from __future__ import annotations

from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import threading
import time

from .notification_delivery import (check_reply, command, encode_event, load_config,
                                    read_line, stop, validate_event, write_input)
from .notification_protocol import encode, event_id, label

REPLAY_SECONDS = 86400
MAX_EPISODES = 256


def reap_later(process):
    # A returning command does not keep a popup/action process as an unreaped child.
    # When this short-lived receiver exits, the OS adopts any still-running child.
    threading.Thread(target=process.wait, daemon=True).start()


def settings(config):
    value = config.get('desktop')
    if (not isinstance(value, dict) or value.get('condition') != 'always'
            or set(value) - {'condition', 'notify_command', 'bus_address', 'state_dir', 'open'}):
        raise ValueError('desktop delivery requires explicit condition="always"; originating-terminal focus is unavailable')
    command(value.get('notify_command', ['/usr/bin/notify-send']))
    if 'bus_address' in value and (not isinstance(value['bus_address'], str)
                                  or not value['bus_address'] or len(value['bus_address']) > 2048):
        raise ValueError('invalid desktop bus address')
    if 'state_dir' in value and (not isinstance(value['state_dir'], str)
                                or not Path(value['state_dir']).is_absolute()):
        raise ValueError('desktop state directory must be absolute')
    routes = value.get('open', [])
    if not isinstance(routes, list) or len(routes) > 16:
        raise ValueError('invalid desktop Open routes')
    seen = set()
    for route in routes:
        if not isinstance(route, dict) or set(route) != {'host', 'instance', 'command'}:
            raise ValueError('invalid desktop Open route')
        key = label(route['host'], 63), label(route['instance'], 128)
        if key in seen:
            raise ValueError('duplicate desktop Open route')
        seen.add(key)
        argv = command(route['command'], placeholders=True)
        if argv.count('{thread}') != 1:
            raise ValueError('desktop Open requires exactly one {thread} argument')
    return value


def open_command(event, config):
    source = event['metadata']
    for route in config.get('open', []):
        if (route['host'], route['instance']) == (source['host'], source['instance']):
            return [source['thread'] if arg == '{thread}' else arg for arg in route['command']]
    return None


def state_database(config):
    path = Path(config.get('state_dir', f'/run/user/{os.getuid()}/codex-notify'))
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('desktop notification state must be a private owned directory')
    path /= 'episodes.sqlite'
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077 or info.st_nlink != 1):
            raise ValueError('invalid desktop notification state file')
    finally:
        os.close(fd)
    database = sqlite3.connect(path, timeout=2)
    database.execute('CREATE TABLE IF NOT EXISTS episodes (event TEXT PRIMARY KEY, at REAL, desktop_id INTEGER)')
    return database


def claim(event, config):
    """Reserve before publishing: a crash can miss an alert, never imply admission."""
    identifier = event_id(event['metadata'])
    with closing(state_database(config)) as database, database:
        database.execute('BEGIN IMMEDIATE')
        database.execute('DELETE FROM episodes WHERE at < ?', (time.time() - REPLAY_SECONDS,))
        row = database.execute('SELECT desktop_id FROM episodes WHERE event = ?', (identifier,)).fetchone()
        if row is not None:
            return reply(event, 'duplicate' if row[0] else 'uncertain', row[0])
        # Replay protection is bounded. Eviction makes a very old episode eligible again.
        database.execute('DELETE FROM episodes WHERE event IN (SELECT event FROM episodes ORDER BY at DESC LIMIT -1 OFFSET ?)',
                         (MAX_EPISODES - 1,))
        database.execute('INSERT INTO episodes VALUES (?, ?, 0)', (identifier, time.time()))
    return None


def admitted(event, config, desktop_id):
    with closing(state_database(config)) as database, database:
        database.execute('UPDATE episodes SET desktop_id = ? WHERE event = ?',
                         (desktop_id, event_id(event['metadata'])))


def reply(event, status, desktop_id):
    return {'v': 1, 'event': event_id(event['metadata']), 'status': status, 'desktop_id': desktop_id}


def notify_argv(event, config):
    argv = [*config.get('notify_command', ['/usr/bin/notify-send']), '--app-name=Codex',
            '--icon=utilities-terminal', '--expire-time=30000',
            '--hint=string:category:' + encode(event['metadata']), '--print-id']
    if open_command(event, config) is not None:
        argv.append('--action=default=Open')
    # Match Kitty's markup guards, already decoded by v1 rich-card consumers.
    # The desktop renders literal assistant HTML, never executable/link markup.
    body = event['body'].replace('<', '<\u200c').replace('&', '&\u200c')
    return [*argv, '--', 'Codex @ ' + event['metadata']['host'], body]


def worker(event, config, *, emit):
    validate_event(event)
    config = settings(config)
    previous = claim(event, config)
    if previous is not None:
        emit(previous)
        return
    environment = os.environ.copy()
    environment['DBUS_SESSION_BUS_ADDRESS'] = config.get('bus_address', f'unix:path=/run/user/{os.getuid()}/bus')
    process = subprocess.Popen(notify_argv(event, config), stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               env=environment)
    acknowledged = False
    try:
        raw = read_line(process.stdout, time.monotonic() + 4, limit=32)
        if not raw.isdigit() or not 1 <= int(raw) <= 0xffffffff:
            raise ValueError('invalid desktop admission ID')
        desktop_id = int(raw)
        admitted(event, config, desktop_id)
        emit(reply(event, 'delivered', desktop_id))
        acknowledged = True
        argv = open_command(event, config)
        if argv is not None:
            # A finite per-popup waiter; no fleet subscription or resident agent daemon.
            action = read_line(process.stdout, time.monotonic() + 35, limit=32)
            if action == b'default':
                opened = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                          stderr=subprocess.DEVNULL, env=environment, start_new_session=True)
                reap_later(opened)
    except (OSError, ValueError, TimeoutError):
        if not acknowledged:
            emit(reply(event, 'uncertain', 0))
    finally:
        stop(process, group=False)
        process.stdout.close()


def receive(event, config_path, helper, *, timeout=6):
    validate_event(event)
    settings(load_config(config_path))
    process = subprocess.Popen([sys.executable, '-B', str(helper), 'desktop-worker', '--config', str(config_path)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                               start_new_session=True)
    accepted = False
    try:
        deadline = time.monotonic() + timeout
        write_input(process, encode_event(event), deadline)
        value = check_reply(json.loads(read_line(process.stdout, deadline)), event)
        # The worker can remain only to await the admitted popup's action.
        accepted = value['status'] == 'delivered'
        if accepted:
            reap_later(process)
        return value
    finally:
        if not accepted:
            stop(process)
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()
