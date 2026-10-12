# Discovery and peer-watch pass

Started 2026-10-12 from planning checkpoint `aef8adf`, with execution requested
as an ordinary goal loop and incremental commits. Human TUI acceptance and
installation remain later scope. Existing sessions are passive observation sources;
all experimental delivery and state-changing checks use task-owned synthetic sessions.

## Research gates

The installed CLI and existing owner both report `0.162.1`. Generated experimental
schemas and bounded passive daemon reads establish the following starting point:

| Gate | Finding | Limit |
| --- | --- | --- |
| Delegation provenance | `source` distinguishes native ordinary origins from the structured `subAgent` family. `parentThreadId` is documented in the installed schema as a subagent parent; `forkedFromId` describes fork ancestry separately. | Synthetic regressions will cover missing/conflicting fields and all subagent variants; no child is spawned for this research check. |
| Active discovery | Loaded inventory was complete in the sampled response; four existing threads were positively loaded and read. Ordinary samples reported `source=vscode`, `threadSource=user`, no parent, with idle and active phases. | A fresh bounded inventory is needed for each selection; titles/history or a CLI-only filter are insufficient. |
| Passive history/goal | `thread/turns/list` with one summary turn returned bounded recent user/agent items and cursors; `thread/goal/get` returned the selected peer's goal. Neither requires peer resume. | A bounded history window is not an occurrence replay guarantee or proof of task completion. |
| Host read path | The existing private Unix client initialized and performed loaded/metadata/history/goal reads without subscribing/resuming any observed thread. Listener identity stayed unchanged. | Restricted command-source access remains unsupported; the adapter must run in the coordinator's qualified host path. |
| Messaging | Retain the earlier native queue message/reply evidence and current queue schema with client message IDs. | The selected route receives a short synthetic integration check later; no existing session has received experimental input. |

Generated schemas, private snapshots and the owner baseline are retained in a
fresh private study directory outside source. No real title, transcript, original
identifier or credential is committed. These gate reads started zero model turns
and admitted zero messages. The requesting thread and existing daemon were preserved.

## Implementation and acceptance

The discovery/read slice adds a passive PeerReader and local peer CLI. Sixteen
new regressions cover native subagent variants, child/name collisions, independent
forks, duplicate roots, incomplete pages/metadata, unavailable targets, owner
replacement, passive method enforcement, shared deadlines and truthful bounded
snapshot/reply semantics. Existing sessions supplied a read-only CLI list/read
smoke: three independent peers excluding the caller, no sampled children or
unclassified records, complete loaded inventory, and one bounded history turn.
The original listener identity was preserved. These checks admitted no messages
and started no model turns. No sampled native child means native child behavior
is supported by the installed schema and offline regressions, not a new live spawn.

The coordinator now supports passive peer snapshots and one-event correlated
message registrations. Peer identity is separate from delivery identity; both are
frozen to one owner. Peer loss/provenance changes require explicit recovery, and
renewal cannot retarget. Cancellation stops the reader without a peer RPC write.
Message registration is atomic and returns durable IDs even if coordinator startup
is unavailable. The native delivery path rechecks independent provenance.

All 127 offline tests pass, including thirteen peer-watch/message cases and three
new CLI boundary cases. The 52-file inventory and whitespace checks pass. Existing
command/watch/wakeup and worker tests remain separate and passing. The capped
synthetic native batch and final review are next; this is not yet native acceptance
of the new peer-watch/message surface.

## First native batch and review correction

The first fresh batch is closed at **3 admissions / 6 started turns**. The quiet
watch case passed: B's message carried its client ID into a completed recipient
turn/reply; A woke on the selected reply, read B once, acknowledged its exact event
and completed its response. Initial unchanged observation caused no model turn.

The busy case's harness asserted admission immediately after observing a pending
journal event, before the next coordinator delivery tick. It therefore failed to
capture a queue-while-busy window and is not counted as native busy acceptance.
This was an assertion/timing error, not a provider failure. Cleanup stopped owned
coordinators, cancelled the pending observation, interrupted only the unfinished
synthetic A foreground turn and archived the two fixtures. No cleanup errors were
reported; the original daemon identity was preserved.

Independent review also reproduced reply-window churn: inserting a new active
turn could evict an older reply and change a multi-reply snapshot without any new
reply. Reply watches now compare the latest completed final reply, with a regression
for that case. Snapshot coverage still explicitly permits missed intermediate events.

A separately prepared targeted recipe will check admission-aware busy delivery,
cancellation and explicit coordinator recovery with new synthetic actors. Its
ceiling is five admissions/eight turns; all prior usage remains counted against
the overall pass ceiling of eight admissions/sixteen turns. The closed first batch
is not reopened, and no provider failure or harness failure replenishes the limit.
