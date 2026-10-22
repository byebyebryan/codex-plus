# Native alignment and natural follow-up results

Completed 2026-10-22 on Snap. This is the source candidate from the
[planned pass](codex-plus-plan.md#next-pass-native-alignment-and-natural-follow-up),
not a new release or managed installation. Installed components remain
**v0.1.0-preview.9** from `0ec803d`; existing MCP processes retain their captured
code. No native owner, report server or managed service was restarted.

## Decisions

Keep the native Codex workflow and current coordinator. The useful changes fit
the existing 15 monitoring tools: bounded reminder history, rediscoverable
outgoing receipts, clearer recap/quiet-follow-up instructions, and a small doctor
extension using native MCP metadata. No new tool, database schema, service,
capability registry or worker workflow was added.

| Research question | Finding and decision |
| --- | --- |
| Can native facilities replace custom machinery? | Retain native thread/goal/execution ownership and the passive peer mechanism. The installed experimental message-board flag is disabled and its generated API has no corresponding communication RPC. No passive subscribe method establishes an equivalent replacement for polling. Defer replacement until a supported surface covers the contract. |
| Do ordinary requests compose the tools? | The owned walkthrough resolved a packaging peer, sent attributed information, observed a blocker, scheduled a later configured MCP check and stopped supervision from ordinary language. Refine instructions to suppress irrelevant chat updates; keep strategy with the model. |
| Can a recap use existing state? | Yes, after closing two reproduced gaps. Page reminders using the existing registration store; let `message_status` rediscover the caller's saved outgoing references. No new summary tool or inbox. |
| Are control and return-to-work boundaries clear? | Native foreground interruption preserved observation. Explicit stop cancelled its selected lineage; helper loss became uncertain coverage; expired recovery refused. Actual compaction completed. Require receipt rereads rather than trusting retained prose. |
| Can diagnosis distinguish selection from loaded code? | Native `mcpServerStatus/list` exposes reported MCP versions for an exact loaded conversation. Use that evidence in the doctor, retaining unknown states and the distinction from payload verification. |

## Native and custom responsibilities

Snap's client and existing owning daemon both reported **Codex 0.163.0**.
The installed release's recorded qualification baseline remains **0.162.1**.
This pass supplies bounded evidence on 0.163.0, not blanket compatibility.

| Responsibility | Owner and retained boundary |
| --- | --- |
| Conversation, goal, model turn, approvals and execution policy | Native Codex. Plus binds the existing loaded thread and exact owner. |
| Reading independent peer state | Native loaded inventory, passive reads and goal/status APIs, with Plus classification and bounded presentation. Ordinary discovery excludes children and uncertain classifications. |
| Peer delivery and later follow-up | Native queue admission; Plus freezes identities, holds bounded intent and records handling/delivery uncertainty. Admission is distinct from acceptance and task success. |
| Endpoint/script observation | Model-selected command/script under verified native session permissions. No new adapter framework. |
| Configured MCP inspection | A scheduled native model turn calls the normal configured tool. No direct MCP RPC bypass. |
| Persistence outside model context | Existing private journals and reference tables. No duplicate task database. |
| Reports and workers | Existing independent reporting and explicitly invoked worker components; identities and behavior unchanged. |

The installed generated schema and native experimental-feature inventory were
checked against the official [app-server documentation](https://learn.chatgpt.com/docs/app-server)
on 2026-10-22. Native status events and `thread/resume` do not establish passive
observation of another thread without lifecycle effects. The disabled
message-board flag is an investigation lead, not replacement proof. No
experimental feature was enabled globally.

## Reproduced gaps and candidate changes

### Bounded reminder inspection

A fixture with 400 settled reminders and one active reminder produced **105,108
bytes** through the old `wake_list`. The same fixture produces **294 bytes** in
the candidate's default view, retaining all **401** registrations.

`wake_list` shares registration pagination with watches: current work and
unresolved receipts first, explicit history, at most 50 registrations per page.
It exposes overdue/expired bounds, stale coordinator evidence, control reasons,
delivery, handling and withdrawal uncertainty. Prompt display is clipped;
history is retained. Existing watch cursors remain compatible, and reminder
cursors cannot be reused as watch cursors.

### Outgoing receipt rediscovery and recap

Previously, `message_status` required a reference that could disappear from
model context. The existing store retained those references. Omitting `message`
now lists this caller's recorded outgoing receipts, newest first, with bounded
pagination. Exact-reference inspection still works.

Reopening the API recovers references without sending or retrying. Sender
ownership is checked. A missing recipient journal reports unknown delivery and
handling without recreating it. This is a same-conversation outgoing receipt
view, not a cross-conversation inbox or fresh recipient activity check.

The first native recap after compaction answered accurately from retained
context but did not reread receipts. That did not prove current inspection.
Guidance was tightened around pending-work questions. The repeated request
called `watch_list`, `wake_list` and argument-free `message_status`; it reported
no active follow-ups and identified packaging's blocker as the last confirmed
state, with cached evidence and no fresh packaging check.

### Quiet useful follow-up

The first watch generated unnecessary "still pending" chat. Guidance now asks
the model to choose relevant signals and, after inspection and acknowledgement,
finish quietly when nothing useful changed. Renewal may also be quiet; ending
coverage or needing a decision should be explained.

In the affected native repeat, a checksum blocker produced a useful update. A
later duplicate/phase callback inspected and acknowledged the event with no
agent message. This proves a quiet callback is possible, not a noise rate or
zero model cost. The finite event allowance still ends observation unless
explicitly continued.

### Read-only loaded-version diagnosis

For `CODEX_THREAD_ID` or explicit `--thread`, the doctor verifies the exact loaded
conversation, then reads native MCP metadata for `codex_plus` and `html_report`.
It compares a connected server's reported version with the selected component.
Missing metadata, disconnected servers and unloaded conversations remain
unknown or unavailable. Live inspection of this conversation reported both MCPs
connected at the selected preview.9 version.

No conversation is resumed, server refreshed or owner started. Reported version
alignment does not verify payload bytes or describe every session. `--no-native`
skips the check. Reporting-only installs work without monitoring's optional
native-introspection module. Client initialization also reports the unified
package version instead of a hardcoded base version.

## Owned native walkthrough

Two fresh independent conversations used the existing daemon and source MCP
candidate. Writes were restricted to those actors; a private configured MCP
fixture represented CI. Active user conversations were not messaged or
interrupted. Transcripts, actor IDs, journals and probe scripts remain private.

| Prompt or controlled event | Observed result |
| --- | --- |
| "Watch the packaging session and tell me if it gets blocked." | Contextual discovery selected the intended independent actor. Bounded registration returned promptly without IDs, JSON or a polling recipe in chat. |
| "Tell it the checksum changed." | Exactly one attributed information message; the receiver recorded handling within its existing task. No acknowledgement ping-pong or new task authority. |
| Packaging reports a checksum mismatch | The watcher inspected and reported the blocker. An irrelevant later callback completed quietly after inspection/acknowledgement. |
| "Check CI again in a little while." | A reminder returned promptly; its later native turn acknowledged and called configured CI inspection once. The source still said running/old checksum, and the model reported that result. A subsequent fixture change to passed was not claimed as observed. |
| "Stop watching that." | The selected lineage and continuation were cancelled; pending lifecycle input was withdrawn where possible. Packaging's work remained intact. A later fresh watch followed a new explicit request. |
| Owned native compaction | A completed `contextCompaction` item established actual compaction; conversation scope and saved references survived. |
| "What am I still waiting on?" after refinement | Watch/reminder/outgoing-receipt reads preceded the recap. Cached task facts were identified instead of presented as a new source check. |
| Interrupt an owned foreground command | Native `turn/interrupt` ended the command while the active watch and same coordinator kept running. This is native interruption evidence, not a physical Esc/TUI test. |
| Abrupt loss of the owned test coordinator | Inspection showed offline/unknown coverage and the last cached running state without restarting anything. The model disclosed uncertainty. |
| Explicit recovery after original lease expiry | Recovery refused; the model inspected the ended registration and left it ended without replacement. Successful recovery inside an unexpired lease was not retested. |

The test MCP configuration initially retained a disabled override; correcting
only the owned actors exposed the candidate tools. This was harness setup, not
a managed installation change. Those actors alone reconnected for revised
guidance. Final explicit stop found no active watches or reminders; their
coordinators had exited. The test conversations were archived after completion.

## Validation and limits

The candidate passes **312 fixture tests**, including reminder bounds/history,
receipt rediscovery after reopening, pagination and sender isolation, missing
journal behavior, loaded metadata uncertainty, reproducible packaging and
reporting-only relocated diagnosis. Worker validation remains separate from
native watch evidence. The clean source inventory passes with 124 files; the
Pages build passes for the walkthrough and eight guides, checking 227 local
links, assets and anchors. No presentation controls or layout were changed, and
this pass does not claim new browser or public-deployment acceptance.

The canonical checkout contains two pre-existing untracked bytecode files.
They are preserved; inventory validation uses a clean candidate copy. Private
configuration and bytecode hashes/modes, plus the native listener identity, are
checked against the starting baseline. No managed apply, release publication,
global MCP refresh or native daemon restart belongs to this pass.

The small native sample does not prove provider recovery, cross-host behavior,
unattended reliability, lossless peer-event capture, physical TUI draft/exit
behavior or Bryan's daily-use acceptance. Fixtures prove bounded pagination,
not that every natural recap follows every cursor. No new credentials, real CI
job or real release was involved. Retain the [soak checklist](soak-checklist.md)
for ordinary work and publish/version a new release before changing managed
pins; never overwrite preview.9 artifacts.
