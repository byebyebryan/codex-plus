# Using Codex Plus day to day

Codex Plus adds explicit worker workflows, watches, later checks, peer messages
and browser reports to the ordinary Codex CLI/TUI. If this is your first visit,
use the [setup guide](getting-started.md) to choose the components you need.
For the managed Snap and Starship preview, open a fresh ordinary session in
the intended environment; monitoring and report MCP tools load from its
configuration. Existing opt-outs remain effective.

Describe what you need in normal language. The model chooses the source,
filtering, cadence and continuation. You do not need a thread UUID, exact session
title, JSON prompt or polling recipe. If the source or destination is unclear,
the model should ask a short clarification.

## Choose the environment first

On Snap, `codex` / `codex agents` use OSS, while `codex-work` /
`codex-work agents` use work. `codex-oss` is retired. A native `--profile`
selects settings inside one home; it does not provide this separation.

Peers are discovered only in the selected daemon. A work conversation cannot
message an OSS conversation through the peer tools, even though both are on
Snap. Reports also use their own selected store and endpoint. Existing sessions
may keep older MCP code until reconnect; a source upgrade alone does not reload
an active process. See [environment selection](environments.md).

Native completion/approval alerts remain available. Codex Plus adds no terminal
relay, custom hook or desktop-notification publisher.

## Start with a real task

For delegated implementation or investigation, choose an explicit
[Luna or adaptive worker workflow](workers.md). Use `$luna-task` for one bounded
assignment or `$luna-goal-loop` for a substantial goal with Luna. Your primary
keeps decisions and review. `$worker-task` and `$worker-goal-loop` let the primary
choose whether delegation helps. A generic “goal loop” does not select a worker.

| What you need | What to say |
| --- | --- |
| Follow another session | “Watch the session doing the packaging work and tell me when it is ready.” |
| Share context | “Tell that session the handoff should include the risks.” |
| Follow an endpoint or run | “Watch this run and tell me if it stalls or fails.” |
| Inspect later | “Check this endpoint again later.” |
| See registrations | “What are you watching, and what checks are scheduled?” |
| Stop a watch | “Stop watching that run.” |
| Cancel a later check | “Cancel the endpoint reminder.” |
| Get a browser report | “Make a browser report of what we learned, with the main risks.” |

Supply an endpoint, run or project reference when it is not already established
in the conversation. Keep credentials in the existing configured connection or
an authorized private reference rather than pasting them into the request.

## Watch another session

Start two independent sessions within the same daemon on one host. One can do
the packaging work while the other observes it. A subagent spawned by a parent
is a different relationship; it is excluded from ordinary peer discovery.

The observing model uses project and recent task context to find the right
session. If two plausible sessions remain, it asks which one. Once selected,
“that session” keeps the same identity even if its title changes. A lost reference
does not silently switch to a different session.

Setup should give a short confirmation of the selected work and useful condition.
Follow-up should report changes relevant to that condition. Routine checks,
ordinary phase changes and successful renewals can remain quiet.
Later updates should explain a meaningful finding, such as readiness or a request
for input. Observation does not resume, interrupt or stop the other session.
Idle status alone does not prove that its task succeeded.

“Tell that session to include the risks” sends an attributed request. The receiver
evaluates it against its existing task and direct user instructions. A receipt
can show received, accepted or declined; accepted does not prove the requested
work finished. Ask “Did it accept that request?” for the cached handling receipt.

Peer communication is currently within one daemon. Installing Codex Plus on two
hosts does not add Snap-to-Starship native messaging.

## Watch an endpoint or inspect through MCP

For an accessible endpoint, the model can select repeated short commands or a
continuing script. Unchanged reads can stay quiet without a model turn per poll.
Useful emitted observations return to your conversation for interpretation.

For a configured MCP source, the model schedules native inspection turns and
calls the selected tool through its normal approved connection. Each check has
model cost. “Check it less often” can guide the next cadence; “Stop watching it”
ends the selected watch. Missing access is explained rather than bypassed.

An observer has a finite lease and event allowance. Expiry means observation
ended, not that the task completed. The model can explicitly continue useful
observation under your existing request or report that it ended. Explicit stop
forbids renewal or replacement.

