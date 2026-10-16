import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from codex_plus.notification_launcher import (filtered_notifications, invocation, launch,
                                              preflight, QUALIFIED_VERSION)


class Launcher(unittest.TestCase):
    def test_dispatch_uses_option_arity_and_command_position(self):
        for argv in ([], ['--no-alt-screen'], ['-m', 'exec', 'Please review this'],
                     ['-c', 'model="review"', 'resume', 'some-session', 'exec'],
                     ['-c', 'model_reasoning_effort=low'],
                     ['resume', '--last'], ['resume', 'session', '--all'],
                     ['--', 'review'], ['say hello', 'review']):
            with self.subTest(argv=argv):
                self.assertTrue(invocation(argv).interactive)
        for argv in (['exec', 'hello'], ['--model', 'x', 'review'], ['agents'], ['fork'],
                     ['--no-daemon'], ['resume', 'session', '--no-daemon'], ['--help'],
                     ['resume', '--help'], ['-m'], ['--profile', 'other'], ['--remote=unix:///x'],
                     ['-c', 'tui.notifications=false'], ['-c', 'tui."notifications"=false'],
                     ['--config=tui={notifications=true}']):
            with self.subTest(argv=argv):
                self.assertFalse(invocation(argv).interactive)

    def test_preserve_native_events_except_completion(self):
        self.assertEqual(filtered_notifications(['approval-requested', 'async-question', 'agent-turn-complete']),
                         ['approval-requested', 'async-question'])
        self.assertEqual(filtered_notifications(True), ['approval-requested', 'plan-mode-prompt', 'async-question'])
        for value in (False, [], ['approval-requested'], 'true'):
            with self.assertRaises(ValueError): filtered_notifications(value)

    def test_remote_new_sessions_use_local_cwd_without_overriding_resume(self):
        cwd = '/workspace/caller with spaces'
        for arguments in ([], ['hello'], ['--', 'resume'], ['-m', 'resume', 'hello']):
            with self.subTest(arguments=arguments):
                parsed = invocation(arguments, cwd=cwd)
                self.assertEqual(parsed.cwd, cwd)
                self.assertEqual(parsed.remote_arguments, ('--cd', cwd, *arguments))
        for arguments in (['resume'], ['resume', 'saved-session'], ['resume', '--last'],
                          ['resume', 'saved-session', '--all']):
            with self.subTest(arguments=arguments):
                self.assertEqual(invocation(arguments, cwd=cwd).remote_arguments, tuple(arguments))

    def test_remote_explicit_cwd_is_absolute_and_other_arguments_are_preserved(self):
        caller = '/workspace/caller'
        target = '/workspace/project with spaces'
        for arguments, expected in (
            (['-C', '../project with spaces', 'hello'], ['-C', target, 'hello']),
            (['--cd', target, 'hello'], ['--cd', target, 'hello']),
            (['-C../project with spaces', 'hello'], ['-C' + target, 'hello']),
            (['-C=../project with spaces', 'hello'], ['-C=' + target, 'hello']),
            (['--cd=../project with spaces', 'hello'], ['--cd=' + target, 'hello']),
            (['resume', 'saved', '-C', '../project with spaces'], ['resume', 'saved', '-C', target]),
        ):
            with self.subTest(arguments=arguments):
                parsed = invocation(arguments, cwd=caller)
                self.assertEqual(parsed.cwd, target)
                self.assertEqual(parsed.remote_arguments, tuple(expected))
        self.assertFalse(invocation(['-C', '--version'], cwd=caller).interactive)

    def preflight(self, config, changed=False, versions=None, **options):
        owner = {'executable': '/usr/bin/codex', 'pid': 1}
        calls = []
        class Client:
            identity = owner
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def call(self, method, params, **kwargs):
                calls.append((method, params))
                return {'config': config}
        identity = iter([owner, {} if changed else owner])
        versions = iter(versions or [QUALIFIED_VERSION, QUALIFIED_VERSION])
        with patch('codex_plus.notification_launcher.Path.resolve', return_value=Path('/usr/bin/codex')):
            result = preflight('/socket', ['-C', '/tmp'], '/usr/bin/codex', client_factory=Client,
                               identity=lambda _: next(identity), version=lambda *a, **k: next(versions),
                               **options)
        return result, calls

    def test_preflight_is_read_only_and_preserves_custom_native_filter(self):
        (owner, overrides), calls = self.preflight({'notify': [], 'tui': {'notifications': [
            'agent-turn-complete', 'async-question', 'approval-requested']}})
        self.assertEqual(calls, [('config/read', {'includeLayers': False, 'cwd': '/tmp'})])
        self.assertEqual(json.loads(overrides[1].split('=', 1)[1]), ['async-question', 'approval-requested'])
        (_, overrides), _ = self.preflight({'notify': None, 'tui': None})
        self.assertEqual(json.loads(overrides[1].split('=', 1)[1]),
                         ['approval-requested', 'plan-mode-prompt', 'async-question'])

    def test_preflight_rejects_hook_focus_and_owner_conflicts(self):
        for config in ({'notify': ['/a/hook']}, {'tui': {'notification_condition': 'always'}},
                       {'tui': {'notifications': False}}):
            with self.assertRaises(ValueError): self.preflight(config)
        with self.assertRaises(ValueError): self.preflight({'notify': []}, changed=True)

    def test_native_version_pairs_are_qualified_individually(self):
        for pair in [('0.162.1', '0.162.1'), ('0.162.1', '0.163.0'), ('0.163.0', '0.163.0')]:
            self.preflight({}, versions=['codex-cli '+version for version in pair])
        for pair in [('0.162.1', '0.164.0'), ('0.163.0', '0.162.1'), ('0.164.0', '0.164.0')]:
            with self.assertRaises(ValueError):
                self.preflight({}, versions=['codex-cli '+version for version in pair])

    def test_automatic_launch_preserves_embedded_and_server_feature_policy(self):
        for config in ({}, {'features': {}}, {'features': {'daemon_auto_start': False}}):
            with self.assertRaisesRegex(ValueError, 'embedded TUI'):
                self.preflight(config, require_native_daemon=True)
        self.preflight({'features': {'daemon_auto_start': True}}, require_native_daemon=True)
        # Explicit run chooses an existing endpoint independently of auto-start.
        self.preflight({'features': {'daemon_auto_start': False}})
        for argv in (['--disable', 'daemon_auto_start'], ['--enable=worktrees'],
                     ['-c', 'features."daemon_auto_start"=false'],
                     ['-c', 'features={worktrees=false}']):
            with self.subTest(argv=argv):
                self.assertFalse(invocation(argv).interactive)
        self.assertTrue(invocation(['--disable', 'hooks']).interactive)

    def test_noninteractive_and_unsupported_argv_are_exact_native_exec(self):
        class NativeExec(Exception): pass
        for argv in (['exec', '--json', 'text with spaces'], ['resume', 'id', '--no-daemon'],
                     ['--disable', 'daemon_auto_start', 'literal prompt'],
                     ['-c', 'features.\"worktrees\"=false', 'literal prompt'],
                     ['--add-dir', '/tmp/with spaces', 'literal prompt'],
                     ['-c', 'sandbox_workspace_write={writable_roots=["/tmp"]}', 'literal prompt']):
            with patch('os.execv', side_effect=NativeExec) as execute:
                with self.assertRaises(NativeExec): launch('/unused', argv)
                execute.assert_called_once_with('/usr/bin/codex', ['/usr/bin/codex', *argv])
        with patch('os.isatty', return_value=False), patch('os.execv', side_effect=NativeExec) as execute:
            with self.assertRaises(NativeExec): launch('/unused', ['interactive text'])
            execute.assert_called_once_with('/usr/bin/codex', ['/usr/bin/codex', 'interactive text'])

    def test_prelaunch_failure_keeps_native_arguments(self):
        class NativeExec(Exception): pass
        with patch('os.isatty', return_value=True), patch('os.execv', side_effect=NativeExec) as execute, \
                patch('codex_plus.notification_run.prepare', side_effect=ValueError('unavailable')):
            with self.assertRaises(NativeExec): launch('/unused', ['hello'])
            execute.assert_called_once_with('/usr/bin/codex', ['/usr/bin/codex', 'hello'])

    @unittest.skipUnless(Path('/usr/bin/codex').is_file(), 'native CLI qualification is host-specific')
    def test_installed_cli_shape_preserves_native_version_stdout(self):
        helper = Path(__file__).resolve().parents[1] / 'scripts/codex-notify'
        actual = subprocess.run([sys.executable, '-B', str(helper), 'launch', '--', '--version'],
                                capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), timeout=5)
        native = subprocess.run(['/usr/bin/codex', '--version'], capture_output=True, timeout=5)
        self.assertEqual((actual.returncode, actual.stdout, actual.stderr),
                         (native.returncode, native.stdout, native.stderr))

    def test_native_signal_exit_is_preserved_in_owned_subprocess(self):
        for sig in (9, 15):
            process = subprocess.run([sys.executable, '-B', '-c',
                'from codex_plus.notification_launcher import native_exit; native_exit(-' + str(sig) + ')'],
                capture_output=True, timeout=5)
            self.assertEqual(process.returncode, -sig)


if __name__ == '__main__': unittest.main()
