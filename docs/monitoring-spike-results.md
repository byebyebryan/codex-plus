# Monitoring spike: initial pass

2026-10-12, Snap continuation checkout. This is a source-level research result,
not a release or installed watch service. The primary executed the new bounded
pass described in [the plan](codex-plus-plan.md#research-and-spike-pass); the
archived study was not restarted. Only synthetic work was observed.

**The native mechanics support a small host coordinator using the existing
daemon's command runner and queue.** A model-prepared observer and a model-selected
one-shot wakeup worked through that path. Complete event-driven handling remains
unaccepted: two admitted observation turns failed with provider capacity errors.
Human TUI acceptance, goal coexistence and daily recovery also remain open.

## Evidence and scope

The CLI and existing daemon both reported `0.162.1`. The Unix socket's resolved
kernel listener had one identified owner. Its PID, start ticks and executable
were frozen with the selected thread in private study state. No second app server
was started and the original owner was preserved.

The test conversation was created through the existing daemon's API and then
attached using the ordinary native TUI. Its source classification remained
`vscode`; this is not evidence that all CLI-created conversations have been
qualified. Loaded membership was checked positively before binding. Existing
working conversations were not destinations for the probes.

Generated stable and experimental schemas were kept outside source. Relevant
findings from the installed binary:

- `command/exec`, streaming and termination are on the stable surface.
- The six `thread/queue/*` operations are on the experimental surface.
- No sleep, wakeup, timer or scheduler method appeared in either generated client
  request schema. This supports using an external timer for the spike; it does
  not establish that Codex has no internal scheduling machinery.

The [official app-server guide](https://learn.chatgpt.com/docs/app-server#command-execution)
provided the command-runner starting point. Installed schema and native probes
established the measured limits below. [Scheduled-task documentation](https://learn.chatgpt.com/docs/automations)
describes web/desktop management, without supplying the CLI-owned timer contract
needed here.

## Native results

| Probe | Result | Evidence limit |
| --- | --- | --- |
| Existing-owner connection | Passed initialization and loaded inventory over WebSocket on the resolved Unix socket. The calling thread was also present in the initial read-only inventory. | Local transport and positive membership; not fleet discovery. |
| Command streaming | stdout and stderr arrived separately; first output at about 0.029 seconds, final result at about 1.032 seconds. | One short synthetic command. |
| Command cancellation | Explicit termination returned an empty success result; the command exited 137. An identified grandchild also stopped in the separate tree probe. | Owned processes identified by exact unique argv and host start ticks. |
| Command timeout | A 300 ms timeout ended the source with exit 124 in about 0.307 seconds. | Short timeout qualification. |
| Output cap | A 128-byte cap set `capReached`; the command continued and exited normally. | The cap truncates; a monitor must reject truncation and terminate its source explicitly. |
| Connection loss | An identified host child stopped after the command's originating connection closed. | A persistent coordinator must own that connection for the requested watch lifetime. |
| Read-only source | An attempted fixture write failed and created no file. | Filesystem write restriction exercised; arbitrary credentials/network sources were not qualified. |
| Idle CLI queue | Native admission succeeded, the reply completed, and its exact marker appeared in the TUI. | Mechanical rendering, not human acceptance. |
| Busy CLI queue | Original turn completed before follow-up. Both replies rendered; a synthetic draft survived. | One bounded ordinary tool turn and a programmatically entered draft. |
| Esc with queued input | Esc interrupted the active turn. The admitted follow-up did not start in the following 12-second observation window and remained in the queue. | Not a permanent pause guarantee. The identified test input was explicitly removed after the probe. |
| Watch cancellation | Cancelling before the controlled emission produced zero events; the owned worker stopped. | Pre-admission native case plus offline race checks. |
| Viewer closure | A quiet source and coordinator stayed active and the test thread remained loaded after only the test TUI was closed. Explicit cancellation then stopped the source. | No model event admitted in this check. |
| Unavailable endpoint | A task-owned non-responsive Unix listener timed out during connection setup in about 10.021 seconds. No watch or event was registered. | Existing daemon remained running; this does not qualify daemon replacement/reconnect. |

The native batch admitted six queued messages: idle, busy, stop-boundary,
progress, completion and wakeup. Five recipient turns started; the stop-boundary
message remained pending and was removed. Direct setup/busy-probe turns are
accounted separately from these follow-ups. Event-driven quiet observation had
zero admissions during six irrelevant fixture updates and a two-second window.
No price or total-inference-cost conclusion follows from these counts.

## Model-prepared observation and timed reassessment

The simulator provides explicit progress, stall/recovery, completion/failure,
noise and occurrence controls. Complete status snapshots are published atomically.
Its fields and controls are fixture conveniences, not a required job schema.

For event-driven supervision, the model prepared a script using a one-second
cadence, selected progress/status/error fields, a progress threshold and a stall
condition. It suppressed startup and timestamp/revision noise. Those were the
model's choices for this request; they are not coordinator rules.

The first registration attempt ran under an explicitly restricted workspace
sandbox and failed resolving the daemon socket. No watch was registered. The
model reported the failure and saved its observer for review. A distinct attempt
under the host's ordinary full-access Codex permissions registered that script;
the helper still ran its source with an explicit read-only native policy.

The helper admitted progress and completion observations with distinct event IDs.
Both processing turns failed with `serverOverloaded` and the message
`Selected model is at capacity`. The first began inspecting the observation;
the second produced no assistant reply. The records remain `native_queued`,
which proves admission only. Neither failure was silently replayed or accepted
as successful supervision.

For the separate timer case, the model chose a 20-second delay and a focused
reassessment prompt, then registered a one-shot wakeup and settled. The timer
admitted one event without a source event; its handling turn completed. The
initial admission ceiling required the model to describe its next supervision
choice rather than register another operation. Executed adaptive renewal remains
a separate acceptance case.

## Offline checks and prototype boundaries

Thirteen separate spike tests cover UTF-8/line framing, transport reads across
timeouts, invalid/oversized records, irrelevant projection churn, distinct repeated
occurrences, finite event admission, cancellation before and during dispatch,
expiry, one-shot replacement, atomic baseline/event rollback, and crash/transport
uncertainty without replay, preservation of cancellation after an in-flight
failure, and truthful rejection of an unknown cancellation ID.
Existing worker metadata tests remain separate.

The source contains a controllable fixture, a bounded local client, a source-probe
script and a temporary monitor/timer helper in `spikes/monitoring/`. Intent and
events use SQLite transactions for the recording experiments. This does not
establish complete service recovery or exactly-once processing.

Lifecycle notices were disabled in native recipes so resource/expiry notices
could not silently consume the batch allowance. The helper distinguishes
registration, active/completed source state, native admission, known preflight
failure and uncertain submission. An in-flight request at cancellation remains
explicit and may subsequently report native admission; cancellation does not
promise retraction.

The helper suspends on an observed native interruption and does not replay an
uncertain event. This only covers control observed during its connection lifetime.
Bryan clarified after reviewing the next-pass proposal that Esc interrupts the
current turn while monitoring remains registered; a full supervision stop is an
explicit message. The helper's interruption guard is a study limitation, not
the selected product behavior. Native post-interruption processing, explicit
cancellation and reconnect/previous-stop handling remain to be qualified.

Goal coexistence is deliberately unqualified. A `thread/goal/cleared` notification
was observed while the target had no goal; this cannot establish how an active
goal behaves. The helper rejects automatic delivery when any goal is present,
rather than resuming or modifying a goal. That conservative study guard does
not meet the final requirement to work naturally with native goal loops.

Normal input and interruption were checked through automated TUI captures.
Bryan's direct human check has not occurred. No claim of human acceptance,
real operational supervision or long-duration reliability is made.

The task-owned test viewer is closed, coordinator workers and sources are stopped,
the queued stop-probe input was removed, and the fixture's temporary folder-trust
entry was restored to its prior state. Raw evidence was retained privately. The
original daemon identity and existing worker files were preserved; no managed
installation or release was changed. Source inventory validation and all 18
tests passed (13 spike checks and five worker metadata tests).

## Implementation recommendation

Use a small host coordinator outside inference to own intent, timers, a finite
admission budget and the native command connection. Reuse the existing daemon
for sandboxed sources and the qualified queue path; keep conversation ownership
there. Python's standard library is sufficient for this local prototype. A new
command runner or replacement frontend has no demonstrated need.

Expose model-selected argv/cwd, source lifetime and limits, useful emitted data,
follow-up instructions and one-shot timing. Keep source-specific filtering and
cadence in scripts or optional helpers. Return frozen destination and effective
bounds with registration; provide unified status/cancel inspection of both kinds.
For the first renewal contract, stop the predecessor before creating a linked
registration with a changed script. Decide on separate acknowledgement after
qualifying the handling receipt, without equating it to an external effect.

A shell helper is usable under the permissions exercised on this host. Restricted
sandbox support needs an explicit control-channel/access design. A host-side typed
tool or narrowly permitted coordinator IPC are candidates; do not work around
that boundary by broadly relaxing user configuration. MCP can expose operations,
but does not supply lifetime or permission inheritance by itself.

Proceed in these bounded slices:

1. Resolve native queue/active-goal coexistence and the chosen human-stop policy.
   These gate the final conversation integration. Use this pass's binding and
   interruption evidence as the starting point, not a substitute for those cases.
2. Extract only the useful source/framing/recording mechanics into a small
   coordinator, with explicit control-channel access and truthful receipts.
   Preserve the simulator and state-transition tests as regression fixtures.
3. Requalify complete event-driven handling after the capacity failures, then
   exercise executed adaptive renewal and Bryan's normal-input/stop acceptance.
   Use a new finite batch plan for those named gaps; do not replay old events.
4. Qualify restart/reconnect and an accessible real source, then prepare one
   release and the scoped chezmoi packaging together.

This initial research batch is complete. It supports the runtime direction and
records concrete integration gates; milestone 1 and daily-use acceptance are
not complete. Raw journals, generated schemas, observer captures and actual
thread/socket/PID bindings remain outside committed source.
