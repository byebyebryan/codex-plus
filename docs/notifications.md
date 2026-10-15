# Codex notification utility

The standalone `scripts/codex-notify` utility augments native Codex completion
notifications. It uses Python's standard library. The configured desktop route
uses `notify-send` and optional SSH; the older terminal route uses Kitty, with
tmux passthrough when the invocation carries an exact pane.
It is independent of the watch coordinator, report server and physical displays.

Chezmoi owns installed configuration and independently pinned helper selection.

## Native recovery and explicit rich mode

Configured completion hooks work with the qualified shared Codex 0.162.1 server.
The remote TUI does not forward its `-c notify=...` override; that earlier probe
did not establish missing hook dispatch. A detached hook lacks the originating
TTY, so the older `/dev/tty` route fails independently of event production.

The currently selected basic recovery keeps ordinary launches on `notify = []`
and native `tui.notifications = ["agent-turn-complete", "approval-requested"]`
with the existing `osc9` method. Settings take effect on the next normal TUI launch.

## Config-driven desktop candidate

The candidate keeps ordinary `codex` launching. It is opt-in while the behavior
choice is unresolved: desktop alerts use **always notify**, and Open can launch
a **new terminal resuming the exact thread**. Originating-terminal focus and
unfocused-only delivery are not provided by this route. The config hook does not
identify that viewer; never infer it from titles, text, cwd or daemon environment.

When selecting this mode for fresh threads, configure native Codex on its owning
host:

```toml
notify = ["/home/bryan/.local/bin/codex-notify", "hook"]
[tui]
notifications = ["approval-requested"]
```

The helper reads `~/.config/codex-plus/notify.toml` (or `--config PATH`). Config
must be an owned regular file without group/world write permission. Example local
delivery, with the receiver and producer using the same config:

```toml
v = 1
socket = "/home/bryan/.codex/app-server-control/app-server-control.sock"
command = ["/home/bryan/.local/bin/codex-notify", "desktop"]

[desktop]
condition = "always"
```

On Snap, use an explicit destination instead of an originating SSH terminal:

```toml
v = 1
socket = "/home/bryan/.codex/app-server-control/app-server-control.sock"
command = ["/usr/bin/ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3", "starship", "/home/bryan/.local/bin/codex-notify", "desktop"]
```

The receiving desktop needs its own `[desktop]` configuration and `notify-send`.
It uses the user's `/run/user/UID/bus`; a trusted `desktop.bus_address` can select
another bus. The source requires an existing shared server. A bounded read of
only the supplied native thread must positively establish `threadSource=user`,
a supported top-level source and unchanged listener ownership. Internal title
tasks also invoke the hook and are excluded by this check. Missing/unknown native
evidence suppresses this candidate's alert; it is not a claim about background
exec, standalone clients or future native versions.

Publication carries one bounded stdin JSON envelope, containing v1 metadata,
title and sanitized body. Incoming text cannot select argv or a destination.
SSH transports only that envelope. Replies bind desktop admission to the exact
episode. No terminal, session roster, prompt history or credentials are forwarded.

The receiver stores at most 256 episode hashes, times and desktop IDs for 24 hours
in a private runtime directory; no response body is stored. Duplicate admitted
episodes do not republish or renew a card. Reservations with unknown admission
return `uncertain`; they never report success or automatically retry. A crash
between reservation and admission can miss an alert. This is bounded best-effort
delivery, not an exactly-once transaction with the desktop server.

Open is offered only for explicitly configured host/instance pairs:

```toml
[[desktop.open]]
host = "starship"
instance = "TOKEN_FROM_IDENTITY"
command = ["/usr/bin/systemd-run", "--user", "--collect", "--quiet", "/usr/bin/kitty", "/usr/bin/codex", "--remote", "unix:///home/bryan/.codex/app-server-control/app-server-control.sock", "resume", "{thread}"]
```

Only a complete `{thread}` argument is replaced, with the validated canonical
UUID. Remote resume commands are separately trusted configuration. `systemd-run`
lets the new terminal inherit the desktop manager's GUI environment instead of
the SSH receiver's environment. There is no automatic activation: an admitted
popup's default action must fire. A finite worker waits at most 35 seconds for
the action; no resident notification/Observer service is added. Graphical focus
and panel Open remain separate acceptance from command/action correlation.

Select one completion publisher. Leaving native completion alerts enabled
alongside this hook can duplicate notices. Conversely, disabling native alerts
while resuming a loaded thread whose hook is still `[]` can lose notices. New
threads read server-side user config without a daemon restart, but loaded threads
retain their hook until the qualified unload/resume boundary. Preserve ongoing
work and basic recovery until a safe mode transition is selected; do not restart
or unload user work to force adoption.

## Optional relay experiment

The earlier explicit client relay remains available:

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
route. Native TUI completion alerts are disabled for this launched client;
native approval alerts remain enabled. Server-side hooks are independent and
must be disabled for this covered context to avoid duplicate publication. A TUI
`notify` override cannot disable a host-owned hook. Stock launches retain the
basic recovery path. This relay is not a launcher requirement or the preferred
config-driven integration.

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

The configured desktop candidate avoids this terminal dependency with different
focus/Open behavior. The optional relay supplies an attached-client route.
Ordinary installed launches continue using native basic recovery until selection.

## Checks

```sh
rtk proxy python3 -B -m unittest discover -s tests -p 'test_notification*.py'
rtk proxy scripts/check
```

Tests use isolated SQLite files and PTYs without desktop effects. Installed
native local/SSH/tmux notification delivery and graphical focus remain separate.

## Config candidate checkpoint: 2026-10-14

The configured desktop candidate is source work, not a selected live preference.
An isolated stock 0.162.1 TUI, private app-server and loopback Responses fixture
reached a private notification bus through the hook. Internal title work produced
no alert after positive native classification was added. Native `notify-send`
admission, v1 metadata/body decoding, duplicate suppression and a configured
default action carrying the exact UUID passed without real credentials or desktop
effects. This proves the action command, not graphical focus or an original viewer.

Controlled actual-owner tests used fresh owned RPC thread configuration on
Starship and Snap, leaving global native config and normal launches unchanged.
Both reached Starship's desktop and rich 349 host association. Local card `100021`
also passed device admission. After panel presentation expired with history still
retained, native newer interrupted turns retired local `100021` and SSH host card
`100022`. Those progress checks continued only the same owned test threads after
correcting harness assumptions; every owned live test thread was archived.

DMS did not emit the expected desktop-close signal, so panel timer expiry is the
accepted observation; desktop popup expiry was not directly proved. The USB link
disconnected before final deletion readback and before SSH board acceptance.
Device deletion and physical rendering/touch remain pending. Original native
owners (Starship PID 17438; Snap PID 62725), native config hashes, live services
and firmware were preserved. Raw private evidence stays outside the source tree.

Selecting always-notify/new-terminal Open versus preserving original-terminal
behavior remains a product decision. The latter needs a client binding absent
from the tested hook; do not make the relay launcher a requirement or silently
select different semantics. Safe adoption across already loaded threads is a
separate gate. Chezmoi remains the distributor; no new runtime pin, global
notification preference or managed desktop route was selected by this checkpoint.
