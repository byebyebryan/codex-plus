# Native owner recovery

The 2026-10-29 investigation found a correct ownership refusal with no supported
way to resume fresh Codex Plus operations after a daemon incarnation changes.
The selected implementation scope is **explicit clean rollover**, diagnosis and
inspectable history. It does not include moving unresolved intent onto a new
owner, quarantine of unsettled work, publication or managed deployment.

This is the unreleased preview.11 source-candidate contract. Installed preview.10 remains unchanged;
its native qualification baseline and the bounded later-version evidence retain
their limits. Implementation and acceptance results are recorded below as they
are established.

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

The reviewed candidate passes all **348 fixture tests**, including 22 dedicated
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
