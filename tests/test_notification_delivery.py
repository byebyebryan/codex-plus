"""Daemon-safe transport/admission tests; no real desktop or user threads."""

from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from codex_plus.notification_delivery import (command, eligible_thread, encode_event, envelope, forward,
                                             load_config, read_event, validate_event)
from codex_plus.notification_desktop import (MAX_EPISODES, claim, notify_argv, open_command,
                                            settings, state_database, worker)
from codex_plus.notification_protocol import decode, event_id, metadata

HELPER = Path(__file__).resolve().parents[1] / 'scripts/codex-notify'
THREAD = '11111111-1111-4111-8111-111111111111'
TURN = '22222222-2222-4222-8222-222222222222'


class Delivery(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.event = {'v': 1, 'metadata': metadata('source', 'instance', THREAD, TURN),
                      'title': 'Codex', 'body': '**Ready** <literal> &amp;\n東京'}
        self.desktop = {'condition': 'always', 'state_dir': str(self.root / 'state')}
        self.notifier = self.root / 'notifier.py'
        self.record = self.root / 'notifier.json'
        self.notifier.write_text('''import json, os, sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({"argv": sys.argv[2:], "bus": os.environ.get("DBUS_SESSION_BUS_ADDRESS"), "tty": os.isatty(0)}))
print(17, flush=True)
if "--action=default=Open" in sys.argv:
    print("default", flush=True)
''')
        self.desktop['notify_command'] = [sys.executable, str(self.notifier), str(self.record)]

    def config(self, desktop=None):
        return {'v': 1, 'desktop': self.desktop if desktop is None else desktop}

    def route(self, argv):
        return {'host': 'source', 'instance': 'instance', 'command': argv}

    def test_payload_normalization_and_exact_identity_without_terminal(self):
        payload = {'type': 'agent-turn-complete', 'thread-id': THREAD, 'turn-id': TURN,
                   'client': 'codex-tui', 'last-assistant-message': ' A\x1b\x07\n\n東京 '}
        with patch('codex_plus.notification_delivery.eligible_thread', return_value=True):
            event = envelope(payload, '/tmp/native.sock')
        self.assertEqual(event['metadata']['thread'], THREAD)
        self.assertEqual(event['metadata']['turn'], TURN)
        self.assertEqual(event['body'], 'A\n\n東京')
        self.assertEqual(read_event(io.BytesIO(encode_event(event))), event)
        for key in ('thread-id', 'turn-id'):
            with self.assertRaises(ValueError):
                envelope({**payload, key: 'not-native'}, '/tmp/native.sock')
        self.assertIsNone(envelope({**payload, 'client': 'codex_exec'}, '/tmp/native.sock'))
        with patch('codex_plus.notification_delivery.eligible_thread', return_value=False):
            self.assertIsNone(envelope(payload, '/tmp/native.sock'))

    def test_positive_native_user_thread_evidence_excludes_internal_and_unknown_work(self):
        calls = []
        thread = {'id': THREAD, 'threadSource': 'user', 'source': 'vscode'}
        class Client:
            identity = 'same'
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def call(self, method, params, **kwargs):
                calls.append((method, params))
                return {'thread': thread}
        check = lambda owner='same': eligible_thread('/tmp/native.sock', THREAD, client_factory=Client, identity=lambda _: owner)
        self.assertTrue(check())
        self.assertFalse(check('different'))
        for key, value in (('threadSource', 'thread_title'), ('threadSource', None),
                           ('source', {'subAgent': {}}), ('source', 'exec'),
                           ('parentThreadId', TURN)):
            old = thread.copy()
            thread[key] = value
            self.assertFalse(check())
            thread.clear(); thread.update(old)
        self.assertEqual({call[0] for call in calls}, {'thread/read'})
        self.assertTrue(all(call[1] == {'threadId': THREAD, 'includeTurns': False} for call in calls))

    def test_event_bounds_duplicate_fields_and_control_injection(self):
        for bad in ({**self.event, 'body': 'x' * 2049}, {**self.event, 'body': 'x\x1b'},
                    {**self.event, 'extra': 1}, {**self.event, 'v': True}):
            with self.assertRaises(ValueError):
                validate_event(bad)
        raw = encode_event(self.event).replace(b'"v":1', b'"v":1,"v":1', 1)
        for raw in (raw, b'x' * 16385):
            with self.assertRaises(ValueError):
                read_event(io.BytesIO(raw))

    def test_config_ownership_and_no_symlink_or_writable_configuration(self):
        path = self.root / 'notify.toml'
        path.write_text('v=1\n')
        self.assertEqual(load_config(path), {'v': 1})
        path.chmod(0o666)
        with self.assertRaises(ValueError):
            load_config(path)
        path.chmod(0o600)
        link = self.root / 'link'
        link.symlink_to(path)
        with self.assertRaises(OSError):
            load_config(link)

    def test_argv_validation_never_interpolates_text(self):
        for bad in (['relative'], [], ['/bin/echo', '{body}'], ['/bin/echo', 'x' * 2049]):
            with self.assertRaises(ValueError):
                command(bad)
        argv = ['/bin/echo', 'literal; $(touch BAD)']
        self.assertEqual(command(argv), argv)
        self.desktop['open'] = [self.route(['/bin/echo', '{thread}'])]
        config = settings(self.config())
        self.assertEqual(open_command(self.event, config), ['/bin/echo', THREAD])
        other = {**self.event, 'metadata': {**self.event['metadata'], 'host': 'elsewhere'}}
        self.assertIsNone(open_command(other, config))

    def test_focus_and_open_limitations_are_explicit(self):
        for condition in (None, 'unfocused', 'guess'):
            with self.assertRaises(ValueError):
                settings(self.config({**self.desktop, 'condition': condition}))
        for argv in (['/bin/echo', 'x{thread}'], ['/bin/echo', '{thread}', '{thread}']):
            with self.assertRaises(ValueError):
                settings(self.config({**self.desktop, 'open': [self.route(argv)]}))

    def test_publish_literal_content_and_metadata_preserved(self):
        argv = notify_argv(self.event, self.desktop)
        category = next(arg.removeprefix('--hint=string:category:') for arg in argv
                        if arg.startswith('--hint=string:category:'))
        self.assertEqual(decode(category), self.event['metadata'])
        self.assertEqual(argv[-2], 'Codex @ source')
        self.assertEqual(argv[-1].replace('<\u200c', '<').replace('&\u200c', '&'), self.event['body'])

    def test_claim_uncertainty_does_not_imply_desktop_admission(self):
        self.assertIsNone(claim(self.event, self.desktop))
        repeated = claim(self.event, self.desktop)
        self.assertEqual(repeated['status'], 'uncertain')
        self.assertEqual(repeated['desktop_id'], 0)

    def test_worker_admits_once_and_does_not_persist_assistant_body(self):
        results = []
        worker(self.event, self.config(), emit=results.append)
        self.assertEqual(results[0]['status'], 'delivered')
        self.assertEqual(results[0]['desktop_id'], 17)
        self.record.unlink()
        worker(self.event, self.config(), emit=results.append)
        self.assertEqual(results[1]['status'], 'duplicate')
        self.assertFalse(self.record.exists())
        with closing(state_database(self.desktop)) as database:
            columns = [row[1] for row in database.execute('PRAGMA table_info(episodes)')]
            self.assertEqual(columns, ['event', 'at', 'desktop_id'])
            self.assertEqual(database.execute('SELECT event FROM episodes').fetchone()[0], event_id(self.event['metadata']))

    def test_open_action_uses_only_configured_source_and_canonical_thread(self):
        opened = self.root / 'opened'
        script = self.root / 'open.py'
        script.write_text('import sys\nfrom pathlib import Path\nPath(sys.argv[1]).write_text(sys.argv[2])\n')
        self.desktop['open'] = [self.route([sys.executable, str(script), str(opened), '{thread}'])]
        results = []
        worker(self.event, self.config(), emit=results.append)
        deadline = time.monotonic() + 2
        while not opened.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertEqual(opened.read_text(), THREAD)

    def test_replay_store_and_source_commands_are_bounded(self):
        with closing(state_database(self.desktop)) as database, database:
            database.executemany('INSERT INTO episodes VALUES (?, ?, ?)',
                                 [(str(i), time.time(), i + 1) for i in range(MAX_EPISODES + 10)])
        claim(self.event, self.desktop)
        with closing(state_database(self.desktop)) as database:
            self.assertEqual(database.execute('SELECT COUNT(*) FROM episodes').fetchone()[0], MAX_EPISODES)

    def test_transport_rejects_wrong_event_and_bounded_timeout(self):
        script = self.root / 'transport.py'
        script.write_text('import json, sys\njson.load(sys.stdin)\nprint(json.dumps({"v":1,"event":"wrong","status":"delivered","desktop_id":1}), flush=True)\n')
        with self.assertRaises(ValueError):
            forward(self.event, [sys.executable, str(script)])
        script.write_text('import json, sys, time\njson.load(sys.stdin)\ntime.sleep(30)\n')
        started = time.monotonic()
        with self.assertRaises(TimeoutError):
            forward(self.event, [sys.executable, str(script)], timeout=.1)
        self.assertLess(time.monotonic() - started, 2)

    def test_detached_command_path_and_duplicate_receipt(self):
        path = self.root / 'notify.toml'
        # JSON strings/arrays are valid for this TOML subset.
        path.write_text('v=1\n[desktop]\ncondition="always"\nstate_dir=' + json.dumps(self.desktop['state_dir'])
                        + '\nnotify_command=' + json.dumps(self.desktop['notify_command']) + '\n')
        argv = [sys.executable, '-B', str(HELPER), 'desktop', '--config', str(path)]
        first = forward(self.event, argv)
        self.assertEqual(first['status'], 'delivered')
        self.assertFalse(json.loads(self.record.read_text())['tty'])
        self.assertEqual(forward(self.event, argv)['status'], 'duplicate')

    def test_concurrent_delivery_reserves_one_episode_before_notifying(self):
        self.notifier.write_text('''import sys, time
from pathlib import Path
with Path(sys.argv[1]).open("a") as stream: stream.write("request\\n")
time.sleep(.2)
print(17, flush=True)
''')
        path = self.root / 'notify.toml'
        path.write_text('v=1\n[desktop]\ncondition="always"\nstate_dir=' + json.dumps(self.desktop['state_dir'])
                        + '\nnotify_command=' + json.dumps(self.desktop['notify_command']) + '\n')
        argv = [sys.executable, '-B', str(HELPER), 'desktop', '--config', str(path)]
        with ThreadPoolExecutor(max_workers=2) as executor:
            jobs = [executor.submit(forward, self.event, argv) for _ in range(2)]
            statuses = [job.result()['status'] for job in jobs]
        self.assertEqual(statuses.count('delivered'), 1)
        self.assertTrue(set(statuses) <= {'delivered', 'duplicate', 'uncertain'})
        self.assertEqual(self.record.read_text(), 'request\n')
        self.assertEqual(forward(self.event, argv)['status'], 'duplicate')


if __name__ == '__main__':
    unittest.main()
