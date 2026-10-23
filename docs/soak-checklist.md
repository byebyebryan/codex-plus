# Daily-use soak checklist

The installed preview is ready for normal-use trials on Snap and Starship.
Bounded synthetic acceptance is complete; a daily-use soak has not been completed.
Use existing work and already authorized sources rather than creating workloads
just to keep a monitor busy. The [daily guide](daily-use.md) supplies the requests.

## During the first several working days

Try a peer watch/message when two independent sessions are already doing related
work. Try an endpoint or log source that matters to a current task, a later check,
and a browser handoff when useful. Include configured MCP inspection when the
task needs it. Host coverage follows actual work; one host's experience does not
prove the other's real-source behavior.

Keep user-facing requests natural. If you repeatedly need exact titles, UUIDs,
JSON or detailed polling recipes, record that as an interaction problem rather
than making it the normal usage pattern.

## What to notice

| Area | Useful evidence |
| --- | --- |
| Setup and discovery | Selected the intended source/session, clarified real ambiguity, excluded subagents, and returned without foreground waiting. |
| Useful follow-up | Relevant changes reached the conversation; no missed transition was concealed by a success summary. |
| Quiet operation | Unchanged data and irrelevant churn did not create needless model turns or repeated chat updates. |
| Permissions/authentication | Used the existing grant/connection; unavailable or expired access was explained without a bypass. |
| Continuation | A useful successor was explicitly registered; expiry was distinguished from task completion. |
| Control | Explicit stop prevented renewal/replacement and left observed work intact; Esc behaved as foreground interruption. |
| Conversation | Follow-ups respected foreground work, human input and drafts; a peer's text did not create new task authority. |
| Delivery/receipts | Queued, handled, accepted/declined and external success were reported separately; uncertainty was not blindly replayed. |
| Returning to work (preview.10+) | A recap reread this conversation's stored receipts, kept pending/failed follow-ups visible and explained stale or missing outcomes without resending or restarting. |
| Cost | Cadence matched the task; MCP checks had visible model use, while quiet command reads avoided inference per poll. |
| Reporting | A readable result and reachable immutable link were useful from the viewing desktop; publication and HTTP delivery were distinguished. |

Record a clear success as well as failures. “No issue noticed” is weaker than
observing a known useful transition, its handling and an effective stop.

## Small private observation note

Copy this into a private working note when a meaningful episode occurs:

```text
Date / host / Codex Plus version and source revision, if known:
Scenario: peer / endpoint / logs / MCP / reminder / report
Request, summarized without private names or credentials:
Expected useful condition:
Observed setup / update / continuation / stop:
Result: useful / noisy / missed / ambiguous / access failure / not observed
Latency or model cost, if actually measured:
Receipt stage and private evidence location, if relevant:
User friction / smallest follow-up:
```

Keep credentials, transcripts, event journals, actual session IDs and private
resource names outside committed source and report exports. A published issue
should use a sanitized trigger, expected/actual behavior, versions and a small
reproduction. Runtime journals and authoritative native history can support
diagnosis privately; summaries alone do not prove a failed or successful tool call.

## Review after representative use

Group findings as interaction, runtime/delivery, source access/provider, cost or
report presentation. Prioritize wrong destination, ineffective stop or lost
useful events before wording improvements. Do not compensate for those findings
by silently retrying ambiguous messages, widening access or restarting an owner.

Keep untested dimensions explicit: longer operation, real credential/provider
recovery, each host's actual sources and personal UX. A week with no relevant
transition is not a completed reliability test. Decide the next bounded pass from
the observed gaps, without promoting this checklist into production acceptance.

This guide starts no watch, reminder, peer message or background job. Normal
requests authorize their own bounded use; collecting feedback requires no new
automatic monitoring of other sessions.
