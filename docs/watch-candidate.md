# Local watch coordinator candidate

Run `scripts/codex-plus-watch` from this checkout. This is a local Linux/Unix
candidate for the qualified `0.162.1` native app-server surface. Queue operations
are experimental. Worker identities and installed paths are unchanged. The separate
[runtime preview](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.1)
is published and verified; its managed rollout is prepared, with live apply deferred.

Bryan's controlled walkthrough found the current interaction hard to follow:
detailed watch instructions, exact destination titles and JSON prompts. The CLI
examples below expose the current low-level candidate. The
[next-pass plan](codex-plus-plan.md#next-pass-natural-requests-and-readable-peer-communication)
now has a tested local interface for ordinary requests, contextual peer selection
and readable event delivery. See the [interaction results](interaction-pass-results.md).
Native tool-output delivery failed its ordering gate; readable queue input remains
selected. The [runtime distribution guide](runtime-distribution.md) describes
the new preview artifact and installed capability path under qualification.

The coordinator owns one private state directory and one existing conversation.
It reuses that conversation's daemon for read-only observation commands and queued
input. It does not create a daemon, choose a saved session by name or automatically
load a cold thread. The model chooses scripts, filtering, cadence and follow-up.

## Passive peer discovery and inspection

### Session-local model interface

`scripts/codex-plus-model` is a local stdio MCP bridge around the existing
reader/coordinator. Its tools expose contextual peer discovery/inspection,
watch setup/list/cancel/renew, information/request sending, handling receipts and
one-shot reassessment. The model chooses detailed options; ordinary user requests
do not need exact titles, UUIDs or polling recipes. Use the reusable
`MODEL_GUIDANCE` in `codex_plus/model.py` as capability guidance once, rather than
inserting a setup/ack recipe into each prompt or callback.

The qualified attachment is a per-thread app-server configuration, with the existing
native daemon and ordinary TUI resume. For a separately authorized local fixture,
set a thread's `config` override as follows, replacing the private placeholders:

```json
{
  "mcp_servers.codex_plus": {
    "command": "/usr/bin/python3",
    "args": [
      "-B", "/home/bryan/code/codex-plus/scripts/codex-plus-model",
      "--state-root", "PRIVATE_STATE_ROOT",
      "--socket", "EXISTING_UNIX_SOCKET",
      "--allowlist", "PRIVATE_THREAD_ALLOWLIST",
      "--max-duration", "120",
      "--max-events", "2"
    ],
    "tools": {
      "watch_start": {"approval_mode": "approve"},
      "watch_cancel": {"approval_mode": "approve"},
      "watch_renew": {"approval_mode": "approve"},
      "peer_send": {"approval_mode": "approve"},
      "event_ack": {"approval_mode": "approve"},
      "wake_schedule": {"approval_mode": "approve"}
    }
  }
}
```

The allowlist is a private JSON array of fresh owned thread UUIDs. It restricts
callers and messaging destinations during experiments; other independent peers
may still be passive observation sources. These small bounds belong to the native
recipe, not the user's natural-language request. Source/command observers still
use the coordinator's read-only filesystem/network policy. The host-side MCP bridge
does not claim restricted-source socket access from that policy.

Approval settings are explicit authorization for this bounded synthetic recipe,
not a global recommendation or authority supplied by incoming text. The bridge
advertises truthful read-only hints for discovery/inspection and cached receipts;
watch/message/handling controls remain writes. A read-only caller with `never`
approval rejected unannotated discovery before the bridge ran. Codex supports
[per-tool MCP approval settings](https://learn.chatgpt.com/docs/extend/mcp?surface=cli);
the fresh native recipe qualified this session-local configuration while retaining
the caller's read-only filesystem sandbox. Controls were not relabeled as reads.

Native MCP metadata supplies matching thread/session and turn identities. Tool
arguments cannot choose the caller. Each operation positively validates the loaded
independent caller and owning listener, retains immutable private state binding,
and verifies the calling turn. Peer references/labels survive tool calls and never
retarget when a name is reused. Children and unknown classification are not ordinary
peer references. Context reads exclude user prompts and tool outputs.

Routine tool results are readable text. `event_ack` handles the unique incoming
event in the current native turn and records received/accepted/declined separately.
An outcome cannot be overwritten, and a conflicting prior consumed-turn receipt
cannot be relinked. `message_status` reads cached handling outcomes without sending
replies. No receipt confers task authority or proves an external effect.

The same interface is included in the immutable runtime preview. Its installed
qualification is recorded in the [distribution report](distribution-pass-results.md),
with the earlier [interaction evidence](interaction-pass-results.md) retained.
Use the [runtime guide](runtime-distribution.md) for installation/configuration;
the examples here remain low-level source diagnostics. Managed live deployment,
cold recovery and native `/exit` interception are not implied.

### Low-level source CLI

The local peer helper reads the current existing daemon without loading, resuming
or subscribing to a peer. It excludes the calling session and known delegated
children from ordinary peer selection. Unknown classification and incomplete
inventory remain visible; exact name resolution refuses ambiguity or an incomplete
inventory. Native delegation provenance is separate from independent fork ancestry.

Use exact identities from the returned inventory:

```sh
rtk proxy scripts/codex-plus-peer list
rtk proxy scripts/codex-plus-peer list --include-children
rtk proxy scripts/codex-plus-peer resolve --name 'EXACT_SESSION_TITLE'
rtk proxy scripts/codex-plus-peer read PEER_UUID --turn-limit 3
```

An explicit `--socket` and `--caller` can select the existing owner/caller; otherwise
the running-daemon version query and `CODEX_THREAD_ID` provide defaults. This is
same-daemon discovery, not a saved/fleet census. Reads include bounded agent/plan
text, runtime phase and native goal status, excluding user prompts/tool outputs.
Truncation and bounded snapshot coverage are declared. No task outcome is inferred
from idle, a completed turn, or a child completion.

See [the peer-pass report](peer-watch-results.md) for current evidence.

## Peer observation and correlated messages

Bind the coordinator state to destination A using the normal binding command.
Select an exact independent B from passive discovery. A peer watch reads B through
the host-side reader and delivers selected changes into A:

```sh
rtk proxy scripts/codex-plus-watch --state STATE_A watch_start --peer PEER_B_UUID --interval 5 --signals reply,needs_input,goal --duration 120 --limit 2 --quiet-initial --followup 'Read fresh peer state and follow up under the existing request'
rtk proxy scripts/codex-plus-watch --state STATE_A renew --id WATCH_UUID --peer PEER_B_UUID --interval 10 --signals reply,goal --duration 120 --limit 2 --quiet-initial
```

Supported signals are phase, needs_input, goal, reply, progress and turn. Reply
requires an explicit final agent message in a completed native turn; progress uses
bounded commentary/plan content. Each is native evidence, not a universal task
outcome. The model chooses signals, interval, initial emission and follow-up.
Intervals range from one to 3600 seconds; history windows range from one to ten
turns, with default three. Snapshot records remain capped at 4 KiB and declare
truncation, snapshot-only coverage and a continuity gap on explicit recovery.
Reads do not resume, subscribe to, enqueue into, change the goal of, or stop B.

Existing watch status/cancel/ack/recover/shutdown apply. Lost peer access or changed
provenance stops observation with a lost-source receipt and requires explicit
recovery. Renewal cannot change the frozen peer or switch source type. Cancellation
and shutdown stop the local reader and reconcile only destination A's owned input.

For an authorized message to B, bind a separate coordinator state to B and use:

```sh
rtk proxy scripts/codex-plus-watch --state STATE_B peer_send --message 'MESSAGE_WITHIN_EXISTING_SCOPE' --duration 120
rtk proxy scripts/codex-plus-watch --state STATE_B status MESSAGE_REGISTRATION_UUID
```

The returned registration/event IDs identify durable intent. Admission, native
turn identity/outcome and acknowledgement remain separate. A startup failure returns
those durable IDs with registered_coordinator_unavailable; inspect them rather than
repeating the send. Acknowledgement proves handling only. Inspect the recipient's
bounded history using the correlated turn ID to identify its reply; there is no
automatic reply protocol or expansion of the recipient's authorization.

During this pass, real active sessions are read-only sources. Experimental messages,
follow-ups and state changes target synthetic sessions. Native integrated acceptance
and controlled TUI evidence are recorded in the peer-pass report; personal UX
assessment and the remaining input/hierarchy checks remain later.

## Deferred peer TUI walkthrough

A primary-driven walkthrough is now recorded in the
[peer-pass evidence](peer-watch-results.md#controlled-native-tui-walkthrough).
Bryan viewed A/B side by side over SSH; technical draft preservation, Esc, scoped
stop, viewer detach and shutdown preview passed with fixture input supplied by the
primary. Queued setup could not override A's prior direct "no watch" instruction;
general task assignment authority through messages remains an open design question.
The checklist retains the remaining personal UX/input/hierarchy acceptance scope.

The automated peer-watch pass is complete. When Bryan is available, prepare fresh
synthetic A/B sessions in the same existing daemon and open A in its native TUI.
Keep any real session used as an observation source read-only; all deliberate
messages and test follow-ups target the synthetic actors.

1. Use natural language to select B from independent peers. Inspect children on
   request and check that ordinary matching never silently picks a delegated child
   or an uncertain/truncated same-name candidate.
2. Register a quiet peer watch, type a draft in A and cause a bounded synthetic B
   reply. Record whether the draft survives and earlier human input keeps its order.
3. Interrupt only a synthetic foreground turn with Esc; verify the independent
   watch remains registered and the next permitted observation follows up.
4. Explicitly stop the watch. Verify no new admission or automatic renewal, while
   B's work and native child orchestration remain available.
5. Detach A's viewer and inspect bounded source/delivery state. Preview coordinator
   shutdown, preserve work when declined, and verify scoped cleanup when confirmed.

Define a fresh small native recipe before further automated checks; completed
allowances remain closed. The controlled walkthrough leaves only idle viewers for
inspection, with helpers and the event keeper stopped and no active intent.
Do not infer human draft/UX acceptance or native /exit protection from RPC receipts.

## Binding and source setup

Use a private directory (0700), an exact loaded thread UUID and its requested Unix
socket. `CODEX_THREAD_ID` and the existing daemon's reported socket can supply
defaults, but both are validated before binding. State cannot silently rebind to
another owner or conversation.

Replace the placeholders below with your selected paths and IDs:

```sh
rtk proxy scripts/codex-plus-watch --state STATE bind --socket SOCKET --thread THREAD_UUID
rtk proxy scripts/codex-plus-watch --state STATE watch_start --cwd WORKDIR --duration 120 --limit 2 --followup 'Inspect this observation under the existing request' -- rtk proxy python3 -B -u OBSERVER.py
rtk proxy scripts/codex-plus-watch --state STATE wake_schedule --after 20 --duration 120 --prompt 'Inspect the run and choose whether further supervision is useful'
```

Registration returns its ID, frozen destination and effective bounds. Registration
is not a source-running or handling receipt. A coordinator starts lazily and is
reused for that state directory; concurrent launchers cannot acquire its owner lock.
It exits after ten idle seconds once intent and connected handling work have settled.
Unobserved admitted input retains its receipt, but does not keep the coordinator
alive beyond the registration's delivery window. Closing the coordinator does not
interrupt an already-started native turn.

Every source uses native `readOnly` filesystem policy with network disabled.
Calling setup requires the qualified host access path; it does not inherit that
read-only source policy. Restricted calling contexts failed the Unix-control probe
and remain unsupported without a separate host-side tool design. Managed MCP
credentials are not assumed available to a source.

Each nonempty UTF-8 line is an occurrence, including identical repeated lines.
stdout records are bounded to 4 KiB, cumulative stdout to 64 KiB and diagnostic
stderr to 16 KiB. Truncation, invalid UTF-8 and malformed selected snapshots stop
the source explicitly and expose source failure separately from job outcome.

Optional `--snapshot-fields status,progress` projects top-level JSON fields and
persists its comparison baseline with the pending event atomically. Timestamp
churn outside those fields stays quiet. The initial snapshot emits by default;
`--quiet-initial` chooses an initial quiet baseline. Task conditions and polling
still belong in the script. A line source needs no universal job schema.

The model chooses positive duration (up to 86400 seconds) and a finite event
limit (1–1000, default two). Native experiments stay within the separately agreed
120-second/two-event bounds; longer operation is not qualified by those tests.
`--notify-end` allows at most one additional source lifecycle notice, including
expiry, within a 30-second delivery window. It does not establish a watched-job
terminal outcome. One-shot timers admit at most one event and create no missed-run
backlog.

## Inspection and controls

```sh
rtk proxy scripts/codex-plus-watch --state STATE list
rtk proxy scripts/codex-plus-watch --state STATE status REGISTRATION_ID
rtk proxy scripts/codex-plus-watch --state STATE cancel REGISTRATION_ID
rtk proxy scripts/codex-plus-watch --state STATE renew --id REGISTRATION_ID --cwd WORKDIR --duration 120 --limit 2 -- rtk proxy python3 -B -u UPDATED_OBSERVER.py
rtk proxy scripts/codex-plus-watch --state STATE ack EVENT_ID
```

Use your actual source argv after `--`; the renewal example is a placeholder.
Renewal first stops/confirms the predecessor, then registers a linked replacement
with the supplied invocation and bounds. It cannot overlap the predecessor or
renew cancelled supervision. Cancellation covers the selected registration's
lineage, including replacements, and remains authoritative during renewal races.
`status` accepts the returned replacement ID before a successor exists and shows
the durable attempt, predecessor and deadline. Lost-source renewal is rejected
without changing intent: explicitly recover the remaining lease or cancel and
register fresh observation. Live-source handshakes end within ten seconds or the
parent lease, whichever comes first. An already-confirmed finished source can
renew directly into a fresh lease after its old lease ends.

Owner loss interrupts a pending attempt; deadline expiry ends it without claiming
a confirmed source stop. Remaining parent intent can be explicitly recovered or
cancelled. Retry creates a distinct attempt receipt and preserves previous failures,
with at most one successful successor. Existing journals migrate transactionally;
legacy request timestamps remain unknown rather than being invented.

Inspection separates intent, source health, control reason, native admission,
queue-start state, live turn outcome and explicit acknowledgement. Cached status
does not connect to native runtime or start observation. When the coordinator is
offline, previously running source health is shown as unknown with its last receipt.

Esc interrupts the current model turn and leaves observation intent registered.
Native paused/budget-stopped/unknown control states hold delivery while bounded
observation continues. No goal setter or goal-resume operation is used. Busy
delivery waits; queue-start refuses an active/pending turn and does not jump an
earlier human input. An explicit message to stop supervision asks the model to
cancel its selected registrations. Already-admitted or in-flight input has a
separate receipt; cancellation does not promise retraction. The coordinator tries
to withdraw only an exact owned entry that is still pending, including after its
delivery window ends. Pending notices expire even while native control is offline.
Cancellation is checked again after queue inspection, before reserving a start;
requests already in flight retain their actual receipt.
Cleanup checks exact native and client event IDs across at most twenty queue pages
under a shared time bound. An incomplete scan stays unknown. `withdraw_state`
and `withdraw_detail` record withdrawal separately from original admission/start
uncertainty: absence is not proof of completion, and a refused/racing delete is
not reported as successful retraction. Known consumed turns remain untouched.

Explicit cancellation while the coordinator is offline may make a bounded native
cleanup connection to the positively loaded frozen target. It does not start a
coordinator, resume a cold thread, restart observation or change a goal. Status
and list remain entirely cached.

Queued events now use readable attributed text, with peer facts and message bodies
quoted as data. Information and action requests have distinct labels; requests
require a frozen sender, revalidated before admission and queue start. Peer text
does not confer new authority. Full identities and raw observations remain in the
journal; compact event references can be used with `ack` only when unambiguous.
Messages include their body once. Native queue/control behavior is unchanged.
Native enqueue proves admission. A successful live turn is not an acknowledgement
or an external-effect receipt; `ack EVENT_ID` records handling only. Unknown or
unadmitted IDs cannot be acknowledged.

The qualified legacy CLI conversation exposed contradictory historical turn
statuses after interruption. Connected live completion and explicit acknowledgement
are journaled separately; history snapshots are not used to overwrite them or
to infer a missing completion during recovery.

## Recovery and shutdown

```sh
rtk proxy scripts/codex-plus-watch --state STATE recover REGISTRATION_ID
rtk proxy scripts/codex-plus-watch --state STATE shutdown
rtk proxy scripts/codex-plus-watch --state STATE shutdown --confirm
```

After coordinator restart, intent, baselines and events persist. An in-flight
admission becomes uncertain and is not blindly replayed. Sources from the previous
connection are marked lost and do not silently restart. Explicit `recover` requests
restart of an unexpired lost source after validating the exact owner and loaded
target; it preserves recorded baseline and admission uncertainty. The observation
gap remains visible. Occurrence sources need their own cursor/gap policy; recovery
does not promise complete log coverage or exactly-once processing.

`shutdown` previews affected owned work and requires `--confirm` when it would
stop registrations or leave pending handling. Confirmation cancels those
registrations, stops only their sources and closes the coordinator. It preserves
the native daemon, conversation, goals and unrelated background shells/tasks.
An explicit cancellation already supplies authority for that selected work.
Confirmed shutdown shares one five-second budget across source termination,
pending-input withdrawal and final source receipts. Its connection closes even
when cleanup is incomplete; unresolved input/source receipts remain visible.

The helper does not intercept native `/exit` or add a native confirmation dialog.
The native viewer remains separate from the coordinator's lifetime. Bryan's
reported Claude exit protection is a reference; its exact task coverage was not
reproduced by this pass.

## Acceptance boundary

See [the goal-loop evidence](coordinator-loop-results.md) for tested behavior and
current limitations. Human draft/input/stop acceptance, an accessible real-source
pilot, longer operation and managed installation remain subsequent checks.

Post-loop review found renewal/cancellation gaps. The corrective unattended pass
resolved them with 94 passing tests and a fresh native batch of four admissions
and five turns. See the
[next-pass plan](codex-plus-plan.md#next-pass-lifecycle-correctness-and-native-tui-acceptance)
and the corrective report for the implemented contracts and evidence limits.

## Deferred TUI walkthrough and real-source pilot

### Current primary-driven interaction demonstration

The earlier lifecycle walkthrough below is historical preparation. For the next
shared interaction review, use the current model interface and fresh A/B fixtures;
closed acceptance actors and their allowances are not reusable. The primary drives
all prompts, synthetic changes, inspection and cleanup. Bryan watches two native
TUI panes over SSH/tmux and assesses the replies; no copy/paste protocol is required.

Before launch, recheck the existing daemon/version and select a new bounded
allowance. Attach the per-thread bridge above, using the reusable `MODEL_GUIDANCE`,
an owned-actor allowlist and fresh private journals. Open both exact actor UUIDs in
their ordinary remote-resume TUI through a launcher that inherits `/dev/tty`.
Identify the windows by A/B role for the viewer; opaque native titles still test
selection by task context. All deliberate controls and messages target these actors.

| Scene driven by the primary | What Bryan should see |
| --- | --- |
| Give B a synthetic validation task, then ask A: "Watch the session validating the samples and tell me when it needs my input." | A identifies the work and acknowledges briefly; no user timing recipe, exact title or UUID. |
| Leave a draft in A and make B report a choice between strict rejection and normalization. | One readable attributed watch update and the actual decision; draft remains intact. |
| Ask A: "Stop watching that session. Keep its validation work intact." | Brief stop acknowledgement; B remains available, with no replacement watch. |
| Ask A: "Tell that session the updated fixture is available." | One readable information message in B and a short send receipt in A. |
| Ask for a batch size within B's task and then one conflicting with its direct limit. | Distinct accepted/declined handling; direct instructions remain effective. |
| Ask A whether the request was accepted. | Cached handling receipt without another message or acknowledgement loop. |

Inspect exact private journals and current native history behind each scene. Always
use the fresh handled event returned by the wait, rather than an earlier pending
record. Take a TUI capture before closing fixtures. After the shared review, cancel
owned watch intent, reconcile exact pending input, stop owned bridges/coordinators
and archive only those actors. Personal UX acceptance is Bryan's assessment.

Bryan requested finishing unattended work before manual steps. This checklist is
prepared for the next shared session; it is not an executed human acceptance test.
Use a fresh private state/fixture and an explicitly selected loaded CLI thread.
Read the binding/setup/control examples above and recheck the native version/owner.
Use the public simulator and a model-prepared read-only observer, with a quiet
initial baseline, 120-second lease and at most two useful events. Choose a fresh
bounded recipe before running it; the corrective native batch is already closed.

1. Keep a recognizable draft in the TUI, trigger a useful fixture observation and
   verify that the draft survives. Also check that earlier submitted human input
   keeps its place ahead of an observation.
2. Interrupt foreground work with Esc, then trigger a fresh observation. Verify
   that it is handled while registered observation remains independent.
3. Register a short watch and one-shot timer, send an explicit stop message, then
   pass their trigger/deadline. Verify cancellation without renewal or later input
   from those registrations; inspect already-admitted receipts separately.
4. Detach the viewer while a bounded observer is registered, reconnect through the
   qualified path and inspect its evidence. Preview coordinator shutdown, decline
   it, then confirm and inspect source/input cleanup. Preserve unrelated work.

Record observed behavior, IDs and outcomes privately, with only sanitized results
in the report. This does not implement a native `/exit` dialog or replace Bryan's
direct acceptance with scripted keystrokes.

Before opening a real-source pilot, fill in this short worksheet:

| Choice | Needed evidence |
| --- | --- |
| Existing cheap task | Identify the selected job/run and owner; prefer work already running. |
| Read-only source | Exact host-readable status/log command, its permissions and any observation gaps. |
| Useful events | Which changes deserve follow-up; what proves actual progress, completion or failure. |
| Model follow-up | Existing permitted actions, reporting and acknowledgement; observation grants no new authority. |
| Lifetime and stop | Source/timer limits, renewal choice, explicit stop and cleanup expectations. |

If no existing job is suitable, select one existing short validation command and
private result path before launching it. Network/credential access, restricted
calling contexts, longer operation and deployment require their own qualification.
The unattended pass has not selected a real source or launched a workload.
