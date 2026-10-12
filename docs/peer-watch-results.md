# Discovery and peer-watch pass

Completed 2026-10-12 from planning checkpoint `aef8adf`, with execution requested
as an ordinary goal loop and incremental commits. A subsequent controlled native
TUI walkthrough is recorded below; Bryan's UX assessment and installation remain
later scope. Existing sessions are passive observation sources;
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

All 128 offline tests pass, including eighteen peer discovery/read cases,
thirteen peer-watch/message cases and three new CLI boundary cases. The 52-file
inventory and whitespace checks pass. Existing
command/watch/wakeup and worker tests remain separate and passing. The capped
synthetic native evidence and review below qualify the local surface within the
recorded Linux/full-access/native 0.162.1 boundary.

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

The first reply-window correction failed the full suite for an empty history:
the selected reply limit was initialized only inside the turn loop. That checkpoint
was committed before honoring the failed check. The follow-up initializes the limit
before iteration; the existing empty-baseline watch regressions cover this case.

A separately prepared targeted recipe checked admission-aware busy delivery,
cancellation and explicit coordinator recovery with new synthetic actors. Its
ceiling is five admissions/eight turns; all prior usage remains counted against
the overall pass ceiling of eight admissions/sixteen turns. The closed first batch
is not reopened, and no provider failure or harness failure replenishes the limit.

## Targeted native acceptance and final review

The separately prepared recipe is complete and closed at **5 admissions / 8 turns**.
Combined usage across both recipes is **8 admissions / 14 started turns**, including
the first harness attempt and its unfinished synthetic foreground turn. There were
zero provider failures. The targeted recipe's eight turns all completed normally.

| Case | Evidence | Limit |
| --- | --- | --- |
| Same-daemon independent actors | Both new synthetic actors were positively loaded and independently classified under the original daemon. | API-created ordinary sessions, not a new human TUI walkthrough. |
| Busy delivery | The watcher event had known native admission while A's foreground turn was active, with no recipient turn yet. The foreground completed normally, followed by the correlated read/ack callback. | Protocol/history receipts qualify ordering; draft/UI behavior remains human acceptance. |
| Explicit stop | A second quiet watch was cancelled before B's message. It emitted no event as B handled that message normally; B's goal state was unchanged by cancellation. | Task-owned synthetic scope; no action against real sessions. |
| Coordinator loss/recovery | Killing only the exact owned A coordinator left a cached unknown-source receipt and preserved its baseline. Explicit recovery produced a declared-gap event, then observed and handled a new B reply. | Snapshot continuity is explicit, not missed-occurrence reconstruction. |
| Handling/correlation | Message/watch event IDs matched persisted native user-message client IDs and completed turn IDs. Actors acknowledged exact events and returned the expected fixture tokens. | Handling does not prove any external task effect. |
| Real active peer observation | Three bounded samples of one actual active independent peer used only loaded/read/history/goal RPCs. Selected facts stayed unchanged, with zero messages/model turns. | Passive reader sampling and earlier discovery smoke; experimental delivery always used synthetic actors. |

Final review tightened exact-name resolution: an unclassified same-name record or
a truncated title cannot masquerade as a unique exact independent-session match.
Exact verified UUID selection remains available. Reply watches compare the latest
completed final reply; idle, native turn completion and child completion do not
invent a task outcome. Older intermediate replies can be missed by a bounded
snapshot window, and that coverage limit is reported.

A zero-turn fork metadata check against an already archived owned fixture was
refused by the daemon. It was not unarchived or retried, and no fork was created.
Independent-fork and native subagent classification therefore rely on the installed
schema plus controlled regressions, not a newly exercised native fork/child lifecycle.
The native task-tool facade itself remains unqualified beyond earlier listing;
this candidate uses the directly qualified native RPC/queue route.

## Cleanup and deferred acceptance

All four synthetic actors were archived and freshly read as notLoaded. All fixture
coordinators are offline, journals have no active/replacing intent or pending
renewal, and all known admitted inputs have a consumed turn receipt or withdrawal
receipt. The first recipe's cleanup interruption was confirmed as interrupted in
persisted native history. No pending owned input or cleanup error remains. The
original listener PID/start/executable identity and positive loaded membership of
the requesting conversation were freshly verified preserved.

