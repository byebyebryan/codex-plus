# Review, refinement and distribution pass

Execution requested from planning checkpoint `755855e`, 2026-10-12. The selected
finish line is a published verified preview and a focused validated managed-rollout
change, without live apply. The previous native recipe remains closed. Fresh
allowance: 24 automatic deliveries / 48 acceptance turns, including failures and
cleanup; each watch is at most 120 seconds/two observations and the whole recipe
allows at most one model-chosen renewal.

## Final status

The loop is complete at **12 deliveries / 42 started acceptance turns**: 40 completed
and two prototype turns interrupted during exact cleanup, with zero provider failures.
Failed harness cases and unacknowledged completed replies remain counted. Released
runtime: **v0.1.0-preview.1**, source `f4db934fc8a5bafe2bc392378c2ab3e26ee1f7c2`.
[Published preview](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.1).

The fetched runtime is byte-identical to the accepted reproducible artifact:
SHA-256 `0f1322e4faeceab05a8ce34d2877d36b83cde19dd47bf45fa57324abdfdcf3ea`.
Its 18 files plus manifest have exact declared modes. The fetched source archive
contains all 65 matching source files and executable flags, SHA-256
`c2ba0ce93d8eb0f3e881bbe969f120a22f9b513024becdc0832c25a3a787b323`.
GitHub's source tar uses 0664/0775 rather than checkout 0644/0755; source acceptance
checks content and Git executable flags, while runtime acceptance verifies full
0644/0755 modes. Worker files are unchanged across the entire release diff.

All **177 tests**, the 65-file inventory and whitespace checks pass. Final native
checks qualified explicit same-owner remaining-lease recovery, cached offline status
without restart, outgoing cancellation preserving completed handling, and default
cross-session approval refusal with no message. Earlier installed checks qualified
shipped guidance, contextual watch/stop with TUI draft capture, information/request
receipts, reminder fire/cancel and active-runtime selection/rollback. The final
runtime uses one compact fixed receipt hint in readable queue input; server guidance
alone did not reliably cause incoming-information receipts.

The new foreground/earlier-human-input matrix was not successfully requalified:
its driver missed the running-command notification and waited on persisted history.
The unchanged queue implementation retains prior runtime/regression evidence;
this pass does not promote that driver failure into a new acceptance claim. A
model-chosen renewal, full daemon-incarnation recovery, long production operation
and personal UX assessment were not newly qualified. The preview does not claim
universal daily reliability or new-task/cross-host authority.

## Managed rollout prepared, live apply deferred

An isolated checkout from published dotfiles base `0598363` holds focused commit
**`1c17dd5`** on local branch `codex-plus-preview-n91wsqir`. It updates the seven
worker-source pins and adds the separate immutable runtime pin, stable entry/
selection symlinks, optional host configuration, policy-preserving merge and a
focused validator/rollout guide. The branch is not merged into canonical source or
applied. Its canonical unpublished desktop commit and concurrent edits are excluded.
One canonical `scripts/check` change advanced independently during this loop; it
was not restored or edited by this work.

The full dotfiles validator passes. Focused tests cover Snap/Starship and unknown
hosts, disabled/enabled settings, explicit machine opt-in, and preservation of MCP
approval/disable, plugin, project and skill preferences. The preview is disabled by
default, with availability distinct from starting a watch. Cross-session sends and
outgoing cancellation retain separate approval/explicit opt-in.

A scoped chezmoi dry-run passed for 11 intended package/worker/runtime/config target
groups. Rendering the current live Codex config produced only the new owned MCP
namespace, with zero other semantic changes; output was kept private. Render and
dry-run are not installed/live acceptance on Snap or Starship. No live apply, global
config mutation or daemon restart occurred. Rollback restores the previous pin/owned
wiring and preserves journals and active native work.

## Cleanup and next shared review

All 17 owned experimental actors have zero loaded membership. Each stage inspected
queues while its actors were still loaded, then archived only those actors. Owned
native viewers, MCP bridges and coordinators are stopped; final process/identity
checks found none. The original listener and this requesting conversation's positive
loaded membership remain preserved. Older walkthrough viewers are untouched.
Private state/captures and real discovery context are not release content.

The primary-driven A/B walkthrough is ready using the published runtime and fresh
owned actors under a new allowance. Bryan observes ordinary watch, readable update,
message/handling and stop; the primary drives prompts/transitions and cleanup. The
last loop's unused allowance is not a reopened recipe. Live deployment/enablement
and personal UX feedback are the remaining selected next steps.

The sections below retain implementation checkpoints and corrections in order;
their pending-gate statements are historical, not the final status above.

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

Fresh receiver tests on `4b27d2d`, including explicit CLI resume configuration,
still produced a completed chat response without a formal receipt. The shipped
guidance alone is insufficient for this incoming-information case. The runtime
event frame now includes one fixed compact receipt instruction naming `event_ack`,
with received versus accepted/declined meaning and the existing-task scope footer.
It adds no target identity, polling recipe or new operational authority. Before
this targeted correction, combined usage was 21 turns / 6 deliveries; the closed
events were not replayed. Publication remains gated on fresh receipt proof.

Fresh `a632c07` installed/native TUI actors passed information receipt, accepted and
declined existing-task requests, cached status without ping-pong, reminder fire and
natural cancellation. During a pending reminder, selecting the earlier immutable
release and then rolling back preserved the exact running coordinator; the reminder
was subsequently handled. The fixed receipt hint is visible readable queue input,
not a hidden native event. Combined usage is now 33 turns / 10 deliveries.

The review additionally closes outgoing message cancellation over the sender's own
reference. It refuses forged sender ownership and preserves completed handling;
cached status now shows intent and withdrawal as well as turn/handling outcomes.
Peer-send opt-in covers this related outgoing control; default write approval is
retained. Native qualification of this last slice remains pending.

Installed capability loading, relocatable artifact/provenance, active-runtime-safe
upgrade/rollback, fresh native/TUI acceptance, publication/fetched-byte verification
and managed rollout preparation remain in progress. Source tests are not proof of
these gates. Private runtime state, real discovery context and captures remain out
of committed files. No live apply, native daemon restart or production work is part
of the selected finish line.
