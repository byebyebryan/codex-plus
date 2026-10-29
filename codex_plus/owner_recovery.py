"""Explicit clean rollover and read-only history for native owner incarnations."""

from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sqlite3
import stat
import tempfile
import time
import urllib.parse
import uuid

from .native import Client
from .peers import PeerReader, thread_id
from .presentation import clean_text, label as display_label, quote
from .store import private_directory


SELECTION_FORMAT = 'codex-plus-owner-selection-v1'
EPOCH_FORMAT = 'codex-plus-owner-epoch-v1'
ARCHIVE_FORMAT = 'codex-plus-owner-archive-v1'
MAX_FILES = 512
MAX_STATE_BYTES = 64 * 1024 * 1024
MAX_ARCHIVES = 64
MAX_ARCHIVE_HISTORY_BYTES = 128 * 1024 * 1024
MAX_JSON_BYTES = 1024 * 1024
MAX_HISTORY_PAGE = 50
MAX_OUTGOING_CHECKS = 1000
MAX_OUTGOING_TARGETS = 20
LOCK_TIMEOUT = 5.0
MAX_PROC_SCAN_SECONDS = 1.5
MAX_QUEUE_SCAN_SECONDS = 5.0
OWNER_KEYS = ('host', 'uid', 'pid_namespace', 'requested_socket', 'resolved_socket',
              'pid', 'start_ticks', 'executable', 'thread_id')
REF_PREFIX = {'peer': 'p', 'watch': 'w', 'message': 'm', 'wake': 't'}
REF_KIND = {value: key for key, value in REF_PREFIX.items()}


class OwnerRecoveryError(ValueError):
    """Actionable owner diagnosis that remains compatible with existing MCP errors."""

    def __init__(self, role, code, caller, recipient=None, detail=''):
        self.role, self.code, self.caller, self.recipient = role, code, caller, recipient
        self.detail = detail
        names = {'caller': 'caller', 'recipient': 'recipient'}
        subject = names.get(role, role)
        fields = [f'{subject}_owner_state={code}', f'caller_thread={caller}']
        if recipient is not None:
            fields.append(f'recipient_thread={recipient}')
        if detail:
            fields.append(detail)
        if role == 'recipient':
            fields.append('This operation registered no new recipient intent; prior delivery and handling remain as recorded. The recipient must run owner_status and, if clean, owner_recover in its own conversation.')
        elif role == 'caller':
            fields.append('Run owner_status in this conversation; owner_recover is available only for a clean exact-thread rollover.')
        super().__init__('; '.join(fields))


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _valid_binding(value):
    if not isinstance(value, dict) or set(value) != set(OWNER_KEYS):
        raise ValueError('owner binding is missing required exact incarnation fields')
    thread_id(value['thread_id'])
    if (isinstance(value['uid'], bool) or not isinstance(value['uid'], int) or
            isinstance(value['pid'], bool) or not isinstance(value['pid'], int) or value['pid'] <= 0):
        raise ValueError('owner binding process identity is invalid')
    for key in ('host', 'pid_namespace', 'requested_socket', 'resolved_socket', 'start_ticks', 'executable'):
        if not isinstance(value[key], str) or not value[key] or len(value[key]) > 4096 or '\x00' in value[key]:
            raise ValueError('owner binding contains invalid text')
    return dict(value)


def logical_binding(value):
    value = _valid_binding(value)
    return {key: value[key] for key in ('host', 'uid', 'pid_namespace', 'requested_socket',
                                        'resolved_socket', 'thread_id')}


def kernel_boot_id():
    value = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    return _valid_boot_id(value)


def _valid_boot_id(value):
    if not isinstance(value, str):
        raise ValueError('owner boot identity must be a canonical nonzero UUID')
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError) as error:
        raise ValueError('owner boot identity must be a canonical nonzero UUID') from error
    if str(parsed) != value or parsed.int == 0:
        raise ValueError('owner boot identity must be a canonical nonzero UUID')
    return value


def _safe_private_dir(path, *, create=False):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('state directory must not be a symlink')
    if not path.exists():
        if not create:
            return None
        path.mkdir(mode=0o700, parents=True, exist_ok=False)
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('state directory must be owned by this user and private (0700)')
    return path


def _managed_dir(container, name, *, create=False):
    container = _safe_private_dir(container)
    path = container / name
    if path.is_symlink():
        raise ValueError('managed owner directory must not be a symlink: ' + name)
    if not path.exists():
        if not create:
            return None
        path.mkdir(mode=0o700)
    return _safe_private_dir(path)


def _archive_dir(thread_root, epoch):
    if not isinstance(epoch, str) or not re.fullmatch(r'(?:legacy-)?[a-f0-9-]{32,36}', epoch):
        raise ValueError('owner archive identity is malformed')
    archives = _managed_dir(thread_root, 'archives')
    if archives is None:
        raise ValueError('owner archive directory is missing')
    path = archives / epoch
    if path.is_symlink():
        raise ValueError('owner archive path must not be a symlink')
    _safe_private_dir(path)
    return path


def _read_json(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f'private state file must not be a symlink: {path.name}')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if info.st_size > MAX_JSON_BYTES:
            raise ValueError(f'private state JSON exceeds its size bound: {path.name}')
        chunks = []
        remaining = MAX_JSON_BYTES + 1
        while remaining:
            chunk = os.read(fd, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b''.join(chunks)
    finally:
        os.close(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError(f'private state file must be owned and private: {path.name}')
    if len(payload) != info.st_size or len(payload) > MAX_JSON_BYTES:
        raise ValueError(f'private state JSON changed during read or exceeds its size bound: {path.name}')
    return json.loads(payload.decode('utf-8'))


def _hash_regular(path, maximum):
    path = Path(path)
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    try:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or
                before.st_mode & 0o077 or before.st_size > maximum):
            raise ValueError('owner archive file is unowned, non-private or oversized')
        digest = hashlib.sha256()
        size = 0
        while True:
            block = os.read(fd, 1024 * 1024)
            if not block:
                break
            size += len(block)
            if size > maximum:
                raise ValueError('owner archive file exceeds its size bound')
            digest.update(block)
        after = os.fstat(fd)
        if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) or size != before.st_size):
            raise ValueError('owner archive file changed during verification')
        return digest.hexdigest()
    finally:
        os.close(fd)


def _atomic_json(path, value, *, before_replace=None):
    path = Path(path)
    if path.is_symlink():
        raise ValueError('private state file must not be a symlink')
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        if before_replace is not None:
            before_replace(temporary)
        temporary.replace(path)
        _fsync_dir(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _lock_path(state_root, thread):
    return Path(state_root) / '.owner-locks' / (thread_id(thread) + '.lock')


@contextmanager
def thread_locks(state_root, threads, *, timeout=LOCK_TIMEOUT, create=True):
    """Acquire stable per-thread locks in canonical order with a finite wait."""
    paths = sorted({_lock_path(state_root, thread) for thread in threads}, key=lambda path: str(path))
    opened = []
    deadline = time.monotonic() + timeout
    try:
        for path in paths:
            if create:
                path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                parent = _safe_private_dir(path.parent)
            else:
                parent = _safe_private_dir(path.parent)
                if parent is None or not path.exists():
                    continue
            if path.is_symlink():
                raise ValueError('stable owner lock must not be a symlink')
            flags = os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0)
            if create:
                flags |= os.O_CREAT
            try:
                fd = os.open(path, flags, 0o600)
            except FileNotFoundError:
                continue
            info = os.fstat(fd)
            if info.st_uid != os.getuid() or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
                os.close(fd)
                raise ValueError('stable owner lock must be owned and private')
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    opened.append(fd)
                    break
                except BlockingIOError:
                    if time.monotonic() >= deadline:
                        os.close(fd)
                        raise TimeoutError('owner state is busy; retry after the active model operation finishes')
                    time.sleep(min(0.025, max(0.001, deadline - time.monotonic())))
        yield
    finally:
        for fd in reversed(opened):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


def _marker(path):
    value = _read_json(path)
    if not isinstance(value, dict) or value.get('format') != SELECTION_FORMAT:
        return None
    required = {'format', 'thread_id', 'epoch', 'selected', 'binding', 'boot_id', 'archives', 'last_recovery'}
    if set(value) != required:
        raise ValueError('owner selection marker is incomplete or unsupported')
    tid = thread_id(value['thread_id'])
    if not isinstance(value['epoch'], str) or not re.fullmatch(r'e-[0-9a-f]{32}', value['epoch']):
        raise ValueError('selected owner epoch identity is malformed')
    if value['selected'] != 'incarnations/' + value['epoch']:
        raise ValueError('selected owner epoch path is malformed')
    _valid_boot_id(value['boot_id'])
    if _valid_binding(value['binding'])['thread_id'] != tid:
        raise ValueError('selection marker thread does not match its active binding')
    if thread_root_name := Path(path).parent.name:
        if thread_root_name != tid:
            raise ValueError('selection marker thread does not match its stable container')
    if not isinstance(value['archives'], list) or len(value['archives']) > MAX_ARCHIVES:
        raise ValueError('owner archive index is incomplete or exceeds its bound')
    seen_archives = set()
    for entry in value['archives']:
        if (not isinstance(entry, dict) or set(entry) != {'epoch', 'manifest_sha256'} or
                not isinstance(entry['epoch'], str) or not re.fullmatch(r'(?:legacy-)?[a-f0-9-]{32,36}', entry['epoch']) or
                not isinstance(entry['manifest_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', entry['manifest_sha256'])):
            raise ValueError('owner archive index contains an invalid entry')
        if entry['epoch'] in seen_archives:
            raise ValueError('owner archive index repeats an incarnation')
        seen_archives.add(entry['epoch'])
    if value['epoch'] in seen_archives:
        raise ValueError('selected owner incarnation is also listed as an archived generation')
    if value['last_recovery'] is not None:
        recovery = value['last_recovery']
        if (not isinstance(recovery, dict) or set(recovery) != {'preview_token', 'receipt'} or
                not isinstance(recovery['preview_token'], str) or not isinstance(recovery['receipt'], dict)):
            raise ValueError('owner selection recovery receipt is malformed')
    return value


def selected_state(thread_root, *, expected_binding=None):
    """Return (state_dir, epoch, binding, selection); never normalizes the binding."""
    thread_root = Path(thread_root)
    _safe_private_dir(thread_root)
    path = thread_root / 'binding.json'
    value = _read_json(path)
    if isinstance(value, dict) and value.get('format') == SELECTION_FORMAT:
        marker = _marker(path)
        incarnations = _managed_dir(thread_root, 'incarnations')
        if incarnations is None:
            raise ValueError('selected owner incarnation directory is missing')
        state = incarnations / marker['epoch']
        _safe_private_dir(state)
        binding = _valid_binding(_read_json(state / 'binding.json'))
        if binding != marker['binding']:
            raise ValueError('selected state binding differs from the stable owner marker')
        epoch = _read_json(state / 'owner-epoch.json')
        if (not isinstance(epoch, dict) or epoch.get('format') != EPOCH_FORMAT or
                epoch.get('epoch') != marker['epoch'] or epoch.get('binding') != binding):
            raise ValueError('selected owner epoch evidence is missing or inconsistent')
        epoch_boot_id = _valid_boot_id(epoch.get('boot_id'))
        if marker['boot_id'] != epoch_boot_id:
            raise ValueError('selected owner boot identity differs from the stable owner marker')
        if expected_binding is not None and binding != expected_binding:
            raise OwnerRecoveryError('caller', 'stale_or_conflicting_incarnation', expected_binding['thread_id'],
                                     detail='The selected model state belongs to another native process incarnation.')
        if expected_binding is not None:
            try:
                current_boot = kernel_boot_id()
            except (OSError, ValueError) as error:
                raise OwnerRecoveryError('caller', 'boot_identity_unknown', expected_binding['thread_id'],
                                         detail='Current kernel boot identity is unavailable.') from error
            if epoch_boot_id != current_boot:
                raise OwnerRecoveryError('caller', 'stale_boot_incarnation', expected_binding['thread_id'],
                                         detail='The selected owner epoch was recorded on another or unknown kernel boot.')
        return state, marker['epoch'], binding, marker
    binding = _valid_binding(value)
    if thread_root.name == binding['thread_id']:
        thread_id(thread_root.name)
    if binding['thread_id'] != thread_root.name:
        raise ValueError('owner binding thread does not match its stable state container')
    if expected_binding is not None and binding != expected_binding:
        raise OwnerRecoveryError('caller', 'stale_incarnation', expected_binding['thread_id'],
                                 detail='The saved caller owner differs from the exact positively loaded current process.')
    return thread_root, 'legacy', binding, None


def recipient_state(thread_root, current_binding, caller_thread):
    """Resolve selected state or provide an actionable recipient-owned failure."""
    try:
        state, epoch, frozen, marker = selected_state(thread_root, expected_binding=current_binding)
        if frozen != current_binding:
            raise ValueError('saved recipient binding differs from its current exact owner')
        return state, epoch, marker
    except (OSError, ValueError, KeyError, TypeError) as error:
        detail = error.detail if isinstance(error, OwnerRecoveryError) else str(error)
        if isinstance(error, OwnerRecoveryError):
            detail = 'The saved recipient owner differs from its verified current incarnation.'
        raise OwnerRecoveryError('recipient', 'stale_or_unavailable_incarnation', caller_thread,
                                 current_binding.get('thread_id'), detail) from error


def _tree_manifest(root, *, ignore_managed=False, ignore_paths=()):
    root = Path(root)
    ignored_paths = {Path(path).absolute() for path in ignore_paths}
    _safe_private_dir(root)
    entries = []
    total = 0
    root_info = root.lstat()
    if not stat.S_ISDIR(root_info.st_mode) or root_info.st_uid != os.getuid():
        raise ValueError('owner state root is unsafe')
    entries.append({'path': '.', 'type': 'directory', 'mode': stat.S_IMODE(root_info.st_mode)})
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(base)
        dirs.sort(); files.sort()
        relative_dir = base.relative_to(root).as_posix()
        ignored = {'archives', 'incarnations'} if relative_dir == '.' and ignore_managed else set()
        for name in list(dirs):
            if name in ignored:
                continue
            child = base / name
            info = child.lstat()
            if (not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or
                    info.st_uid != os.getuid() or info.st_mode & 0o077):
                raise ValueError('owner state contains a linked, non-private or unowned directory')
        dirs[:] = [name for name in dirs if not (relative_dir == '.' and name in ignored)]
        if relative_dir != '.':
            info = base.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise ValueError('owner state contains an unsafe directory')
            entries.append({'path': relative_dir, 'type': 'directory', 'mode': stat.S_IMODE(info.st_mode)})
        for name in files:
            path = base / name
            if path.absolute() in ignored_paths:
                continue
            info = path.lstat()
            if (not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or
                    info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_nlink != 1):
                raise ValueError('owner state contains an unsafe linked or special file')
            total += info.st_size
            if len(entries) >= MAX_FILES or total > MAX_STATE_BYTES:
                raise ValueError('owner state scan exceeds the bounded archive limit')
            flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
            fd = os.open(path, flags)
            try:
                before = os.fstat(fd)
                chunks = []
                read_size = 0
                while True:
                    chunk = os.read(fd, min(1024 * 1024, max(1, info.st_size + 1)))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    read_size += len(chunk)
                    if read_size > MAX_STATE_BYTES:
                        raise ValueError('owner state file exceeds the bounded archive limit')
                after = os.fstat(fd)
            finally:
                os.close(fd)
            if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) or
                    read_size != info.st_size):
                raise ValueError('owner state changed during its bounded scan')
            content = b''.join(chunks)
            entries.append({'path': path.relative_to(root).as_posix(), 'type': 'file',
                            'mode': stat.S_IMODE(info.st_mode), 'size': info.st_size,
                            'sha256': _sha(content)})
    entries.sort(key=lambda entry: (entry['path'], entry['type']))
    digest = _sha(_canonical(entries))
    return {'entries': entries, 'sha256': digest, 'bytes': total}


