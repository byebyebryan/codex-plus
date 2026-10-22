# Daily-use refinement and unified-release results

Started 2026-10-21. The selected scope is recorded in the
[implementation plan](codex-plus-plan.md#current-pass-daily-use-refinement-and-unified-releases).

## Baseline

Read-only review found an offline coordinator could leave detailed watch status
claiming a running source; source failures were omitted from model status;
default reminder expiry rejected delays of two minutes or longer; historical
watches produced unbounded output; and runtime tests were absent from CI.
The existing 288 fixture tests passed in a clean isolated source copy.

Monitoring preview.3 and reporting preview.8 were both built from `c73c237`.
Snap and Starship select those artifacts, while current-facing documentation
still described older Starship selections. The locally installed Codex client
reports 0.163.0; the monitoring manifest records qualification against 0.162.1.
Neither fixture tests nor documentation publication requalify native protocols.

## Execution and acceptance

The watch/reminder slice passes 293 fixture tests in an isolated source copy.
Status list and detailed inspection share coordinator freshness handling, expose
source/control failures and bounded event/renewal receipts, and retain unresolved
delivery. Default watch listing includes active and unresolved registrations;
history is retained with explicit bounded pages. A 202-watch fixture verifies
settled history is omitted from ordinary output and available without duplicate
entries across history pages. Pending renewal references are inspectable.

Reminder expiry now defaults to the requested delay plus 120 seconds, capped at
the configured lifetime. Its receipt states the remaining delivery window; a
delay at the lifetime limit is rejected before job admission. Explicit expiry
still must follow the due time. A ten-minute reminder fixture remains unique
while its owner is busy and starts within its delivery window when idle.

Existing active sessions and services are preserved; managed live applies and
native model trials are outside this pass. Artifact and publication results will
be recorded as the remaining slices complete.
