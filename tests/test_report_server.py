"""Actual HTTP and isolated tmux lifecycle acceptance checks."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler, Request

from codex_plus.reports.config import Config
from codex_plus.reports import hosting, server
from codex_plus.reports.store import Store


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='report-server-'); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0)); self.port = reservation.getsockname()[1]
        self.options = Config(self.root / 'data', f'http://fixture.invalid:{self.port}/reports/', server_bind='127.0.0.1')
        self.config = self.root / 'report.toml'
        self.config.write_text(f'schema = 1\ndata_root = {json.dumps(str(self.options.data_root))}\n'
                               f'base_url = {json.dumps(self.options.base_url)}\nserver_bind = "127.0.0.1"\n')
        self.opener = build_opener(ProxyHandler({}))
        self.store = Store(self.options)

    def web(self):
        web = server.make_server(self.options)
        Thread(target=web.serve_forever, daemon=True).start()
        self.addCleanup(web.server_close); self.addCleanup(web.shutdown)
        return f'http://127.0.0.1:{self.port}'

    def publish(self):
        source = self.root / 'export'; source.mkdir()
        (source / 'index.html').write_text('<h1>Static report</h1><script src="assets/app.js"></script>')
        (source / 'assets').mkdir(); (source / 'assets/app.js').write_text('document.title="Loaded";')
        (source / 'résumé.html').write_text('<h1>Unicode</h1>')
        (source / 'nested').mkdir(); (source / 'nested/index.html').write_text('<h1>Nested</h1>')
        return self.store.publish(source, 'Static report')

    def test_http_serves_assets_head_unicode_and_correct_nested_index_redirect(self):
        report = self.publish(); url = self.web() + '/reports/' + report['report_id']
        for suffix, text in [('/', b'Static report'), ('/assets/app.js', b'Loaded'),
                             ('/r%C3%A9sum%C3%A9.html', b'Unicode'), ('/nested/index.html', b'Nested'), ('/nested/', b'Nested')]:
            with self.opener.open(url + suffix, timeout=3) as response:
                self.assertEqual(response.status, 200); self.assertIn(text, response.read())
                if 'nested' in suffix: self.assertIn('/nested/', response.geturl())
        with self.opener.open(Request(url + '/', method='HEAD'), timeout=3) as response:
            self.assertEqual(response.status, 200); self.assertEqual(response.read(), b'')
        with self.opener.open(f'http://127.0.0.1:{self.port}/reports/_server-health', timeout=3) as response:
            value = json.load(response)
            self.assertEqual(value['component'], 'code-report-server'); self.assertNotIn('data_root', value)

    def test_http_refuses_private_paths_traversal_listing_and_symlinks(self):
        report = self.publish(); url = self.web()
        private = self.root / 'private.txt'; private.write_text('private sentinel')
        (Path(report['snapshot_path']) / 'link.txt').symlink_to(private)
        for path in ['/', '/metadata/store.json', '/reports/../metadata/store.json', '/reports/%2e%2e/private.txt',
                     f'/reports/{report["report_id"]}/assets/', f'/reports/{report["report_id"]}/link.txt',
                     '/reports/%FF', '/reports/.write-partial']:
            with self.assertRaises(HTTPError) as failure:
                self.opener.open(url + path, timeout=3)
            self.assertEqual(failure.exception.code, 404, path)
            failure.exception.close()

    def test_hosting_check_is_generic_http_without_tailscale_or_tmux(self):
        self.publish(); self.web()
        resolve = socket.getaddrinfo
        def lookup(host, *args, **kwargs):
            return resolve('127.0.0.1' if host == 'fixture.invalid' else host, *args, **kwargs)
        with patch('socket.getaddrinfo', side_effect=lookup), patch('subprocess.run', side_effect=AssertionError('no external command')):
            self.assertEqual(hosting.inspect_hosting(self.options)['state'], 'verified')
        self.assertEqual(server.health(self.options)['fingerprint'], server.fingerprint(self.options))

    def test_foreground_http_rejects_https_and_unowned_store(self):
        with self.assertRaises(ValueError): server.make_server(Config(self.root / 'https', 'https://fixture.invalid/reports/'))
        self.options.data_root.mkdir(); (self.options.data_root / 'other.txt').write_text('untouched')
        with self.assertRaises(ValueError): server.make_server(self.options)
        self.assertEqual((self.options.data_root / 'other.txt').read_text(), 'untouched')

    @unittest.skipUnless(shutil.which('tmux'), 'tmux control is optional')
    def test_tmux_survives_launcher_exit_reuses_session_and_preserves_other_sessions(self):
        controller = server.Controller(self.options, self.config, socket_path=self.root / 'tmux.sock')
        self.addCleanup(lambda: controller.tmux('kill-session', '-t', '=unrelated-test', optional=True))
        self.addCleanup(lambda: controller.tmux('kill-session', '-t', '=code-report-server', optional=True))
        controller.tmux('new-session', '-d', '-s', 'unrelated-test', 'sleep', '60')
        command = [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'scripts/code-report-server'),
                   '--config', str(self.config), '--tmux-socket', str(self.root / 'tmux.sock'), '--json', 'start']
        def start():
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        with ThreadPoolExecutor(max_workers=3) as pool:
            receipts = list(pool.map(lambda _: start(), range(3)))
        self.assertEqual(len({x['session_id'] for x in receipts}), 1)
        self.assertEqual(sum(not x['reused'] for x in receipts), 1)
        self.assertEqual(controller.status()['state'], 'running')
        report = self.publish()
        with self.opener.open(f'http://127.0.0.1:{self.port}/reports/{report["report_id"]}/', timeout=3) as response:
            self.assertEqual(response.status, 200)
        original = controller.status()['session_id']
        self.assertNotEqual(controller.start(restart=True)['session_id'], original)
        with controller.locked(): controller.stop_owned()
        self.assertEqual(controller.status()['state'], 'stopped')
        self.assertTrue(controller.tmux('display-message', '-p', '-t', '=unrelated-test:', '#{session_id}').startswith('$'))
        self.assertTrue(Path(report['snapshot_path']).is_dir())

    @unittest.skipUnless(shutil.which('tmux'), 'tmux control is optional')
    def test_tmux_refuses_foreign_named_session_and_additional_user_panes(self):
        controller = server.Controller(self.options, self.config, socket_path=self.root / 'tmux.sock')
        self.addCleanup(lambda: controller.tmux('kill-session', '-t', '=code-report-server', optional=True))
        sid = controller.tmux('new-session', '-d', '-P', '-F', '#{session_id}', '-s', 'code-report-server', 'sleep', '60')
        with self.assertRaises(ValueError): controller.start()
        with self.assertRaises(ValueError): controller.stop_owned()
        self.assertEqual(controller.tmux('display-message', '-p', '-t', '=code-report-server:', '#{session_id}'), sid)
        controller.tmux('kill-session', '-t', sid)
        receipt = controller.start()
        controller.tmux('split-window', '-d', '-t', receipt['session_id'], 'sleep', '60')
        with self.assertRaises(ValueError): controller.stop_owned()
        self.assertEqual(len(controller.tmux('list-panes', '-t', receipt['session_id'], '-F', '#{pane_id}').splitlines()), 2)


if __name__ == '__main__': unittest.main()
