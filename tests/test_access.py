import copy
from contextlib import closing
from pathlib import Path
import tempfile
import unittest

from codex_plus.access import current, effective, resolve, validate_grant
from codex_plus.store import Store


class Native:
    def __init__(self, cwd, sandbox):
        self.binding = {'thread_id': 'owned', 'requested_socket': '/fixture'}
        self.response = {'thread': {'id': 'owned'}, 'cwd': cwd,
                         'sandbox': sandbox, 'activePermissionProfile': None}
        self.calls = []

    def bind(self, identity):
        return dict(self.binding)

    def call(self, method, params):
        self.calls.append((method, params))
        return copy.deepcopy(self.response)


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = str(Path(self.tmp.name).resolve())
        self.native = Native(self.cwd, {'type': 'dangerFullAccess'})

    def grant(self, **options):
        return resolve(self.native, self.native.binding, self.cwd, **options)

    def test_full_access_can_use_read_only_filesystem_with_existing_network(self):
        value = self.grant(source_access='read_only', network_access='required')
        self.assertEqual(value['request'], {'sandboxPolicy': {'type': 'readOnly', 'networkAccess': True}})
        self.assertEqual(self.native.calls, [('thread/resume', {'threadId': 'owned', 'excludeTurns': True})])

    def test_default_retains_authorized_session_filesystem_for_authentication_caches(self):
        self.native.response['sandbox'] = {'type': 'workspaceWrite', 'networkAccess': True,
            'writableRoots': [self.cwd], 'excludeSlashTmp': True}
        value = self.grant()
        self.assertEqual(value['request']['sandboxPolicy'], self.native.response['sandbox'])
        self.assertEqual(current(self.native, self.native.binding, value, self.cwd), value['request'])

    def test_restricted_session_cannot_request_network_by_tool_arguments(self):
        self.native.response['sandbox'] = {'type': 'readOnly', 'networkAccess': False}
        with self.assertRaisesRegex(ValueError, 'does not authorize'):
            self.grant(network_access='required')
        self.assertFalse(self.grant()['request']['sandboxPolicy']['networkAccess'])

    def test_network_can_be_narrowed_without_granting_filesystem_writes(self):
        value = self.grant(source_access='read_only', network_access='off')
        self.assertEqual(value['request'], {'sandboxPolicy': {'type': 'readOnly', 'networkAccess': False}})
        with self.assertRaisesRegex(ValueError, 'read_only'):
            self.grant(network_access='off')

    def test_named_profile_keeps_native_anchor_and_does_not_use_legacy_widening(self):
        self.native.response['sandbox'] = {'type': 'readOnly', 'networkAccess': True}
        self.native.response['activePermissionProfile'] = {'id': 'restricted-reader', 'source': 'named'}
        value = self.grant()
        self.assertEqual(value['request'], {'permissionProfile': 'restricted-reader'})
        with self.assertRaises(ValueError):
            resolve(self.native, self.native.binding, '/', network_access='inherit')
        with self.assertRaises(ValueError):
            self.grant(network_access='off')

    def test_owner_and_returned_thread_must_match(self):
        with self.assertRaises(ValueError):
            resolve(self.native, {'thread_id': 'other'}, self.cwd)
        self.native.response['thread']['id'] = 'other'
        with self.assertRaises(ValueError):
            self.grant()

    def test_changed_permissions_require_explicit_new_intent(self):
        value = self.grant()
        self.native.response['sandbox'] = {'type': 'readOnly', 'networkAccess': False}
        with self.assertRaisesRegex(ValueError, 'changed'):
            current(self.native, self.native.binding, value, self.cwd)

    def test_changed_private_execution_request_is_rejected_by_journal_validation(self):
        value = self.grant(source_access='read_only', network_access='off')
        value['request']['sandboxPolicy']['networkAccess'] = True
        with self.assertRaisesRegex(ValueError, 'does not match'):
            validate_grant(value, self.cwd)
        with closing(Store(Path(self.cwd)/'state')) as store:
            with self.assertRaises(ValueError):
                store.create('watch', {'command': ['true'], 'cwd': self.cwd, 'execution': value})
            self.assertEqual(store.jobs(), [])

    def test_unknown_external_policy_is_unavailable_instead_of_server_default(self):
        self.native.response['sandbox'] = {'type': 'externalSandbox', 'networkAccess': 'enabled'}
        with self.assertRaisesRegex(ValueError, 'cannot be represented'):
            self.grant()


if __name__ == '__main__':
    unittest.main()
