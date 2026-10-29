# Implementation handoff

Updated 2026-10-29. The owner-recovery source candidate is isolated on Starship
in `/home/bryan/code/codex-plus-owner-recovery`, based on maintained main. Preserve
the older report checkout and the existing worktrees. Installed release state
below remains the separately qualified preview.10 rollout.

## Current scope and entry points

Codex Plus supplies bounded observation, later checks, same-daemon peer
coordination and independent static reports around native Codex. Native Codex
owns its conversations, goals, execution policy and daemons. Worker workflows
remain explicitly invoked; a generic goal loop does not activate them.

The selected [owner-recovery pass](owner-recovery.md) follows the 2026-10-29
investigation. It implements explicit clean same-thread rollover, bootstrap
diagnosis and immutable inspectable history, while refusing live or uncertain
work. It is an unreleased preview.11 source candidate. The loop completed with
348 passing fixture tests, reproducible relocated packages and seven completed
owned native turns on 0.165.0. Two fresh messages were handled; old unknown turn
outcomes remained unknown. The actors/helpers are closed and the original owner
and real incident archives are preserved. No recovered incident
state is replayed; no existing owner, installed release or managed configuration
is changed by this source work. The recovery document records the qualified
artifact revision, evidence limits and deferred publication/deployment gates.