No daemon restart, global trust/config edit, real-session write/interrupt, worker
change, installation, push or publication was performed. Private study recipes,
raw snapshots and histories remain outside source. The public report carries only
sanitized findings. Local source/artifact acceptance does not establish an installed
integration, restricted calling access or cross-host support.

The automated objective is complete. The prepared
[peer TUI checklist](watch-candidate.md#deferred-peer-tui-walkthrough) covers natural
selection, understandable hierarchy, draft/input preservation, Esc, explicit stop
and viewer detach. Human acceptance, longer operation, native child/fork lifecycle,
full cursor replay and managed packaging remain subsequent scope. Native /exit
confirmation is not implemented by this helper.

## Controlled native TUI walkthrough

On 2026-10-12 Bryan viewed Snap's native TUI over SSH from Starship and requested
primary-driven controls. Fresh independent synthetic A/B actors used the existing
0.162.1 daemon and appeared side by side in tmux. The primary supplied prompts and
the fixture draft; Bryan did not need to copy prompts between sessions. These are
native TUI checks with driver-supplied input, rather than a claim that Bryan personally
typed or accepted every step.

The fresh ceiling was **8 automatic admissions / 16 started turns**, with watches
bounded to 120 seconds and two events. Usage reached that ceiling: 15 turns completed,
one foreground turn was interrupted with native Esc, and none failed. All eight
admitted inputs have completed turn receipts; seven were acknowledged. The setup
refusal below remains unacknowledged and counted. No replay replenished the allowance.

| Case | Native evidence | Limit |
| --- | --- | --- |
| Discovery | A resolved B's exact title through passive discovery and reported its independent identity, no parent and idle status. | No native child was created; hierarchy and ambiguous-name cases retain earlier schema/regression evidence. |
| Draft | An unsent fixture draft survived the queued setup message and, after direct watch setup and restoring the draft, B's reply/read/ack callback. | Real native composer with driver-supplied input; typing ergonomics and Bryan's assessment remain separate. |
| Esc | An actual Escape key interrupted A's foreground turn. Its watch stayed active and handled the next B reply. | Turn interruption and watch continuity, without inferring background-shell survival. |
| Explicit stop | A cancelled a fresh selected watch while B's synthetic work stayed active. B completed normally, kept its goal state and handled a later message without another A event or replacement watch. | Task-owned work; native child orchestration was not exercised. |
| Viewer detach | Closing only A's viewer preserved the daemon/watch. A handled B's reply without its viewer; reattachment displayed that history. | Existing owner/client connections remained; no cold-recovery or native-exit claim. |
| Shutdown | Preview required confirmation and preserved live intent when left unconfirmed. Confirmed scoped cleanup then stopped the helpers. | Candidate shutdown preview, without native `/exit` interception. |

### Message delivery and task authority

The first queued setup reached A while its draft survived, but A refused to start
a watch because its last direct instruction said "don't start a watch yet". It
completed the native turn without acknowledging the event. The driver initially
waited for an acknowledgement that would not arrive, then inspected the actual
reply and issued a direct TUI watch request instead of replaying the message.

Successful delivery does not establish permission to change the recipient's task.
Observation/follow-up text does not confer new authority. Existing authorized watch
callbacks and B's explicitly scoped synthetic message handling succeeded. General
independent-peer task assignment/control remains a design question; direct TUI
input does not qualify authority transfer through messages.

### End state and remaining acceptance

All coordinators and the fixture event keeper are stopped, with zero active or
replacing intent. Fresh checks preserved the original listener PID/start/executable
identity and the requesting conversation's loaded membership. Only idle A/B viewers
remain for Bryan to inspect; no automatic watch, renewal or follow-up remains. This
recipe is closed; further automated turns need a separately bounded recipe.

Private launchers, journals, captures and identities stay outside source. Interactive
launchers attached their controlling terminal because RTK captures stdout; remote
resume retained actor permissions because native remote resume rejects overrides.
No daemon restart, global trust/config edit, real-session message/interrupt,
installation or publication occurred.

Technical draft/Esc/stop/detach/shutdown checks passed. Bryan's UX feedback, human
input-order assessment, native child/fork lifecycle, longer operation and managed
packaging remain subsequent scope.
