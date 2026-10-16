"""Environment separation across CLI/MCP, daemon discovery and real private tmux."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from codex_plus import context
from codex_plus.model_server import default_state_root, existing_socket
from codex_plus.reports import cli, config, mcp, server


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='codex-environments-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home'
        self.home.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith(('CODEX_', 'XDG_'))}
        env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.root / 'config'),
                   XDG_DATA_HOME=str(self.root / 'data'), XDG_STATE_HOME=str(self.root / 'state'))
        self.environ = patch.dict(os.environ, env, clear=True)
        self.environ.start(); self.addCleanup(self.environ.stop)

    def select(self, suffix):
        os.environ['CODEX_HOME'] = str(self.home / suffix)
        return context.resolve()

    def test_legacy_defaults_and_canonical_home_identity_are_readonly(self):
        legacy = context.resolve()
        self.assertTrue(legacy.legacy)
        self.assertEqual(legacy.state_root(), self.root / 'state/codex-plus')
        self.assertEqual(config.config_path(), self.root / 'config/codex-plus/report.toml')
        self.assertEqual(config.load().data_root, self.root / 'data/codex-plus/reports')
        self.assertEqual(context.report_session(config.config_path()), server.SESSION)
        other = self.select('other')
        self.assertNotEqual(other.state_root(), legacy.state_root())
        self.assertNotEqual(other.report_config(), legacy.report_config())
        self.assertNotEqual(other.report_data(), legacy.report_data())
        self.assertFalse(other.state_root().exists())
        self.assertFalse(other.report_config().exists())
        self.assertFalse(other.report_data().exists())
        other.home.mkdir()
        alias = self.home / 'alias'; alias.symlink_to(other.home)
        os.environ['CODEX_HOME'] = str(alias)
        self.assertEqual(context.resolve(), other)
        self.assertEqual(context.socket_path(), other.socket)

    def test_explicit_overrides_win_and_diagnostics_report_effective_storage(self):
        ctx = self.select('other')
        chosen = self.root / 'private.toml'
        chosen.write_text('schema=1\ndata_root=' + json.dumps(str(self.root / 'preserved-store')) + '\n')
        os.environ.update(CODEX_PLUS_REPORT_CONFIG=str(chosen),
                          CODEX_PLUS_STATE_ROOT=str(self.root / 'preserved-state'),
                          CODEX_PLUS_SOCKET='unix://' + str(self.root / 'selected.sock'))
        self.assertEqual(default_state_root(), self.root / 'preserved-state')
        self.assertEqual(config.config_path(), chosen)
        self.assertEqual(config.load().data_root, self.root / 'preserved-store')
        self.assertEqual(existing_socket(), str(self.root / 'selected.sock'))
        self.assertEqual(str(context.socket_path()), existing_socket())
        explicit = self.root / 'explicit.toml'
        self.assertEqual(ctx.report_config(explicit), explicit)
        self.assertEqual(ctx.state_root(self.root / 'explicit-state'), self.root / 'explicit-state')
        self.assertEqual(existing_socket(str(self.root / 'explicit.sock')), str(self.root / 'explicit.sock'))
        info = context.describe()
        self.assertEqual(info['report_data_root'], str(self.root / 'preserved-store'))
        self.assertFalse(info['daemon_checked'])
        for key in ('CODEX_HOME', 'CODEX_PLUS_REPORT_CONFIG', 'CODEX_PLUS_STATE_ROOT', 'CODEX_PLUS_SOCKET'):
            with patch.dict(os.environ, {key: 'relative/path'}):
                with self.assertRaises(ValueError): context.describe()

    def test_install_snippets_can_pin_home_without_host_specific_profile_names(self):
        from codex_plus import package as runtime_package
        from codex_plus.reports import package as report_package
        home = self.home / 'other'
        runtime = runtime_package.mcp_config(self.root / 'runtime', enabled=False, codex_home=home)
        report = report_package.mcp_config(self.root / 'reports', enabled=False, codex_home=home)
        self.assertEqual(runtime['env'], {'CODEX_HOME': str(home), 'CODEX_PLUS_SOCKET': '', 'CODEX_PLUS_STATE_ROOT': ''})
        self.assertEqual(report['env'], {'CODEX_HOME': str(home), 'CODEX_PLUS_REPORT_CONFIG': ''})
        for module in (runtime_package, report_package):
            with self.assertRaises(ValueError): module.mcp_config(self.root / 'missing', enabled=False, codex_home='relative')

    def test_missing_explicit_report_config_refuses_shared_store_fallback(self):
        self.select('.codex')
        with patch.dict(os.environ, {'CODEX_PLUS_REPORT_CONFIG': str(self.root / 'missing.toml')}):
            with self.assertRaises(ValueError): config.load()
        with self.assertRaises(ValueError): config.load(self.root / 'missing.toml')
        self.assertFalse(context.resolve().report_data().exists())

    def test_missing_daemon_never_discovers_the_other_home_or_starts_one(self):
        selected = self.select('other')
        calls = []
        def status(argv, **kwargs):
            calls.append((argv, os.environ['CODEX_HOME']))
            return subprocess.CompletedProcess(argv, 0, json.dumps({'status': 'stopped'}))
        with self.assertRaises(ValueError): context.existing_socket(run=status)
        self.assertEqual(calls, [(['rtk', 'proxy', 'codex', 'app-server', 'daemon', 'version'], str(selected.home))])

    def test_same_thread_id_in_two_native_homes_has_independent_monitoring_state(self):
        from test_model import Backend, A, TURN_A
        from codex_plus.model import ModelAPI
        paths = []
        for index, suffix in enumerate(('.codex', 'other')):
            ctx = self.select(suffix)
            backend = Backend()
            backend.identity = {**backend.identity, 'requested_socket': str(ctx.socket), 'pid': 1000 + index}
            backend.bind = lambda thread, timeout=None, b=backend: {**b.identity, 'thread_id': thread}
            with patch('codex_plus.peers.listener_identity', return_value=backend.identity):
                with ModelAPI(default_state_root(), str(ctx.socket), {'thread_id': A, 'turn_id': TURN_A},
                              client_factory=lambda *a, b=backend, **kw: b) as api:
                    paths.append(api.state)
                    self.assertEqual(api.frozen['requested_socket'], str(ctx.socket))
                    self.assertEqual(api.store.jobs(), [])
        self.assertNotEqual(paths[0], paths[1])
        self.assertTrue(all((p / 'binding.json').is_file() for p in paths))
        self.assertNotEqual((paths[0] / 'binding.json').read_text(), (paths[1] / 'binding.json').read_text())

    def test_cli_and_mcp_defaults_publish_to_the_same_separate_stores(self):
        ids = {}
        for suffix in ('.codex', 'other'):
            ctx = self.select(suffix)
            source = self.root / (suffix + '.html')
            source.write_text('<h1>' + suffix + '</h1>')
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(cli.main(['--json', 'publish', '--source', str(source), '--title', suffix]), 0)
            ids[suffix] = json.loads(out.getvalue())['report_id']
            response = mcp.Server().handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                        'params': {'name': 'report_list', 'arguments': {}}})['result']
            self.assertFalse(response['isError'])
            self.assertEqual([r['report_id'] for r in response['structuredContent']['reports']], [ids[suffix]])
            self.assertTrue(ctx.report_data().is_dir())
        self.assertNotEqual(ids['.codex'], ids['other'])
        self.select('.codex')
        response = mcp.Server().handle({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                    'params': {'name': 'report_get', 'arguments': {'report_id': ids['other']}}})['result']
        self.assertTrue(response['isError'])

    def test_cli_and_mcp_subprocesses_inherit_the_same_report_override(self):
        self.select('other')
        chosen = self.root / 'private.toml'
        chosen.write_text('schema=1\ndata_root=' + json.dumps(str(self.root / 'explicit-store')) + '\n')
        os.environ['CODEX_PLUS_REPORT_CONFIG'] = str(chosen)
        root = Path(__file__).resolve().parents[1]
        output = subprocess.check_output([sys.executable, '-B', root / 'scripts/codex-plus-report', '--json', 'doctor'], text=True)
        self.assertEqual(json.loads(output)['data_root'], str(self.root / 'explicit-store'))
        info = json.loads(subprocess.check_output([sys.executable, '-B', root / 'scripts/codex-plus-context'], text=True))
        self.assertEqual(info['report_data_root'], str(self.root / 'explicit-store'))
        self.assertFalse((self.root / 'explicit-store').exists())
        self.assertFalse(context.resolve().report_data().exists())

    @unittest.skipUnless(shutil.which('tmux'), 'tmux control is optional')
    def test_two_live_servers_restart_and_stop_independently_on_one_private_socket(self):
        controllers = []
        for suffix in ('.codex', 'other'):
            ctx = self.select(suffix)
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
            path = ctx.report_config(); path.parent.mkdir(parents=True)
            path.write_text('schema=1\ndata_root=' + json.dumps(str(ctx.report_data())) +
                            '\nbase_url="http://fixture.invalid:' + str(port) + '/reports/"\nserver_bind="127.0.0.1"\n')
            controller = server.Controller(config.load(), path, socket_path=self.root / 'tmux.sock')
            controllers.append(controller)
            self.addCleanup(lambda c=controller: c.tmux('kill-session', '-t', '=' + c.session, optional=True))
            self.assertEqual(controller.start()['state'], 'running')
        first, second = controllers
        self.assertNotEqual(first.session, second.session)
        second_pid = second.status()['pid']
        self.assertEqual(first.start(restart=True)['state'], 'running')
        self.assertEqual(second.status()['pid'], second_pid)
        with first.locked(): first.stop_owned()
        self.assertEqual(first.status()['state'], 'stopped')
        self.assertEqual(second.status()['state'], 'running')
        self.assertEqual(second.status()['pid'], second_pid)

    @unittest.skipUnless(shutil.which('tmux'), 'tmux control is optional')
    def test_existing_matching_legacy_report_server_is_adopted_without_restart(self):
        ctx = self.select('other')
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
        path = ctx.report_config(); path.parent.mkdir(parents=True)
        path.write_text('schema=1\ndata_root=' + json.dumps(str(ctx.report_data())) +
                        '\nbase_url="http://fixture.invalid:' + str(port) + '/reports/"\nserver_bind="127.0.0.1"\n')
        old = server.Controller(config.load(), path, socket_path=self.root / 'tmux.sock')
        old.session = server.SESSION  # Emulate the old release's fixed session name.
        self.addCleanup(lambda: old.tmux('kill-session', '-t', '=' + server.SESSION, optional=True))
        receipt = old.start()
        new = server.Controller(config.load(), path, socket_path=self.root / 'tmux.sock')
        adopted = new.start()
        self.assertTrue(adopted['reused'])
        self.assertEqual(adopted['pid'], receipt['pid'])
        self.assertEqual(adopted['session'], server.SESSION)


if __name__ == '__main__':
    unittest.main()
