"""Conservative native CLI dispatch and existing-server notification preflight."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import tomllib

from .native import Client, listener_identity

QUALIFIED_VERSION = 'codex-cli 0.162.1'
QUALIFIED_PAIRS = {(QUALIFIED_VERSION, QUALIFIED_VERSION),
                   (QUALIFIED_VERSION, 'codex-cli 0.163.0'),
                   ('codex-cli 0.163.0', 'codex-cli 0.163.0')}
NATIVE_EVENTS = ('agent-turn-complete', 'approval-requested', 'plan-mode-prompt', 'async-question')
SERVER_FEATURES = {'daemon_auto_start', 'worktrees', 'transcript_v2',
                   'realtime_conversation', 'standalone_web_search'}
VALUE_OPTIONS = {'-c', '--config', '-m', '--model', '-s', '--sandbox', '-C', '--cd',
                 '--add-dir', '-a', '--ask-for-approval', '--enable', '--disable',
                 '--local-provider'}
FLAG_OPTIONS = {'--strict-config', '--approve-for-me', '--dangerously-bypass-approvals-and-sandbox',
                '--dangerously-bypass-hook-trust', '--search', '--no-alt-screen', '--oss'}
NATIVE_COMMANDS = {'agents', 'exec', 'e', 'review', 'login', 'logout', 'mcp', 'plugin', 'app-server',
                   'remote-control', 'completion', 'update', 'doctor', 'sandbox', 'debug', 'apply',
                   'a', 'resume', 'queue', 'archive', 'delete', 'migrate-rollouts', 'unarchive',
                   'fork', 'cloud', 'exec-server', 'features', 'help'}


@dataclass(frozen=True)
class Invocation:
    interactive: bool
    cwd: str
    reason: str = ''


def invocation(arguments, cwd=None):
    """Only recognize qualified syntax; unknown native syntax stays native."""
    cwd = os.path.abspath(cwd or os.getcwd())
    index, command = 0, None
    while index < len(arguments):
        arg = arguments[index]
        if arg == '--':
            break  # Remaining arguments are positional text, never helper options.
        if arg in ('-h', '--help', '-V', '--version'):
            return Invocation(False, cwd, 'native help/version')
        if arg.startswith('-'):
            name, equals, value = arg.partition('=')
            if not equals and len(arg) > 2 and arg[:2] in ('-c', '-m', '-s', '-C', '-a'):
                name, value, equals = arg[:2], arg[2:], '='
            if name in VALUE_OPTIONS:
                if not equals:
                    index += 1
                    if index == len(arguments):
                        return Invocation(False, cwd, 'native option validation')
                    value = arguments[index]
                if name == '--add-dir':
                    return Invocation(False, cwd, 'native additional workspace roots')
                if name in ('-C', '--cd'):
                    cwd = os.path.abspath(os.path.expanduser(value))
                elif name in ('--enable', '--disable') and value in SERVER_FEATURES:
                    return Invocation(False, cwd, 'explicit native daemon feature policy')
                elif name in ('-c', '--config'):
                    key, separator, _ = value.partition('=')
                    if not separator:
                        return Invocation(False, cwd, 'native option validation')
                    try:
                        override = tomllib.loads(key + '=true')
                    except tomllib.TOMLDecodeError:
                        return Invocation(False, cwd, 'native option validation')
                    # Parse quoted/dotted TOML keys too. Explicit publication
                    # settings remain the caller's native notification policy.
                    tui = override.get('tui', {})
                    if ('notify' in override or not isinstance(tui, dict)
                            or any(key.startswith('notification') for key in tui)):
                        return Invocation(False, cwd, 'explicit native notification policy')
                    features = override.get('features', {})
                    if not isinstance(features, dict) or SERVER_FEATURES.intersection(features):
                        return Invocation(False, cwd, 'explicit native daemon feature policy')
                    if 'sandbox_workspace_write' in override:
                        return Invocation(False, cwd, 'explicit native workspace policy')
                index += 1
                continue
            if name in FLAG_OPTIONS and not equals:
                index += 1
                continue
            if command == 'resume' and name in ('--last', '--all', '--include-non-interactive') and not equals:
                index += 1
                continue
            return Invocation(False, cwd, 'unqualified native option')
        if command is None:
            if arg in NATIVE_COMMANDS:
                command = arg
                if command != 'resume':
                    return Invocation(False, cwd, 'native command')
            else:
                command = 'default'
        # Later positionals are text, not a scan for subcommand words. Native
        # options are still recognized after a prompt/session ID, as Clap does.
        index += 1
    return Invocation(True, cwd)


def filtered_notifications(value):
    if value is True:
        return [event for event in NATIVE_EVENTS if event != 'agent-turn-complete']
    if value is False:
        raise ValueError('native notifications are disabled')
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError('unsupported native notification settings')
    if 'agent-turn-complete' not in value:
        raise ValueError('native completion notifications are disabled')
    return [event for event in value if event != 'agent-turn-complete']


def preflight(path, arguments, executable, *, client_factory=Client, identity=listener_identity,
              version=subprocess.check_output, require_native_daemon=False):
    parsed = invocation(arguments)
    if not parsed.interactive:
        raise ValueError(parsed.reason)
    executable = str(Path(executable).resolve(strict=True))
    tui_version = version([executable, '--version'], text=True, timeout=2).strip()
    if tui_version not in {pair[0] for pair in QUALIFIED_PAIRS}:
        raise ValueError('native TUI version is outside the qualified notification scope')
    owner = identity(path)
    daemon_version = version([owner['executable'], '--version'], text=True, timeout=2).strip()
    if (tui_version, daemon_version) not in QUALIFIED_PAIRS:
        raise ValueError('native TUI/daemon pair is outside the qualified notification scope')
    with client_factory(path, experimental=True, timeout=4) as client:
        response = client.call('config/read', {'includeLayers': False, 'cwd': parsed.cwd}, timeout=4)
        config = response.get('config')
        if not isinstance(config, dict) or config.get('notify') not in (None, []):
            raise ValueError('configured server hook conflicts with relay completion publication')
        features = config.get('features') or {}
        if require_native_daemon and (not isinstance(features, dict)
                                      or features.get('daemon_auto_start') is not True):
            raise ValueError('native configuration selects an embedded TUI')
        tui = config.get('tui')
        if tui is None:
            tui = {}
        if not isinstance(tui, dict) or tui.get('notification_condition') not in (None, 'unfocused'):
            raise ValueError('relay requires the native unfocused notification policy')
        notifications = tui.get('notifications')
        remaining = filtered_notifications(True if notifications is None else notifications)
        if identity(path) != client.identity or owner != client.identity:
            raise ValueError('native notification owner changed during preflight')
    return owner, ['-c', 'tui.notifications=' + json.dumps(remaining, separators=(',', ':'))]


def native_exit(code):
    """Retain native signal exit semantics after the relay has cleaned up."""
    if code < 0:
        import signal
        if -code not in (signal.SIGKILL, signal.SIGSTOP):
            signal.signal(-code, signal.SIG_DFL)
        os.kill(os.getpid(), -code)
    return code


def launch(path, arguments, executable='/usr/bin/codex'):
    """Automatic shell entry point: unsupported calls keep exact native behavior."""
    if not Path(executable).is_absolute():
        raise ValueError('native Codex executable must be absolute')
    if not invocation(arguments).interactive or not os.isatty(0) or not os.isatty(1):
        os.execv(executable, [executable, *arguments])
    import asyncio
    from .notification_run import prepare, run
    try:
        prepared = prepare(path, arguments, executable, automatic=True)
    except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.SubprocessError):
        os.execv(executable, [executable, *arguments])
    return native_exit(asyncio.run(run(path, arguments, executable, prepared=prepared)))
