import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from codex_plus.native import RpcError, listener_identity


class NativeOwnerTests(unittest.TestCase):
    def test_kernel_listener_uid_is_verified_instead_of_assuming_the_caller_uid(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); requested = root/'socket'; requested.touch()
            proc = root/'proc'; (proc/'net').mkdir(parents=True)
            (proc/'net/unix').write_text('header\n0000: 0000 0000 00010000 0001 01 1234 '+str(requested)+'\n')
            process = proc/'321'; (process/'fd').mkdir(parents=True)
            (process/'fd/0').symlink_to('socket:[1234]')
            (process/'exe').symlink_to('/usr/bin/python3')
            (process/'stat').write_text('321 (fixture) '+' '.join(['0']*19+['123']+['0']*4))
            def mapped(value):
                if str(value)=='/proc':return proc
                if str(value)=='/proc/net/unix':return proc/'net/unix'
                return Path(value)
            actual_uid=os.getuid()
            with patch('codex_plus.native.Path',side_effect=mapped):
                result=listener_identity(str(requested))
                self.assertEqual(result['uid'],actual_uid)
                self.assertEqual(result['pid'],321)
                with patch('codex_plus.native.os.getuid',return_value=actual_uid+1):
                    with self.assertRaises(RpcError):listener_identity(str(requested))


if __name__=='__main__':unittest.main()
