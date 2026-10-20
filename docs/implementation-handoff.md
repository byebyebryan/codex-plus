# Implementation handoff

Updated 2026-10-20. Continue in `/home/bryan/code/codex-plus` on Snap.

## Current scope and entry points

Codex Plus supplies bounded observation, later checks, same-daemon peer
coordination and independent static reports around native Codex. Native Codex
owns its conversations, goals, execution policy and daemons. Worker workflows
remain explicitly invoked; a generic goal loop does not activate them.

Start with the [daily guide](daily-use.md), [worker workflows](workers.md), [architecture](architecture.md),
[environment contract](environments.md) and [public walkthrough](https://dev.byebyebryan.com/codex-plus/).
The [implementation plan](codex-plus-plan.md) and [reconciliation results](reconciliation-results.md)
record this pass. The [historical checkpoints](implementation-history.md) preserve
older migration, notification, rollout and acceptance evidence.

## Source, releases and installed state

| Layer | Current fact |
| --- | --- |
| Monitoring release | preview.3, source `c73c237`, 15 MCP tools. |
| Reporting release | preview.8, source `c73c237`, four MCP tools. |
| Snap | Both releases selected through chezmoi; default OSS and dedicated work homes. |
| Starship | Runtime preview.2 / reports preview.7 remain installed; upgrade is a separate apply. |
| Source | Multi-environment support retained; notification component retired. |
| Notification delivery | Native Codex to terminal. Formatting belongs to Kitty/chezmoi. Enrichment and the 349 inspector are parked/retired. |

Source documentation may advance beyond the selected immutable artifacts.
Existing MCP processes keep their captured code until normal reconnect. The
[runtime guide](runtime-distribution.md) and [report guide](html-report-usage.md)
explain independent installation, serving and rollback.

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
