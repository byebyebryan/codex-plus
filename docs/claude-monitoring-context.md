# Claude monitoring context and Snap continuation

Captured 2026-10-11 for continuation on Snap. This is a planning handoff, not
an implemented watch service or a new research trial. Read it with the
[implementation handoff](implementation-handoff.md) and
[draft plan](codex-plus-plan.md).

## Latest request and design tenet

Bryan asked to plan properly before implementation, then requested capturing
the context here and moving development to Snap. The next conversation should
continue that planning rather than immediately execute the old first-watch recipe.

Use Claude Code's existing behavior and Bryan's actual operational histories as
the starting point. Do not design the capability from scratch around a narrow
synthetic example. His explicit tenet is to give the model control and options
for setup, using rigid rules only when they are robust and broadly generalizable.

This broadens the earlier JSON-snapshot-only proposal. A snapshot/projection
helper remains useful, but should be an option alongside model-prepared scripts,
background event output and timed reassessment. Preserve native Codex planning,
goals, continuing conversations, human input and the existing owning daemon.
Agent Observer is not an initial dependency; coordination follows this capability.

## Actual workflow to preserve

Bryan's reported Claude workflow includes watching a deployment, inspecting
metrics and logs, supervising overnight evaluations, and responding to problems
within an agreed action plan. During a backfill, changing capacity led to repeated
scaling decisions while another independently inspectable conversation worked on
automation. Morning reporting is part of this continuing supervision.

The earlier sanitized study reconstructed backfill/capacity, evaluation,
scheduling and separate-session coordination episodes. It did not independently
audit the private production outcome. Monitoring, waking, deciding, authorized
action, renewed observation and handoff are the useful sequence to preserve.

## Claude mechanics checked

Snap's installed Claude Code reported `2.1.296` during this inspection. Current
official documentation was fetched on 2026-10-11; recheck it before depending on
version-specific behavior.

| Primitive | Runtime behavior | Model control |
| --- | --- | --- |
| Monitor | Runs a background command and delivers each output line as an event; can also consume a WebSocket source | Prepare the script/source, select what it emits and request a duration |
| Adaptive loop / ScheduleWakeup | Returns to the conversation after a delay | Pick the next delay and prompt; reschedule or stop |
| CronCreate / CronList / CronDelete | Manage one-shot or recurring prompts in the session | Choose task instructions and timing |

