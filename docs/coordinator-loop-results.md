# Coordinator goal loop: evidence and candidate status

Execution started 2026-10-12 on Snap after Bryan requested the agreed goal loop
and incremental commits. The research-to-local-candidate pass is complete. Human TUI acceptance,
real-workload supervision and installation remain pending.

The [execution contract](codex-plus-plan.md#large-goal-loop-research-to-a-reviewed-local-candidate)
allows two finite native batches, with 24 follow-up admissions and 40 started
native test turns overall. The original research batch remains closed.

Post-loop read-only review reproduced two additional cases outside the completed
native matrix: renewal of an already-lost source can remain `replacing` past
expiry, and cancellation does not inspect an owned pending input after an
uncertain queue start. Existing tests still pass. These findings qualify the
candidate's readiness for a pilot; the
[next-pass plan](codex-plus-plan.md#next-pass-lifecycle-correctness-and-native-tui-acceptance)
records their proposed resolution and acceptance. No new native trial was run
for that review.

## Corrective unattended pass: in progress

Bryan requested executing the next pass with incremental commits and deferring
manual steps. The fresh ordinary goal covers fixes, offline/native acceptance,
cleanup and prepared handoff. Human acceptance and a selected real-source pilot
remain pending. The older closed batch counts below are not renewed allowance.

The first corrective slice rejects lost-source renewal without intent mutation,
adds finite durable renewal attempts, resolves pending replacement IDs, preserves
failed retries and migrates existing receipts transactionally. It also reaches
the cancellation path for an uncertain start. All 76 tests pass at this checkpoint;
pagination-aware cancellation, shared shutdown cleanup and a fresh native batch
are still required before unattended completion.

## Checkpoints and preservation

`8f3b380` commits the existing planning drafts, first-spike source and results,
plus the corrected Esc/explicit-stop/exit-lifecycle contract. Its explicit public
inventory and all 18 pre-existing tests passed. Existing worker files were not
changed. Nothing has been published or installed.

The installed CLI and existing owning daemon both reported `0.162.1`. Positive
loaded membership of the requesting conversation was verified; it is not a test
destination. Native tests use a separate synthetic conversation created through
the ordinary CLI/TUI on that same daemon. Bindings, transcripts, generated schemas,
fixture state and raw evidence remain private and outside source.

## Conversation and control findings

| Case | Result | Boundary |
| --- | --- | --- |
| Ordinary CLI creation | Dedicated CLI/TUI invocation created the fixture conversation; exact viewer ID, cwd and positive loaded membership agreed. | The daemon reports `source=vscode`, `originator=codex-tui`, `threadSource=user`. A `sourceKinds=[cli]` inventory filter missed it; source classification alone cannot qualify its creation path. |
| Empty CLI thread | It was positively loaded and readable before the first prompt, but `thread/resume` returned no-rollout-found. The ordinary first TUI prompt then established persisted history and completed. | Loaded membership and resumable saved history are separate facts. |
| Active goal | Corrected bounded probe admitted and handled an observation while native goal status remained active, with objective and allowance preserved. Driver later marked the fixture done and the goal became complete. | A task-owned trailing turn was interrupted during probe cleanup after goal completion; this is not direct human acceptance. |
| Paused goal | Pure preflight held delivery; the native queue was unchanged. A separate read-only native source executed successfully while the goal stayed paused. | Observation lifetime and delivery eligibility are independent. No goal-resume or queue-start call was made in the paused state. |
| Esc | Current tool turn was interrupted. Independent source output continued and exited normally; a later CLI-queued follow-up remained pending for the 60-second check. | CLI admission alone did not provide the required post-interruption wakeup. |
| Exact queue-start alternative | After validating idle runtime and no stopped goal, starting the exact owned head entry through `thread/queue/start` produced a completed handling turn without goal mutation. The same method refused a busy turn with `thread already has an active or pending turn`, leaving its entry queued. | Receiver handling and native admission remain separate receipts. |
| Viewer-closed event | Ordinary `/exit` closed only the owned viewer. A new event admitted afterward through `thread/queue/add` completed its handling turn, correlated by its supplied `clientUserMessageId` to persisted `userMessage.clientId`. | The study connection kept the target loaded. Closing that final client later left it unloaded; the helper must keep its connection and reject unqualified cold targets. |
| Start/admission race | An extra start raced automatic consumption and received `queued submission not found`; persisted correlated history proved completed handling. | That error cannot turn known admission into failed/uncertain enqueue or justify replay. |
| Restricted control access | Native read-only and restricted workspace policies with network disabled both denied a task-owned Unix control-channel probe with `Operation not permitted`. | Moving a socket into the writable fixture directory did not establish control access. No global permissions were relaxed. |

The first active-goal recipe had an insufficient synthetic token allowance: the
installed model context exhausted it before queueing. Its queued input was removed
by exact test identity and the result was excluded from active-goal acceptance.
It supplies a native budget-limited-state observation, not proof of successful
delivery into an active goal. The corrected case checks active status immediately
before admission and uses a finite allowance sufficient for this context.

## Candidate control contract

`spikes/monitoring/control.py` is a pure study preflight. It permits positively
bound live idle/busy states with an eligible active/completed/no goal; stopped or
unknown goals, unknown input capability and waiting/unknown runtime states hold
delivery. It does not change goals or control source lifetime. Esc is not inferred
to cancel monitoring or install a durable follow-up pause.

Nine separate control/delivery tests cover eligible/stopped/unknown goals,
busy/waiting runtime states, strict input capability, exact thread matching,
interruption independence and known admission after a failed/unknown start.
The research helper now uses the qualified preflight and direct native queue
operations with stable event IDs. Its blanket interruption guard is removed.
Its per-registration worker and stopped-state source suspension remain prototype
limitations; observation/delivery separation belongs in the candidate. This is
a description of the prototype checkpoint; the extracted coordinator is qualified
below.

Full-access calling setup is the qualified host starting point from the first
spike. Read-only native source execution remains a separate policy. Restricted
calling contexts need a host-side tool/control design and must report unsupported
access clearly, without silent sandbox downgrade or assumed credential inheritance.

## Complete supervision and explicit stop

The model prepared a read-only observer with a one-second cadence, selected useful
fields and a 20-point progress threshold. Six irrelevant fixture updates produced
zero emissions/admissions. Progress and terminal observations had distinct event
IDs, were correlated to recipient turns, and each produced fresh inspection and
a successful live `turn/completed` outcome.

The first measurement recipe stopped early because it treated a persisted
`thread/turns/list` status as the handling outcome. In this earlier-interrupted
legacy CLI conversation, that page reported `interrupted` while the matching live
completion notification reported `completed` and the final assistant response
acknowledged the event. A fresh named recipe reused the model-prepared script and
required correlated live outcomes. Both progress and completion passed, while
the contradictory stored statuses remained visible. Do not overwrite live receipts
with a later historical snapshot or use that snapshot alone to resolve recovery.

For timed adaptation, the model chose a short wakeup, inspected the stalled fixture
and actually registered a terminal observer as its continuation. The driver then
completed the fixture; the continuation event was inspected and supervision ended.
Two follow-up admissions covered that scenario. This qualifies executed adaptive
continuation; linked in-place renewal remains a candidate acceptance case.

An explicit stop message cancelled both a quiet marker-controlled observer and a
pending timer. Triggering the marker and passing the timer deadline after effective
cancellation produced no new events or replacement registrations. No event had
been admitted before cancellation in this particular check; in-flight boundaries
still require truthful receipts and race tests.

The integration batch is closed at **10 follow-up admissions and 19 started native
test turns**, including setup, goal continuation and the failed measurement
recipes. No provider-capacity failure occurred. Candidate/recovery acceptance has
its separate allowance of at most 12 admissions and 20 started turns; unused
integration allowance is not an automatic retry pool.

## Local candidate and native acceptance

The source candidate now lives in `codex_plus/` with a direct
`scripts/codex-plus-watch` entry point. See [the candidate guide](watch-candidate.md).
It extracts the qualified local transport/control/framing mechanics and adds one
coordinator owner, private SQLite intent/events, live handling receipts, explicit
acknowledgement, source/delivery separation, one-shot timers, projection baselines,
lineage cancellation, stopped-predecessor renewal, explicit source recovery and a
shutdown preview/confirmation boundary. It uses one coordinator connection per
private state directory and keeps the exact existing daemon and conversation.

| Candidate case | Observed result | Evidence limit |
| --- | --- | --- |
| Model-prepared snapshot source | The model wrote its observer and registered selected fields with a quiet initial baseline. Six irrelevant updates produced no admission; progress and terminal events had distinct IDs, explicit acknowledgements and live completed handling turns. | Controlled synthetic data, not real-job outcome acceptance. |
| Active/paused goal | Source output continued and the event stayed pending while paused. After explicit driver resume, delivery and handling succeeded with the goal objective and finite allowance preserved. | The coordinator never resumed or altered the goal. Goal continuation added separately counted native turns. |
| Actual Esc | Native TUI Esc interrupted a foreground sleep turn. The candidate source stayed running; a fresh subsequent observation was handled and acknowledged. | Automated owned TUI, not Bryan's direct draft/input walkthrough. |
| Renewal | A running predecessor stopped before its linked successor began; exactly one Python reader existed. Cancelling the parent later cancelled the successor too. | The native command has wrapper/sandbox processes; those are not separate readers. |
| Coordinator crash and recovery | Killing only the identity-verified coordinator stopped its owned native command chain. Cached inspection stayed offline and did not restart it. Explicit recovery used a new coordinator generation, preserved projection baseline, suppressed unchanged state and handled a fresh event. | Observation gap remains; no exactly-once log coverage or native-daemon restart claim. |
| Shutdown preview | An unconfirmed shutdown returned its affected-work preview and preserved the coordinator/work. Confirmed cleanup stopped only its owned resources. | No native `/exit` interception or new TUI confirmation dialog. |
| Native source failures | A write attempt failed under native read-only policy without creating the file. Malformed selected JSON stopped the source with an error receipt and zero admissions. | Source failure does not establish watched-job failure. |
| One-shot timer and cancellation | A ten-second timer admitted/handled one event; a fifteen-second timer cancelled before due produced none. Completed timer intent settled. | Finite one-shot scheduling; no recurring backlog or long-duration acceptance. |

The candidate batch is closed at **7 admissions and 11 started native turns**.
Together with integration, the pass used **17 admissions and 30 started native
test turns**, with **zero provider-capacity failures**. Failed measurement recipes,
setup and goal continuations are included; neither batch's spare allowance is
renewed. The older first-spike batch and its capacity failures remain separately
recorded in the initial report.

## Review, corrections and validation

Primary review and native checks found and corrected these boundaries:

- Recovery must reconcile the previous owner before accepting a lost-source restart.
- A submitted source stays `starting` until real native output proves execution.
- Pending lifecycle notices must expire even when native control is unavailable;
  admitted receipts remain truthful after their delivery window ends.
- Cancellation/expiry is checked transactionally after queue inspection, before
  queue-start reservation. A request already in flight remains a separate receipt.
- Registrations created while a native receive/RPC yields need deadline
  initialization before use. The malformed-source recipe exposed this race; it
  was retained as failed evidence, fixed and rerun under a fresh case name.

The first renewal measurement incorrectly counted native wrapper processes as
duplicate readers; the corrected measurement counted the Python leaf and retained
the entire chain for the crash check. An exploratory candidate timer used a
one-second delay outside the agreed ten-to-thirty-second recipe bounds. It remains
in accounting; the qualifying timer recipe was repeated at ten seconds. A staged
whitespace failure was mistakenly committed in the initial candidate slice and
corrected in the next slice; subsequent commits checked exit status before commit.

All **64 tests** pass: 5 metadata/checker, 13 original spike, 9 control/delivery
and 37 candidate tests. Candidate tests exercise transactional baseline/event
rollback, output bounds, stopped/unknown control, admission/start uncertainty,
live correlation, cancellation races, lease expiry, renewal, recovery, single
ownership and shutdown/status behavior. They remain separate from worker metadata
validation. The explicit **46-file inventory**, `git diff --check` and staged
whitespace checks pass. Reproduce the offline checks from the checkout:

```sh
rtk proxy scripts/check
rtk proxy python3 -B -m unittest discover -s tests -p 'test_*.py'
rtk proxy git diff --check
```

## Reproduction, cleanup and usage

The [candidate guide](watch-candidate.md) provides the checked CLI forms. For a
short synthetic walkthrough, create a fresh private simulator fixture with
`spikes/monitoring/simulator.py`, bind an exact positively loaded native thread,
and have the model prepare a bounded read-only observer of that fixture. Register
120 seconds/two events with `status,progress` projection and a quiet initial
baseline; generate noise, then progress and completion. Inspect each event's
admission, live turn and explicit acknowledgement separately. A ten-second
one-shot reassessment exercises the timer path. Use explicit selected cancellation
and the shutdown preview/confirmation commands to finish. Actual paths, source
scripts and IDs belong in private state, not committed examples.

Private raw receipts, case recipes, ledger, schemas and transcripts were retained
outside source, including unsuccessful measurements. Final cleanup verified no
active candidate intent, native source or coordinator, no pending fixture input
or synthetic goal, and the owned viewer closed. The task's temporary trust entry
was removed while preserving all other parsed configuration and bytes. The
original daemon PID/start identity/executable and requesting thread's positive
loaded membership matched the saved baseline. Worker agents, skills and legacy
identities have no changes from the planning checkpoint. Nothing was pushed,
published, deployed, applied through chezmoi or run against a real workload.

The primary goal tool supplied a pre-report checkpoint of **894,621 tracked
tokens and 9,520 tracked seconds**. This is that tool's primary-goal accounting,
not a provider bill or a sum of native test-turn usage. The native ledger records
the counts above; this pass did not establish a reliable aggregate charge or
cost advantage.

## Remaining acceptance and next action

Supported scope is a local Linux/Unix candidate on native `0.162.1`, with experimental
queue methods and the qualified full-access caller path. Restricted calling
contexts remain unsupported. Longer operation, native-daemon restart, complete
cursor-based source recovery, fleet discovery and managed installation remain
unqualified. Agent Observer is not a dependency.

Review it with Bryan in the native TUI: retain a draft/earlier human input,
interrupt current work, receive a fresh observation, explicitly stop supervision,
and inspect the destructive-shutdown preview. Then choose an already-accessible,
cheap real source. An existing short validation run publishing its final exit
status into private state is a practical pilot; choose its command/status path
before launching it. Actual Claude work was left alone. Release publication and
chezmoi revision/checksum/validator changes remain a separate installation pass.
