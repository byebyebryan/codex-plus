# Review, refinement and distribution pass

Execution requested from planning checkpoint `755855e`, 2026-10-12. The selected
finish line is a published verified preview and a focused validated managed-rollout
change, without live apply. The previous native recipe remains closed. Fresh
allowance: 24 automatic deliveries / 48 acceptance turns, including failures and
cleanup; each watch is at most 120 seconds/two observations and the whole recipe
allows at most one model-chosen renewal.

## Baseline and prioritized review

Codex still reports 0.162.1. The existing listener and requesting conversation
were positively verified. Local source was clean at `755855e`; freshly queried
GitHub main still selects `56b7158`. Canonical dotfiles have concurrent edits,
including the portable Codex template and validator. Their file hashes/modes are
recorded privately, and rollout work will be isolated. No managed file or native
session was changed for this baseline.

| Finding | Refinement | Evidence |
| --- | --- | --- |
| Model-facing one-shot wakeups could be created but not listed/cancelled. | Add cached `wake_list` and exact `wake_cancel` over existing coordinator controls. | Reminder registration, passive listing and selected cancellation regression. |
| A consumed cancelled reminder could still create replacement work through the model API. | Apply the cancelled-supervision guard to reminder callbacks as well as watches. | Cancelled correlated reminder refuses a replacement. |
| The calling turn could be interrupted during native validation after the early model guard. | Recheck native calling context immediately before CLI intent writes. | Interruption during validation leaves no registration. This narrows the race; it is not a cross-process atomic authorization claim. |
| Watch/reminder intent persisted before coordinator startup failed, but the caller received only a tool error and could repeat it. | Return a durable registered/coordinator-unavailable receipt and retain the model reference. | Startup failure preserves one watch and one reminder, inspectable without retry. |
| Lost-source recovery existed only on the low-level CLI. | Add explicit `watch_recover`, retaining frozen source, remaining lease, gap and uncertain delivery. | Lost source refuses renewal; explicit recovery does not create another source identity. |
| Reusable capability guidance was injected by the previous fixture driver. | Advertise generic guidance in MCP initialization instructions. | Protocol regression verifies the shipped instructions; native installed-client qualification is pending. |

All 167 tests pass at this refinement checkpoint. The source inventory now includes
this sanitized report. Worker files, identities and activation metadata are unchanged.
Readable queue delivery remains selected; the failed standalone-tool-output ordering
gate is carried forward rather than replayed.

## Remaining gates

The source now builds a reproducible 18-file runtime artifact plus its manifest,
with source revision, content hashes, modes and explicit compatibility. Isolated
installation verifies before extraction, refuses traversal/links/duplicates or
changed immutable releases, and activates/rolls back only a release-selection
symlink. Relocated stdio tests load shipped guidance with no source import path;
disabled configuration needs no installation/native endpoint. Native endpoint
selection is lazy/status-only and private state is outside the artifact. Default
approval separates own supervision controls from optional peer-send approval.
All 174 tests pass; native installed-model activation remains pending.

## Installed qualification and targeted corrections

The `1df7a72` artifact builds reproducibly and installs outside the source checkout.
A fresh native session quoted its shipped guidance and called `watch_list` and
`wake_list` without driver-injected capability instructions. Automatic status-only
endpoint resolution found the existing owner. No registration was created.

The initial ambiguity fixture emitted a concise baseline/alternate choice and
created no watch, but its driver timed out waiting for turn completion and closed
the actors. The next driver incorrectly expected an in-progress command in persisted
history; the finite foreground pause had already completed. Its watch lease ending
notice remains counted. Neither closed fixture was resumed or replayed.

A fresh core pair established a quiet contextual watch and handled a useful update
with one fresh peer read/current-event acknowledgement. A native TUI capture shows
readable watch input with the unsent draft preserved, closing the earlier capture
gap. Ordinary stop cancelled its selected lineage. This evidence does not establish
the failed new foreground/earlier-human-input ordering fixture.

The information receiver then completed a chat response without calling `event_ack`.
That is a genuine receipt-guidance gap, not successful formal handling. The generic
server instructions now explicitly require one acknowledgement for every watch,
lifecycle, reminder and peer-message event, distinguishing received from request
acceptance/decline. Native requalification uses fresh actors. The owner audit also
found that the native listener UID was assumed from the caller; it now verifies the
actual listener process UID, with an adverse-owner regression. All 175 tests pass.
At this checkpoint the closed prototypes used 15 turns / 4 deliveries, including
the ending notice and undelivered/withdrawn generated events. Allowance is retained.

Installed capability loading, relocatable artifact/provenance, active-runtime-safe
upgrade/rollback, fresh native/TUI acceptance, publication/fetched-byte verification
and managed rollout preparation remain in progress. Source tests are not proof of
these gates. Private runtime state, real discovery context and captures remain out
of committed files. No live apply, native daemon restart or production work is part
of the selected finish line.
