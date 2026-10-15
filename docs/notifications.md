# Codex notification utility

The standalone `scripts/codex-notify` utility augments native Codex completion
notifications through Kitty. It uses Python's standard library and the originating
terminal, with tmux passthrough when the invocation carries an exact pane.
It is independent of the watch coordinator, report server and physical displays.

The current ownership checkpoint moves the existing chezmoi helper and its
fourteen behavioral checks into this repository. Chezmoi still owns installed
configuration and helper selection; distribution has not switched yet.

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

Rich notification identity, explicit client routing and lifecycle controls have
their own following acceptance gates. This ownership checkpoint does not claim
that the existing terminal-routing regression is repaired.

## Checks

```sh
rtk proxy python3 -B tests/test_notifications.py
rtk proxy scripts/check
```

Tests use isolated SQLite files and PTYs without desktop effects. Installed
native local/SSH/tmux notification delivery and graphical focus remain separate.
