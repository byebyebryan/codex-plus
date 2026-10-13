import copy
import gzip
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from codex_plus import package
from codex_plus.model_server import Server, existing_socket
from codex_plus.cli import coordinator_info


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        repo = Path(__file__).resolve().parents[1]
        self.files = {name: (repo / name).read_bytes() for name in package.RUNTIME_FILES}
        self.metadata = package.manifest(self.files, '1' * 40)

    def archive(self, *, metadata=None, files=None, extra=None):
        path = self.root / ('artifact-' + str(len(list(self.root.glob('artifact-*')))) + '.tar.gz')
        content = dict(self.files if files is None else files)
        content['runtime.json'] = json.dumps(metadata or self.metadata).encode()
        with tarfile.open(path, 'w:gz') as out:
            for name, data in content.items():
                info = tarfile.TarInfo('codex-plus-runtime/' + name)
                info.mode, info.size = package.file_mode(name), len(data)
                out.addfile(info, io.BytesIO(data))
            if extra: out.addfile(extra, io.BytesIO(b''))
        return path

    def test_relocated_install_runs_stdio_and_shipped_guidance_without_source_imports(self):
        prefix = self.root / 'installed elsewhere'
        archive = self.archive()
        release = package.install(archive, prefix, package.sha(archive.read_bytes()))
        package.activate(prefix, self.metadata['source_revision'])
        config = package.mcp_config(prefix)
        request = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'}) + '\n'
        result = subprocess.run([config['command'], *config['args']], input=request, text=True,
            cwd=self.root, capture_output=True, timeout=10, check=True,
            env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': ''})
        response = json.loads(result.stdout)
        self.assertIn('Explicit stop', response['result']['instructions'])
        self.assertEqual(package.verify_install(release), self.metadata)
        self.assertFalse((self.root / 'codex-plus').exists())
        self.assertEqual(config['default_tools_approval_mode'], 'writes')
        self.assertNotIn('peer_send', config['tools'])
        self.assertIn('peer_send', package.mcp_config(prefix, allow_peer_send=True)['tools'])

    def test_checksum_content_and_link_attacks_are_rejected_before_installation(self):
        archive = self.archive()
        with self.assertRaises(ValueError): package.install(archive, self.root/'bad', '0'*64)
        self.assertFalse((self.root/'bad').exists())
        content = dict(self.files); content['codex_plus/model.py'] += b'\n# modified\n'
        with self.assertRaises(ValueError): package.read_archive(self.archive(files=content))
        for name, kind in (('../escape', tarfile.REGTYPE), ('scripts/codex-plus-model', tarfile.SYMTYPE)):
            entry = tarfile.TarInfo('codex-plus-runtime/' + name); entry.type = kind; entry.linkname = '/tmp/escape'
            with self.assertRaises(ValueError): package.read_archive(self.archive(extra=entry))

    def test_duplicate_unexpected_and_oversized_members_fail_closed(self):
        for name, size in (('LICENSE', 0), ('private-state.json', 0), ('runtime.json', package.MAX_FILE_BYTES+1)):
            entry = tarfile.TarInfo('codex-plus-runtime/'+name); entry.size=size
            if size:
                # Size-bound rejection does not require providing an inflated member.
                path=self.root/'oversized.tar.gz'
                with gzip.open(path,'wb') as out:out.write(entry.tobuf())
            else:path=self.archive(extra=entry)
            with self.assertRaises(ValueError):package.read_archive(path)

    def test_release_selection_upgrade_rollback_preserves_captured_runtime_and_state(self):
        prefix = self.root/'installed'; first = package.install(self.archive(), prefix)
        package.activate(prefix, '1'*40)
        captured = (prefix/'current/scripts/codex-plus-model').resolve()
        second_meta = copy.deepcopy(self.metadata); second_meta['source_revision']='2'*40
        second = package.install(self.archive(metadata=second_meta),prefix)
        package.activate(prefix,'2'*40)
        self.assertEqual(captured.parent.parent,first)
        self.assertTrue(captured.exists());self.assertTrue(second.exists())
        private = self.root/'private';private.mkdir();(private/'journal').write_text('pending uncertainty')
        package.activate(prefix,'1'*40)
        self.assertEqual((prefix/'current').resolve(),first)
        self.assertEqual((private/'journal').read_text(),'pending uncertainty')
        (first/'LICENSE').write_text('changed')
        with self.assertRaises(ValueError):package.install(self.archive(),prefix)

    def test_disabled_config_needs_no_runtime_and_listing_needs_no_native_endpoint(self):
        config=package.mcp_config(self.root/'missing',enabled=False)
        self.assertFalse(config['enabled']);self.assertFalse(config['required'])
        with patch('codex_plus.model_server.subprocess.run') as command:
            for method in ('initialize','tools/list'):
                self.assertIn('result',Server(self.root/'state',None).handle({'jsonrpc':'2.0','id':1,'method':method}))
            command.assert_not_called()
        self.assertFalse((self.root/'state').exists())

    def test_previous_preview_inventory_supports_upgrade_and_selection_rollback(self):
        old_files = {name: self.files[name] for name in package.PREVIOUS_RUNTIME_FILES}
        old_files['codex_plus/__init__.py'] = b"VERSION = '0.1.0-preview.1'\n"
        old_meta = package.manifest(old_files, '3'*40)
        old_meta['version'] = '0.1.0-preview.1'
        prefix = self.root/'installed'
        old = package.install(self.archive(metadata=old_meta, files=old_files), prefix)
        new = package.install(self.archive(), prefix)
        package.activate(prefix, '3'*40)
        self.assertEqual(package.verify_install(old)['version'], '0.1.0-preview.1')
        package.activate(prefix, '1'*40)
        self.assertEqual((prefix/'current').resolve(), new)
        package.activate(prefix, '3'*40)
        self.assertEqual((prefix/'current').resolve(), old)
        with self.assertRaises(ValueError):
            package.read_archive(self.archive(metadata=old_meta))
        unsupported = copy.deepcopy(old_meta); unsupported['version'] = 'unknown'
        with self.assertRaises(ValueError):
            package.read_archive(self.archive(metadata=unsupported, files=old_files))

    def test_coordinator_from_previous_verified_release_is_recognized_by_new_runtime(self):
        old_files = {name: self.files[name] for name in package.PREVIOUS_RUNTIME_FILES}
        old_meta = package.manifest(old_files, '3'*40); old_meta['version'] = '0.1.0-preview.1'
        release = package.install(self.archive(metadata=old_meta, files=old_files), self.root/'old-prefix')
        state = self.root/'private-state'; state.mkdir()
        identity = {'pid': 123456, 'start_ticks': 'fixture', 'executable': '/usr/bin/python3'}
        (state/'coordinator.json').write_text(json.dumps({**identity, 'state': str(state), 'generation': 'fixture'}))
        argv = b'\0'.join([b'python3', str(release/'scripts/codex-plus-watch').encode(), b'--state', str(state).encode(), b'serve'])
        original = Path.read_bytes
        def read_bytes(path):
            return argv if str(path)=='/proc/123456/cmdline' else original(path)
        with patch('codex_plus.cli.process_identity', return_value=identity), patch.object(Path,'read_bytes',read_bytes):
            self.assertEqual(coordinator_info(state)['runtime_version'], '0.1.0-preview.1')
            (release/'LICENSE').write_text('tampered')
            self.assertIsNone(coordinator_info(state))

    def test_release_selection_refuses_shared_writable_prefix_and_invalid_config_bounds(self):
        prefix=self.root/'installed';package.install(self.archive(),prefix)
        prefix.chmod(0o777)
        with self.assertRaises(ValueError):package.activate(prefix,'1'*40)
        self.assertFalse((prefix/'current').exists())
        for options in ({'max_duration':float('inf')},{'max_events':True},{'max_duration':0}):
            with self.assertRaises(ValueError):package.mcp_config(self.root/'missing',enabled=False,**options)

    def test_auto_endpoint_query_is_status_only_and_refuses_absent_owner(self):
        with patch.dict('os.environ',{},clear=True),patch('codex_plus.model_server.subprocess.run') as run:
            run.return_value.stdout=json.dumps({'status':'running','socketPath':'unix:///fixture/socket'})
            self.assertEqual(existing_socket(),'/fixture/socket')
            self.assertEqual(run.call_args.args[0],['rtk','proxy','codex','app-server','daemon','version'])
            run.return_value.stdout=json.dumps({'status':'stopped'})
            with self.assertRaises(ValueError):existing_socket()


if __name__ == '__main__': unittest.main()
