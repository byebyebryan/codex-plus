import asyncio
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codex_plus.notification_run import Prepared, run
from test_notification_rich import THREAD, OLD, frame


class Relay(unittest.TestCase):
    def check_relay(self, malformed=False):
        async def scenario(root):
            native_path = root / 'native.sock'
            request = b'GET / HTTP/1.1\r\n\r\n' + frame({
                'id': 1, 'method': 'thread/start', 'params': {}}, mask=True)
            response = (b'HTTP/1.1 101 Switching\r\n\r\n' + frame({'id': 1, 'result': {
                'thread': {'id': THREAD, 'source': 'cli', 'threadSource': 'user'}}})
                + frame({'method': 'item/completed', 'params': {'threadId': THREAD, 'turnId': OLD,
                   'item': {'type': 'agentMessage', 'phase': 'final_answer', 'text': 'Owned relay fixture'}}})
                + frame({'method': 'turn/completed', 'params': {'threadId': THREAD,
                   'turn': {'id': OLD, 'status': 'completed'}}}))
            if malformed:
                response = b'HTTP/1.1 101 ' + b'x' * 17000 + b'\r\n\r\n' + response
            received = []

            async def backend(reader, writer):
                try:
                    received.append(await reader.readexactly(len(request)))
                    writer.write(response)
                    await writer.drain()
                    await reader.read()
                finally:
                    writer.close()

            server = await asyncio.start_unix_server(backend, path=str(native_path))
            executable = root / 'native-fixture'
            result = root / 'received.json'
            executable.write_text('#!/usr/bin/env -S python3 -B\n'
                'import hashlib,json,socket,sys\n'
                'from pathlib import Path\n'
                'p=sys.argv[sys.argv.index("--remote")+1].removeprefix("unix://")\n'
                's=socket.socket(socket.AF_UNIX);s.settimeout(3);s.connect(p)\n'
                's.sendall(' + repr(request) + ')\n'
                'data=bytearray()\n'
                'while len(data)<' + str(len(response)) + ':\n'
                ' chunk=s.recv(65536)\n'
                ' if not chunk:raise RuntimeError("unexpected native EOF")\n'
                ' data.extend(chunk)\n'
                'Path(' + repr(str(result)) + ').write_text(json.dumps(dict(sha256=hashlib.sha256(data).hexdigest(),argv=sys.argv[1:])))\n'
                's.close()\nsys.exit(17)\n')
            executable.chmod(0o700)
            read_fd, write_fd = os.pipe()
            owner = {'resolved_socket': str(native_path)}
            prepared = Prepared(owner, write_fd, False, ['-c', 'tui.notifications=[]'], 'test-viewer')
            try:
                with patch('codex_plus.notification_run.listener_identity', return_value=owner):
                    async with asyncio.timeout(5):
                        code = await run(str(native_path), ['owned argument'], str(executable), prepared=prepared)
                emitted = os.read(read_fd, 65536)
                self.assertEqual(code, 17)
                self.assertEqual(received, [request])
                self.assertEqual(json.loads(result.read_text())['sha256'], hashlib.sha256(response).hexdigest())
                self.assertEqual(json.loads(result.read_text())['argv'][-1], 'owned argument')
                self.assertEqual(emitted.count(b'\x1b]99;'), 2)
                if malformed:
                    self.assertIn(b'codex-notify-status-test-viewer', emitted)
                else:
                    self.assertIn(b'f=Q29kZXg=', emitted)
                    self.assertNotIn(b'codex-notify-status-', emitted)
            finally:
                os.close(read_fd)
                server.close()
                await server.wait_closed()
        with tempfile.TemporaryDirectory() as directory:
            asyncio.run(scenario(Path(directory)))

    def test_native_bytes_argv_and_exit_survive_observation(self):
        self.check_relay()

    def test_observation_failure_reports_once_and_preserves_native_bytes(self):
        self.check_relay(malformed=True)


if __name__ == '__main__': unittest.main()