def _copy_tree(source, destination, expected):
    source, destination = Path(source), Path(destination)
    destination.mkdir(mode=0o700, parents=True, exist_ok=False)
    dirs = [entry for entry in expected['entries']
            if entry['type'] == 'directory' and entry['path'] != '.']
    for entry in sorted(dirs, key=lambda item: item['path'].count('/')):
        target = destination / PurePosixPath(entry['path'])
        target.mkdir(mode=0o700, parents=True, exist_ok=False)
        target.chmod(entry['mode'])
    for entry in expected['entries']:
        if entry['type'] != 'file':
            continue
        relative = PurePosixPath(entry['path'])
        src, dst = source / relative, destination / relative
        dst.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        src_info = src.lstat()
        if not stat.S_ISREG(src_info.st_mode) or stat.S_ISLNK(src_info.st_mode):
            raise ValueError('owner state changed while preparing its archive')
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
        src_fd = os.open(src, flags)
        dst_fd = os.open(dst, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        try:
            before = os.fstat(src_fd)
            digest = hashlib.sha256()
            copied = 0
            while True:
                chunk = os.read(src_fd, 1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk); copied += len(chunk)
                view = memoryview(chunk)
                while view:
                    written = os.write(dst_fd, view)
                    view = view[written:]
            after = os.fstat(src_fd)
            os.fsync(dst_fd)
        finally:
            os.close(src_fd); os.close(dst_fd)
        if (digest.hexdigest() != entry['sha256'] or copied != entry['size'] or
                (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)):
            raise ValueError('owner state changed while its archive was being copied')
        dst.chmod(entry['mode'])
    destination.chmod(stat.S_IMODE(source.stat().st_mode))
    copied = _tree_manifest(destination)
    if copied['entries'] != expected['entries'] or copied['sha256'] != expected['sha256']:
        raise ValueError('archived owner files or modes failed exact verification')


def _copy_private_file(source, target, maximum):
    source, target = Path(source), Path(target)
    if source.is_symlink():
        raise ValueError('SQLite source or sidecar must not be a symlink')
    source_fd = os.open(source, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    target_fd = None
    try:
        before = os.fstat(source_fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid() or
                before.st_mode & 0o077 or before.st_nlink != 1 or before.st_size > maximum):
            raise ValueError('SQLite source or sidecar is unowned, linked, non-private or oversized')
        target_fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY |
            getattr(os, 'O_NOFOLLOW', 0), 0o600)
        total = 0
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > maximum:
                raise ValueError('SQLite source or sidecar exceeds its size bound')
            view = memoryview(chunk)
            while view:
                written = os.write(target_fd, view)
                view = view[written:]
        after = os.fstat(source_fd)
        os.fsync(target_fd)
        if ((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) !=
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) or total != before.st_size):
            raise ValueError('SQLite source or sidecar changed during its bounded copy')
        return before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns
    finally:
        os.close(source_fd)
        if target_fd is not None:
            os.close(target_fd)