For most watches, Claude writes a small script. Filtering and polling can live
in that script rather than in a universal source schema. Monitor has an ending
notice, allowing the model to decide whether another watch is needed. The
documented default was five minutes and maximum thirty minutes; these are Claude
product limits, not selected Codex Plus defaults. [Monitor reference](https://code.claude.com/docs/en/tools-reference#monitor-tool).

Without an explicit loop interval, Claude can choose a new delay after each
iteration or use Monitor. ScheduleWakeup can stop a pending wakeup. Cron fires
wait for an idle session, and missed intervals do not create a backlog of runs.
Resume has exceptions: self-paced loops and background monitors are not restored.
These limits are useful design evidence, not a promise that a continuing thread
keeps every external observer alive. [Scheduling reference](https://code.claude.com/docs/en/scheduled-tasks).

### Interruption versus monitoring stop: clarified 2026-10-12

The installed CLI still reports `2.1.296`. Current official docs distinguish
turn interruption from monitor cancellation: Esc interrupts the current response
or tool call; a monitor ends on explicit cancellation, session end or its
deadline. [Interactive controls](https://code.claude.com/docs/en/interactive-mode),
[Monitor lifetime](https://code.claude.com/docs/en/tools-reference#monitor-tool).

One separate rule applies to a self-paced `/loop`: Esc while waiting clears its
pending wakeup. Independent scheduled tasks remain registered.
[Loop stop behavior](https://code.claude.com/docs/en/scheduled-tasks#stop-a-loop).
These are documentation findings, not a new live monitor-interruption probe.

Bryan clarified that Codex Plus should preserve this distinction: Esc interrupts
the current turn; an explicit message stops the selected supervision. The earlier
proposed blanket pause of automatic follow-up on Esc is withdrawn. Native goal
pause/budget limits still require separate qualification and must not be overridden.

### Exit protection: reported 2026-10-12

Bryan reports that Claude asks for confirmation before quitting or `/exit` kills
running background shells/tasks. Preserve this as a user-observed behavior; the
exact prompt and which task types it covers have not been reproduced here.
The current docs confirm exit cleanup of background tasks and distinguish
backgrounding the session, which keeps them running.
[Background command lifecycle](https://code.claude.com/docs/en/interactive-mode#background-bash-commands).

The design implication is to distinguish interrupting a turn, detaching a viewer,
explicitly stopping supervision and shutting down its owner. Show affected owned
work and require confirmation when a requested shutdown would terminate it.
Native Codex exit controls and extension hooks remain to be qualified; do not
assume a helper can intercept `/exit` or equate viewer closure with cancellation.

## Fresh selected Snap history inspection

Four selected main histories were re-read on Snap. The scan's event window was
2026-09-24 00:00 UTC through 2026-10-12 06:29:45 UTC, which was still October 11
in Bryan's timezone. Analysis ran on the source host; only fixed-vocabulary
counts and sanitized mechanism descriptions were exported. No private transcript,
command, script text, resource name, original session ID or credential is included
here. Selection is not a census or a task-success sample.

| Selected case | Observed mechanism |
| --- | --- |
| Earlier preparation/evaluation | 12 Monitor requests, with inline loops and sleeps |
| Watch-heavy operational conversation | 300 Monitor requests; 290 script invocations; 299 non-error Monitor results and one error |
| Backfill/capacity conversation | 35 Monitor requests; inline polling and script use; error handling and capacity-related query shapes |
| Evaluation follow-up | One Monitor request; two twenty-minute ScheduleWakeup requests and two explicit stop requests |

Eleven distinct historical script bodies written in the watch-heavy conversation
were matched to later Monitor invocations. Their lexical shapes included loops,
conditional output and change comparisons. Literal polling delays included forty
and sixty seconds. Some script paths had multiple Write requests, supporting
adaptation during the work. This is static historical evidence, not execution of
those scripts during this inspection.

Monitor requests followed errors after about twenty seconds in one conversation
and thirteen minutes in another. Repeated thirty-minute watch requests and
expiry-related notices are consistent with renewal. No causal claim is made for
every notification or subsequent turn, and a non-error tool response is not a
production effect receipt. The inspection started no monitor, scheduled task,
peer message, evaluation or cleanup operation.

## Implications for Codex Plus

Investigate background event delivery and model-controlled wakeups together.
The model should be able to choose a suitable read-only command/script, optional
snapshot filtering, an emitted-event source or a timed follow-up. Let it select
cadence, thresholds, useful observations, renewal and follow-up within the user's
existing scope. Avoid requiring one fixed polling interval, terminal condition,
source schema or intervention workflow for every job.

The runtime should provide exact destination binding, owned-process cleanup,
status/cancellation, visible resource bounds, stable event identities and truthful
receipts. Observations do not expand authorization. Keep these responsibilities
separate from decisions about the watched job. Do not deduplicate occurrence
events merely because two lines have identical text; optional snapshot filtering
has different semantics from a stream of occurrences.

Quiet observation should avoid accidental model turns. Deliberately scheduled
reassessment is a separate choice, so count its wakeups separately. Persist
intent and pending events outside model context, and expose uncertain delivery.
Do not promise exactly-once processing or automatically override a human stop.

## Planning still to finish on Snap

1. Walk through one representative real-use scenario and a short, bounded pilot.
   Choose a source that is already accessible; do not launch an expensive job.
2. Define the smallest useful Monitor-style and wakeup operations, including
   whether renewal updates an existing watch or creates another one.
3. Agree on source/output modes, user-visible receipts and configurable bounds.
   Decide which helpers belong in the first slice and which can follow.
4. Specify idle/busy delivery, human stop, unavailable owner, cancel/expiry and
   restart behavior. Freeze the exact native owner/thread after validation.
5. Set short offline and native acceptance checks, then agree on implementation
   slices. Python plus native queued delivery is a candidate, not a frozen API.

## Source transfer and reference availability

Continue in `/home/bryan/code/codex-plus` on Snap. Its old development checkout
was `/home/bryan/code/codex-worker-kit`, clean on `main` at `ee9894f`, with the
old GitHub remote. The requested preparation updates that checkout to published
rename commit `56b7158`, changes the remote and moves it to the new path, then
copies only the reviewed source/doc drafts. These drafts remain uncommitted.
Verify status and actual bytes at the start of the next conversation.

The full sibling `agent-harness-research` archive currently exists on Starship,
not Snap. This note carries the context needed to continue planning. When a
specific prototype or historical question needs more evidence, read the named
Starship reference rather than assuming the archive is installed on Snap:

- `docs/user-context.md`: reported operational workflow and independent sessions.
- `reports/usage-map.md` and `reports/cases.md`: sampled coverage and episode limits.
- `notes/2026-10-10-baseline.md`: original Claude mechanism references.
- `docs/current-direction.md`: Codex-first decisions and closed-study scope.
- `notes/2026-10-11-codex-daily-workflow-follow-up.md`: ordinary-session delivery.
- `notes/2026-10-11-codex-desktop-app-overlap.md`: native scheduling overlap.

The original research goal is closed. This source transfer does not deploy a
service, alter chezmoi pins, activate a worker skill or control other sessions.
