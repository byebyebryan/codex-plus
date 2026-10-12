# Coordinator goal loop: evidence and candidate status

Execution started 2026-10-12 on Snap after Bryan requested the agreed goal loop
and incremental commits. This report is in progress. Human TUI acceptance,
real-workload supervision and installation remain pending.

The [execution contract](codex-plus-plan.md#large-goal-loop-research-to-a-reviewed-local-candidate)
allows two finite native batches, with 24 follow-up admissions and 40 started
native test turns overall. The original research batch remains closed.

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
not yet a claim that the product coordinator is implemented.

Full-access calling setup is the qualified host starting point from the first
spike. Read-only native source execution remains a separate policy. Restricted
calling contexts need a host-side tool/control design and must report unsupported
access clearly, without silent sandbox downgrade or assumed credential inheritance.

## Remaining work

Exercise complete model-prepared observation and executed timed adaptation.
Use those gates to extract the local coordinator and test cancellation, renewal,
truthful receipts and recovery. Preserve capacity failures and in-flight boundaries.
The morning report will distinguish automated native checks from Bryan's pending
TUI acceptance and separate installation scope.
