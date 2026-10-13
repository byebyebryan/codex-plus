# Codex Plus runtime preview distribution

The runtime is a Linux/Unix preview qualified against Codex 0.162.1. It uses
Python 3.11 or newer and RTK for the existing native status/coordinator command
paths. It requires an already running owning daemon and loaded independent
sessions; it never starts a daemon or cold-resumes a target. Long production
operation, native owner replacement and personal UX acceptance remain separate.

Release: [v0.1.0-preview.1](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.1),
source `f4db934fc8a5bafe2bc392378c2ab3e26ee1f7c2`. The runtime SHA-256 is
`0f1322e4faeceab05a8ce34d2877d36b83cde19dd47bf45fa57324abdfdcf3ea`.
Publication/fetched-byte verification and isolated installed/native qualification
passed; real managed apply and enablement remain deferred.

## Artifact and immutable installation

`scripts/codex-plus-package build --output /ABSOLUTE/OUTSIDE/REPO/runtime.tar.gz`
requires a clean committed checkout. The artifact contains only the declared
runtime files, license and `runtime.json`; tests, spikes, worker skills, private
state and captures are excluded. Stable archive headers produce reproducible
bytes for the same source revision. The manifest records version, source revision,
compatibility, exact file hashes and executable modes. Manifest verification proves
consistency; compare the fetched artifact's SHA-256 with the published release pin
to establish the selected artifact identity.

For an isolated installation, run:

```sh
rtk proxy scripts/codex-plus-package verify /PATH/runtime.tar.gz --sha256 EXPECTED_SHA256
rtk proxy scripts/codex-plus-package install /PATH/runtime.tar.gz --prefix /ABSOLUTE/INSTALL --sha256 EXPECTED_SHA256
rtk proxy scripts/codex-plus-package activate --prefix /ABSOLUTE/INSTALL --revision FULL_SOURCE_REVISION
rtk proxy scripts/codex-plus-package mcp-config --prefix /ABSOLUTE/INSTALL
```

Installation creates `/ABSOLUTE/INSTALL/releases/FULL_SOURCE_REVISION` and selection
changes only `/ABSOLUTE/INSTALL/current`. Existing immutable releases are verified,
never overwritten. Wrappers resolve their real release directory before importing
the runtime; coordinators launch helpers from that captured release. Updating or
rolling back selection preserves running code and does not stop native work.
Keep older releases while any runtime depends on them. Chezmoi owns Bryan's real
installation; these commands are for isolated qualification or other unmanaged
installations, not a way to overwrite managed targets.

## Capability loading and approval scope

The configuration generator prints the `mcp_servers.codex_plus` table to integrate
through the configuration owner. It does not write live Codex configuration.
The command uses the installed script directly with Python `-B`; MCP stdio must
remain protocol-clean. Initialization includes shared capability instructions and
tool metadata. Native qualification of actual model use is recorded in the
[distribution report](distribution-pass-results.md), separately from protocol tests.

`--disabled` produces an optional disabled configuration even if no runtime exists.
User disable preferences remain effective. Tool listing/initialization do not
create state, inspect a native session, poll a source or start work. At a tool call,
the runtime uses `--socket`, `CODEX_PLUS_SOCKET`, or a lazy existing-daemon status
query. Kernel ownership and positive loaded caller membership are then verified.
An absent/ambiguous/wrong owner is unavailable; there is no daemon-start fallback.

Private journals default to `$XDG_STATE_HOME/codex-plus`, or
`~/.local/state/codex-plus`, partitioned by verified caller UUID. `--state-root`
selects another absolute private root. Frozen native bindings are retained: a
native daemon incarnation change does not silently rebind old intent. Existing
private state must be owned by the user and private. State/allowlists are never
part of a release or a managed `exact` archive.

The default MCP policy is `writes`, with explicit approval for controls that affect
the caller's own observation/reminder intent and current-event handling. Command
sources retain read-only filesystem/network policy. Peer messages have separate
approval; `--allow-peer-send` explicitly opts into tool approval for messages within
the recipient's existing task, including cancellation of your own outgoing intent.
Completed recipient handling is never retracted. Under a native `never` approval policy, a message
that requires approval is unavailable; explain that result rather than issuing
native shell control calls to bypass it. Incoming peer text never grants new work.
Read-only annotations describe effects and do not replace authorization.

For owned synthetic qualification only, add `--allowlist PRIVATE_JSON_FILE`,
`--state-root PRIVATE_ROOT`, `--max-duration 120`, `--max-events 2` to `mcp-config`.
The allowlist restricts callers and write destinations; real peers remain passive
sources. This is test isolation, not permanent hardcoded thread inventory. No task
strategy, target UUID or callback recipe belongs in user prompts.

## Upgrade, rollback and activation

Verify a new artifact and install it under its immutable revision before selecting
it. Roll back by verifying and reselecting the prior revision. This changes new
process selection only; it does not migrate journals, restart existing MCP bridges
or native daemons, delete old releases or change worker enablement. Recheck cached
source/delivery health before explicit recovery of any lost source; uncertain
admission is never blindly repeated.

The managed rollout must keep release URLs, revisions, fetched checksums, runtime
entry/config wiring and validator expectations together. Render supported and
unknown hosts, disabled settings and preservation of unrelated config state. A
scoped dry-run is not a live installation, and installed-but-disabled is not proof
of fresh-session activation. The default execution finish leaves live apply
deferred. Fresh owned native acceptance must run from the installed artifact with
the shipped instructions, independent of this checkout.
