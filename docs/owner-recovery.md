# Native owner recovery

## Source candidate: preview.21 soak refinement

Preview.21 is a local candidate; preview.20 remains published and managed.
After a successful handoff releases its writer, the coordinator re-enters the
same captured release using the selected epoch path. Its launch arguments and
private process record agree again, so strict status checks can recognize the
live successor and avoid a duplicate startup attempt. Owner/writer/queue proofs,
original observation bounds and the RTK log boundary remain unchanged.

Receipt observation is separate from source observation. An acknowledged native
callback can still be running after the source is cancelled or expires. The
candidate observes that exact positively running turn and uses bounded passive
history after reconnect to reconcile terminal receipts. Missing or conflicting
evidence stays unknown; no input, source or external action is replayed, and
immutable archives are not rewritten. Cached inspection does not restart work.

Manual recovery still requires an explicit request, unchanged same-mode preview
and confirmation. The shared owner error now describes clean/quarantine/resume
without suggesting that a send should repair its recipient. A host reboot is
different from a same-boot daemon replacement: original monotonic lease anchors
do not survive the new boot, and missed reminders are not replayed as catch-up.

## Preview.20: MCP-started coordinator handoff

The health/follow-up pass found a launch-path defect in published preview.19.
Its earlier zero-turn restart fixture started the coordinator with a log outside
the journal. A watch registered through the actual MCP instead used
`ensure_coordinator`, whose RTK supervisor retained `coordinator.log` inside the
journal. After the Python coordinator released its writer, the supervisor's
open log descriptor still correctly triggered the conservative open-state guard.
Automatic handoff therefore remained deferred. The failed fixture and a separate
no-model descriptor reproduction were retained; no real monitor was repaired.

Preview.20 places new supervisor logs in a private
`.coordinator-logs` namespace outside the entire stable thread container and its
epochs. Old logs and loaded helpers remain unchanged. Journal descriptors,
writer locks, process-incarnation proof and original continuation eligibility
remain strict. This changes launch log placement, not the recovery gate.

