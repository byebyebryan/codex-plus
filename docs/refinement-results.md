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

The unified release uses version `0.1.0-preview.9` from one authoritative constant.
Both MCP initialization responses, report plugin manifests and worker/runtime/report
artifact identities agree. The release builder creates three deterministic archives,
`release.json` and `SHA256SUMS`; its offline verifier rejects mixed revisions,
unexpected paths, changed bytes, mismatched inventories and checksum files.
Existing monitoring previews 1–3 and reporting previews 7–8 remain selectable.

The read-only doctor verifies selected manifest contents/modes and reports enabled
MCP configuration, effective managed storage paths, legacy/mixed installations and
client/owner version evidence. It does not expose unrelated MCP arguments or
environment credentials, start services or claim loaded-process versions. A fresh
Snap check confirms both native client and owner are 0.163.0, outside the recorded
0.162.1 qualification. Fresh passive SSH reads confirm Starship also selects the
earlier preview.3/preview.8 artifacts. Current-facing docs now reflect that fact.

A dedicated read-only-permission CI workflow runs the complete fixture suite and
release build/verification on Python 3.11 and 3.14. Its tmux tests use owned private
sockets; RTK and Actions dependencies are pinned. Pages retains separate deployment
permissions. The expanded local suite passed 302 tests before the final CLI reminder
regression was added; final source/CI counts are recorded below.