## Check again later

“Check this endpoint again in a little while” registers one future reassessment
and returns now. The model should not hold the foreground turn open with sleep
or repeatedly poll while waiting. A due check follows native conversation
control and can wait behind active work; it is not an exact-time alarm.

The default expiry leaves up to two minutes for delivery after the requested
delay, within the configured lifetime limit. The receipt states that window;
the model can choose an explicit longer expiry when the request needs it.
If active work outlasts expiry, the reminder records that outcome.

A reminder is separate from a watch. Ask to list or cancel the relevant reminder
when you want to stop it. The preview does not provide a recurring calendar or
cron service.

## Inspect follow-up health

Ask “What are you watching?” for bounded active and unresolved watch status.
Source failures, observation gaps, control holds and uncertain delivery are
reported with cached receipt freshness. An offline coordinator makes a previous
running receipt unknown. Ask for watch history to page through settled entries;
history and handling receipts remain retained.

The unreleased source candidate extends this inspection to reminders and
outgoing-message discovery; installed preview.9 retains its earlier behavior.
Ask "What checks are still pending?" for active and unresolved reminders. The
answer distinguishes cached intent, due time, lease expiry and handling. Ask for
reminder history to include settled checks; both lists are bounded and paginated.
Inspection leaves existing follow-ups unchanged and explains stale evidence.

A reminder's acknowledgement confirms receipt before follow-up work finishes.
Pending or unknown native turn outcomes remain visible. Failed or interrupted
follow-ups need attention until you explicitly cancel that reminder; its receipts
stay in history. Cancellation preserves an already running native turn, whose
unknown outcome remains visible until a terminal receipt is recorded. Inspection
does not infer completion from missing receipts or retry the follow-up.

"What am I still waiting on?" combines this conversation's watches, reminders
and recorded outgoing-message receipts. References survive context compaction;
message inspection can rediscover them without another send. Each receipt shows
the stored information/request kind and a short quoted message excerpt, so
several messages to the same peer can be distinguished. The model should
state incomplete coverage and distinguish last confirmed facts from current
activity. This is a recap of the bound conversation, not an inventory across
other conversations, environments or hosts.

Detailed inspection shows up to three event receipts with unresolved delivery
first, plus bounded renewal details. A receipt records observation, admission or
handling; it does not establish that the watched work succeeded.

## Stop, interrupt or leave

| Action | Effect |
| --- | --- |
| Press Esc | Interrupts the foreground turn. Independent watches/reminders remain registered within their bounds. |
| Say “Stop watching that run” | Cancels that watch and forbids renewal/replacement; the observed work stays intact. |
| Cancel a reminder | Stops the selected future reassessment; reports any already admitted delivery. |
| Detach the TUI | Does not itself cancel observation while the owning runtime remains available. |
| Lose the owner or source | Stops or holds work with an unavailable/gap receipt; no automatic owner replacement or cold resume. |

Cancellation cannot undo an already handled message or an external action.
The preview does not intercept native `/exit` to add a background-task
confirmation dialog. Treat viewer detachment and daemon shutdown separately.

## Make a browser report

Ask for a report when a result benefits from a shareable view. The report skill
and four report MCP tools publish immutable static HTML, list/get reports and
delete a specifically selected report. Reports are grouped by project.

Publishing can start or reuse the separately managed report server; read-only
listing does not start it. The returned link remains useful independently of
TUI attachment while its host and serving endpoint are online. From an SSH Kitty
terminal, Ctrl+Shift-click opens it in the local desktop browser.

See the [report guide](html-report-usage.md) for hosting and storage details.

## What daily use is testing

Useful watches, messages, endpoint access, configured MCP inspections and explicit
stop passed bounded native acceptance on both hosts. Those checks used synthetic
sources and owned sessions. Real credentials/provider recovery, long unattended
operation and your judgment of the interaction still need daily-use evidence.

Use the [soak checklist](soak-checklist.md) during normal work. See
[how the package works](architecture.md) for component boundaries, Claude
workflow coverage and evidence, or the [browser walkthrough](presentation.md)
for four illustrative scenes. Low-level CLI diagnostics remain in the
[technical watch guide](watch-candidate.md).
