# Implementation handoff

Updated 2026-10-21. Continue in `/home/bryan/code/codex-plus` on Snap.

## Current scope and entry points

Codex Plus supplies bounded observation, later checks, same-daemon peer
coordination and independent static reports around native Codex. Native Codex
owns its conversations, goals, execution policy and daemons. Worker workflows
remain explicitly invoked; a generic goal loop does not activate them.

The current refinement pass fixes status freshness, reminder expiry and bounded
watch history; adds full fixture CI and read-only installation diagnosis; and
unifies workers, monitoring and reporting under **v0.1.0-preview.9**. See
[the refinement results](refinement-results.md) for source/artifact/publication
acceptance and deferred live activation. The documentation passes below are
completed context, not the current execution scope.

Start with [setup](getting-started.md), the [daily guide](daily-use.md), [worker workflows](workers.md), [architecture](architecture.md),
[environment contract](environments.md) and [public walkthrough](https://dev.byebyebryan.com/codex-plus/).
The [implementation plan](codex-plus-plan.md) and [reconciliation results](reconciliation-results.md)
record this pass. The [historical checkpoints](implementation-history.md) preserve
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
| Published unified release | v0.1.0-preview.9, source `0ec803d`; one version, tag and release manifest, with optional worker/monitoring/report archives. Fetched bytes match reproducible candidates. |
| Managed upgrade | Prepared on dotfiles branch `codex-plus-preview-9`, commit `6aad69e`, draft PR #5. Source review/live apply remain deferred. |
| Earlier selected artifacts | Monitoring preview.3 and reporting preview.8, source `c73c237`; 15 monitoring and four reporting MCP tools. |
| Snap | Earlier artifacts remain selected through chezmoi; default OSS and dedicated work homes. |
| Starship | Same preview.3/preview.8 selections, freshly verified; earlier preview.2/preview.7 descriptions were stale. |
| Native compatibility | Snap client and owner 0.163.0; recorded qualification baseline 0.162.1. No new native model trial in this pass. |
| Source | Multi-environment support retained; notification component retired. |
| Notification delivery | Native Codex to terminal. Formatting belongs to Kitty/chezmoi. Enrichment and the 349 inspector are parked/retired. |

Source documentation may advance beyond the selected immutable artifacts.
Existing MCP processes keep their captured code until normal reconnect. The
[runtime guide](runtime-distribution.md) and [report guide](html-report-usage.md)
explain optional component installation, serving and rollback under one release.
`scripts/codex-plus-doctor` checks selected manifests and native version evidence
without starting services. Selection does not establish loaded process versions.

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
manifests, script-excluded apply and convergence. Canonical chezmoi has concurrent
desktop edits, so the upgrade remains isolated in its draft PR. No live apply,
service restart or new native model trial belongs to this completed pass.

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
