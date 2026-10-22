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
Snap and Starship selected those artifacts, while current-facing documentation
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

A dedicated CI workflow with read-only GitHub permissions runs the complete fixture suite and
release build/verification on Python 3.11 and 3.14. Its tmux tests use owned private
sockets; RTK and Actions dependencies are pinned. Pages retains separate deployment
permissions. The expanded local suite passed 302 tests before the final CLI reminder
regression was added; final source/CI counts are recorded below.

## Published release and validation

Completed 2026-10-21. Source commits are `a983f3d` (plan), `d54a85d` (watch/reminder
fixes) and `0ec803d` (unified release, diagnosis, CI and guides). The single
[v0.1.0-preview.9 release](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.9)
binds all components to source `0ec803df806fc311bab6ccafe2dd4fc6bdf12ad2`.
All five fetched assets match two independently built candidates byte for byte.

| Archive | SHA-256 |
| --- | --- |
| Workers | `14ee7f3334eaabb9c6210fcb650a35865331ae729df1303ccbc41083d1537248` |
| Monitoring | `eca07dd88aa54539610c21eb65768b793854a22d2339afec99ea52a48a461703` |
| Reporting | `cc1d9f805755e1e841b80e2530dac75c993e5b58f91329ae02ad7fc148bce874` |

The final suite passes **303 tests** locally and in both jobs of
[CI run 39735947262](https://github.com/byebyebryan/codex-plus/actions/runs/39735947262)
on Python 3.11 and 3.14. Both jobs also build and verify the complete release.
The 123-file inventory, agent/skill validation and `git diff --check` pass.
All agent, skill and legacy payload bytes remain unchanged.

Actual relocated artifacts initialize both MCP adapters with version preview.9
and list 15 monitoring/four report tools without native access. New tooling also
verifies Snap's selected old monitoring preview.3/report preview.8 installations.
The release verifier rejects mixed identities, changed checksums and unsafe paths.

[Pages run 39735947123](https://github.com/byebyebryan/codex-plus/actions/runs/39735947123)
published the updated guides successfully. Eleven public routes/assets returned
HTTP 200 with exact candidate bytes. Owned browser checks passed all eight guide
routes and 16 illustrative scene states at widths 1440, 768, 390 and 320, with
keyboard, copy fallbacks, environment selection and zero browser errors. These
checks validate presentation and delivery; they are not native watch trials.

## Initial managed candidate: 2026-10-21

The initial dotfiles candidate was commit `6aad69e`, branch `codex-plus-preview-9`, in
[PR #5](https://github.com/byebyebryan/dotfiles/pull/5), drafted before the later direct publication below. It updates worker,
monitoring and report URLs/revisions/fetched checksums, selectors, doctor wiring,
validators and release notes together. Worker payload hashes remain unchanged;
the compatibility worker tree gains its product identity manifest.

Codex Plus and split-home validators pass. The report artifact checker passes
isolated extraction/publication/CLI/MCP/retained-data/convergence checks on all
three supported profiles. The full checker's exact Codex Plus pin section passes;
the unrelated full desktop/fleet checker was not run for this scoped candidate.
Separate disposable Snap and Starship homes pass targeted status/diff/dry-run,
script-excluded fixture apply, three-component manifest verification and
convergence. No native daemon or real report service starts for these checks.

Concurrent desktop edits appeared in the canonical chezmoi checkout during this
pass. They remained untouched; that initial managed upgrade was isolated on its
draft branch, with publication to main and live apply deferred to the later request below.

## Managed rollout: 2026-10-22

Bryan requested direct publication, followed by bringing Snap and Starship up to
date. Dotfiles main contains the nine-file upgrade as `4598b2a`; PR #5 is closed
without merging. Both canonical source checkouts contain those pins. Snap's
overlapping local checker edit was retained, and Starship's local commits were
merged with published history without publishing that unrelated work. Uncommitted
and untracked desktop edits on both hosts were preserved.

Targeted `chezmoi status`, `diff` and verbose dry runs showed only the new
release directories, selection links, doctor entry point and worker manifest.
The live applies excluded scripts and addressed only those component targets and
their existing agent/skill entry points. All three payload inventories, hashes,+modes, versions and source revisions verified before changing selection links.
Older immutable releases remain installed for captured processes and rollback.

| Host/context | Workers | Monitoring | Reporting |
| --- | --- | --- | --- |
| Snap OSS and work | preview.9 | preview.9 | preview.9 |
| Starship default | preview.9 | preview.9 | preview.9 |

All three components resolve to source `0ec803d`. Read-only installed diagnosis
passes in every context, and scoped managed diffs converge to empty. Existing
configuration/auth files, worker agent/skill files and private profile modes are
unchanged across 128 protected Snap paths and 68 Starship paths. The 24 captured
Snap native/MCP/report process identities and 23 Starship identities were retained.
Snap's two report endpoints and Starship's report
endpoint retain HTTP 200 and byte-identical catalog responses. No daemon, MCP
bridge or report server was restarted, and no new native model workload was run.

## Remaining evidence boundaries

Both hosts select preview.9; existing MCP/native/report processes retain their
captured code until normal reconnect. The rollout establishes installation and
preservation, without a global refresh, real watch/reminder, peer write or new
native model trial. Codex 0.163.0 compatibility remains unqualified against the recorded
0.162.1 baseline. Long-run/provider recovery and daily UX remain ordinary-use
evidence, not outcomes inferred from fixtures. Pre-existing untracked bytecode
in the source checkout is preserved.