def _snapshot_database(source_dir, snapshot_path):
    source_dir, snapshot_path = Path(source_dir), Path(snapshot_path)
    _safe_private_dir(source_dir)
    database = source_dir / 'journal.sqlite3'
    if not database.exists() or database.is_symlink():
        raise ValueError('legacy journal is missing or linked; its history is unknown')
    wal, shm = Path(str(database) + '-wal'), Path(str(database) + '-shm')
    if wal.is_symlink() or shm.is_symlink():
        raise ValueError('legacy SQLite WAL sidecars must not be symlinks')
    if wal.exists() != shm.exists():
        raise ValueError('legacy SQLite WAL sidecars are incomplete; consistent history cannot be proved')
    work = Path(tempfile.mkdtemp(prefix='codex-plus-journal-'))
    try:
        sources = [source for source in (database, wal, shm) if source.exists()]
        copied = {source: _copy_private_file(source, work / source.name, MAX_STATE_BYTES)
                  for source in sources}
        if sum(signature[2] for signature in copied.values()) > MAX_STATE_BYTES:
            raise ValueError('SQLite database and sidecars exceed their aggregate size bound')
        for source in (database, wal, shm):
            if source in copied:
                try:
                    info = source.lstat()
                except OSError as error:
                    raise ValueError('SQLite source or sidecar disappeared during snapshot') from error
                current = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
                if stat.S_ISLNK(info.st_mode) or current != copied[source]:
                    raise ValueError('SQLite source or sidecar changed during snapshot')
            elif source.exists() or source.is_symlink():
                raise ValueError('SQLite sidecar appeared during snapshot')
        uri = 'file:' + urllib.parse.quote(str(work / database.name), safe='/')
        connection = sqlite3.connect(uri, uri=True, timeout=2)
        try:
            quick = connection.execute('PRAGMA quick_check').fetchone()
            if not quick or quick[0] != 'ok':
                raise ValueError('legacy journal integrity is not confirmed')
            tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {'jobs', 'events', 'renewals'}.issubset(tables):
                raise ValueError('legacy journal schema is incomplete; history cannot be classified')
            target = sqlite3.connect(snapshot_path)
            try:
                connection.backup(target)
                check = target.execute('PRAGMA integrity_check').fetchone()
                if not check or check[0] != 'ok':
                    raise ValueError('SQLite history snapshot failed integrity verification')
            finally:
                target.close()
        finally:
            connection.close()
        snapshot_path.chmod(0o400)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _open_snapshot(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('archived history database is missing')
    uri = 'file:' + urllib.parse.quote(str(path), safe='/') + '?mode=ro&immutable=1'
    connection = sqlite3.connect(uri, uri=True, timeout=2)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def _snapshot_reader(path):
    connection = _open_snapshot(path)
    try:
        yield connection
    finally:
        connection.close()


def _archive_manifest(archive_dir):
    archive_dir = Path(archive_dir)
    if archive_dir.parent.name == 'archives':
        _archive_dir(archive_dir.parent.parent, archive_dir.name)
    else:
        _safe_private_dir(archive_dir)
    manifest_path = archive_dir / 'manifest.json'
    manifest = _read_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get('format') != ARCHIVE_FORMAT:
        raise ValueError('owner archive manifest is missing or unsupported')
    if set(manifest) != {'format', 'epoch', 'binding', 'source_tree', 'snapshot', 'boot_id',
                         'preview_token', 'prepared_for'}:
        raise ValueError('owner archive manifest is incomplete')
    if not isinstance(manifest['epoch'], str) or not re.fullmatch(r'(?:legacy-)?[a-f0-9-]{32,36}', manifest['epoch']):
        raise ValueError('owner archive identity is malformed')
    _valid_binding(manifest['binding'])
    if (not isinstance(manifest['source_tree'], dict) or
            set(manifest['source_tree']) != {'entries', 'sha256', 'bytes'} or
            not isinstance(manifest['source_tree'].get('entries'), list) or
            type(manifest['source_tree'].get('bytes')) is not int or
            not 0 <= manifest['source_tree']['bytes'] <= MAX_STATE_BYTES or
            manifest['source_tree'].get('sha256') != _sha(_canonical(manifest['source_tree']['entries']))):
        raise ValueError('owner archive source manifest is invalid')
    entries = manifest['source_tree']['entries']
    if len(entries) > MAX_FILES:
        raise ValueError('owner archive source manifest exceeds its file bound')
    for entry in entries:
        if (not isinstance(entry, dict) or entry.get('type') not in ('file', 'directory') or
                not isinstance(entry.get('path'), str) or entry['path'] == '' or
                '\x00' in entry['path'] or PurePosixPath(entry['path']).is_absolute() or
                any(part in ('..', '.') for part in PurePosixPath(entry['path']).parts) or
                type(entry.get('mode')) is not int or not 0 <= entry['mode'] <= 0o777):
            raise ValueError('owner archive source manifest contains an unsafe path or mode')
        if entry['type'] == 'file' and (type(entry.get('size')) is not int or entry['size'] < 0 or
                not isinstance(entry.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', entry['sha256'])):
            raise ValueError('owner archive source manifest contains an invalid file receipt')
    prepared = manifest['prepared_for']
    if (not isinstance(prepared, dict) or set(prepared) != {'source_digest', 'selected_epoch', 'current_binding'} or
            prepared['source_digest'] != manifest['source_tree']['sha256'] or
            not isinstance(prepared['selected_epoch'], str) or
            not re.fullmatch(r'e-[0-9a-f]{32}', prepared['selected_epoch']) or
            _valid_binding(prepared['current_binding'])['thread_id'] != manifest['binding']['thread_id']):
        raise ValueError('owner archive preparation evidence is invalid')
    snapshot = manifest['snapshot']
    if not isinstance(snapshot, dict) or set(snapshot) != {'file', 'sha256'} or snapshot['file'] != 'journal.snapshot.sqlite3' or not re.fullmatch(r'[0-9a-f]{64}', snapshot['sha256']):
        raise ValueError('owner archive journal snapshot manifest is invalid')
    path = archive_dir / snapshot['file']
    if _hash_regular(path, MAX_STATE_BYTES) != snapshot['sha256']:
        raise ValueError('owner archive journal snapshot failed checksum verification')
    return manifest


def _archive_refs(connection):
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_refs'").fetchone():
        return []
    return [dict(row) for row in connection.execute('SELECT * FROM model_refs ORDER BY rowid')]


def _has_table(connection, name):
    return connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None


def archive_entries(state_root, thread):
    """Return verified archives in the explicit stable selection index."""
    thread_root = Path(state_root) / thread_id(thread)
    if not thread_root.exists():
        return []
    _safe_private_dir(thread_root)
    marker = _marker(thread_root / 'binding.json')
    if marker is None:
        return []
    result = []
    total = 0
    for entry in marker['archives']:
        archive = _archive_dir(thread_root, entry['epoch'])
        manifest = _archive_manifest(archive)
        if _sha(_canonical(manifest)) != entry['manifest_sha256']:
            raise ValueError('owner archive failed stable marker checksum verification')
        total += manifest['source_tree']['bytes']
        if total > MAX_ARCHIVE_HISTORY_BYTES:
            raise ValueError('verified owner archive history exceeds its aggregate byte bound')
        _verify_archive_source(archive, manifest['source_tree'])
        result.append((entry['epoch'], archive, manifest))
    return result


def historical_refs(state_root, thread, kind=None, *, limit=50, offset=0, page=False):
    """Read archived model references only; records carry explicit archive identity."""
    if kind is not None and kind not in REF_PREFIX:
        raise ValueError('unknown model reference kind')
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_HISTORY_PAGE:
        raise ValueError('historical reference page size must be from 1 through 50')
    if isinstance(offset, bool) or not isinstance(offset, int) or not 0 <= offset <= 100000:
        raise ValueError('historical reference offset is outside its bound')
    result = []
    total = 0
    entries = archive_entries(state_root, thread)
    for epoch, archive, manifest in reversed(entries):
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            if not _has_table(connection, 'model_refs'):
                continue
            sql = 'SELECT * FROM model_refs' + (' WHERE kind=?' if kind else '') + ' ORDER BY rowid DESC'
            rows = connection.execute(sql, (kind,) if kind else ())
            for row in rows:
                total += 1
                if offset <= total - 1 < offset + limit:
                    result.append({**dict(row), '_archive_epoch': epoch,
                        '_archive_manifest': manifest, '_caller_binding': manifest['binding']})
        except sqlite3.Error as error:
            raise ValueError('archived reference history is incomplete') from error
        finally:
            connection.close()
    if not page and (offset != 0 or total > limit):
        raise ValueError('archived references exceed one bounded page; request an explicit offset page')
    return result


def historical_ref(state_root, thread, kind, ref):
    """Find one explicit archived identity, returning None when it is not historical."""
    for epoch, archive, manifest in archive_entries(state_root, thread):
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            if not _has_table(connection, 'model_refs'):
                continue
            row = connection.execute('SELECT * FROM model_refs WHERE kind=? AND ref=?', (kind, ref)).fetchone()
            if row:
                return {**dict(row), '_archive_epoch': epoch,
                    '_archive_manifest': manifest, '_caller_binding': manifest['binding']}
        finally:
            connection.close()
    return None


def historical_label_exists(state_root, thread, kind, label):
    if not isinstance(label, str):
        return False
    for _epoch, archive, manifest in archive_entries(state_root, thread):
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            if not _has_table(connection, 'model_refs'):
                continue
            if connection.execute('SELECT 1 FROM model_refs WHERE kind=? AND label=? LIMIT 1',
                                  (kind, label)).fetchone():
                return True
        finally:
            connection.close()
    return False


def archived_event_ids(state_root, thread):
    values = set()
    for _epoch, archive, manifest in archive_entries(state_root, thread):
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            values.update(row[0] for row in connection.execute('SELECT id FROM events'))
        finally:
            connection.close()
    return values


def historical_incoming(state_root, thread, client_ids, turn_id=None):
    """True when a native callback points to an event in any archived owner."""
    wanted = {value for value in client_ids if isinstance(value, str)}
    if turn_id is not None:
        wanted.add(turn_id)
    if not wanted:
        return False
    for _epoch, archive, manifest in archive_entries(state_root, thread):
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='events'").fetchone():
                continue
            for row in connection.execute('SELECT id,turn_id FROM events'):
                if row['id'] in wanted or row['turn_id'] in wanted:
                    return True
        finally:
            connection.close()
    return False


def reference_highwater(state_root, thread):
    """Return per-kind high-water IDs across the selected journal and all archives."""
    thread = thread_id(thread)
    result = {kind: 0 for kind in REF_PREFIX}
    thread_root = Path(state_root) / thread
    if thread_root.exists():
        state, _epoch, _binding, _marker_value = selected_state(thread_root)
        journal = state / 'journal.sqlite3'
        if journal.is_file():
            with _state_snapshot(state) as connection:
                for kind, value in _ref_highwater(connection).items():
                    result[kind] = max(result[kind], value)
    for _epoch, archive, manifest in archive_entries(state_root, thread):
        with _snapshot_reader(archive / manifest['snapshot']['file']) as connection:
            for kind, value in _ref_highwater(connection).items():
                result[kind] = max(result[kind], value)
    return result


def ensure_reference_counters(db, highwater=None):
    db.execute('''CREATE TABLE IF NOT EXISTS model_ref_counters (
        kind TEXT PRIMARY KEY, next_value INTEGER NOT NULL CHECK(next_value>=0))''')
    values = highwater or {kind: 0 for kind in REF_PREFIX}
    for kind in REF_PREFIX:
        row = db.execute('SELECT next_value FROM model_ref_counters WHERE kind=?', (kind,)).fetchone()
        floor = max(values.get(kind, 0), _current_ref_max(db, kind))
        if row is None:
            db.execute('INSERT INTO model_ref_counters VALUES (?,?)', (kind, floor))
        elif row[0] < floor:
            db.execute('UPDATE model_ref_counters SET next_value=? WHERE kind=?', (floor, kind))


def _current_ref_max(db, kind):
    row = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_refs'").fetchone()
    if not row:
        return 0
    maximum = 0
    prefix = REF_PREFIX[kind]
    for result in db.execute('SELECT ref FROM model_refs WHERE kind=?', (kind,)):
        match = re.fullmatch(re.escape(prefix) + r'(\d+)', result[0])
        if match:
            maximum = max(maximum, int(match.group(1)))
    return maximum


def allocate_reference(db, kind):
    """Allocate a bare reference after every persisted historical value."""
    if kind not in REF_PREFIX:
        raise ValueError('unknown model reference kind')
    ensure_reference_counters(db)
    row = db.execute('SELECT next_value FROM model_ref_counters WHERE kind=?', (kind,)).fetchone()
    value = max(row[0], _current_ref_max(db, kind)) + 1
    db.execute('UPDATE model_ref_counters SET next_value=? WHERE kind=?', (value, kind))
    return REF_PREFIX[kind] + str(value)


def history_summary(state_root, thread):
    """Short default-recap disclosure for old generations and unknown outcomes."""
    thread = thread_id(thread)
    thread_root = Path(state_root) / thread
    if not thread_root.exists():
        return 'No archived owner history is registered for this exact conversation.'
    try:
        state, _epoch, _binding, marker = selected_state(thread_root)
        archives = archive_entries(state_root, thread)
        summary = _history_summary(thread_root, state, marker, archives)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
        return 'Archived owner history is incomplete or unavailable; outcomes remain unknown (' + str(error)[:200] + ').'
    unknown = summary['acknowledged_unknown_outcomes']
    completeness = 'complete' if summary['complete'] else 'incomplete; missing receipts remain unknown'
    return (f"Archived history: {summary['archives']} owner incarnation(s), {summary['jobs']} registrations, "
            f"{summary['events']} events; scan {completeness}. "
            f"Acknowledged events with missing native completion: {unknown}; these outcomes remain unknown.")


def message_receipt_record(state_root, sender_thread, row, *, endpoint_cache=None, _sender_verified=False):
    """Return typed receipt evidence after verifying both frozen message endpoints."""
    sender_thread = thread_id(sender_thread)
    if not isinstance(row, dict):
        row = dict(row)
    if _sender_verified:
        ref_row = row
        sender_binding = _valid_binding(row.get('_caller_binding'))
    elif row.get('_archive_epoch'):
        ref_row = historical_ref(state_root, sender_thread, 'message', row.get('ref'))
        if ref_row is None or ref_row['identity'] != row.get('identity'):
            raise ValueError('historical outgoing reference no longer resolves to its archived sender')
        sender_binding = _valid_binding(ref_row['_caller_binding'])
    else:
        sender_state, _epoch, sender_binding, _selection = selected_state(Path(state_root) / sender_thread)
        with _state_snapshot(sender_state) as sender_db:
            current_ref = sender_db.execute('SELECT * FROM model_refs WHERE kind=? AND ref=?',
                                            ('message', row.get('ref'))).fetchone()
            if not current_ref or current_ref['identity'] != row.get('identity'):
                raise ValueError('current outgoing reference does not resolve in the selected sender journal')
            ref_row = dict(current_ref)
    if sender_binding['thread_id'] != sender_thread:
        raise ValueError('sender authority does not match the current conversation')
    frozen = json.loads(ref_row['binding'])
    recipient_binding = _valid_binding(frozen)
    target_thread = recipient_binding['thread_id']
    cache = endpoint_cache if endpoint_cache is not None else {}
    if target_thread not in cache:
        target_root = Path(state_root) / target_thread
        active = None
        archives = []
        if target_root.exists() or target_root.is_symlink():
            state, epoch, active_binding, marker = selected_state(target_root)
            active = (state, epoch, active_binding)
            if active_binding != recipient_binding:
                archives = archive_entries(state_root, target_thread)
        cache[target_thread] = (active, archives)
    active, archives = cache[target_thread]
    endpoint = None
    if active and active[2] == recipient_binding:
        endpoint = ('active', active[0], None, active[1])
    elif active or archives:
        try:
            for epoch, archive, manifest in archives:
                if manifest['binding'] == recipient_binding:
                    endpoint = ('archive', archive, manifest, epoch)
                    break
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ValueError('recipient receipt archive is incomplete or unverifiable') from error
    receipt = None
    response = None
    destination_job = None
    if endpoint:
        kind, directory, manifest, recipient_epoch = endpoint
        @contextmanager
        def endpoint_db():
            if kind == 'archive':
                connection = _open_snapshot(directory / manifest['snapshot']['file'])
                try:
                    yield connection
                finally:
                    connection.close()
            else:
                with _state_snapshot(directory) as connection:
                    yield connection
        with endpoint_db() as recipient_db:
            receipt = recipient_db.execute('SELECT * FROM events WHERE id=?', (ref_row['identity'],)).fetchone()
            if receipt:
                destination_job = recipient_db.execute('SELECT * FROM jobs WHERE id=?', (receipt['job_id'],)).fetchone()
                if recipient_db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_responses'").fetchone():
                    response = recipient_db.execute('SELECT outcome,detail FROM model_responses WHERE event_id=?',
                                                    (ref_row['identity'],)).fetchone()
    if not receipt or not destination_job:
        raise ValueError('recipient receipt unavailable; delivery and handling remain unknown; do not resend')
    recipient_spec = json.loads(destination_job['spec'])
    if destination_job['kind'] != 'message' or recipient_spec.get('sender') != sender_binding:
        raise ValueError('this caller does not own this message receipt; stored purpose is withheld')
    if receipt['kind'] != 'message' or receipt['job_id'] != destination_job['id']:
        raise ValueError('recipient message receipt is corrupt or mismatched')
    return {'ref': ref_row['ref'], 'identity': ref_row['identity'],
            'sender_binding': sender_binding, 'recipient_binding': recipient_binding,
            'recipient_epoch': recipient_epoch, 'recipient_archived': kind == 'archive',
            'event': dict(receipt), 'job': dict(destination_job), 'spec': recipient_spec,
            'response': dict(response) if response else None}


def historical_message_receipt(state_root, sender_thread, row):
    """Read an outgoing receipt at its exact frozen sender and recipient bindings."""
    record = message_receipt_record(state_root, sender_thread, row)
    receipt, job, spec, response = (record['event'], record['job'],
                                    record['spec'], record['response'])
    text = (f"{record['ref']}: intent {job['intent']}; {receipt['delivery']}; "
            f"withdrawal {receipt['withdraw_state']}; turn {receipt['turn_outcome'] or 'not yet known'}; "
            f"handling {'acknowledged' if receipt['acknowledged'] else 'not acknowledged'}")
    if response:
        text += f"; recipient {response['outcome']}: {str(response['detail'])[:256]}"
    text += '. Receipt/acceptance does not prove an external effect.\nStored '
    text += display_label(spec.get('message_kind', 'information')) + ':\n'
    text += quote(clean_text(spec.get('prompt', ''), 512))
    return text


def _history_summary(thread_root, state, marker, archives):
    summary = {'archives': len(archives), 'jobs': 0, 'events': 0, 'renewals': 0,
               'acknowledged_unknown_outcomes': 0, 'complete': True}
    try:
        if (Path(state) / 'journal.sqlite3').is_file():
            with _state_snapshot(state) as connection:
                current = _journal_counts(connection)
                for key, value in current.items():
                    summary[key] += value
    except (OSError, ValueError, sqlite3.Error):
        summary['complete'] = False
    for _epoch, archive, manifest in archives:
        try:
            with _snapshot_reader(archive / manifest['snapshot']['file']) as connection:
                counts = _journal_counts(connection)
                for key, value in counts.items():
                    summary[key] += value
        except (OSError, ValueError, sqlite3.Error):
            summary['complete'] = False
    return summary


def _journal_counts(connection):
    return {'jobs': connection.execute('SELECT COUNT(*) FROM jobs').fetchone()[0],
            'events': connection.execute('SELECT COUNT(*) FROM events').fetchone()[0],
            'renewals': connection.execute('SELECT COUNT(*) FROM renewals').fetchone()[0],
            'acknowledged_unknown_outcomes': connection.execute(
                "SELECT COUNT(*) FROM events WHERE delivery='native_queued' AND acknowledged=1 AND turn_outcome IS NULL").fetchone()[0]}


def _ref_highwater(connection):
    values = {kind: 0 for kind in REF_PREFIX}
    if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_refs'").fetchone():
        for row in connection.execute('SELECT kind,ref FROM model_refs'):
            prefix = REF_PREFIX.get(row['kind'])
            match = re.fullmatch(re.escape(prefix or '\0') + r'(\d+)', row['ref'])
            if match:
                values[row['kind']] = max(values[row['kind']], int(match.group(1)))
    if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_ref_counters'").fetchone():
        for row in connection.execute('SELECT kind,next_value FROM model_ref_counters'):
            if row['kind'] in values and type(row['next_value']) is int:
                values[row['kind']] = max(values[row['kind']], row['next_value'])
    return values


def _queue_snapshot(client, thread):
    cursor, seen, rows = None, set(), []
    deadline = time.monotonic() + MAX_QUEUE_SCAN_SECONDS
    for _ in range(20):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('native queue scan exceeded its total time bound')
        params = {'threadId': thread, 'limit': 100}
        if cursor is not None:
            params['cursor'] = cursor
        page = client.call('thread/queue/list', params, timeout=min(1.0, remaining))
        data = page.get('data')
        if not isinstance(data, list) or len(data) > 100:
            raise ValueError('native queue scan is malformed or incomplete')
        rows.extend(data)
        if len(rows) > 2000:
            raise ValueError('native queue scan exceeds its bound')
        if len(_canonical(rows)) > 1024 * 1024:
            raise ValueError('native queue receipt scan exceeds its byte bound')
        cursor = page.get('nextCursor')
        if cursor is None:
            return {'count': len(rows), 'sha256': _sha(_canonical(rows)), 'empty': not rows}
        if not isinstance(cursor, str) or not cursor or cursor in seen:
            raise ValueError('native queue pagination is incomplete or repeated')
        seen.add(cursor)
    raise ValueError('native queue scan exceeded its page bound')


def _process_proof(binding):
    """True if the saved exact process is gone, false if alive, None if uncertain."""
    pid = binding['pid']
    proc = Path('/proc') / str(pid)
    try:
        info = proc.stat()
    except FileNotFoundError:
        return True
    except OSError:
        return None
    if info.st_uid != binding['uid']:
        return None
    try:
        tail = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
        current = {'pid': pid, 'start_ticks': tail[19], 'executable': os.readlink(proc / 'exe')}
    except (OSError, IndexError):
        return None
    return current != {key: binding[key] for key in ('pid', 'start_ticks', 'executable')}


def _tracked_coordinator(state_dir):
    """Validate a persisted coordinator identity and prove its exact process state."""
    path = Path(state_dir) / 'coordinator.json'
    if path.is_symlink():
        raise ValueError('tracked coordinator metadata must not be a symlink')
    if not path.exists():
        return {'state': 'absent'}
    record = _read_json(path)
    required = {'pid', 'start_ticks', 'executable', 'generation', 'state'}
    if not isinstance(record, dict) or set(record) != required:
        raise ValueError('tracked coordinator metadata is corrupt or incomplete')
    if (isinstance(record['pid'], bool) or not isinstance(record['pid'], int) or record['pid'] <= 0 or
            not isinstance(record['start_ticks'], str) or not record['start_ticks'] or
            not isinstance(record['executable'], str) or not record['executable'] or
            not isinstance(record['state'], str) or record['state'] != str(Path(state_dir).resolve())):
        raise ValueError('tracked coordinator state path or process identity is invalid')
    try:
        if str(uuid.UUID(record['generation'])) != record['generation']:
            raise ValueError
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError('tracked coordinator generation identity is invalid') from error
    identity = {'pid': record['pid'], 'uid': os.getuid(),
                'start_ticks': record['start_ticks'], 'executable': record['executable']}
    proof = _process_proof(identity)
    return {'state': 'unknown' if proof is None else 'gone' if proof else 'alive',
            'record': record}


def _held_lock(path):
    path = Path(path)
    if not path.exists():
        return False
    if path.is_symlink():
        raise ValueError(f'{path.name} must not be a symlink')
    fd = os.open(path, os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0))
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    finally:
        os.close(fd)


def _open_state_processes(state_dir):
    """Return positive open-state evidence and disclose an incomplete FD census."""
    prefix = str(Path(state_dir).resolve()) + os.sep
    proc_root = Path('/proc')
    unreadable = 0
    reasons = []
    try:
        processes = []
        for process in proc_root.iterdir():
            if process.name.isdecimal():
                processes.append(process)
                if len(processes) > 4096:
                    unreadable += 1
                    reasons.append('process_limit')
                    break
    except OSError:
        return {'holder': None, 'partial': True, 'unreadable_processes': 1,
                'reasons': ['process_inventory_unavailable']}
    current = os.getpid()
    deadline = time.monotonic() + MAX_PROC_SCAN_SECONDS
    for process in processes:
        if time.monotonic() >= deadline:
            unreadable += 1
            reasons.append('deadline')
            break
        if not process.name.isdecimal() or int(process.name) == current:
            continue
        try:
            if process.stat().st_uid != os.getuid():
                continue
        except FileNotFoundError:
            continue
        except OSError:
            unreadable += 1
            reasons.append('process_identity_unreadable')
            continue
        try:
            fds = []
            for fd in (process / 'fd').iterdir():
                fds.append(fd)
                if len(fds) > 512:
                    unreadable += 1
                    reasons.append('descriptor_limit')
                    fds = []
                    break
        except FileNotFoundError:
            continue
        except OSError:
            unreadable += 1
            reasons.append('descriptor_inventory_unreadable')
            continue
        for fd in fds:
            try:
                target = os.readlink(fd)
            except FileNotFoundError:
                continue
            except OSError:
                unreadable += 1
                reasons.append('descriptor_target_unreadable')
                continue
            if target.startswith(prefix):
                return {'holder': process.name, 'partial': unreadable > 0,
                        'unreadable_processes': unreadable, 'reasons': sorted(set(reasons))}
    return {'holder': None, 'partial': unreadable > 0,
            'unreadable_processes': unreadable, 'reasons': sorted(set(reasons))}


def _has_unsettled_work(connection):
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if tables - {'jobs', 'events', 'renewals', 'model_refs', 'model_responses', 'model_ref_counters', 'turn_receipts', 'sqlite_sequence'}:
        raise ValueError('legacy journal contains unclassified tables')
    jobs = [dict(row) for row in connection.execute('SELECT * FROM jobs')]
    renewals = [dict(row) for row in connection.execute('SELECT * FROM renewals')]
    events = [dict(row) for row in connection.execute('SELECT * FROM events')]
    problems = []
    if any(row['intent'] not in ('active', 'replacing', 'expired', 'cancelled', 'replaced', 'completed') for row in jobs):
        problems.append('unclassified_registration_state')
    if any(row['intent'] in ('active', 'replacing') for row in jobs):
        problems.append('active_or_replacing_registration')
    source_states = ('none', 'pending', 'starting', 'running', 'stop_requested',
                     'stopped', 'completed', 'lost', 'error')
    if any(row['source_state'] not in source_states for row in jobs):
        problems.append('unclassified_source_state')
    if any(row['source_state'] in ('starting', 'running', 'stop_requested', 'lost') for row in jobs):
        problems.append('unresolved_source_owner')
    if any(row['state'] not in ('pending', 'done', 'expired', 'cancelled', 'interrupted') for row in renewals):
        problems.append('unclassified_renewal_state')
    if any(row['state'] == 'pending' for row in renewals):
        problems.append('pending_renewal')
    start_states = ('pending', 'starting', 'started', 'unknown', 'not_in_queue', 'withdrawn')
    turn_outcomes = (None, 'completed', 'failed', 'interrupted')
    if any(event['delivery'] not in ('pending', 'dispatching', 'uncertain', 'native_queued', 'cancelled', 'expired')
           or event.get('withdraw_state', 'none') not in ('none', 'unknown', 'consumed', 'not_pending', 'withdrawn')
           or event.get('start_state') not in start_states
           or event.get('turn_outcome') not in turn_outcomes
           or type(event['acknowledged']) is not int or event['acknowledged'] not in (0, 1)
           for event in events):
        problems.append('unclassified_event_state')
    for event in events:
        if event['delivery'] in ('pending', 'dispatching', 'uncertain'):
            problems.append('unresolved_admission')
            break
    if any(event.get('withdraw_state') == 'unknown' for event in events):
        problems.append('unresolved_withdrawal')
    if any(event['delivery'] == 'native_queued' and not event['acknowledged'] for event in events):
        problems.append('unacknowledged_queued_input')
    # An acknowledged event may correctly retain turn_outcome=NULL. That outcome
    # is displayed as unknown but does not alone make clean rollover unsafe.
    return sorted(set(problems)), {'jobs': len(jobs), 'events': len(events), 'renewals': len(renewals),
                                  'acknowledged_unknown_outcomes': sum(
                                      event['delivery'] == 'native_queued' and event['acknowledged'] and
                                      event.get('turn_outcome') is None for event in events)}


def _install_ref_tables(state_dir, highwater):
    from .store import Store
    store = Store(Path(state_dir))
    try:
        store.db.executescript('''
            CREATE TABLE IF NOT EXISTS model_refs (
                kind TEXT NOT NULL, ref TEXT NOT NULL, identity TEXT NOT NULL,
                binding TEXT, label TEXT NOT NULL DEFAULT '',
                PRIMARY KEY(kind,ref), UNIQUE(kind,identity));
            CREATE TABLE IF NOT EXISTS model_responses (
                event_id TEXT PRIMARY KEY REFERENCES events(id),
                turn_id TEXT NOT NULL, outcome TEXT NOT NULL, detail TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS model_ref_counters (
                kind TEXT PRIMARY KEY, next_value INTEGER NOT NULL CHECK(next_value>=0));
        ''')
        with store.transaction():
            for kind, value in highwater.items():
                row = store.db.execute('SELECT next_value FROM model_ref_counters WHERE kind=?', (kind,)).fetchone()
                if row is None:
                    store.db.execute('INSERT INTO model_ref_counters VALUES (?,?)', (kind, value))
                elif row['next_value'] < value:
                    store.db.execute('UPDATE model_ref_counters SET next_value=? WHERE kind=?', (value, kind))
    finally:
        store.close()


def _validate_prepared_tree(thread_root, old_binding, source_tree):
    """Validate any marker-last artifacts left by an interrupted apply."""
    thread_root = Path(thread_root)
    selected_ids = set()
    archives = _managed_dir(thread_root, 'archives')
    incarnations = _managed_dir(thread_root, 'incarnations')
    if archives is not None:
        children = list(archives.iterdir())
        if len(children) > MAX_ARCHIVES:
            raise ValueError('uncommitted owner archive count exceeds its bound')
        for child in children:
            if child.is_symlink() or not child.is_dir():
                raise ValueError('uncommitted owner archive contains an unsafe entry')
            _safe_private_dir(child)
            manifest = _archive_manifest(child)
            prep = _read_json(child / 'preparation.json')
            if (manifest['binding'] != old_binding or manifest['source_tree']['sha256'] != source_tree['sha256'] or
                    prep.get('format') != 'codex-plus-owner-preparation-v1' or
                    prep.get('source_digest') != source_tree['sha256'] or
                    prep.get('preview_token') != manifest['preview_token'] or
                    prep.get('archive_epoch') != manifest['epoch'] or
                    prep.get('archive_sha256') != _sha(_canonical(manifest)) or
                    prep.get('selected_epoch') != manifest['prepared_for']['selected_epoch'] or
                    prep.get('binding') != manifest['prepared_for']['current_binding']):
                raise ValueError('uncommitted owner preparation does not match the current legacy state')
            _verify_archive_source(child, source_tree)
            epoch = manifest['prepared_for']['selected_epoch']
            new_state = _managed_dir(thread_root, 'incarnations')
            if new_state is not None and (new_state / epoch).exists():
                _verify_state_epoch(new_state / epoch, epoch, manifest['prepared_for']['current_binding'])
            selected_ids.add(epoch)
    if incarnations is not None:
        children = list(incarnations.iterdir())
        if len(children) > MAX_ARCHIVES:
            raise ValueError('uncommitted owner epoch count exceeds its bound')
        for child in children:
            if child.is_symlink() or not child.is_dir():
                raise ValueError('uncommitted owner epoch contains an unsafe entry')
            if child.name not in selected_ids:
                raise ValueError('uncommitted owner epoch has no matching verified archive')
    # An archive can be complete before the new state is renamed into place.


class Recovery:
    """Bootstrap owner tools; caller identity and active turn are verified natively."""

    def __init__(self, root, requested, context, *, client_factory=Client, require_active=True):
        self.root = Path(root).absolute()
        if self.root.exists():
            _safe_private_dir(self.root)
        self.requested = requested
        self.context = dict(context)
        thread_id(self.context['thread_id'])
        if self.context.get('turn_id') is not None:
            uuid.UUID(self.context['turn_id'])
        self.require_active = require_active
        self.client = client_factory(requested, experimental=True)
        try:
            self.binding = _valid_binding(self.client.bind(self.context['thread_id']))
            if self.binding['thread_id'] != self.context['thread_id']:
                raise ValueError('native caller binding does not match the verified active thread')
            PeerReader(self.client).validate(self.binding)
            self._check_active_turn()
        except BaseException:
            self.client.close()
            raise

    def close(self):
        self.client.close()

    def __enter__(self): return self
    def __exit__(self, *args): self.close()

    def _check_active_turn(self):
        if not self.require_active:
            return None
        if not self.context.get('turn_id'):
            raise ValueError('verified native active turn metadata is required for owner recovery')
        page = self.client.call('thread/turns/list', {'threadId': self.context['thread_id'],
            'limit': 1, 'itemsView': 'summary', 'sortDirection': 'desc'}, timeout=5)
        turns = page.get('data', [])
        if not turns or turns[0].get('id') != self.context['turn_id'] or turns[0].get('status') != 'inProgress':
            raise ValueError('owner recovery requires the exact active native caller turn')
        self.active_turn = turns[0]
        return self.active_turn

    def _state_target(self, peer=None):
        caller = self.binding['thread_id']
        if peer is None:
            return caller, self.binding, 'caller'
        row = self._reference('peer', peer)
        frozen = _valid_binding(json.loads(row['binding']))
        if frozen['thread_id'] == caller:
            raise ValueError('owner_status peer selector cannot name the caller')
        current = _valid_binding(self.client.bind(frozen['thread_id']))
        PeerReader(self.client).validate(current)
        return frozen['thread_id'], current, 'recipient'

    def _reference(self, kind, ref):
        thread_root = self.root / self.binding['thread_id']
        if not thread_root.exists() and not thread_root.is_symlink():
            raise ValueError('caller has no registered state or peer reference history')
        state, epoch, frozen, marker = selected_state(thread_root)
        db = state / 'journal.sqlite3'
        if not db.is_file():
            raise ValueError('caller reference journal is unavailable')
        with _state_snapshot(state) as connection:
            row = connection.execute('SELECT * FROM model_refs WHERE kind=? AND ref=?', (kind, ref)).fetchone()
            if row:
                return dict(row)
        for entry in reversed(marker['archives'] if marker else []):
            archive = _archive_dir(self.root / self.binding['thread_id'], entry['epoch'])
            manifest = _archive_manifest(archive)
            if _sha(_canonical(manifest)) != entry['manifest_sha256']:
                raise ValueError('caller archive failed index verification')
            connection = _open_snapshot(archive / manifest['snapshot']['file'])
            try:
                row = connection.execute('SELECT * FROM model_refs WHERE kind=? AND ref=?', (kind, ref)).fetchone()
                if row:
                    return {**dict(row), '_archive_epoch': entry['epoch'],
                            '_archive_manifest': manifest, '_caller_binding': manifest['binding']}
            finally:
                connection.close()
        raise ValueError('peer reference is missing; rediscover the intended peer in the current owner incarnation')

    def _resolve_archives(self, thread_root, marker):
        if marker is None:
            return []
        rows = []
        for entry in marker['archives']:
            archive = _archive_dir(thread_root, entry['epoch'])
            manifest = _archive_manifest(archive)
            if _sha(_canonical(manifest)) != entry['manifest_sha256']:
                raise ValueError('owner archive failed stable marker checksum verification')
            _verify_archive_source(archive, manifest['source_tree'])
            rows.append((entry['epoch'], archive, manifest))
        return rows

    def _outgoing_work(self, sender_thread, sender_binding, rows, *, locks_held=False):
        """Classify every saved outgoing registration against its exact recipient receipt."""
        if not rows:
            return [], [], []
        problems, evidence, targets = [], [], set()
        prepared = []
        if len(rows) > MAX_OUTGOING_CHECKS:
            return ['outgoing_message_history_exceeds_scan_bound'], [
                {'state': 'incomplete', 'count': len(rows)}], []
        for row in rows:
            try:
                frozen = _valid_binding(json.loads(row['binding']))
                caller_binding = _valid_binding(row.get('_caller_binding'))
                if caller_binding['thread_id'] != sender_thread:
                    raise ValueError('outgoing reference belongs to another caller thread')
                if logical_binding(caller_binding) != logical_binding(self.binding):
                    raise ValueError('outgoing sender belongs to a different logical owner realm')
                targets.add(frozen['thread_id'])
                prepared.append((row, frozen, caller_binding))
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
                problems.append('outgoing_reference_binding_unknown')
                evidence.append({'ref': row.get('ref'), 'identity': row.get('identity'),
                                 'state': 'unknown', 'reason': str(error)[:160]})
        if len(targets) > MAX_OUTGOING_TARGETS:
            problems.append('outgoing_recipient_count_exceeds_bound')
            return sorted(set(problems)), evidence, sorted(targets)
        if not prepared:
            return sorted(set(problems)), evidence, sorted(targets)

        def inspect_rows():
            endpoint_cache = {}
            for row, recipient_binding, caller_binding in prepared:
                ref = row.get('ref')
                identity = row.get('identity')
                target = recipient_binding['thread_id']
                # A settled cached receipt grants history inspection, not fresh
                # peer control. Closed peers must not need cold resume merely
                # to prove that their recorded message has already settled.
                current_recipient = _valid_binding({**self.client.identity, 'thread_id': target})
                if logical_binding(recipient_binding) != logical_binding(current_recipient):
                    problems.append('outgoing_recipient_scope_changed')
                    evidence.append({'ref': ref, 'identity': identity, 'recipient_thread': target,
                                     'state': 'unknown', 'reason': 'recipient_logical_scope_changed'})
                    continue
                target_root = Path(self.root) / target
                if target_root.exists() or target_root.is_symlink():
                    try:
                        recipient_state, _epoch, saved_recipient, _marker_value = selected_state(target_root)
                        for lock_name in ('owner.lock', 'launch.lock'):
                            if _held_lock(recipient_state / lock_name):
                                raise TimeoutError('recipient coordinator or helper lock is held')
                        coordinator = _tracked_coordinator(recipient_state)
                        if coordinator['state'] in ('alive', 'unknown', 'invalid'):
                            raise TimeoutError('recipient tracked coordinator is active or uncertain')
                        process_scan = _open_state_processes(recipient_state)
                        if process_scan and process_scan.get('holder'):
                            raise TimeoutError('recipient state is open by a live process')
                        if saved_recipient == current_recipient:
                            selected_state(target_root, expected_binding=current_recipient)
                        else:
                            proof = _process_proof(saved_recipient)
                            if proof is False:
                                raise TimeoutError('previous recipient process incarnation is alive')
                            if proof is None:
                                raise TimeoutError('previous recipient process liveness is unknown')
                    except TimeoutError as error:
                        problems.append('outgoing_recipient_busy')
                        evidence.append({'ref': ref, 'identity': identity, 'recipient_thread': target,
                                         'state': 'unknown', 'reason': str(error)[:160]})
                        continue
                    except (OSError, ValueError, KeyError, TypeError) as error:
                        problems.append('outgoing_recipient_state_unknown')
                        evidence.append({'ref': ref, 'identity': identity, 'recipient_thread': target,
                                         'state': 'unknown', 'reason': str(error)[:160]})
                        continue
                try:
                    receipt = message_receipt_record(self.root, sender_thread, row,
                        endpoint_cache=endpoint_cache, _sender_verified=True)
                    event, job = receipt['event'], receipt['job']
                    status = {'ref': ref, 'identity': identity, 'recipient_thread': target,
                        'recipient_epoch': receipt['recipient_epoch'], 'intent': job['intent'],
                        'delivery': event['delivery'], 'withdraw_state': event['withdraw_state'],
                        'acknowledged': event['acknowledged'], 'turn_id': event['turn_id'],
                        'turn_outcome': event['turn_outcome'], 'response': receipt['response'],
                        'spec_sha256': _sha(_canonical(receipt['spec']))}
                    evidence.append(status)
                    if job['intent'] not in ('active', 'replacing', 'expired', 'cancelled', 'replaced', 'completed'):
                        problems.append('outgoing_registration_state_unknown')
                    if job['intent'] in ('active', 'replacing'):
                        problems.append('outgoing_active_or_replacing_registration')
                    if event['delivery'] not in ('pending', 'dispatching', 'uncertain', 'native_queued',
                                                  'cancelled', 'expired'):
                        problems.append('outgoing_event_state_unknown')
                    if event['delivery'] in ('pending', 'dispatching', 'uncertain'):
                        problems.append('outgoing_unresolved_admission')
                    if event['delivery'] == 'native_queued' and event['acknowledged'] != 1:
                        problems.append('outgoing_unacknowledged_queued_input')
                    if event['withdraw_state'] not in ('none', 'unknown', 'consumed', 'not_pending', 'withdrawn'):
                        problems.append('outgoing_withdrawal_state_unknown')
                    if event['withdraw_state'] == 'unknown':
                        problems.append('outgoing_unresolved_withdrawal')
                    if type(event['acknowledged']) is not int or event['acknowledged'] not in (0, 1):
                        problems.append('outgoing_acknowledgement_state_unknown')
                    if event['turn_outcome'] not in (None, 'completed', 'failed', 'interrupted'):
                        problems.append('outgoing_turn_outcome_unknown')
                except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
                    problems.append('outgoing_receipt_unknown')
                    evidence.append({'ref': ref, 'identity': identity, 'recipient_thread': target,
                                     'state': 'unknown', 'reason': str(error)[:160]})

        try:
            if locks_held:
                inspect_rows()
            else:
                with thread_locks(self.root, targets, timeout=0, create=False):
                    inspect_rows()
        except TimeoutError:
            problems.append('outgoing_recipient_busy')
            evidence.append({'state': 'unknown', 'reason': 'recipient_thread_lock_busy'})
        return sorted(set(problems)), evidence, sorted(targets)

    def _capture(self, thread, current_binding, role):
        thread_root = self.root / thread
        if not thread_root.exists() and not thread_root.is_symlink():
            return {'thread_root': thread_root, 'state': None, 'epoch': None, 'old_binding': None,
                    'marker': None, 'problems': ['not_registered'], 'summary': {}, 'queue': None,
                    'source_tree': None, 'token': None, 'safe': False, 'role': role,
                    'current_binding': current_binding, 'history': []}
        _safe_private_dir(thread_root)
        try:
            state, epoch, old_binding, marker = selected_state(thread_root)
        except (OSError, ValueError, KeyError, TypeError) as error:
            return {'thread_root': thread_root, 'state': None, 'epoch': None, 'old_binding': None,
                    'marker': None, 'problems': ['corrupt_or_incomplete_selection'], 'summary': {}, 'queue': None,
                    'source_tree': None, 'token': None, 'safe': False, 'role': role,
                    'current_binding': current_binding, 'detail': str(error), 'history': []}
        try:
            history = self._resolve_archives(thread_root, marker)
        except (OSError, ValueError, KeyError, TypeError) as error:
            history = []
            history_error = str(error)
        else:
            history_error = None
        late_callback, late_callback_error = False, None
        if role == 'caller':
            try:
                late_callback = self._late_archived_callback(state, marker)
            except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
                late_callback_error = str(error)
        try:
            boot_id = kernel_boot_id()
        except (OSError, ValueError):
            boot_id = None
        saved_boot_id = self._saved_boot_id(state, marker)
        boot_changed = bool(epoch != 'legacy' and saved_boot_id and boot_id and saved_boot_id != boot_id)
        boot_is_current = (epoch == 'legacy' or
                           saved_boot_id is not None and boot_id is not None and saved_boot_id == boot_id)
        if old_binding == current_binding and not boot_changed and boot_is_current:
            history_summary = _history_summary(thread_root, state, marker, history)
            return {'thread_root': thread_root, 'state': state, 'epoch': epoch, 'old_binding': old_binding,
                    'marker': marker, 'problems': ['already_current'], 'summary': {}, 'queue': None,
                    'source_tree': None, 'token': marker['last_recovery']['preview_token'] if marker and marker['last_recovery'] else None,
                    'safe': False, 'role': role, 'current_binding': current_binding, 'history': history,
                    'history_error': history_error, 'history_summary': history_summary,
                    'saved_boot_id': saved_boot_id, 'boot_id': boot_id,
                    'late_archived_callback': late_callback,
                    'late_callback_error': late_callback_error}
        problems = []
        if late_callback:
            problems.append('late_archived_callback')
        if late_callback_error:
            problems.append('archived_callback_scan_unknown')
        if logical_binding(old_binding) != logical_binding(current_binding):
            problems.append('logical_scope_changed')
        if epoch != 'legacy' and (saved_boot_id is None or boot_id is None):
            problems.append('boot_identity_unknown')
        process_gone = True if boot_changed else _process_proof(old_binding)
        if process_gone is False:
            problems.append('old_exact_process_alive')
        elif process_gone is None:
            problems.append('old_process_incarnation_unknown')
        lock_paths = [state / 'owner.lock', state / 'launch.lock']
        try:
            if any(_held_lock(path) for path in lock_paths):
                problems.append('coordinator_or_helper_lock_held')
        except OSError as error:
            problems.append('owner_lock_state_unknown')
            lock_error = str(error)
        else:
            lock_error = None
        try:
            coordinator = _tracked_coordinator(state)
        except (OSError, ValueError, TypeError, KeyError) as error:
            coordinator = {'state': 'invalid', 'detail': str(error)}
            problems.append('tracked_coordinator_metadata_invalid')
        if coordinator['state'] == 'alive':
            problems.append('tracked_coordinator_alive')
        elif coordinator['state'] == 'unknown':
            problems.append('tracked_coordinator_liveness_unknown')
        process_scan = _open_state_processes(state)
        if process_scan is None:
            process_scan = {'holder': None, 'partial': True, 'unreadable_processes': 0,
                            'reasons': ['scan_result_unknown']}
        if process_scan.get('holder'):
            problems.append('state_open_by_live_process')
        try:
            queue = _queue_snapshot(self.client, thread)
            if not queue['empty']:
                problems.append('native_queue_not_empty')
        except (OSError, ValueError, KeyError, RuntimeError, TimeoutError) as error:
            queue = {'error': str(error)}
            problems.append('native_queue_scan_incomplete')
        source_tree = None
        summary = {}
        outgoing_rows = []
        outgoing_scan_problem = None
        try:
            source_tree = _tree_manifest(state, ignore_managed=(marker is None))
            if marker is None:
                _validate_prepared_tree(thread_root, old_binding, source_tree)
            if not (state / 'journal.sqlite3').exists():
                raise ValueError('journal missing; absence cannot prove a clean owner state')
            with tempfile.TemporaryDirectory(prefix='codex-plus-owner-read-') as temporary:
                snapshot = Path(temporary) / 'journal.sqlite3'
                _snapshot_database(state, snapshot)
                connection = _open_snapshot(snapshot)
                try:
                    work_problems, summary = _has_unsettled_work(connection)
                    problems.extend(work_problems)
                    if role == 'caller' and _has_table(connection, 'model_refs'):
                        count = connection.execute("SELECT COUNT(*) FROM model_refs WHERE kind='message'").fetchone()[0]
                        if count > MAX_OUTGOING_CHECKS:
                            outgoing_scan_problem = 'outgoing_message_history_exceeds_scan_bound'
                        else:
                            outgoing_rows.extend({**dict(row), '_caller_binding': old_binding}
                                for row in connection.execute("SELECT * FROM model_refs WHERE kind='message' ORDER BY rowid"))
                finally:
                    connection.close()
            if role == 'caller' and not outgoing_scan_problem:
                for archive_epoch, archive, manifest in history:
                    with _snapshot_reader(archive / manifest['snapshot']['file']) as archived_db:
                        if not _has_table(archived_db, 'model_refs'):
                            continue
                        count = archived_db.execute("SELECT COUNT(*) FROM model_refs WHERE kind='message'").fetchone()[0]
                        if len(outgoing_rows) + count > MAX_OUTGOING_CHECKS:
                            outgoing_scan_problem = 'outgoing_message_history_exceeds_scan_bound'
                            outgoing_rows = []
                            break
                        outgoing_rows.extend({**dict(row), '_archive_epoch': archive_epoch,
                            '_archive_manifest': manifest, '_caller_binding': manifest['binding']}
                            for row in archived_db.execute("SELECT * FROM model_refs WHERE kind='message' ORDER BY rowid"))
        except (OSError, ValueError, sqlite3.Error) as error:
            problems.append('state_scan_or_journal_incomplete')
            state_error = str(error)
            if role == 'caller':
                outgoing_scan_problem = 'outgoing_message_history_incomplete'
        else:
            state_error = None
        if history_error:
            problems.append('archived_history_incomplete')
            if role == 'caller' and marker:
                outgoing_scan_problem = 'outgoing_message_history_incomplete'
        outgoing_evidence = []
        outgoing_threads = []
        if role == 'caller':
            if outgoing_scan_problem:
                problems.append(outgoing_scan_problem)
                outgoing_evidence = [{'state': 'incomplete', 'reason': outgoing_scan_problem}]
            else:
                try:
                    outgoing_problems, outgoing_evidence, outgoing_threads = self._outgoing_work(
                        thread, old_binding, outgoing_rows)
                    problems.extend(outgoing_problems)
                except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, TimeoutError) as error:
                    problems.append('outgoing_receipt_scan_incomplete')
                    outgoing_evidence = [{'state': 'incomplete', 'reason': str(error)[:160]}]
        outgoing_proof = _sha(_canonical(outgoing_evidence))
        if boot_id is None:
            problems.append('current_boot_identity_unavailable')
        preview_body = {'thread': thread, 'role': role, 'old_binding': old_binding,
                        'current_binding': current_binding, 'state_epoch': epoch,
                        'tree': source_tree['sha256'] if source_tree else None,
                        'queue': queue, 'outgoing_proof': outgoing_proof,
                        'problems': sorted(set(problems)), 'boot_id': boot_id}
        token = 'owner-preview:' + _sha(_canonical(preview_body))
        safe = not problems
        return {'thread_root': thread_root, 'state': state, 'epoch': epoch, 'old_binding': old_binding,
                'marker': marker, 'problems': sorted(set(problems)), 'summary': summary, 'queue': queue,
                'source_tree': source_tree, 'token': token, 'safe': safe, 'role': role,
                'current_binding': current_binding, 'history': history, 'history_error': history_error,
                'state_error': state_error, 'lock_error': lock_error, 'boot_id': boot_id,
                'saved_boot_id': saved_boot_id, 'boot_changed': boot_changed,
                'coordinator': coordinator, 'process_scan': process_scan,
                'outgoing_rows': outgoing_rows, 'outgoing_threads': outgoing_threads,
                'outgoing_evidence': outgoing_evidence, 'outgoing_proof': outgoing_proof,
                'late_archived_callback': late_callback, 'late_callback_error': late_callback_error,
                'preview_body': preview_body}

    def status(self, *, peer=None, incarnation=None, reference=None, category='summary', limit=20, offset=0):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_HISTORY_PAGE:
            raise ValueError('owner history page size must be from 1 through 50')
        if isinstance(offset, bool) or not isinstance(offset, int) or not 0 <= offset <= 100000:
            raise ValueError('owner history offset is outside its bound')
        self._check_active_turn()
        with thread_locks(self.root, [self.binding['thread_id']], timeout=LOCK_TIMEOUT, create=False):
            thread, current, role = self._state_target(peer)
        with thread_locks(self.root, [self.binding['thread_id'], thread], timeout=LOCK_TIMEOUT, create=False):
            captured = self._capture(thread, current, role)
        if incarnation is not None or reference is not None or category != 'summary':
            return self._history_text(captured, incarnation, reference, category, limit, offset)
        return self._status_text(captured)

    def call(self, name, args):
        if not isinstance(args, dict):
            raise ValueError('owner tool arguments must be an object')
        if name == 'owner_status':
            return self.status(**args)
        if name == 'owner_recover':
            return self.recover(**args)
        raise ValueError('unknown owner recovery operation')

    def _status_text(self, data):
        role, thread, current = data['role'], data['current_binding']['thread_id'], data['current_binding']
        if role == 'recipient':
            lines = ['Recipient owner diagnosis; no recipient write or repair was attempted.',
                     'caller_thread=' + self.binding['thread_id'], 'recipient_thread=' + thread]
        else:
            lines = ['Caller owner diagnosis.', 'caller_thread=' + thread]
        if data['problems'] == ['not_registered']:
            lines += ['state=not_registered', 'No Codex Plus owner state exists for this exact thread.']
            return '\n'.join(lines)
        if data.get('detail'):
            lines += ['state=corrupt_or_incomplete', 'detail=' + data['detail'][:400],
                      'Recovery is refused because owner history cannot be verified.']
            return '\n'.join(lines)
        old = data.get('old_binding')
        if old:
            lines += ['saved_incarnation=' + str(data['epoch']),
                      f"saved_process={old['pid']}@{old['start_ticks']} ({old['executable']})",
                      f"current_process={current['pid']}@{current['start_ticks']} ({current['executable']})",
                      'same_logical_realm=' + str(logical_binding(old) == logical_binding(current)).lower()]
        lines.append('saved_boot_identity=' + (data.get('saved_boot_id') or
                     ('unknown (legacy evidence unavailable)' if data.get('epoch') == 'legacy' else 'unknown')))
        lines.append('current_boot_identity=' + (data.get('boot_id') or 'unknown'))
        if data.get('boot_changed'):
            lines.append('The exact saved process tuple appears reused after a kernel reboot; the old process incarnation is gone.')
        if data.get('late_archived_callback'):
            lines.append('active_turn_is_archived_callback=true; this turn cannot authorize new intent or rollover.')
        if data.get('late_callback_error'):
            lines.append('archived_callback_scan=unknown: ' + data['late_callback_error'][:250])
        if data.get('summary'):
            summary = data['summary']
            lines.append(f"history_counts=jobs:{summary['jobs']}, events:{summary['events']}, renewals:{summary['renewals']}, acknowledged_unknown_turn_outcomes:{summary['acknowledged_unknown_outcomes']}")
        coordinator = data.get('coordinator')
        if coordinator:
            lines.append('tracked_coordinator=' + coordinator['state'])
            if coordinator.get('detail'):
                lines.append('tracked_coordinator_detail=' + coordinator['detail'][:250])
        process_scan = data.get('process_scan')
        if process_scan:
            completeness = 'partial' if process_scan.get('partial') else 'complete'
            lines.append(f"process_fd_scan={completeness}; unreadable={process_scan.get('unreadable_processes', 0)}; positive_holder={process_scan.get('holder') or 'none'}")
            if process_scan.get('reasons'):
                lines.append('process_fd_scan_reasons=' + ','.join(process_scan['reasons'][:4]))
        if role == 'caller' and data.get('outgoing_rows') is not None:
            classified = sum(1 for row in data.get('outgoing_evidence', []) if row.get('delivery') is not None)
            unknown = sum(1 for row in data.get('outgoing_evidence', [])
                          if row.get('delivery') == 'native_queued' and row.get('acknowledged') == 1
                          and row.get('turn_outcome') is None)
            lines.append(f"outgoing_message_receipts={len(data['outgoing_rows'])}; classified={classified}; acknowledged_unknown_turn_outcomes={unknown}")
            if unknown:
                lines.append('Acknowledged outgoing receipts with missing native completion remain unknown and are preserved; that alone does not block rollover.')
        if data.get('history_error'):
            lines.append('archive_history=unavailable: ' + data['history_error'][:300])
        if data['problems'] == ['already_current']:
            lines.append('state=already_current')
            if data.get('history_summary'):
                summary = data['history_summary']
                lines.append(f"history_summary=archives:{summary['archives']}, registrations:{summary['jobs']}, events:{summary['events']}, acknowledged_unknown_turn_outcomes:{summary['acknowledged_unknown_outcomes']}, complete:{str(summary['complete']).lower()}")
            if data.get('token'):
                lines.append('completed_preview=' + data['token'])
                lines.append('previous_recovery_receipt=' + json.dumps(data['marker']['last_recovery']['receipt'], sort_keys=True))
            lines.append('The selected state is bound to the current exact native owner.')
            return '\n'.join(lines)
        lines.append('state=' + ('clean_rollover_available' if data['safe'] else 'rollover_refused'))
        if data['problems']:
            lines.append('blockers=' + ', '.join(data['problems']))
        if data.get('summary', {}).get('acknowledged_unknown_outcomes'):
            lines.append('Acknowledged queued receipts with missing native completion remain unknown and are preserved; that alone does not block rollover.')
        if data['token']:
            lines.append('expected_preview=' + data['token'])
        if role == 'recipient':
            lines.append('This caller may inspect recipient state but cannot rotate it; run owner_status in the recipient conversation.')
        elif data['safe']:
            lines.append('Next: call owner_recover with this exact expected_preview and confirm=true. Recovery sends no native input and starts no source.')
        else:
            lines.append('Settle or clarify the listed blockers, then request a fresh owner_status preview. No reset or intent migration is available.')
        return '\n'.join(lines)

    def recover(self, *, expected_preview, confirm=False):
        if not isinstance(expected_preview, str) or not re.fullmatch(r'owner-preview:[0-9a-f]{64}', expected_preview):
            raise ValueError('expected_preview must be an owner_status preview token')
        if confirm is not True:
            raise ValueError('explicit confirm=true is required for owner rollover')
        thread = self.binding['thread_id']
        with thread_locks(self.root, [thread], timeout=LOCK_TIMEOUT, create=True):
            thread_root = self.root / thread
            _safe_private_dir(thread_root)
            current = _valid_binding(self.client.bind(thread))
            if current != self.binding:
                raise ValueError('current exact native owner changed; request owner_status again')
            self._check_active_turn()
            marker = _marker(thread_root / 'binding.json')
            state, _epoch, _binding, marker = selected_state(thread_root)
            if self._late_archived_callback(state, marker):
                raise ValueError('active caller turn belongs to an archived event; it cannot authorize owner recovery')
            if marker and marker['last_recovery'] and marker['last_recovery']['preview_token'] == expected_preview:
                if marker['binding'] != current:
                    raise ValueError('completed recovery token is stale for the current owner incarnation')
                selected_state(thread_root, expected_binding=current)
                return json.dumps(marker['last_recovery']['receipt'], sort_keys=True)
            captured = self._capture(thread, current, 'caller')
            if captured['token'] != expected_preview:
                raise ValueError('owner_status preview is stale or conflicts with current state; request a fresh preview')
            if not captured['safe']:
                raise ValueError('clean rollover is refused: ' + ', '.join(captured['problems']))
            self._check_active_turn()
            if self.client.bind(thread) != current:
                raise ValueError('native owner changed during recovery preparation')
            with thread_locks(self.root, captured['outgoing_threads'], timeout=0, create=False):
                if captured['outgoing_rows']:
                    outgoing_problems, outgoing_evidence, _threads = self._outgoing_work(
                        thread, captured['old_binding'], captured['outgoing_rows'], locks_held=True)
                    if outgoing_problems:
                        raise ValueError('outgoing recipient state changed or became unsettled: ' + ', '.join(outgoing_problems))
                    if _sha(_canonical(outgoing_evidence)) != captured['outgoing_proof']:
                        raise ValueError('recipient receipts changed after owner_status; request a fresh preview')
                def commit_check(atomic_temp=None):
                    self._check_active_turn()
                    if _valid_binding(self.client.bind(thread)) != current:
                        raise ValueError('native owner changed before stable selection; prepared state remains unselected')
                    if self._late_archived_callback(captured['state'], captured['marker']):
                        raise ValueError('active caller turn belongs to a previous archived event; no owner rollover was committed')
                    final_queue = _queue_snapshot(self.client, thread)
                    if final_queue != captured['queue'] or not final_queue['empty']:
                        raise ValueError('native queue changed after preview; prepared state remains unselected')
                    _verify_tree_unchanged(captured['state'], captured['source_tree'],
                        ignore_managed=(captured['marker'] is None),
                        ignore_paths=(atomic_temp,) if atomic_temp is not None else ())
                    if captured['outgoing_rows']:
                        final_problems, final_evidence, _threads = self._outgoing_work(
                            thread, captured['old_binding'], captured['outgoing_rows'], locks_held=True)
                        if final_problems or _sha(_canonical(final_evidence)) != captured['outgoing_proof']:
                            raise ValueError('outgoing recipient receipts changed or became uncertain before selection')
                receipt = self._prepare_rollover(captured, expected_preview, commit_check)
                return json.dumps(receipt, sort_keys=True)

    def _prepare_rollover(self, captured, preview, commit_check):
        thread_root, source_state = captured['thread_root'], captured['state']
        current, old = captured['current_binding'], captured['old_binding']
        old_epoch = captured['epoch']
        epoch = 'e-' + _sha((preview + _sha(_canonical(current))).encode())[:32]
        archive_epoch = old_epoch if old_epoch != 'legacy' else 'legacy-' + _sha(preview.encode())[:32]
        archives_dir = _managed_dir(thread_root, 'archives', create=True)
        incarnations_dir = _managed_dir(thread_root, 'incarnations', create=True)
        archive_path = archives_dir / archive_epoch
        new_state = incarnations_dir / epoch
        previous_archives = list(captured['marker']['archives']) if captured['marker'] else []
        if len(previous_archives) >= MAX_ARCHIVES:
            raise ValueError('owner archive generation bound reached; no history will be discarded')
        archive_bytes = sum(item[2]['source_tree']['bytes'] for item in captured.get('history', []))
        if archive_bytes + captured['source_tree']['bytes'] > MAX_ARCHIVE_HISTORY_BYTES:
            raise ValueError('owner archive history would exceed its aggregate byte bound; no history will be discarded')
        highwater = {kind: 0 for kind in REF_PREFIX}
        archive_digest = None
        if archive_path.exists():
            manifest = _archive_manifest(archive_path)
            if (manifest.get('preview_token') != preview or manifest['epoch'] != archive_epoch or
                    manifest['prepared_for'] != {'source_digest': captured['source_tree']['sha256'],
                        'selected_epoch': epoch, 'current_binding': current}):
                raise ValueError('conflicting prepared owner archive exists; inspect owner_status before retry')
            prep = _read_json(archive_path / 'preparation.json')
            if prep.get('archive_sha256') != _sha(_canonical(manifest)) or prep.get('preview_token') != preview:
                raise ValueError('prepared owner archive receipt is incomplete')
            _verify_archive_source(archive_path, captured['source_tree'])
            archive_digest = _sha(_canonical(manifest))
            if prep.get('selected_epoch') != epoch or prep.get('binding') != current or prep.get('source_digest') != captured['source_tree']['sha256']:
                raise ValueError('prepared owner archive conflicts with its source receipt')
            with _snapshot_reader(archive_path / manifest['snapshot']['file']) as connection:
                highwater = _ref_highwater(connection)
            archive_stage = None
        elif new_state.exists():
            raise ValueError('prepared owner state exists without its verified archive')
        else:
            staging_parent = self.root / '.owner-recovery-pending'
            staging_parent.mkdir(mode=0o700, exist_ok=True)
            _safe_private_dir(staging_parent)
            staging = staging_parent / (thread_root.name + '-' + epoch + '-' + uuid.uuid4().hex)
            staging.mkdir(mode=0o700, exist_ok=False)
            archive_stage = staging / 'archive'
            archive_stage.mkdir(mode=0o700)
            source_manifest = captured['source_tree']
            _copy_tree(source_state, archive_stage / 'source', source_manifest)
            snapshot_path = archive_stage / 'journal.snapshot.sqlite3'
            _snapshot_database(archive_stage / 'source', snapshot_path)
            snapshot_hash = _sha(snapshot_path.read_bytes())
            archive_manifest = {'format': ARCHIVE_FORMAT, 'epoch': archive_epoch,
                'binding': old, 'source_tree': source_manifest,
                'snapshot': {'file': 'journal.snapshot.sqlite3', 'sha256': snapshot_hash},
                'boot_id': self._saved_boot_id(source_state, captured['marker']),
                'preview_token': preview,
                'prepared_for': {'source_digest': source_manifest['sha256'],
                                 'selected_epoch': epoch, 'current_binding': current}}
            _atomic_json(archive_stage / 'manifest.json', archive_manifest)
            _archive_manifest(archive_stage)
            archive_digest = _sha(_canonical(archive_manifest))
            with _state_snapshot(archive_stage / 'source') as as_snapshot:
                highwater = _ref_highwater(as_snapshot)
            _verify_tree_unchanged(source_state, source_manifest, ignore_managed=(captured['marker'] is None))
            _verify_archive_source(archive_stage, source_manifest)
            prep = {'format': 'codex-plus-owner-preparation-v1', 'thread_id': current['thread_id'],
                    'source_digest': source_manifest['sha256'], 'preview_token': preview,
                    'archive_epoch': archive_epoch, 'archive_sha256': archive_digest,
                    'selected_epoch': epoch, 'binding': current}
            _atomic_json(archive_stage / 'preparation.json', prep)
            os.replace(archive_stage, archive_path)
            _fsync_dir(archives_dir)
            shutil.rmtree(staging, ignore_errors=True)
        for entry in previous_archives:
            existing_archive = _archive_dir(thread_root, entry['epoch'])
            manifest = _archive_manifest(existing_archive)
            if _sha(_canonical(manifest)) != entry['manifest_sha256']:
                raise ValueError('prior owner archive failed verification')
            with _snapshot_reader(existing_archive / manifest['snapshot']['file']) as as_snapshot:
                previous_highwater = _ref_highwater(as_snapshot)
            for kind, value in previous_highwater.items():
                highwater[kind] = max(highwater[kind], value)
        if archive_path.exists():
            with _snapshot_reader(archive_path / _archive_manifest(archive_path)['snapshot']['file']) as connection:
                for kind, value in _ref_highwater(connection).items():
                    highwater[kind] = max(highwater[kind], value)
        if new_state.exists():
            _verify_state_epoch(new_state, epoch, current, expected_boot_id=captured['boot_id'])
        else:
            staging_parent = self.root / '.owner-recovery-pending'
            staging_parent.mkdir(mode=0o700, exist_ok=True)
            _safe_private_dir(staging_parent)
            state_stage = staging_parent / (thread_root.name + '-' + epoch + '-' + uuid.uuid4().hex)
            state_stage.mkdir(mode=0o700, exist_ok=False)
            try:
                _atomic_json(state_stage / 'binding.json', current)
                _atomic_json(state_stage / 'owner-epoch.json', {'format': EPOCH_FORMAT, 'epoch': epoch,
                    'binding': current, 'boot_id': captured['boot_id'], 'created': int(time.time()),
                    'previous_epoch': old_epoch, 'archive_epoch': archive_epoch})
                _install_ref_tables(state_stage, highwater)
                _verify_state_epoch(state_stage, epoch, current, expected_boot_id=captured['boot_id'])
                os.replace(state_stage, new_state)
                _fsync_dir(incarnations_dir)
            finally:
                shutil.rmtree(state_stage, ignore_errors=True)
        receipt = {'state': 'recovered', 'caller_thread': current['thread_id'],
            'previous_epoch': archive_epoch, 'selected_epoch': epoch,
            'archive_sha256': archive_digest, 'boot_id': captured['boot_id'],
            'legacy_boot_identity': 'missing' if old_epoch == 'legacy' else 'recorded',
            'history_retained_read_only': True, 'intent_migrated': False,
            'native_input_submitted': False, 'sources_started': False}
        return self._commit_selection(captured, preview, epoch, archive_epoch, archive_digest,
                                      archive_path, new_state, commit_check, receipt=receipt)

    def _late_archived_callback(self, state, marker):
        current = self.active_turn if hasattr(self, 'active_turn') else None
        if current is None:
            current = self._check_active_turn()
        if not current:
            return False
        wanted = {item.get('clientId') for item in current.get('items', [])
                  if item.get('type') == 'userMessage' and isinstance(item.get('clientId'), str)}
        if isinstance(self.context.get('turn_id'), str):
            wanted.add(self.context['turn_id'])
        if not wanted:
            return False
        if marker:
            state_path = Path(state)
            thread_root = state_path.parent.parent if state_path.parent.name == 'incarnations' else state_path.parent
            archives = self._resolve_archives(thread_root, marker)
        else:
            archives = []
            with _state_snapshot(state) as connection:
                if _has_table(connection, 'events'):
                    for row in connection.execute('SELECT id,turn_id FROM events'):
                        if row['id'] in wanted or row['turn_id'] in wanted:
                            return True
        for _epoch, archive, manifest in archives:
            with _snapshot_reader(archive / manifest['snapshot']['file']) as connection:
                if not _has_table(connection, 'events'):
                    continue
                for row in connection.execute('SELECT id,turn_id FROM events'):
                    if row['id'] in wanted or row['turn_id'] in wanted:
                        return True
        return False

    def _commit_selection(self, captured, preview, epoch, archive_epoch, archive_digest,
                          archive_path, new_state, commit_check, receipt=None):
        current, thread_root = captured['current_binding'], captured['thread_root']
        if receipt is None:
            receipt = {'state': 'recovered', 'caller_thread': current['thread_id'],
                'previous_epoch': archive_epoch, 'selected_epoch': epoch,
                'archive_sha256': archive_digest, 'boot_id': captured['boot_id'],
                'legacy_boot_identity': 'missing' if captured['epoch'] == 'legacy' else 'recorded',
                'history_retained_read_only': True, 'intent_migrated': False,
                'native_input_submitted': False, 'sources_started': False}
        previous_archives = list(captured['marker']['archives']) if captured['marker'] else []
        previous_archives.append({'epoch': archive_epoch, 'manifest_sha256': archive_digest})
        selection = {'format': SELECTION_FORMAT, 'thread_id': current['thread_id'],
            'epoch': epoch, 'selected': 'incarnations/' + epoch, 'binding': current,
            'boot_id': captured['boot_id'],
            'archives': previous_archives,
            'last_recovery': {'preview_token': preview, 'receipt': receipt}}
        # The stable binding marker is the final commit point and remains a
        # mismatch barrier for legacy ModelAPI clients.
        def verify_prepared_state(atomic_temp=None):
            commit_check(atomic_temp)
            _verify_state_epoch(new_state, epoch, current, expected_boot_id=captured['boot_id'])
        _atomic_json(thread_root / 'binding.json', selection, before_replace=verify_prepared_state)
        _verify_selection(thread_root, selection)
        return receipt

    @staticmethod
    def _saved_boot_id(source_state, marker):
        if marker:
            epoch_path = source_state / 'owner-epoch.json'
            try:
                epoch = _read_json(epoch_path)
                if (not isinstance(epoch, dict) or epoch.get('format') != EPOCH_FORMAT or
                        epoch.get('epoch') != marker.get('epoch') or epoch.get('binding') != marker.get('binding')):
                    return None
                boot_id = _valid_boot_id(epoch.get('boot_id'))
                return boot_id if boot_id == _valid_boot_id(marker.get('boot_id')) else None
            except (OSError, ValueError, TypeError):
                return None
        return None

    def _history_text(self, captured, incarnation, reference, category, limit, offset):
        if captured.get('history_error'):
            raise ValueError('archived history unavailable; outcomes remain unknown: ' + captured['history_error'][:300])
        if category not in ('summary', 'jobs', 'events', 'references', 'handling'):
            raise ValueError('owner history category must be summary, jobs, events, references or handling')
        thread_root = captured['thread_root']
        marker = captured.get('marker')
        archives = captured.get('history', [])
        if incarnation is not None:
            archives = [entry for entry in archives if entry[0] == incarnation]
            if not archives:
                raise ValueError('selected archive incarnation is unavailable; no state was recreated')
        if reference is not None:
            if not isinstance(reference, str) or not re.fullmatch(r'[pwmt]\d{1,9}', reference):
                raise ValueError('historical reference must be an exact bare p/w/m/t reference')
            kind = REF_KIND[reference[0]]
            matches = []
            for entry in archives:
                connection = _open_snapshot(entry[1] / entry[2]['snapshot']['file'])
                try:
                    if not _has_table(connection, 'model_refs'):
                        continue
                    row = connection.execute('SELECT * FROM model_refs WHERE kind=? AND ref=?', (kind, reference)).fetchone()
                    if row:
                        matches.append((entry, dict(row)))
                finally:
                    connection.close()
            if len(matches) != 1:
                raise ValueError('historical reference is missing or ambiguous; select its archive incarnation')
            entry, row = matches[0]
            return self._history_reference(entry, row)
        if category == 'summary':
            return self._status_text(captured)
        if not archives:
            return 'No verified archived owner incarnation is available for this exact thread.'
        if len(archives) != 1 and incarnation is None:
            lines = ['Archived owner incarnations; choose incarnation explicitly for a bounded page:']
            lines.extend(f"{epoch}: owner pid {manifest['binding']['pid']}@{manifest['binding']['start_ticks']}" for epoch, _path, manifest in archives)
            return '\n'.join(lines)
        epoch, archive, manifest = archives[0]
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            rows, total = _history_rows(connection, category, limit, offset)
            refs = _archive_refs(connection)
            unknown = connection.execute("SELECT COUNT(*) FROM events WHERE delivery='native_queued' AND acknowledged=1 AND turn_outcome IS NULL").fetchone()[0]
        finally:
            connection.close()
        lines = [f'Archived incarnation {epoch}; immutable read-only snapshot.',
                 f'category={category}; showing {len(rows)} of {total}; offset={offset}; acknowledged_unknown_turn_outcomes={unknown}']
        for row in rows:
            lines.append(json.dumps(row, sort_keys=True, ensure_ascii=False)[:1000])
        if offset + len(rows) < total:
            lines.append(f'next_offset={offset + len(rows)}')
        if category == 'references' and refs:
            lines.append('Historical references are read only; controls and continuation are unavailable.')
        return '\n'.join(lines)

    def _history_reference(self, entry, row):
        epoch, archive, manifest = entry
        connection = _open_snapshot(archive / manifest['snapshot']['file'])
        try:
            result = {'incarnation': epoch, 'reference': row['ref'], 'kind': row['kind'],
                      'label': row.get('label', ''), 'identity': row['identity'], 'historical': True}
            if row['kind'] in ('watch', 'wake'):
                job = connection.execute('SELECT * FROM jobs WHERE id=?', (row['identity'],)).fetchone()
                if job:
                    result['job'] = dict(job)
                    result['events'] = [dict(event) for event in connection.execute(
                        'SELECT id,kind,delivery,withdraw_state,acknowledged,turn_outcome,turn_error FROM events WHERE job_id=? ORDER BY sequence',
                        (row['identity'],))]
            elif row['kind'] == 'message':
                event = connection.execute('SELECT * FROM events WHERE id=?', (row['identity'],)).fetchone()
                if event:
                    job = connection.execute('SELECT * FROM jobs WHERE id=?', (event['job_id'],)).fetchone()
                    result['receipt'] = {key: event[key] for key in ('delivery', 'withdraw_state', 'acknowledged', 'turn_id', 'turn_outcome', 'turn_error')}
                    if job:
                        result['intent'] = job['intent']
                        result['stored_kind'] = json.loads(job['spec']).get('message_kind', 'information')
                    if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_responses'").fetchone():
                        response = connection.execute('SELECT outcome,detail FROM model_responses WHERE event_id=?', (row['identity'],)).fetchone()
                        if response:
                            result['handling'] = dict(response)
            elif row['kind'] == 'peer':
                result['binding'] = json.loads(row['binding']) if row.get('binding') else None
        finally:
            connection.close()
        return 'Archived immutable reference; historical controls are refused.\n' + json.dumps(result, sort_keys=True, ensure_ascii=False)[:2500]


def _verify_archive_source(archive_stage, source_manifest):
    actual = _tree_manifest(Path(archive_stage) / 'source')
    if actual['entries'] != source_manifest['entries'] or actual['sha256'] != source_manifest['sha256']:
        raise ValueError('owner archive source content or modes failed verification')


def _verify_tree_unchanged(source, expected, *, ignore_managed=False, ignore_paths=()):
    actual = _tree_manifest(source, ignore_managed=ignore_managed, ignore_paths=ignore_paths)
    if actual['entries'] != expected['entries'] or actual['sha256'] != expected['sha256']:
        raise ValueError('owner source state changed after its preview')


def _verify_state_epoch(state, epoch, binding, *, expected_boot_id=None):
    _safe_private_dir(state)
    if _valid_binding(_read_json(Path(state) / 'binding.json')) != binding:
        raise ValueError('new owner epoch binding failed verification')
    data = _read_json(Path(state) / 'owner-epoch.json')
    if (not isinstance(data, dict) or data.get('format') != EPOCH_FORMAT or
            data.get('epoch') != epoch or data.get('binding') != binding):
        raise ValueError('new owner epoch evidence failed verification')
    boot_id = _valid_boot_id(data.get('boot_id'))
    if expected_boot_id is not None and boot_id != _valid_boot_id(expected_boot_id):
        raise ValueError('new owner epoch boot identity differs from the captured current boot')
    connection = sqlite3.connect('file:' + urllib.parse.quote(str(Path(state) / 'journal.sqlite3'), safe='/') + '?mode=ro&immutable=1', uri=True)
    try:
        result = connection.execute('PRAGMA integrity_check').fetchone()
        if not result or result[0] != 'ok':
            raise ValueError('new owner epoch journal failed integrity verification')
        if not {'model_refs', 'model_responses', 'model_ref_counters'}.issubset(
                {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}):
            raise ValueError('new owner epoch model reference tables are incomplete')
    finally:
        connection.close()


def _verify_selection(thread_root, marker):
    selected = _marker(Path(thread_root) / 'binding.json')
    if selected != marker:
        raise ValueError('stable owner selection failed read-back verification')
    state = Path(thread_root) / marker['selected']
    _verify_state_epoch(state, marker['epoch'], marker['binding'], expected_boot_id=marker['boot_id'])


def _history_rows(connection, category, limit, offset):
    queries = {
        'jobs': ("SELECT id,kind,intent,created,expires,due,source_state,source_detail,control_reason FROM jobs ORDER BY created DESC,id DESC",),
        'events': ("SELECT id,job_id,sequence,kind,delivery,withdraw_state,withdraw_detail,acknowledged,start_state,turn_id,turn_outcome,turn_error,detail FROM events ORDER BY created DESC,sequence DESC,id DESC",),
        'references': ("SELECT kind,ref,identity,binding,label FROM model_refs ORDER BY rowid DESC",),
        'handling': ("SELECT event_id,turn_id,outcome,detail FROM model_responses ORDER BY rowid DESC",),
    }
    sql = queries[category][0]
    if category == 'references' and not _has_table(connection, 'model_refs'):
        return [], 0
    if category == 'handling' and not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='model_responses'").fetchone():
        return [], 0
    total = connection.execute('SELECT COUNT(*) FROM (' + sql + ')').fetchone()[0]
    rows = [dict(row) for row in connection.execute(sql + ' LIMIT ? OFFSET ?', (limit, offset))]
    for row in rows:
        for key, value in tuple(row.items()):
            if key in ('detail', 'source_detail', 'control_reason', 'withdraw_detail', 'turn_error') and value:
                row[key] = str(value)[:256]
            if key == 'binding' and value:
                try:
                    binding = json.loads(value)
                    row[key] = {'thread_id': binding.get('thread_id'), 'pid': binding.get('pid'),
                                'start_ticks': binding.get('start_ticks')}
                except (ValueError, TypeError):
                    row[key] = 'invalid archived binding'
    return rows, total


@contextmanager
def _state_snapshot(state_dir):
    """Read a coherent database copy without opening or checkpointing source WAL files."""
    with tempfile.TemporaryDirectory(prefix='codex-plus-state-read-') as temporary:
        snapshot = Path(temporary) / 'journal.sqlite3'
        _snapshot_database(state_dir, snapshot)
        connection = _open_snapshot(snapshot)
        try:
            yield connection
        finally:
            connection.close()
