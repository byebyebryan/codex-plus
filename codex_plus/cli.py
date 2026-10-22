"""Source-checkout CLI and private single-owner coordinator lifecycle."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
import uuid

from .engine import Engine
from .context import existing_socket
from .native import Client
from .peers import PeerReader, DEFAULT_SIGNALS
from .store import Store, private_directory
from .presentation import compact_ref, label as display_label
from .access import resolve as source_permissions, mcp_spec, configured_mcp
from . import VERSION


def process_identity(pid: int) -> dict | None:
    try:
        root = Path('/proc') / str(pid)
        tail = (root / 'stat').read_text().rsplit(')', 1)[1].split()
        return {'pid': pid, 'start_ticks': tail[19], 'executable': os.readlink(root / 'exe')}
    except (OSError, IndexError):
        return None


def coordinator_info(root: Path) -> dict | None:
    try:
        info = json.loads((root / 'coordinator.json').read_text())
        identity = process_identity(info['pid'])
        if identity != {key: info[key] for key in ('pid', 'start_ticks', 'executable')}:
            return None
        argv = (Path('/proc') / str(info['pid']) / 'cmdline').read_bytes().split(b'\0')
        wrapper = str(Path(__file__).resolve().parents[1] / 'scripts/codex-plus-watch').encode()
        if b'serve' not in argv or str(root).encode() not in argv or info.get('state') != str(root):
            return None
        runtime_version = VERSION
        if wrapper not in argv:
            candidates = [Path(arg.decode()) for arg in argv if arg.endswith(b'/scripts/codex-plus-watch')]
            if len(candidates) != 1:
                return None
            release = candidates[0].parent.parent
            from .package import verify_install
            if not release.is_absolute() or release.stat().st_uid != os.getuid() or release.stat().st_mode & 0o022:
                return None
            runtime_version = verify_install(release)['version']
        return {**info, 'runtime_version': runtime_version}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def atomic_json(path: Path, value):
    if path.is_symlink():
        raise ValueError('private state file must not be a symlink')
    temporary = path.with_name(path.name + '.' + str(uuid.uuid4()) + '.tmp')
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def binding(root: Path) -> dict:
    path = root / 'binding.json'
    if path.is_symlink():
        raise ValueError('binding must not be a symlink')
    try:
        return json.loads(path.read_text())
    except FileNotFoundError as error:
        raise ValueError('bind this private state directory to an existing conversation first') from error


def validate_binding(root: Path) -> dict:
    frozen = binding(root)
    with Client(frozen['requested_socket'], experimental=True) as client:
        if client.bind(frozen['thread_id']) != frozen:
            raise ValueError('frozen native owner or thread changed')
        thread = client.call('thread/read', {'threadId': frozen['thread_id']})['thread']
        if thread.get('canAcceptDirectInput') is not True:
            raise ValueError('native input capability is unavailable or unknown')
    return frozen


def ensure_coordinator(root: Path):
    with (root / 'launch.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if coordinator_info(root):
            return
        wrapper = Path(__file__).resolve().parents[1] / 'scripts/codex-plus-watch'
        fd = os.open(root / 'coordinator.log', os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'ab') as log:
            child = subprocess.Popen(['rtk', 'proxy', sys.executable, '-B', str(wrapper),
                '--state', str(root), 'serve'], stdin=subprocess.DEVNULL,
                stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if coordinator_info(root):
                return
            if child.poll() is not None:
                raise RuntimeError('coordinator failed to start; inspect its private log')
            time.sleep(0.05)
        raise TimeoutError('coordinator startup receipt unavailable')


def accepted_coordinator(root: Path, result: dict) -> dict:
    """Keep durable accepted intent distinguishable from a refused operation."""
    try:
        ensure_coordinator(root)
    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
        result.update(state='registered_coordinator_unavailable', coordinator_error=str(error))
    return result


def serve(root: Path):
    with (root / 'owner.lock').open('a') as owner:
        try:
            fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('a coordinator already owns this state directory')
        store = Store(root)
        engine = Engine(store, binding(root))
        identity = process_identity(os.getpid())
        if identity is None:
            raise RuntimeError('cannot establish coordinator process identity')
        record = {**identity, 'generation': engine.generation, 'state': str(root)}
        atomic_json(root / 'coordinator.json', record)
        stopping = False

        def request_stop(signum, frame):
            nonlocal stopping
            stopping = True

        signal.signal(signal.SIGTERM, request_stop)
        signal.signal(signal.SIGINT, request_stop)
        try:
            idle_since = None
            while not stopping:
                engine.tick()
                active = any(job['intent'] in ('active', 'replacing') for job in store.jobs())
                awaiting = any(event['delivery'] == 'pending' or
                    event['delivery'] == 'native_queued' and event['expires'] > store.clock() and event['turn_outcome'] is None and
                    event['withdraw_state'] != 'withdrawn' and not event['acknowledged'] for event in store.events())
                if not active and not awaiting and not engine.sources and not engine.peer_polls and not engine.inspections and not engine.command_due:
                    idle_since = idle_since or time.monotonic()
                    if time.monotonic() - idle_since >= 10:
                        break
                else:
                    idle_since = None
                if engine.client is None:
                    time.sleep(0.2)
        finally:
            try:
                engine.close()
            finally:
                store.close()
                try:
                    current = json.loads((root / 'coordinator.json').read_text())
                    if current.get('generation') == engine.generation:
                        (root / 'coordinator.json').unlink()
                except (OSError, ValueError):
                    pass


def inspection(store: Store, job_id: str | None = None, *, watches=None) -> dict:
    info = coordinator_info(store.root)
    attempts = store.renewals()
    target = job_id
    if job_id:
        try:
            store.job(job_id)
        except ValueError:
            target = store.renewal(job_id)['parent_id']
        attempts = [row for row in attempts if row['parent_id'] == target or row['new_id'] == job_id]
    page = store.watch_page(**watches) if watches is not None else None
    jobs = page['registrations'] if page is not None else [store.job(target)] if target else store.jobs()
    if page is not None:
        selected = {job['id'] for job in jobs}
        attempts = [row for row in attempts if row['parent_id'] in selected]
    if info is None:
        for job in jobs:
            if job['source_state'] in ('starting', 'running', 'stop_requested'):
                job['last_source_state'] = job['source_state']
                job['source_state'] = 'unknown'
    return {'coordinator': {'state': 'running' if info else 'offline',
            'generation': info['generation'] if info else None},
        'destination': binding(store.root), 'registrations': jobs,
        'events': [event for job in jobs for event in store.recent_events(job['id'])] if page is not None else store.events(target),
        'renewals': attempts, 'page': {k: v for k, v in page.items() if k != 'registrations'} if page is not None else None,
        'source_receipts_may_be_stale': info is None}


def shutdown_preview(store: Store) -> dict:
    affected = [job for job in store.jobs() if job['intent'] in ('active', 'replacing')]
    admitted = [event for event in store.events() if event['delivery'] in
        ('dispatching', 'native_queued', 'uncertain') and not event['acknowledged'] and
        event['turn_outcome'] not in ('completed', 'failed', 'interrupted')]
    return {'needs_confirmation': bool(affected or admitted),
        'affected': [{'id': job['id'], 'kind': job['kind'], 'source_state': job['source_state']}
                     for job in affected],
        'in_flight_or_admitted_events': admitted,
        'native_conversation_owner_will_be_preserved': True}


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--state', type=Path, required=True,
                        help='Private directory for one existing native conversation')
    commands = result.add_subparsers(dest='operation', required=True)
    bind = commands.add_parser('bind', help='Freeze a positively loaded exact thread and owner')
    bind.add_argument('--socket', help='Requested Unix socket path or unix://PATH')
    bind.add_argument('--thread', help='Exact UUID; defaults to validated CODEX_THREAD_ID')
    for name in ('watch_start', 'renew'):
        command = commands.add_parser(name)
        if name == 'renew':
            command.add_argument('--id', required=True)
        command.add_argument('--cwd')
        command.add_argument('--duration', type=float, default=120)
        command.add_argument('--limit', type=int, default=2)
        command.add_argument('--followup', default='Inspect this observation under the existing request.')
        command.add_argument('--label', help='Readable watch context; does not change native identity')
        command.add_argument('--snapshot-fields', help='Comma-separated top-level JSON projection fields')
        command.add_argument('--quiet-initial', action='store_true')
        command.add_argument('--notify-end', action='store_true')
        command.add_argument('--peer', help='Exact independent peer UUID in the same daemon; replaces command source')
        command.add_argument('--interval', type=float)
        command.add_argument('--signals', default=','.join(DEFAULT_SIGNALS))
        command.add_argument('--turn-limit', type=int, default=3)
        command.add_argument('--source-access', choices=('session', 'read_only'), default='session')
        command.add_argument('--network-access', choices=('inherit', 'off', 'required'), default='inherit')
        command.add_argument('--mcp-server')
        command.add_argument('--mcp-tool')
        command.add_argument('--mcp-arguments', default='{}')
        command.add_argument('--command-interval', type=float)
        command.add_argument('command', nargs=argparse.REMAINDER)
    wake = commands.add_parser('wake_schedule')
    wake.add_argument('--after', type=float, required=True)
    wake.add_argument('--duration', type=float, help='Expiry from registration; default delay plus up to 120 seconds')
    wake.add_argument('--prompt', required=True)
    message = commands.add_parser('peer_send', help='Send one correlated input to this state directory destination')
    message.add_argument('--message', required=True)
    message.add_argument('--duration', type=float, default=120)
    message.add_argument('--kind', choices=('information', 'request'), default='information')
    message.add_argument('--sender', help='Exact independent sender UUID; revalidated before delivery')
    for name in ('status', 'cancel', 'ack', 'recover'):
        commands.add_parser(name).add_argument('id')
    commands.add_parser('list')
    stop = commands.add_parser('shutdown')
    stop.add_argument('--confirm', action='store_true', help='Stop only this coordinator and its owned registrations')
    commands.add_parser('serve', help='Run the coordinator in the foreground')
    return result


def main(argv=None, *, before_write=None) -> int:
    args = parser().parse_args(argv)
    os.umask(0o077)
    root = private_directory(args.state)
    if args.operation == 'serve':
        serve(root)
        return 0
    if args.operation == 'bind':
        thread_id = args.thread or os.environ.get('CODEX_THREAD_ID')
        if not thread_id:
            raise ValueError('exact thread UUID is required')
        uuid.UUID(thread_id)
        requested = existing_socket(args.socket, run=subprocess.run)
        with Client(requested, experimental=True) as client:
            frozen = client.bind(thread_id)
            thread = client.call('thread/read', {'threadId': thread_id})['thread']
            if thread.get('canAcceptDirectInput') is not True:
                raise ValueError('direct input capability unavailable')
        existing = root / 'binding.json'
        if existing.exists() and binding(root) != frozen:
            raise ValueError('state is already bound; use a separate private directory for another target')
        atomic_json(existing, frozen)
        print(json.dumps({'state': 'bound', 'destination': frozen}))
        return 0
    store = Store(root)
    try:
        if args.operation in ('watch_start', 'renew'):
            frozen = validate_binding(root)
            command = args.command[1:] if args.command[:1] == ['--'] else args.command
            if not command and not args.peer and not args.mcp_server:
                raise ValueError('source argv is required after --')
            if args.peer and args.mcp_server:
                raise ValueError('choose one observation source')
            if (args.peer or args.mcp_server) and args.command_interval is not None:
                raise ValueError('--command-interval applies only to command sources')
            spec = {'duration': args.duration,
                'event_limit': args.limit, 'followup': args.followup,
                'snapshot_fields': args.snapshot_fields.split(',') if args.snapshot_fields else None,
                'quiet_initial': args.quiet_initial, 'notify_end': args.notify_end}
            if args.label:
                spec['label'] = args.label
            if args.peer:
                if command or args.cwd:
                    raise ValueError('choose --peer or a command/cwd source')
                with Client(frozen['requested_socket'], experimental=True) as client:
                    peer = PeerReader(client).resolve(target=args.peer, caller=frozen['thread_id'])
                if {key: value for key, value in peer.items() if key != 'thread_id'} != {
                        key: value for key, value in frozen.items() if key != 'thread_id'}:
                    raise ValueError('peer owner changed before registration')
                spec.update(peer=peer, interval=args.interval if args.interval is not None else 5,
                            signals=args.signals.split(','), turn_limit=args.turn_limit)
            elif args.mcp_server:
                if command or args.cwd or args.snapshot_fields or args.peer:
                    raise ValueError('choose a command, peer or scheduled MCP inspection')
                if args.source_access != 'session' or args.network_access != 'inherit':
                    raise ValueError('command access choices do not apply to MCP inspection')
                spec.update(mcp=mcp_spec(args.mcp_server, args.mcp_tool, json.loads(args.mcp_arguments)),
                    interval=args.interval if args.interval is not None else 30)
                with Client(frozen['requested_socket'], experimental=True) as client:
                    configured_mcp(client, frozen, spec['mcp'])
            else:
                if args.interval is not None:
                    raise ValueError('use --command-interval for a periodic command, or provide a continuing observer script')
                spec.update(command=command, cwd=str(Path(args.cwd or os.getcwd()).resolve()))
                if args.command_interval is not None:
                    spec['command_interval'] = args.command_interval
                with Client(frozen['requested_socket'], experimental=True) as client:
                    spec['execution'] = source_permissions(client, frozen, spec['cwd'],
                        args.source_access, args.network_access)
            active = coordinator_info(root)
            if active and active['runtime_version'] != VERSION:
                raise ValueError('an older runtime owns this conversation\'s supervision; settle that owned work before registering or renewing source capabilities')
            if args.operation == 'watch_start':
                if before_write: before_write()
                job_id = store.create('watch', spec)
            else:
                # Startup reconciles a previous owner before accepting renewal.
                ensure_coordinator(root)
                if before_write: before_write()
                job_id = store.request_renewal(args.id, spec)
            attempt = store.renewal(job_id) if args.operation == 'renew' else None
            result = {'id': job_id, 'state': 'registered' if attempt is None else 'replacement_' + attempt['state'],
                'renewal': attempt,
                'predecessor': args.id if args.operation == 'renew' else None,
                'destination': binding(root), 'effective_bounds': {
                    'duration': args.duration, 'source_events': args.limit, 'record_bytes': 4096,
                    'stdout_bytes': 65536, 'stderr_bytes': 16384, 'lifecycle_notices': int(args.notify_end)},
                'source_policy': ({'type': 'passivePeerRpc', 'observed_peer': peer,
                                   'resumes_peer': False} if args.peer else
                                  {'type': 'nativeModelInspection', 'server': spec['mcp']['server'],
                                   'tool': spec['mcp']['tool'], 'uses_model_turn': True} if spec.get('mcp') else
                                  spec['execution']['request'])}
            print(json.dumps(accepted_coordinator(root, result)))
        elif args.operation == 'peer_send':
            frozen = validate_binding(root)
            with Client(frozen['requested_socket'], experimental=True) as client:
                PeerReader(client).validate(frozen)
                sender = PeerReader(client).resolve(target=args.sender, caller=frozen['thread_id']) if args.sender else None
                sender_label = display_label(client.call('thread/read', {'threadId': args.sender})['thread'].get('name')) if sender else None
            spec = {'duration': args.duration, 'prompt': args.message,
                    'followup': args.message, 'message_kind': args.kind}
            if sender:
                spec.update(sender=sender, sender_label=sender_label)
            if before_write: before_write()
            with store.transaction():
                job_id = store.create('message', spec)
                event_id = store.emit(job_id, args.message, 'message')
                if event_id is None:
                    raise ValueError('message lease ended before registration completed')
            result = {'id': job_id, 'event_id': event_id, 'state': 'registered',
                      'destination': frozen, 'admission_is_not_handling': True}
            print(json.dumps(accepted_coordinator(root, result)))
        elif args.operation == 'wake_schedule':
            from .store import wake_duration
            duration = wake_duration(args.after, args.duration)
            validate_binding(root)
            if before_write: before_write()
            job_id = store.create('wake', {'after': args.after, 'duration': duration,
                'prompt': args.prompt, 'followup': args.prompt})
            print(json.dumps(accepted_coordinator(root, {'id': job_id, 'state': 'registered', 'after': args.after,
                'duration': duration, 'event_limit': 1, 'destination': binding(root)})))
        elif args.operation in ('status', 'list'):
            print(json.dumps(inspection(store, args.id if args.operation == 'status' else None)))
        elif args.operation == 'cancel':
            if before_write: before_write()
            result = store.cancel(args.id)
            if coordinator_info(root) is None:
                Engine(store, binding(root)).close()
                result['events'] = [event for event in store.events() if event['job_id'] in result['cancelled']]
            print(json.dumps(result))
        elif args.operation == 'ack':
            identity = args.id
            if identity.startswith('e-'):
                matches = [event['id'] for event in store.events() if compact_ref('e', event['id']) == identity]
                if len(matches) != 1:
                    raise ValueError('event reference is missing or ambiguous; inspect its exact identity')
                identity = matches[0]
            print(json.dumps(store.acknowledge(identity)))
        elif args.operation == 'recover':
            validate_binding(root)
            ensure_coordinator(root)
            if before_write: before_write()
            store.request_recovery(args.id)
            print(json.dumps({'id': args.id, 'state': 'recovery_requested',
                'observation_gap': True, 'uncertain_admissions_will_not_be_replayed': True}))
        elif args.operation == 'shutdown':
            preview = shutdown_preview(store)
            if preview['needs_confirmation'] and not args.confirm:
                print(json.dumps(preview))
                return 2
            for job in store.jobs():
                if job['intent'] in ('active', 'replacing'):
                    store.cancel(job['id'])
            info = coordinator_info(root)
            if info:
                os.kill(info['pid'], signal.SIGTERM)
                deadline = time.monotonic() + 7
                while coordinator_info(root) and time.monotonic() < deadline:
                    time.sleep(0.05)
            else:
                Engine(store, binding(root)).close()
            print(json.dumps({'shutdown_requested': True, 'coordinator_stopped': coordinator_info(root) is None,
                'native_owner_preserved': True, 'receipts': store.events()}))
        return 0
    finally:
        store.close()


def entrypoint():
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, TimeoutError, sqlite3.Error) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        raise SystemExit(1)
