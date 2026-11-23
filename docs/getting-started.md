# Get started with Codex Plus

Ask your coding agent to install the components you need. All three ship in
the same release and work from an ordinary Codex session.

## Choose what to install

- **[Workers](#set-up-workers)** Choose a model for an assignment or let your primary decide what to delegate.
- **[Monitoring](#set-up-monitoring-and-coordination)** Watch a job, schedule a one-time check, or contact another open session.
- **[Reporting](#set-up-reporting)** Publish charts and findings to a host you can reach from your browser.

## Install or manage with your agent

Give your agent this request. Add the component names if you only want part of the release.

> Read https://dev.byebyebryan.com/codex-plus/manage.md and install Codex Plus on this machine.

For an existing installation, ask it to “upgrade my existing Codex Plus
installation.” The agent identifies the configuration owner, verifies the
selected release archives and preserves your settings, reports and active work.
It can start from an ordinary coding session. The same guide covers inspection,
configuration, rollback, cleanup and uninstall.
[Read the agent guide](manage-agent.md) · [Plain Markdown for your agent](https://dev.byebyebryan.com/codex-plus/manage.md).

## If your setup is already managed

Use the configuration manager that owns your agent, skill and MCP files. For
Snap, Starship and Carbon, that is chezmoi. Explicit opt-outs still apply. Open a
fresh ordinary session in the environment where you want to use the component.
An existing MCP connection adopts the selected code on its normal reconnect.

On Snap, `codex` selects personal/OSS work and `codex-work` selects work. Each
has its own conversations, tools, follow-up state and report store.
[Choose an environment](environments.md).

## Set up workers

Install four native roles (`luna-max`, `sol-xhigh`, `astra-xhigh` and
`terra-6-1-xhigh`) and seven workflow skills. Your client and account need
access to custom agents, skills and the selected models. You choose the
primary, which reviews the work and checks the result.
[Worker installation](workers.md#installation).

```text
$adaptive-task Add Markdown and plain-text exports for the agreed reading-list
format. Verify both through the CLI.
```

The adaptive task can run independent assignments in parallel. Choose a named
task to specify the worker, or an explicit goal loop for work through final
acceptance. [Compare the workflows](workers.md#choose-a-workflow).

## Set up monitoring and coordination

The released monitoring archive requires Linux, Python 3.11 or newer and RTK.
Integrate the generated MCP table through your configuration owner. The
release qualification baseline is Codex 0.162.1. Later trials cover specific paths on Codex 0.163.0 and
restart, callback and ephemeral-peer behavior on 0.167.2.
[Installation and qualification](runtime-distribution.md).

> Watch this run and tell me if it stalls or fails.

Give Codex a source your session can already access and describe the change
you care about. The 17 monitoring tools also support reminders and communication
between independent loaded sessions in the same daemon.
[Watch a run](daily-use.md#choose-a-follow-up) · [Contact another session](session-communication.md).

## Set up reporting

The report publisher runs independently of a native agent owner. Configure
its CLI or four MCP tools and a URL reachable from your viewing desktop.
Use tmux for optional automatic hosting or serve the report store’s public
subtree through your own HTTP server. [Report setup and hosting](html-report-usage.md#configuration-and-hosting).

> Make a browser report of the results, including the risks.

Publication saves a snapshot. A delivery check verifies the served HTML
bytes. Open the link on your viewing desktop to check the presentation.
[From export to browser](html-report-usage.md#from-export-to-browser).

## Try one useful request

Pick a task you can check yourself. For a watch, ask “What are you watching?”
to see its registration or “Stop watching that run” to cancel it. Esc interrupts
the foreground turn while independent observation continues within its bounds.
For a worker assignment, ask the primary how it verified the result.
[Everyday requests](daily-use.md) · [Interactive walkthrough](https://dev.byebyebryan.com/codex-plus/walkthrough/#scenes).

Use the [daily-use checklist](soak-checklist.md) to record outcomes and friction
during ordinary work. The [architecture guide](architecture.md) explains how
the components fit together.

## Released and source features

**v0.1.0-preview.30** supplies the released workflows shown in these guides. Release archives for workers, monitoring and reporting share a version and source commit. An existing MCP process adopts the selected archive on reconnect. [Release verification](runtime-distribution.md#one-codex-plus-release).

| Available in | What to expect |
| --- | --- |
| Changed in preview.30 | Luna workflows verify execution evidence. [Routing diagnostics](routing-diagnostics.md) preserve study assignments across primary changes and recover usage after failed turns. |
| Added in preview.29 | Both adaptive workflows can [run independent assignments in parallel](workers.md#working-in-parallel), including implementation. |
| Added in preview.28 | Astra primaries can opt into [bounded Sol delegation](workers.md#optional-escalation) and a [private daily study](routing-diagnostics.md#astra-primary-daily-study). |
| Added in preview.27 | Adaptive tasks and goal loops summarize who did what and can show [observed tokens by model](routing-diagnostics.md#current-run-usage). |
| Changed in preview.26 | Explicit adaptive workflows make Astra XHigh available by default for supported Sol or current Terra primaries. Luna workflows stay Luna-only. |

<details>
<summary>Earlier previews, from preview.25 back to preview.9</summary>

| Available in | What to expect |
| --- | --- |
| Fixed in preview.25 | Model upgrades no longer block new-study enrollment. An explicit backed-up update preserves an existing study and its bounds while exact versions remain available for analysis. |
| Added in preview.24 | Resolve latest available stable worker versions at managed refresh, preserve exact preferences, and recognize supported primary families. Preview.25 superseded its frozen-study policy. |
| Fixed in preview.23 | Native nullable Unix-second timing fields normalize to UTC. Outer record precision remains available for enrollment and worker boundaries. |
| Added in preview.22 | Opt-in [private Sol/Luna routing diagnostics](routing-diagnostics.md), with prospective bounded enrollment and read-only native accounting. No Terra route or comparison trial is enabled. |
| Fixed in preview.21 | Truthful coordinator status after handoff, callback completion tracking after early acknowledgement, clearer argument errors and partial ephemeral-peer inspection. Read the [qualification](native-qualification-results.md#soak-driven-reliability-preview21-source-candidate) for acceptance and limits. |
| Fixed in preview.20 | Normal MCP-started coordinator handoff now keeps supervisor logs outside the frozen journal. The doctor distinguishes endpoint, loaded-caller and version/metadata gaps. A bounded native restart completes a model callback. See [qualification](native-qualification-results.md#health-and-restart-follow-up-preview20-source-pass). |
| Added in preview.19 | Verified daemon restart handoff, bounded stale inspection, quarantine and opt-in replay-safe source continuation under original limits. Uncertain messages/commands stay quarantined. See [recovery and adoption limits](owner-recovery.md#daemon-restart-candidate-preview19). |
| Added in preview.18 | Explicit `$sol-task`, `$astra-task` and GPT-6.1 `$terra-task` for one named review, investigation or implementation, preserving the primary. Older installations need an upgrade. See the [contract](workers.md#choose-sol-or-astra-explicitly-source-candidate) and [Terra variant selection](workers.md#choose-current-terra-explicitly-source-candidate). |
| Changed in preview.17 | Removed the worker-name compatibility entries. Use the four canonical Luna/adaptive workflows and update old prompts. |
| Added in preview.16 | Introduced canonical `$adaptive-task` and `$adaptive-goal-loop` names with worker-name compatibility entries, which preview.17 removed. Routing and Luna workflows stayed unchanged. |
| Added in preview.15 | Optional primary-aware escalation and the Astra XHigh role, defaulting off. Added read-only loaded-primary selection with graceful reporting-only fallback. Natural-language permission and native role pins remain separate. |
| Added in preview.14 | Correct native collaboration discovery and direct role selection in all four worker workflows. |
| Added in preview.13 | The existing read-only doctor accepts `--human` for readable diagnostics. JSON remains the default. Pages builds check published and managed guide declarations independently. Preview.12 archives remain verifiable and selectable for rollback. |
| Added in preview.12 | Explicit watch cancellation closes attention for a terminal source error while preserving history and unresolved delivery. See the [native qualification results](native-qualification-results.md). |
| Added in preview.11 | Explicit owner diagnosis and clean same-thread rollover, with immutable archived history. Active or uncertain intent refuses recovery. See the [contract and acceptance](owner-recovery.md). |
| Added in preview.10 | Bounded reminder history, outgoing-message rediscovery with kind and quoted purpose, pending/failed follow-up visibility, and reported MCP-version diagnosis for one loaded conversation. |
| Preview.9 and later | Worker workflows, watches, one-shot later checks, same-daemon peer coordination, reports and selected-file diagnosis. |

The “What am I still waiting on?” example uses preview.10's inspection
improvements. Existing preview.9 artifacts retain their original contents.
Select a newer release through your configuration owner. [Inspection behavior](daily-use.md#inspect-follow-up-health) · [Review evidence and limits](native-alignment-results.md#review-corrections).

</details>