A relocated private candidate completed the normal MCP path on native 0.167:
the model registered one replay-safe read-only command watch, its baseline stayed
quiet, the controller replaced only the fixture daemon and reattached only that
owned conversation, and the coordinator resumed with the original lease. A
fresh synthetic source change produced one admitted event, model acknowledgement
and a completed callback. Both setup and callback turns completed with native
Luna/max selection. The queue ended empty and no replacement registration was
created. See the [qualification receipt](native-qualification-results.md#health-and-restart-follow-up-preview20-source-pass).

This closes one bounded post-restart model-follow-up gap. It does not qualify
every pre-existing watch, general native 0.167 compatibility, authenticated
endpoint/MCP recovery, long outages or daily-use reliability. Preview.20 is
published; the [handoff](implementation-handoff.md) separates managed installation
from code adoption by existing helpers.

<a id="daemon-restart-candidate-preview19"></a>

## Daemon restart recovery: preview.19

Preview.19 publishes the restart fix. Per-host installation and loaded helper
versions are recorded separately in the [handoff](implementation-handoff.md).
The preview.11 contract and evidence below remain a
historical record. A daemon restart does not invalidate the conversation or its
saved user request. The process-incarnation guard still fences old writers.

An upgraded coordinator detects a changed native owner, closes its old journal
and releases its owner lock before requesting a handoff. The handoff requires
the same host, user, PID namespace, requested/resolved endpoint and exact
positively loaded independent conversation. It proves the old exact process
ended, including an unreaped zombie, verifies readable state/history, excludes
live or unclassified helpers, and requires an empty native input queue. It never
starts a native daemon or loads a cold conversation. If the client has not yet
reattached the conversation, recovery waits rather than choosing another thread.

The existing versioned selector and immutable archives are retained. Handoff
creates fresh registration identities and fresh references. Old references,
event IDs, commands and delivery receipts remain historical; they are never
retargeted or replayed to discover an outcome. Confirmed native withdrawal is a
settled receipt without pretending that the input was acknowledged. Unknown or
contradictory withdrawal still stays unresolved.

Only eligible active observations continue. Original expiry, reminder due time,
event/notice allowance, projection baseline and source permissions remain in
effect. New registrations also record same-boot monotonic lease/due anchors, so
wall-clock rollback cannot restore elapsed supervision time. Legacy rows without
that evidence are quarantined rather than guessing their remaining lifetime.
No cancelled, expired, exhausted, replacing or unresolved-renewal lineage
is revived. Uncertain old events, including acknowledged callbacks without a
final outcome, prevent automatic continuation of that registration. Observations
record a gap and wait a full source interval before their first new poll.

Passive peer watches default to continuation after validating the same independent
peer in the successor daemon. Commands and scheduled MCP inspections default to
manual recovery. The registering model may select `restart=resume` only for a
source safe to repeat within the original request. A read-only sandbox does not
prove that a command or remote endpoint is replay safe. Native command permissions
and MCP availability are checked again before any new execution; changed access
holds the source. The native primary, tool approvals and selected MCP remain native.

Unresolved intent that cannot continue is preserved in the archive. An expired
lost command still has an unknown outcome and may have surviving external
effects. Quarantine restores unrelated fresh control without declaring that
command stopped or complete. Ordinary recap/history output discloses retained
uncertainty; stale list tools return bounded previous-owner records without
opening the normal writable Store, polling, recovery or source execution.

For explicit recovery, `owner_status` and `owner_recover` take the same `mode`:

| Mode | Effect |
| --- | --- |
| `clean` (default) | Preserve the earlier strict clean-state contract. |
| `quarantine` | Archive unsettled intent, retain unknown effects and start fresh control without replay. |
| `resume` | Also prepare eligible continuations under original bounds. The explicit MCP/CLI interface requests their coordinator; inspect watch receipts for actual execution. |

All modes require an unchanged same-mode preview and `confirm=true`; none bypass
a live writer, unknown old owner, changed logical scope, corrupt history or
nonempty queue. The core selection receipt records `sources_started=false` and
`native_input_submitted=false` for the archive/selection transaction. A separate
`continuation_coordinator` receipt reports a subsequent explicit resume request;
registration/coordinator availability is not proof of source execution.
Automatic coordinator handoff starts its own next generation after selection.

From the source checkout, use `scripts/codex-plus-owner --thread THREAD_UUID
status --mode quarantine` (or `resume`), then `recover --mode` with that same
preview. Managed installation follows the published release through chezmoi.
Existing loaded preview.18 helpers do not acquire
automatic handoff from a source update. No global MCP reload or daemon restart
is an adoption shortcut; the exposed native reload RPC has no server/thread
selector. The actual preview.18 artifact can read the new selector and explicit
quarantine receipt in fixtures. Its default list output lacks the new uncertainty
warning, and it does not gain automatic handoff or the new options. Normal code
adoption remains necessary; this compatibility fixture is not a live deployment.

The source qualification receipt is recorded in the implementation handoff.
Private incident journals and native fixture captures stay outside source.

### Preview.19 qualification

Candidate `7a54f41` passes 420 tests and the 145-file repository gate. Its
relocated artifact reports preview.19 and 17 monitoring tools; runtime/report
manifests and modes verify, and actual preview.18 archives remain accepted for
rollback. Ten skill validators pass with worker roles and invocation unchanged.

The disposable native 0.167 restart recipe proves automatic coordinator handoff,
fresh peer observation, an opted-in command executing again under its unchanged
native grant, original deadlines, quarantined expired/lost command history and
paused-goal delivery control. It starts no model turn. An additional admission
probe did begin one turn because the native idle queue consumed its input
immediately; withdrawal and handling stayed unknown and were never replayed.
This is not proof of a completed model follow-up after restart or general native
0.167 compatibility. The source pass preserved production owners, Starship
bindings and installed preview.18. See the [handoff receipt](implementation-handoff.md#unreleased-preview19-daemon-restart-recovery)
for the acceptance boundary and adoption limits.

The 2026-10-29 investigation found a correct ownership refusal with no supported
way to resume fresh Codex Plus operations after a daemon incarnation changes.
The selected implementation scope is **explicit clean rollover**, diagnosis and
inspectable history. It does not include moving unresolved intent onto a new
owner or quarantine of unsettled work. Publication and managed deployment have
their own acceptance gates.

This is the preview.11 recovery contract. Older installed processes keep their
captured code until normal reconnect; the native qualification baseline and
bounded later-version evidence retain their limits. Implementation and acceptance
results are recorded below.

## Incident and product boundary

The saved caller binding differed from the current owner only in process ID,
process start ticks and executable. The host, user, PID namespace, requested and
resolved sockets, and exact positively loaded thread matched. The old process
was absent. Normal model tools failed during caller construction. After caller
repair, passive peer discovery/inspection worked but sending met the same stale
binding in the recipient's state directory.

Maintained main and the installed preview.10 implementation matched for the
affected modules. Invented fixtures reproduced both endpoint failures, PID reuse
refusal and the stale-reference error left by a binding-only rewrite. This does
not establish a native API regression or explain what replaced the daemon.

The original guard must remain: an existing registration cannot silently acquire
a different owner. The defect is the combination of one per-thread state slot,
frozen references and no supported recovery/history path. Reconnecting the MCP
process does not change the saved binding.

The recovered incident is not an instruction to reset other sessions. Its
private archives remain outside source. A completed, accepted message whose
native turn outcome was never recorded retains that unknown outcome; neither
handling nor fulfilled delivery proves the entire turn or an external effect.

## Clean rollover contract

Use native caller metadata for model-facing recovery. An operator interface must
select an exact thread and existing environment. Never infer identity from a
title, recent activity, another caller, or a peer's claim of user authorization.

Diagnosis is available before ordinary model-state construction. It identifies
caller versus recipient failures, the old/current incarnation, registration
effects and safe next steps. Inspection starts no daemon, coordinator, source,
model turn or queue submission. Native loaded inventory and passive metadata
reads establish eligibility without cold-resuming a thread.

An explicit rollover requires an unchanged preview token and confirmation. The
host, user, namespace, requested/resolved endpoint and exact thread must match;
the new owner must positively load that independent thread, and the old exact
process incarnation must be gone. PID alone is insufficient: process start ticks
matter. New recovery evidence includes boot identity without silently changing
every legacy native binding. Missing legacy evidence is disclosed.

Refuse rollover for:

- a live or unclassified coordinator/helper, held ownership lock or incomplete
  proof that the old process incarnation ended;
- active/replacing jobs or pending renewal attempts;
- pending, dispatching or uncertain admission, unresolved unacknowledged native
  queue input, unresolved withdrawal, or an outgoing registration whose exact
  recipient receipt is unsettled or unavailable;
- changed scope, unloaded/ambiguous targets, corrupt state or incomplete scans.

An acknowledged, settled registration may retain an unknown final native turn
outcome. Preserve and display that uncertainty. It is not automatically active
delivery intent and must not require inventing a successful completion to permit
clean rollover.

Refusal retains old intent and evidence. This slice has no force/reset option.
Settling live or uncertain work requires its own scoped action; future quarantine
needs a separate contract and acceptance for old callbacks and surviving effects.

Helper safety uses exclusive launch/owner locks, classified journal state and
exact tracked coordinator identities. A broader process-descriptor scan adds a
veto when it positively finds a live accessor. Protected unrelated processes can
make that census partial; the result says so and never claims all same-user
descriptors were inspected. An unknown tracked helper still refuses rollover.

## State, references and history

Each persistent owner incarnation has its own immutable binding and journal.
It is distinct from the coordinator's existing run generation. A stable per-thread
selection chooses the state for fresh operations. Existing legacy state remains
usable until an explicit recovery changes its layout.

Recovery preserves a verified snapshot of the entire old state and its modes.
The stable thread container must never disappear in a way that lets an older
MCP process recreate a fresh legacy journal. A versioned marker fences older
code; new code normalizes the active native binding before passing it to ordinary
native execution and control paths.

Use a stable lock outside movable generation state, with bounded acquisition.
All participating model operations and recovery share that boundary. Revalidate
the active generation and native caller before intent writes. Recovery must
survive interruption between preparation, archive verification, fresh-state
creation and atomic selection. A repeated committed operation returns its
receipt; conflicting or stale previews refuse. Never replay a send to recover
its receipt.

Historical references keep their original binding and generation. Fresh
references cannot reuse an old bare reference for another object. Old labels
must not automatically select the new incarnation of a similarly named peer.
Historical inspection can use explicit same-conversation history authority;
historical mutation and continuation remain unavailable.

Read archives through a genuinely read-only path, not the normal Store constructor
that initializes/migrates schemas and WAL settings. Missing journals or archives
remain unavailable and are never recreated. Bound pages and displayed text;
report incomplete coverage. Returning-to-work answers must disclose historical
unknown outcomes rather than interpret an empty fresh journal as full completion.

Recognize events belonging to previous incarnations. A late old callback cannot
become unclassified fresh input capable of registering a watch, reminder, renewal
or message. Preserve an already consumed native turn and its evidence; do not
interrupt it as a side effect of recovery.

Recover each endpoint separately. A sender's request to send a message is not
permission to rotate the recipient's state. Recovery itself sends no message,
restarts no observation and migrates no intent or references into fresh control.

## Using the source candidate

In a conversation connected to the candidate MCP, ask to diagnose its changed
owner. `owner_status` uses verified native caller metadata even when ordinary
tools refuse. An explicit recovery request permits `owner_recover` with the
unchanged `expected_preview` and `confirm=true`. Normal native tool approval
still applies; generated configuration does not silently add recovery to the
automatically approved watch/reminder controls. Recipient diagnosis is read only.

For operator diagnosis of one exact loaded conversation, from the source checkout:

```sh
rtk proxy scripts/codex-plus-owner --thread THREAD_UUID status
rtk proxy scripts/codex-plus-owner --thread THREAD_UUID recover --expected-preview PREVIEW_TOKEN --confirm
rtk proxy scripts/codex-plus-owner --thread THREAD_UUID status --category references --incarnation ARCHIVE_EPOCH
```

`--state-root` and `--socket` select an explicit existing environment; keep the
global options before `status` or `recover`. Recovery has no peer selector. Use
the returned archive identity and exact reference with `owner_status` to inspect
history; `message_status` also includes saved outgoing history and uses a separate
archive cursor after current receipts. A historic reference is not a control for
fresh work. Re-run discovery and choose the resulting fresh reference instead.

Existing manual incident archives are not imported automatically. This source
work does not alter those archives or reset the already recovered conversations.

## Acceptance gates

Fixture acceptance covers both endpoints; settled versus live/uncertain work;
held locks and PID reuse; changed host/user/namespace/socket/thread; malformed or
missing state; stale previews; repeated apply; concurrent send/recovery; crash
boundaries; immutable archives; reference identity and missing-history behavior;
and late callback refusal. Assert native write/source-start counts as well as
returned receipts. Keep existing worker checks separate from watch evidence.

The proposed native acceptance uses two fresh owned independent conversations,
at most eight started native turns and two peer messages, including cleanup.
It uses isolated candidate state and session-local MCP configuration under the
existing owner. Synthetic stale bindings exercise caller and recipient recovery;
real session state, installed code, native owners and report servers are preserved.
No daemon restart or real workload is needed. Record actual admissions, handling,
uncertainty and cleanup separately. Do not replay the recovered incident.

Run focused fixtures first, then the full meaningful suite, source inventory,
whitespace checks and an external Pages build. Verify relocated runtime MCP/CLI
packaging independently. Publication, managed pins, live installation and personal
use acceptance remain separate gates after the reviewed source candidate.

## Implementation and evidence

The Luna goal loop implements this contract on an isolated worktree from
maintained main. Luna supplied the recovery/archive core and its initial safety
fixtures. The primary integrated model tools, CLI and packaging, reviewed the
failure boundaries and completed additional cross-endpoint and corruption cases.

The initial reviewed candidate passed all **348 fixture tests**, including 22 dedicated
recovery tests, plus the 128-file inventory and whitespace checks. The external
Pages build verifies 234 local links/assets/anchors. Runtime packaging retains
the exact preview.9/.10 inventories for rollback verification; recovery approval
is not silently added to existing auto-approved controls.

The final isolated runtime is source `ae108c7d68513ceb81803df284cd146444b30c37`,
with 25 payload members plus its manifest. Two builds match SHA-256
`763adea15542fed9d147f0e36414bbf33892fc6e058cf19f5c1ba945270d7444`.
Relocated installation verifies, and the new verifier accepts the actual
preview.10 runtime/report payload members. Pre-existing incident bytecode in the
managed runtime was preserved; its extra-file inventory finding was not cleared
or normalized into an installation pass.

The bounded native recipe completed on the existing Codex **0.165.0** owner:

| Scene | Result |
| --- | --- |
| Stale caller | Normal discovery refused, then native model calls to bootstrap status and explicit clean recovery succeeded. |
| Stale recipient | Discovery/inspection worked after caller recovery; the send refused before registration and the model identified the recipient boundary. |
| Independent recipient recovery | Explicit clean recovery succeeded; the saved outgoing receipt remained readable as accepted with unknown native turn completion. |
| Fresh messages | Two separately authorized information messages were admitted and acknowledged; both callback turns completed. No refused/uncertain send was automatically replayed. |
| History and cleanup | Both archives verify, original legacy journal bytes remain identical, and the seeded acknowledged outcome remains unknown. Both actors are archived/unloaded; no fixture MCP or coordinator remains. The original owner and both real incident archives are unchanged. |

The recipe used **seven completed native turns**, including two message callbacks,
two explicit clean rollovers and two fresh messages. There were no provider-failed
turns. The stale state/history was invented; the test did not replace a live daemon
or modify a real conversation. All model inference in the recipe used Luna.

Initial rollover/delivery used the immutable `01e19be` candidate. A subsequent
diagnostic wording fix removed nested caller instructions from recipient errors;
its regression passes, and fixture configuration then selected the final `ae108c7`
package for receipt inspection and the second message. Both owned adapters
reported preview.11 and 17 tools. Reported version/configuration is separate from
loaded-memory payload attestation; no general process-memory verification is
claimed. The control and delivery paths were unchanged by that wording fix.

Private fixture receipts and raw captures remain outside committed source under
the owner's repair-evidence directory. This pass does not establish long-run
reliability, an actual under-load owner replacement, general 0.165.0 compatibility,
physical TUI behavior or personal UX acceptance. The release compatibility
baseline remains 0.162.1.

Only positively loaded recovering callers are needed. Settled cached outgoing
receipts do not require loading closed peers. Missing or corrupt archives report
unknown history and never recreate it. Unselected staging left by an interrupted
preparation is retained rather than broadly deleted; only verified preparation
matching the exact operation is reused. This is not an automatic cleanup or
quarantine service.

The original older report checkout, existing worktrees, managed installations and
the recovered incident archives are preserved. Publication and deployment remain
outside this source loop.

## Release review (2026-10-29)

The separately authorized review/publication pass found and fixed two refusal
gaps before release: a malformed saved boot identity could be mistaken for a
reboot, and unrecognized event start/outcome states could pass the clean-state
gate. Boot identities must now be canonical nonzero UUIDs, agree between the
stable selector and selected epoch, and match the captured boot again before
selection commits. Unclassified journal states refuse recovery; acknowledged
events with a null final turn outcome remain eligible and retain that unknown.

The final source gate passes **351 tests**, including 25 recovery and 48 model
tests, plus the 128-file inventory and whitespace checks. The external Pages
build verifies 234 local links/assets/anchors. These final review fixes have
fixture coverage; the closed seven-turn native sample above was not reopened and
does not qualify this later revision through a new model trial. Worker identities,
explicit workflow invocation and existing approval preferences remain unchanged.

Publication, fetched-artifact verification and scoped managed rollout are
subsequent gates. No live incident recovery or daemon restart is part of them.

## Preview.11 publication and managed rollout

Completed 2026-10-29 under separate review/commit/push/publish/deploy authorization.
The immutable release is **v0.1.0-preview.11**, source
`5c9ec1d4368d6c5908f6a041f3081349fa5b2fd6`. All five assets match two independent
builds and fetched-artifact verification. Exact-main CI passed on Python 3.11 and
3.14. Pages publication succeeded and all 11 public pages/assets matched the
candidate bytes. Later receipt-only documentation does not change the release.

| Component archive | SHA-256 |
| --- | --- |
| Workers | `bb7b0eee80ed18b2915ac23d99d3dc368314492d807ab432351629dbd7f1f8d8` |
| Monitoring | `5d5ae50dc7362eccbd4cbcac9070786ab71470185f9891cec50d77abf933f031` |
| Reporting | `2601dd594dd57eba20b2ea87064e103b1f2f4da468b835667fff81a0a501c885` |

Dotfiles pin commit `68d3480263bf9d0c2411322907ac69d9281b831b` updates published
URLs/revisions/checksums and validators together, and adds the stable operator
helper link. The full dotfiles check and isolated report installation on all
three profiles pass. Existing worker/skill identities and nine approved controls
remain unchanged; `owner_recover` retains normal native approval.

Scoped status, diff and script-excluded dry-runs preceded each host's apply.
Runtime/report payloads and worker provenance were installed and checked against
the fetched archives before changing selectors. Exact inventories, bytes and
modes pass on Snap, Starship and Carbon; the existing worker payload bytes are
unchanged. Old runtime/report trees, including Starship's pre-existing incident
bytecode, remain identical. All scoped diffs converge.

Fresh stdio initialize/tools-list checks through each installed native MCP command
report preview.11 and **17 monitoring/four report tools** in Snap OSS, Snap work,
Starship and Carbon. These are protocol/installation checks, not new native model
turns or proof that already loaded processes adopted the release. No global MCP
refresh, native daemon/server restart, real-session reset, recovery or intent
replay occurred during rollout.

All **252 protected paths** match baseline bytes/modes, including native config,
auth, agents, skills and report config. All 13 baseline native Codex executable
processes retain their PID/start-ticks/executable identities. The broader process
census also records seven Python/shell processes ending during the elapsed work;
it does not claim every initial MCP/helper remained alive. The rollout issued no
stop/restart command. Surviving report servers retain their exact identities.
CLI/owner versions remain 0.165.0 across the four contexts; the release's qualified
native baseline stays 0.162.1.

HTTP baselines are unchanged: Starship and Snap work return 200 with identical
catalog hashes; Snap OSS (`:8787`) and Carbon report URLs were unavailable before
rollout and remain so. Their service availability is not an acceptance pass or a
new regression attributed to this update. Repair evidence and private captures
remain outside source under `owner-recovery-release-20261029T095309Z`.
