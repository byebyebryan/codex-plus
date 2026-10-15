# Codex notification utility

The standalone `scripts/codex-notify` utility augments native Codex completion
notifications through Kitty. It uses Python's standard library and the originating
terminal, with tmux passthrough when the invocation carries an exact pane.
It is independent of the watch coordinator, report server and physical displays.

Chezmoi owns installed configuration and independently pinned helper selection.

## Native recovery and explicit rich mode

Qualified shared/remote Codex 0.162.1 TUIs emit native completion alerts without
invoking the configured external callback. Ordinary launches use `notify = []`
and native `tui.notifications = ["agent-turn-complete", "approval-requested"]`
with the existing `osc9` method. Settings take effect on the next normal TUI launch.

Rich mode is explicit:

```sh
codex-notify run
codex-notify run -- resume THREAD_UUID
codex-notify run --socket /path/to/native.sock -- -C /trusted/project resume THREAD_UUID
codex-notify identity
```

It requires an existing user-owned shared daemon and an attached Kitty terminal.
The native TUI connects through a private transient Unix relay. All native bytes
pass unchanged; the observer binds successful explicit `thread/start` and
`thread/resume` responses. Rosters, titles and daemon environments never grant a
route. Native completion alerts and the old callback are disabled only for this
launched client; native approval alerts remain enabled. Stock launches retain
the basic recovery path.

Rich completions carry exact native IDs, a useful body and unfocused-only Kitty
OSC 99 presentation with native terminal focus actions. Child/system/title
threads are excluded. Each attached viewer owns its route; multiple viewers can
publish the same episode, which consumers can deduplicate. Closing a viewer ends
its route without ending the daemon or thread. Reconnection does not replay old
completions. No persistent transcript or event log is kept.

This opt-in adapter is qualified against the recorded native version. `exec`,
fork, alternate remote routing and embedded/no-daemon operation are outside rich
mode. Use the ordinary CLI for those commands. Missing observations can miss a
rich alert; they never justify guessed identity. Oversized frames are skipped
without buffering while raw native traffic continues. The transient socket is
mode 0600 in a mode 0700 directory. Local/SSH/tmux and physical acceptance are
recorded separately from unit tests.

## Metadata contract v1

The D-Bus category is `x-codex-plus.notification.v1.` plus canonical unpadded
base64url of sorted compact ASCII JSON. Exact fields are `v` (integer 1),
`provider` (`codex`), `host`, `instance`, `thread`, `turn`, `kind` (`completion`)
and `body_format` (`markdown` or `plain`). The category is at most 1,536 characters.
Host/instance labels are at most 63/128 UTF-8 bytes without controls; native IDs
are canonical UUIDs. Unknown/duplicate fields, unsupported versions and
noncanonical encodings are rejected. Labels are data, not authentication or
executable routing.

Host is the source hostname. Instance is the first 24 hex characters of SHA-256
of the absolute configured native socket path; it survives daemon restarts and
identifies a configured source, not a process incarnation. The episode tuple is
`(provider, host, instance, thread, turn, kind)` and its event ID is SHA-256 of the
tuple's compact JSON. Different opaque turn IDs imply no order.

## Scoped read-only inspection

`codex-notify inspect [--socket PATH]` reads one bounded stdin JSON request:
`{"v":1,"nonce":"32 lowercase hex characters","cards":[...metadata...]}`.
At most 32 outstanding cards are admitted. Output echoes version, nonce,
host/instance and maps event IDs to `current`, `superseded` or `unknown`.

Only `thread/turns/list` is issued, using descending summary history and at most
32 turns per requested thread, under a six-second total native deadline. The
original completed turn must be present behind a newer turn to prove supersession;
the newer turn may already have finished. Missing old history, malformed replies,
timeout and listener ownership changes yield unknown. No thread is started or
resumed; no prompt, response or roster is returned.

Consumers configure exact trusted local/SSH argv separately. Incoming metadata
cannot select an executable or destination. Polling can stop without matching
outstanding cards and can continue after desktop popup expiry while device history
remains. Supersession is a local card policy, not proof the user read the notice.

## Callback behavior

The utility accepts one native notification JSON argument. It handles
`agent-turn-complete`, skips noninteractive `codex_exec` callbacks and positively
identified children, and reads Codex's local SQLite index read-only for child
classification. Missing classification allows the ordinary completion through.
It sanitizes the last assistant message, preserves paragraph boundaries, clips
to 2,048 UTF-8 bytes and emits a Kitty OSC 99 notification titled `Codex`.
Kitty supplies unfocused-only delivery and its originating-terminal focus action.
Unsupported terminals and expected delivery failures remain quiet.

## Known delivery boundary

A callback must have a real originating terminal or explicit tmux pane to use
this legacy delivery path. A detached shared daemon's inherited Kitty indicators
do not supply that route: `/dev/tty` fails when there is no controlling terminal.
Fresh native qualification must distinguish embedded CLI and shared/remote TUI
execution; a callback captured from one does not prove the other.

The explicit rich launcher supplies an attached client route independently of
this callback limitation. Ordinary launches use native basic notifications.

## Checks

```sh
rtk proxy python3 -B -m unittest discover -s tests -p 'test_notification*.py'
rtk proxy scripts/check
```

Tests use isolated SQLite files and PTYs without desktop effects. Installed
native local/SSH/tmux notification delivery and graphical focus remain separate.
