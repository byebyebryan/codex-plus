"""Read-only selection of one Codex environment; never starts owners or moves data."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib


def absolute(value):
    path = Path(value).expanduser()
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('an absolute path without parent traversal is required')
    return path


def override(explicit, variable, default):
    if explicit is not None:
        return absolute(explicit)
    value = os.environ.get(variable)
    return absolute(value) if value else default


@dataclass(frozen=True)
class Context:
    home: Path
    key: str
    legacy: bool
    state_base: Path
    config_base: Path
    data_base: Path

    @property
    def socket(self):
        return self.home / 'app-server-control/app-server-control.sock'

    def state_root(self, explicit=None):
        default = self.state_base / 'codex-plus'
        if not self.legacy:
            default = default / 'environments' / self.key
        return override(explicit, 'CODEX_PLUS_STATE_ROOT', default)

    def report_config(self, explicit=None):
        default = self.config_base / 'codex-plus'
        if not self.legacy:
            default = default / 'environments' / self.key
        return override(explicit, 'CODEX_PLUS_REPORT_CONFIG', default / 'report.toml')

    def report_data(self):
        root = self.data_base / 'codex-plus'
        return root / 'reports' if self.legacy else root / 'environments' / self.key / 'reports'


def resolve():
    default = (Path.home() / '.codex').resolve()
    home = absolute(os.environ.get('CODEX_HOME') or default).resolve()
    return Context(home, hashlib.sha256(str(home).encode()).hexdigest()[:24], home == default,
                   absolute(os.environ.get('XDG_STATE_HOME') or Path.home() / '.local/state'),
                   absolute(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config'),
                   absolute(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share'))


def socket_path(explicit=None):
    value = explicit or os.environ.get('CODEX_PLUS_SOCKET')
    return absolute(value.removeprefix('unix://')) if value else resolve().socket


def existing_socket(explicit=None, *, run=None):
    if explicit or os.environ.get('CODEX_PLUS_SOCKET'):
        return str(socket_path(explicit))
    # Native discovery selects CODEX_HOME. It is a status-only query, never a start.
    run = run or subprocess.run
    context = resolve()
    environment = {**os.environ, 'CODEX_HOME': str(context.home)}
    status = json.loads(run(['rtk', 'proxy', 'codex', 'app-server', 'daemon', 'version'],
                            capture_output=True, text=True, check=True, timeout=10, env=environment).stdout)
    if status.get('status') != 'running':
        raise ValueError('existing native daemon is unavailable; none was started')
    value = status.get('socketPath')
    if not isinstance(value, str) or not value:
        raise ValueError('existing native Unix endpoint is unavailable')
    return str(absolute(value.removeprefix('unix://')))


def report_session(path):
    context = resolve()
    path = absolute(path).resolve()
    legacy = (context.config_base / 'codex-plus/report.toml').resolve()
    key = hashlib.sha256(str(path).encode()).hexdigest()[:24]
    return 'codex-report-server' if path == legacy else 'codex-report-server-' + key


def describe(*, state_root=None, report_config=None, socket=None):
    context = resolve()
    result = {'schema': 1, 'codex_home': str(context.home), 'environment_key': context.key,
            'legacy_defaults': context.legacy, 'socket': str(socket_path(socket)),
            'socket_override': bool(socket or os.environ.get('CODEX_PLUS_SOCKET')),
            'state_root': str(context.state_root(state_root)),
            'report_config': str(context.report_config(report_config)),
            'default_report_data_root': str(context.report_data()),
            'report_server_session': report_session(context.report_config(report_config)),
            'daemon_checked': False}
    selected = context.report_config(report_config)
    values = {}
    if selected.exists() or selected.is_symlink():
        if selected.is_symlink() or not selected.is_file() or selected.stat().st_size > 65536:
            raise ValueError('report config must be a bounded regular file')
        values = tomllib.loads(selected.read_text())
    result['report_config_exists'] = selected.is_file()
    result['report_data_root'] = str(absolute(values.get('data_root') or context.report_data()))
    result['report_base_url'] = values.get('base_url')
    result['report_server_autostart'] = values.get('server_autostart', False)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', type=Path)
    parser.add_argument('--report-config', type=Path)
    parser.add_argument('--socket')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(describe(state_root=args.state_root, report_config=args.report_config,
                                  socket=args.socket), indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}))
        return 1