The **preview.10 publication and managed rollout is complete**. Release source
`078c630` supplies workers, monitoring and reporting under one tag; dotfiles main
`49cfc41` selects it on Snap (OSS/work), Starship and Carbon. All manifests verify,
scoped diffs converge and fresh MCP protocol discovery reports preview.10 with
15 monitoring/four report tools. All 39 recorded native/MCP/report processes,
265 protected paths and four HTTP report endpoints match the starting baseline.
No daemon/server restart, global MCP refresh or new native model trial occurred.
See the [full receipt](refinement-results.md#preview10-publication-and-managed-rollout).

The [documentation follow-up](site-polish-results.md#source-documentation-follow-up-2026-10-22)
completed 2026-10-22 after the recap fixes. It reconciles source/release availability
across the entry points and guides, and adds a fifth illustrative catch-up scene.
All 20 authored scene states pass actual candidate browser checks at desktop,
tablet and narrow mobile widths, alongside the eight guide routes and controls.
That local pass preserved runtime, worker and skill bytes. The authorized
publication packages the reviewed work as preview.10. Public delivery/browser
and managed rollout checks passed independently, with no historical trial replayed.

The [native alignment and natural follow-up pass](native-alignment-results.md)
completed 2026-10-22 after Bryan's project review and goal-loop request. Its source
candidate bounds reminder history, rediscovers outgoing receipts through the
existing tool, refines recap/quiet-follow-up guidance and adds native MCP version
metadata to the doctor. The 15-tool monitoring surface and native ownership stay
intact. Owned synthetic trials supply bounded 0.163.0 evidence; the candidate is
included in preview.10. Managed deployment remains outside that research pass.

The review follow-up fixes two recap gaps: acknowledged reminder callbacks stay
visible while their outcome is unknown or needs attention, and outgoing receipts
include the stored message kind and a bounded quoted purpose. Explicit reminder
cancellation closes known failure attention while preserving native work and
history. Five new regressions bring the fixture suite to 317; these fixes add no
new native-runtime qualification. See the [review results](native-alignment-results.md#review-corrections).

The completed refinement pass fixes status freshness, reminder expiry and bounded
watch history; adds full fixture CI and read-only installation diagnosis; and
unifies workers, monitoring and reporting under **v0.1.0-preview.9**. See
[the refinement results](refinement-results.md) for source/artifact/publication
acceptance and the subsequent scoped managed rollout. The documentation passes below are
completed context, not the current execution scope.

Start with [setup](getting-started.md), the [daily guide](daily-use.md), [worker workflows](workers.md), [architecture](architecture.md),
[environment contract](environments.md) and [public walkthrough](https://dev.byebyebryan.com/codex-plus/).
The [implementation plan](codex-plus-plan.md) records the proposed pass and completed
contracts; the [reconciliation results](reconciliation-results.md) record the earlier
environment/documentation pass. The [historical checkpoints](implementation-history.md) preserve
older migration, notification, rollout and acceptance evidence.

The [site polish pass](site-polish-results.md) adds the component-based setup
path, a fourth illustrative scene for Luna and publication/navigation refinements.
Its source and publication acceptance remains separate from runtime qualification.
That pass is complete: eight HTML guides and 16 illustrative scene states passed
actual public delivery/browser checks at desktop, tablet and mobile widths.
The publication workflow uses pinned Pages actions on Ubuntu 24.04; its build and
deploy completed without annotations. Only the pre-existing untracked bytecode
remains outside committed source.

The repository-discovery follow-up makes the HTML site prominent in the README,
pairs all eight guides with their Markdown sources, and aligns guide/repository
navigation and GitHub metadata. Its plan and acceptance belong to the same
[polish results](site-polish-results.md). The follow-up is complete: Pages
deployed successfully without annotations, all 11 public pages/assets matched
the candidate bytes, and actual GitHub/Pages desktop and mobile checks passed.
Runtime, agent and skill files and the pre-existing bytecode are unchanged.
Continue with ordinary use and its evidence.

## Source, releases and installed state

| Layer | Current fact |
| --- | --- |
| Published unified release | v0.1.0-preview.10, source `078c630`; one version, tag and release manifest, with optional worker/monitoring/report archives. Fetched bytes match reproducible candidates. |
| Managed upgrade | Published directly to dotfiles main as `49cfc41`; scoped live rollout completed 2026-10-22 on all three hosts. |
| Earlier artifacts retained | Monitoring preview.3 and reporting preview.8, source `c73c237`, remain available for captured processes and rollback. |
| Snap | Workers, monitoring and reporting preview.10 selected; all manifests verify in default OSS and dedicated work contexts. |
| Starship | Same three preview.10 selections verified; private configuration, processes and report serving preserved. |
| Carbon | Same three preview.10 selections verified through the trusted Starship SSH route; configuration, processes and serving preserved. |
| Native compatibility | Snap client and owner 0.163.0; release baseline remains 0.162.1. Bounded owned 0.163.0 trials do not establish blanket compatibility or long-run qualification. |
| Source | Reviewed natural-follow-up refinements packaged as preview.10, validated separately from the earlier installed preview.9. Multi-environment support retained; notification component retired. |
| Notification delivery | Native Codex to terminal. Formatting belongs to Kitty/chezmoi. Enrichment and the 349 inspector are parked/retired. |

Source documentation may advance beyond the selected immutable artifacts.
Existing MCP processes keep their captured code until normal reconnect. The
[runtime guide](runtime-distribution.md) and [report guide](html-report-usage.md)
explain optional component installation, serving and rollback under one release.
`scripts/codex-plus-doctor` checks selected manifests and native version evidence
without starting services. Preview.10 can also read reported MCP
versions for one positively loaded conversation. Selection or reported versions
do not establish loaded payload bytes; absent metadata remains unknown.

## Snap environment contract

| | OSS | Work |
| --- | --- | --- |
| Native command | `codex`, `codex agents` | `codex-work`, `codex-work agents` |
| Home | `~/.codex` | `~/.codex-work` |
| Explicit monitoring root | `~/.local/state/codex-plus-oss` | `~/.local/state/codex-plus-work` |
| Explicit report config | `~/.config/codex-plus/report.toml` | `~/.config/codex-plus/report-work.toml` |
| Report endpoint | `http://snap:8787/reports/` | `http://snap:8788/reports/` |
| Company MCPs | Omitted | Snap Bridge and gateway enabled |

The same account uses independent auth caches and native owners. This is
configuration separation under one Unix user, not a security boundary. Do not
recreate `codex-oss` or move the retained history. Private config and wrappers
belong to chezmoi; Codex Plus does not install a profile registry or migrate data.
Its canonical-home defaults apply only where explicit paths are absent. Pass the
actual overrides to `codex-plus-context` when diagnosing this managed setup.

## Acceptance and remaining work

The deployed environment pass verified both fresh MCP entry points, separate
stores, exact installed manifests, company-MCP admission and both HTTP endpoints.
The earlier native acceptance covers bounded watches, messages, inspections,
continuation and explicit stop on owned synthetic sessions. Those facts do not
establish provider recovery, long unattended reliability or personal UX.

The refinement release passes 303 fixture tests locally and in Python 3.11/3.14
CI, reproducible artifact verification, relocated CLI/MCP discovery, old-artifact
verification and public guide delivery/browser checks. Managed installation is
qualified in disposable Snap/Starship profile homes, including all three aligned
manifests, script-excluded apply and convergence. The subsequent user-authorized
rollout applied only selected Codex Plus targets on Snap and Starship, with
chezmoi scripts excluded. Payloads verified before selection; source edits,
private configuration, worker bytes, native/MCP processes and report serving were
preserved. All three report endpoints retained HTTP 200 and identical content.
See the [rollout receipt](refinement-results.md#managed-rollout-2026-10-22).
That managed rollout performed no service restart, global MCP refresh or new
native model trial.

The subsequent natural-follow-up source candidate, including review corrections,
passes 317 fixture tests.
Owned trials cover contextual peer choice, message handling, a known blocker, a
later configured MCP check, explicit stop, actual compaction and foreground
interruption that preserves observation. Helper loss is reported as uncertain;
expired recovery refuses. See the [results and limits](native-alignment-results.md)
before extending those claims.

Use the [soak checklist](soak-checklist.md) during ordinary work. No pending
historical trial, actor budget or wakeup should be replayed. Do not create a
watch, message, model workload or notification experiment merely to refresh docs.

## Continuation and validation

Commit directly to main, preserving concurrent edits. Prefix shell commands with
RTK. Run `scripts/check`, the meaningful test suite, `git diff --check`, and the
Pages builder outside the checkout. Presentation changes need actual browser
checks of scene state, environment selection, controls and desktop/mobile layout.
Public Pages deployment is separate from immutable report publication and from
managed runtime deployment. Retain source/artifact/installed/live evidence levels.
Do not restart native owners or report servers, repin workers, change credentials
or perform managed applies without a task that calls for those actions.
