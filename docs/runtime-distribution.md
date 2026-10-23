# Codex Plus releases and monitoring installation

The runtime is a Linux/Unix preview qualified against Codex 0.162.1. It uses
Python 3.11 or newer and RTK for the existing native status/coordinator command
paths. It requires an already running owning daemon and loaded independent
sessions; it never starts a daemon or cold-resumes a target. Long production
operation, native owner replacement and personal UX acceptance remain separate.

## One Codex Plus release

The published release is [v0.1.0-preview.9](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.9),
source `0ec803d`. Workers, monitoring and reporting share one
version, source commit, GitHub tag and release. A reporting-only fix still advances
the product version; release notes identify which capabilities changed. Components
remain optional and keep their own configuration, data and running processes.

The single release contains three archives, `release.json` and `SHA256SUMS`:

| Component | Archive |
| --- | --- |
| Workers | `codex-plus-workers-0.1.0-preview.9.tar.gz` |
| Monitoring | `codex-plus-runtime-0.1.0-preview.9.tar.gz` |
| Reporting | `codex-plus-report-0.1.0-preview.9.tar.gz` |

`codex_plus/__init__.py` is the authoritative version. Both MCP adapters, report
plugin manifests and all component manifests use it. The worker archive retains
the existing default and optional legacy identities; packaging does not enable
legacy skills or change explicit workflow invocation.

Main also contains unreleased recap/history and loaded-MCP metadata refinements.
They are not in the preview.9 archives. See
[released and source features](getting-started.md#released-and-source-features)
and [candidate evidence](native-alignment-results.md). A new unified release is
required before updating managed URLs, revisions and checksums; existing tags
and artifacts are immutable. Documentation publication is a separate operation.

From a clean committed checkout, build into a new directory outside it:

```sh
rtk proxy scripts/codex-plus-release build --output /ABSOLUTE/OUTSIDE/REPO/release
rtk proxy scripts/codex-plus-release verify /ABSOLUTE/OUTSIDE/REPO/release
```

The verifier checks all archives, exact member inventories, modes, component
versions, source revisions and checksums. Builds refuse existing output. Compare
the fetched release's hashes with the reviewed/pinned identities; a self-consistent
manifest alone does not authenticate its publisher. Install selected component
archives through their existing installers or configuration owner. Older tags and
artifacts remain available; current installers retain validation/selection support
for monitoring previews 1–3 and reporting previews 7–8.

Command sources inherit verified native session permissions, including existing
networking and authorized cache writes. Filesystem read-only and network-off are
narrowing choices; network-required verifies an existing grant. Periodic short
commands or continuing observer scripts can poll authenticated endpoints quietly.
Configured MCP inspection uses scheduled native model turns under normal approval
and authentication, with a model cost per check. The direct MCP RPC is excluded
because controlled qualification exposed an approval bypass. Real-source/auth and
long-operation acceptance remain separate from local fixture results.

## Current managed state

Snap and Starship select workers, monitoring and reporting **preview.9**, source
`0ec803d`, through chezmoi following the scoped rollout on 2026-10-22. All three
manifests verify on both hosts, including Snap's OSS/work contexts. Existing
explicit storage paths, configuration, native owners, active MCP processes and
report servers are preserved. Already loaded MCP processes adopt the selected
release on normal reconnect. See the [rollout receipt](refinement-results.md#managed-rollout-2026-10-22)
and the earlier [environment deployment receipt](environments.md#snap-multi-environment-deployment-2026-10-15).

Workers retain their own installation. The 349 inspector
is retired, and native notifications remain selected. The earlier [managed activation report](managed-activation-results.md)
records the original two-host deployment. Report publication/hosting remains
independent of the monitoring runtime.

## Read-only diagnosis

Run `rtk proxy scripts/codex-plus-doctor` from this checkout, or the shipped
`scripts/codex-plus-doctor` inside a selected monitoring/reporting release.
`--runtime-prefix`, `--report-prefix` and `--worker-prefix` select nondefault
installations. The selected `CODEX_HOME` chooses MCP configuration and native
status queries; managed state/report path overrides are reflected. `--no-native`
limits diagnosis to local files and configuration.

The result reports optional/missing or legacy installations, local manifest
integrity, aligned/mixed component versions, enabled MCP configuration and native
client/owner versions. It never starts or restarts a daemon, MCP process, watch or
report server. Selected files and enabled config do not establish already loaded
process versions. Codex 0.163.0 is currently outside the recorded 0.162.1 native
release qualification baseline. The source candidate has bounded owned 0.163.0
trials; daily use and fixture CI do not silently extend that evidence to blanket
compatibility or long unattended operation.

The unreleased source candidate adds the following metadata check; installed
preview.9 retains its earlier selected-file diagnosis.
When `CODEX_THREAD_ID` is available, or `--thread` selects an already loaded
conversation, `loaded_mcp` reads that conversation's native MCP metadata. It
compares reported monitoring/reporting versions with selected manifests. Missing
metadata stays unknown; the doctor never resumes a thread or refreshes a server.
A reported version does not verify loaded payload bytes or describe every
conversation. `--no-native` skips this inspection; `loaded_processes_checked`
remains false because the doctor does not scan or verify running process code.
The reporting-only archive retains file and native CLI diagnosis; the monitoring
component supplies the optional client for native MCP metadata inspection.

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
private state must be owned by the user and mode 0700. A pre-existing 0755 root
is rejected; scoped rollout may narrow only that owned root without deleting or
changing its journals. State/allowlists are never
part of a release or a managed `exact` archive.

The default MCP policy is `writes`, with explicit approval for controls that affect
the caller's own observation/reminder intent and current-event handling. Command
sources retain the caller's effective permissions unless explicitly narrowed.
Legacy jobs without an execution grant retain their earlier offline policy.
Peer messages have separate approval. Bryan's Snap/Starship managed policy enables
the optional server and explicitly approves peer_send/message_cancel alongside the
seven watch/reminder controls while preserving existing explicit preferences.
For generated configurations, `--allow-peer-send` explicitly opts into tool approval
for messages within
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
of fresh-session activation. The managed installation pass applies only the selected
runtime/wiring and Codex Plus configuration; its host evidence is recorded in the
implementation handoff. Fresh owned native acceptance must run from the installed
artifact with the shipped instructions, independent of this checkout.

### Earlier component artifacts

The previous monitoring release, [v0.1.0-preview.3](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.3),
used source `c73c237c734eb7e20b46185cccd471edfc803520`. Its runtime SHA-256 is
`43908c4b5b238fdbb81187050f0e7bfd4653a6f4d3677e1f1c9577ff443cd24f`,
with 21 declared runtime files plus its manifest. It remains historical/rollback
evidence; it is not the current unified release. The
[source-access report](source-access-pass-results.md) separates source, artifact,
installed native qualification and managed wiring from live apply/enablement.
