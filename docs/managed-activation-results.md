# Managed installation and activation on Snap and Starship

Completed 2026-10-14 under Bryan's selected two-host plan and explicit prohibition
on disturbing active work or restarting either daemon. The monitoring preview is
installed, configured and qualified independently on both hosts. A real-source
pilot and Bryan's personal walkthrough remain separate acceptance.

## Distribution and installation identity

The runtime remains the published v0.1.0-preview.2 artifact from source
`2274f4b54817fae88c3762c39c1284b8b1eb2695`. Fetched runtime SHA-256 is
`d4b23b83339f2a59bd12eadc0408695d899b993020d0fa496dc394de9e49ecdf`.
No runtime rebuild or repin was needed. Each installation has exactly the 19
manifested payload files plus runtime.json, with matching fetched bytes and modes.

Dotfiles `fa6c9c0289b290c5b4191c9f729a910164eae5c4` publishes optional default
availability on Snap and Starship and nine explicit control approvals, including
peer_send/message_cancel. Unknown hosts get no automatic server entry. Existing
explicit availability choices, disabled tools and custom approval preferences
remain authoritative; required=false keeps the component optional.

Each apply used that clean published source and five groups: immutable release,
current selection, model launcher, package launcher and Codex configuration. Apply
scripts were excluded. A tested `codexPlusOnly` override restricted the shared
config modifier to this MCP entry; Starship's three unrelated legacy settings were
preserved. The full dotfiles check, component validator, rendered semantic diffs,
scoped status/diff/dry-run and installed verification passed. Final scoped managed
status is converged on both hosts.

A direct release-directory apply needed its missing parent created first. Snap's
existing owned runtime-state root was mode 0755 and rejected by the first actual
tool call. Its mode was narrowed to 0700 without changing existing contents. State
and journals remain runtime-owned and outside managed exact archives. Neither
finding required a runtime change or daemon restart.

## Native acceptance

Both hosts run Codex 0.162.1 and Python 3.14.8. Ordinary fresh native TUI sessions
connected to each existing Unix daemon, loaded all 15 installed tools from managed
configuration and successfully called watch_list. No per-thread codex_plus
configuration was injected for this activation gate. Bounded fixture-only
state/allowlist/source overrides were used subsequently and are separate evidence.

| Gate | Snap | Starship |
| --- | --- | --- |
| Fetched/installed manifest, bytes, modes and symlinks | Passed | Passed |
| Managed enablement and nine control approvals | Passed | Passed |
| Default fresh TUI loading and installed tool execution | Passed | Passed |
| Contextual independent-peer discovery | Passed | Passed |
| Attributed information message and handled receipt | Passed | Passed |
| Useful peer readiness callback, acknowledgement and stop | Passed | Passed |
| Authenticated HTTP baseline, changed readiness and stop | Passed | Passed |
| One-shot configured MCP inspection and handled receipt | Passed | Passed |
| Cleanup and original daemon incarnation | Passed | Passed |

The peer scene used two independent loaded sessions, contextual discovery rather
than user-supplied UUIDs, one fresh status read per useful callback and explicit
acknowledgement. The model reported readiness and stopped observation while the
report conversation remained intact. No subagent was created. Existing real peers
were passive discovery/context sources only, with write destinations restricted to
fresh owned synthetic actors.

The endpoint fixture supplied a private synthetic bearer credential and filtered
unchanged periodic reads without inference per poll. Snap inherited session access;
Starship selected read-only filesystem access with existing network permission.
Both reported the ready transition, acknowledged it and cancelled the observer.
The timed scene scheduled a native model turn that actually called the configured
read_status MCP tool under its approved native connection and acknowledged the wake.
It did not use direct MCP RPC or bypass authentication/approval.

## Partial trials and corrections

One Snap model turn failed with serverOverloaded before sending a message. It was
closed without replay. A later distinct information-message fixture passed.
Several private-harness assertions also needed correction: job state is
source_state, source events use kind=source, and cancellation need not be repeated
when a readiness callback already stopped the observer. The harness initially
mistook handled peer receipts for timeouts. Actual native histories and journal
receipts prove those callbacks succeeded; the false-negative trial records were
retained rather than overwritten or rerun as product fixes.

The premature endpoint assertion interrupted two already-consumed timer callbacks
before either executed its MCP inspection. Fresh bounded settlement checks then
proved completed configured inspections on both hosts. Those two old journals
lack cached terminal receipts because their coordinators closed first; separate
native histories prove the turns interrupted and pre-archive queue checks proved
no input remained. No observation or message was replayed to invent a receipt.

The first native viewer launch also failed before creating a thread because RTK
captured its terminal output. Giving the native TUI actual terminal descriptors
fixed the private launcher. These are qualification-harness findings, not changes
to shipped runtime code.

## Resource and preservation audit

The combined pass used exactly 32 started native model turns: 28 completed, one
provider failure and three cleanup interruptions. Ten automatic deliveries include
the two interrupted timer callbacks. Authenticated HTTP fixtures received 23 calls;
configured MCP fixtures received two calls. The conservative combined observation
upper bound is 440.03 seconds, below the ten-minute limit. Each lease was at most
180 seconds/two source events, with no automatic successor. No further inference
was admitted after the ceiling.

All 18 owned actors are archived. There are no owned loaded actors, running jobs,
remaining native queued inputs, fixture processes, viewers or coordinators. Existing
runtime releases/journals and report data/hosting were preserved. Snap's report
server remained running. Both original native listener identities, including PID
and start ticks, match their baseline; no restart or global MCP reload occurred.

The ten existing worker agent/skill files match the selected source on both hosts;
worker identities, enablement and explicit invocation were untouched. No worker
skill or agent delegation was activated.

Starship installation used an isolated pinned checkout. Its original local history,
including its distinct Observer-selection commit, and all baseline dirty bytes
remain preserved. Its canonical branch advanced concurrently for a report-release
commit; that change was retained rather than rolled back. New Snap/Starship
Observer edits also remain outside this rollout. Kitty, SSH, Claude and
Observer/Mesh targets received no apply from this pass. Semantic comparison proves
all unrelated live Codex values were preserved.

## Everyday use and remaining limits

Open a fresh ordinary Codex session on either host and ask, for example, "Watch
the session handling the packaging report and tell me when it is ready," "Tell
that session the handoff needs a short risk summary," "Check this endpoint again
later," or "Stop watching it." The model selects source, filtering, cadence and
follow-up through the installed capabilities. Existing sessions were not globally
refreshed. Cross-host native messaging is not introduced by two-host installation.

Synthetic qualification does not establish real credential/provider recovery,
production endpoint behavior, long unattended operation, exit protection or personal
UX acceptance. Those can be selected next; they do not require installation or a
daemon restart to begin a fresh-session walkthrough.
