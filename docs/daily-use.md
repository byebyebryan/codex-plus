<a id="using-codex-plus-day-to-day"></a>

# Watches and reminders

You can leave a job running and keep working in the same Codex conversation.
Tell Codex what would change your next step. That might be an export finishing,
a service coming back online, or another agent asking for input.

> Watch the export pipeline in CI. Tell me when the archive is ready, a test
> fails, or the run needs input.

This follows a pattern from background monitoring in Claude Code. A command
or script handles the routine reads without using model turns. You hear back
in this thread when one of your conditions is met.

> Check the export pipeline once in 20 minutes. Is the archive ready?

Use a reminder for one later check. When Codex runs it, you get the status it
finds, even if the pipeline is still running.

## Choose a follow-up

- **[Watch a run](#read-a-command-or-script)** Follow a log or status endpoint with a command or script.
- **[Check once later](#check-again-later)** Ask Codex to return to this conversation for one check after a delay.
- **[Watch a session](#watch-another-session)** Follow another open session on the same daemon. Ask for an update when that agent needs input.
- **[Schedule an MCP inspection](#inspect-a-configured-mcp-source)** Use a tool already connected to the session. Each inspection uses a model turn.

For initial setup, choose the components and open a fresh ordinary session in
the intended environment. Existing opt-outs still apply on managed installs.
[Choose components](getting-started.md#choose-what-to-install).

## Start with a real task

If the run is new to the conversation, include its link or log path. A
one-time check can wait behind active work and may expire before it runs.
Ask “What are you watching, and what checks are scheduled?” to see what Codex
set up, or “What am I still waiting on?” for the cached recap.
[Read a follow-up recap](#return-to-unfinished-work).

For delegated work, choose an explicit [worker workflow](workers.md#choose-a-workflow).

## Watch another session

Peer communication uses two independent, loaded sessions in the same daemon.
A child agent belongs to its primary and is excluded from peer discovery.
Codex uses project and recent task context to find a peer, asks if the match is
ambiguous, and reports when a reference disappears. [Find, message and inspect
independent sessions](session-communication.md) for the worked example and
boundaries.

Routine reads and phase changes can stay quiet. If you need to take over a
file, ask the other agent to tell you when it has finished editing. A session
can sit idle with work still open, and accepting a message only records its
agreement to the request.

## Watch an endpoint or inspect through MCP

### Read a command or script

> Watch this run and tell me if it stalls or fails.

The model can repeat a short command or run a continuing script against a
source that the session can access. Its filter can emit just the changes that
merit a turn in your conversation. Give the endpoint or run reference if it
is new to the conversation. Use the configured connection or an
authorized private reference for credentials.

### Inspect a configured MCP source

If the source is available through MCP, Codex schedules a native turn and
calls the tool over its ordinary approved connection. Each check uses model
time. Say “Check it less often” to guide the next cadence. If access is
missing, Codex identifies the gap.

Both kinds of watch have a finite lease and event allowance. On expiry, the
model can report that observation ended or explicitly continue it under your
original request. The final state of the watched task needs its own evidence.
“Stop watching that run” cancels the watch and forbids renewal or replacement.

## Check again later

Ask “Check again in 20 minutes” when you want one update even if nothing
changes. You can use the conversation in the meantime. If a turn is still
running when the reminder comes due, the check waits. By default it can wait
up to two minutes past the requested delay, within the configured lifetime
limit. The receipt shows that window. Codex can set a longer expiry if needed.

If the turn stays busy past expiry, the reminder records that outcome. Ask
“Cancel the endpoint reminder” to cancel that one check. Recurring calendar
events and cron schedules are outside this preview.

## Inspect follow-up health

Ask “What are you watching?” for active watches and unresolved findings.
The recap gives the age of cached receipts and flags source failures, gaps,
control holds or uncertain delivery. A previously running observer has unknown
status if its coordinator is offline. Request watch history for bounded pages
of settled entries and retained handling receipts.

In preview.21, tracking continues for a callback known to be running even
after early acknowledgement, source expiry or cancellation. After reconnect,
a bounded read of native history may recover a missing final receipt.
Otherwise the outcome stays unknown. Existing helpers pick up the change on
normal code adoption.

An ephemeral peer can expose its name, project and phase even when native
history or goals are unavailable. Codex reports those fields as unsupported
and can only watch available signals. The same independent-session rule applies.

<a id="return-to-unfinished-work--source-preview"></a>

### Return to unfinished work

Preview.10 added these ways to recover context. [Release history](getting-started.md#released-and-source-features).

| Ask | What the recap should cover |
| --- | --- |
| “What checks are still pending?” | This conversation's active reminders, unknown follow-up outcomes and failures needing attention, with due time, expiry and receipt freshness. |
| “Did it accept my request?” | The stored message kind, a short quoted excerpt and its received/accepted/declined handling receipt. Completion needs separate evidence. |
| “What am I still waiting on?” | Watches, reminder follow-ups and recorded outgoing messages, with stale or missing evidence explained. |
| “Show me the history.” | Bounded pages of settled registrations and retained receipts. Codex reads or identifies additional pages. |

> I’m still watching packaging for a blocker. The CI reminder was received, but
> its follow-up turn hasn’t finished. Packaging accepted the release-note request. I don’t
> have a completion receipt. This recap uses the last recorded status for both.

Inspection reads cached receipts for this conversation. Its saved references
survive context compaction. Polling a source, resending a message or restarting
an observer is a separate action.

### Interpret the receipt

- **Acknowledged** means the reminder reached the conversation. Its follow-up turn may still be running.
- **Failed or interrupted** stays visible until you cancel the reminder. Cancellation keeps its receipts, including an already consumed turn whose outcome is unknown.
- **Unknown** means a terminal receipt or reliable delivery evidence is missing. A coordinator exit leaves this unresolved. The model can report an unresolved withdrawal or delivery without retrying the input.

Detailed inspection shows up to three event receipts, giving unresolved
delivery priority, plus bounded renewal details. Since preview.12, cancelling
a watch closes attention for a known terminal source error. The error stays in
history. Uncertain delivery or withdrawal and unacknowledged native input stay
visible. Preview.11 used the earlier cancellation behavior.
[Qualification and correction](native-qualification-results.md).

## Stop, interrupt or leave

| Action | Effect |
| --- | --- |
| Press Esc | Interrupts the foreground turn. Independent watches/reminders remain registered within their bounds. |
| Say “Stop watching that run” | Cancels that watch and forbids renewal or replacement. The observed work stays under its owner’s control. |
| Cancel a reminder | Stops the selected future reassessment and reports any already admitted delivery. |
| Detach the TUI | Independent observation can continue within its bounds while the owning runtime is available. |
| Lose the owner or source | Stops or holds follow-up and records the gap. Owner recovery requires explicit action. |

Cancellation cannot undo an already handled message or an external action.
The preview does not intercept native `/exit` to add a background-task
confirmation dialog. Treat viewer detachment and daemon shutdown separately.

### After a daemon restart

With preview.19 code loaded, eligible peer watches and un-emitted reminders
can continue within their original bounds after a verified daemon restart.
Commands and scheduled MCP checks require an original `restart=resume` choice
for a source safe to repeat. Older registrations without trustworthy lease
evidence and uncertain deliveries stay quarantined. Ask “What am I still
waiting on?” for cached state and gaps. The model can use explicit owner
recovery when needed. [Recovery and adoption limits](owner-recovery.md#daemon-restart-candidate-preview19).

## Make a browser report

> Make a browser report of what we learned, with the main risks.

The report skill or four report MCP tools can publish an immutable copy and
return its link, list or inspect existing snapshots, and delete a report you
select.
Reports are grouped by project. Publishing can start or reuse the
separately managed server. A read-only listing leaves its state alone.
The link works independently of the TUI while the host and endpoint are
online. From an SSH Kitty terminal, Ctrl+Shift-click opens the link on your
desktop. [Publish and find reports](html-report-usage.md#publish-and-find-reports).

## Choose the environment first

On Snap, `codex` and `codex agents` use OSS. `codex-work` and
`codex-work agents` use work. `codex-oss` is retired. A native `--profile`
chooses settings within the selected home.

Each environment has its own daemon, peers, report store and endpoint. Peer
messages stay within the selected daemon even when both environments run on
Snap. Existing sessions can retain older MCP code until reconnect.
[Environment selection](environments.md).

Completion and approval alerts use native Codex and terminal behavior; the
monitoring runtime adds no terminal relay or notification hook.
[Notification ownership](notifications.md).

## What daily use is testing

Useful watches, messages, endpoint access, configured MCP inspections and explicit
stop passed bounded native acceptance on Snap and Starship. Those checks used synthetic
sources and owned sessions. Real credentials/provider recovery, long unattended
operation and your judgment of the interaction still need daily-use evidence.

Use the [soak checklist](soak-checklist.md) during normal work. See
[how the package works](architecture.md) for component boundaries, Claude
workflow coverage and evidence, or the [browser walkthrough](https://dev.byebyebryan.com/codex-plus/walkthrough/#scenes)
for illustrative examples. Low-level CLI diagnostics remain in the
[technical watch guide](watch-candidate.md).
