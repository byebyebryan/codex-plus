# Codex Plus

Codex Plus extends the native Codex CLI with background watches, messages
between open sessions, worker assignments, and HTML reports. Your chosen
model keeps the task context and uses the usual Codex tools and approvals.

Workers and goal loops came first, as a way to manage the token cost of long
tasks. The watches draw on background monitoring in Claude Code. Reporting
gives every session in an environment the same way to publish its findings.

**[Explore Codex Plus](https://dev.byebyebryan.com/codex-plus/)** ·
[Try the walkthrough](https://dev.byebyebryan.com/codex-plus/walkthrough/)

**Install or manage with your agent:** give it the
[agent guide](https://dev.byebyebryan.com/codex-plus/manage.md) and say
“Install Codex Plus” or “Upgrade my existing installation.” The
[HTML guide](https://dev.byebyebryan.com/codex-plus/manage/) has copyable requests
for inspection, configuration, rollback, cleanup and uninstall too.

## Start here

| What you want | Try this in Codex |
| --- | --- |
| [Watch for changes or check back later](docs/daily-use.md) | “Watch the export queue and tell me if a job needs input.” For a one-time follow-up, “Check the queue again in twenty minutes.” |
| [Publish an HTML report](docs/html-report-usage.md) | “Plot the benchmark results side by side and give me a report link I can share.” |
| [Contact another session](docs/session-communication.md) | “Ask the session preparing the release if it’s still editing the migration guide. I’d like to take the next pass.” |
| [Choose who does the work](docs/workers.md) | `$astra-task Review this patch for compatibility.` Use `$adaptive-task` to let your primary decide who takes each part. |

Workers, monitoring and reporting share **one Codex Plus version and release**.
Monitoring includes both watches and session communication. Choose the
components you need in the [setup guide](docs/getting-started.md).

## Current status

**v0.1.0-preview.30** includes seven worker workflows and four current roles.
The preview is ready for daily-use trials.

Preview.30 keeps a continuing goal in its original routing study when the primary
changes, recovers usage after failed turns, and checks native execution evidence
before attributing a handoff to Luna.

Preview.29 lets either adaptive workflow run independent assignments concurrently.
The primary chooses a model for each assignment, gives each change one owner,
and checks the combined result. [Working in parallel](docs/workers.md#working-in-parallel)

Preview.28 lets an Astra primary delegate to Sol when you opt in. Use either
[adaptive workflow](docs/workers.md#optional-escalation) normally for Astra/Luna,
or permit Sol for the request. Operators can enable a bounded
[private daily-use comparison](docs/routing-diagnostics.md#astra-primary-daily-study).

Preview.27 adds a short contribution summary to the adaptive workflows, with
observed tokens by model when native records are available.

Preview.26 makes [Astra XHigh available by default](docs/workers.md#optional-escalation)
inside the explicit adaptive workflows for Sol and current Terra primaries.
The Luna workflows keep Luna as their only delegated model.

Preview.25 records exact model versions without blocking study enrollment.
An explicit, backed-up policy update lets an existing study continue across
model upgrades with its original history and bounds.

Preview.24 adds family-based model preferences resolved at managed refresh,
exact-model overrides and version-aware diagnostic studies.

Preview.23 accepts nullable native Unix-second timeline fields while preserving
the precision of outer record timestamps for episode boundaries.

Preview.22 adds [private routing diagnostics](docs/routing-diagnostics.md): bounded
prospective A enrollment, assignment/outcome records and read-only native usage
collection. The adaptive routing policy stays unchanged. Worker model versions now follow
[family preferences resolved at managed refresh](docs/workers.md#model-versions),
with exact-version overrides and concrete native role files.
There is no Terra-enabled policy or A/B trial.

Preview.21 keeps coordinator status accurate after repeated handoffs, tracks slow
callbacks after early acknowledgement, clarifies invalid options and preserves
partial peer inspection when native ephemeral history/goals are unsupported.
It retains preview.20's MCP launch and read-only doctor fixes.
See the [qualification receipt](docs/native-qualification-results.md#soak-driven-reliability-preview21-source-candidate)
and [current handoff](docs/implementation-handoff.md) for delivery and adoption.

It retains [daemon restart recovery](docs/owner-recovery.md#daemon-restart-candidate-preview19), preserving historical uncertainty and continuing only eligible observations within their original bounds. Commands and MCP checks need their original replay-safe restart policy; legacy intent without a trustworthy lease anchor stays quarantined.
It retains explicit `$sol-task`, `$astra-task` and GPT-6.1 `$terra-task` for bounded
review, validation, investigation or implementation without changing your primary.
The old worker-name compatibility entries remain removed.
It retains optional primary-aware escalation in the two
adaptive worker workflows, the `astra-xhigh` role, read-only primary selection
and graceful reporting-only metadata fallback. Explicit Luna workflows use Luna
as their only delegated model.
It retains the native-control discovery fix, readable diagnostics, watch history
and preview rollback support. See [released and source features](docs/getting-started.md#released-and-source-features).
Updating a guide or checkout does not upgrade an installed runtime.

Use `--human` with the existing read-only doctor for a readable summary; JSON
remains the default. Pages builds check current-release guide claims. A native plugin
spike is a partial fit: discovery prefixes skill names and worker registration
remains unqualified. Existing archives and chezmoi remain the distribution path.
See the [review and packaging results](docs/reliability-packaging-results.md).

**Preview.11** adds explicit diagnosis and clean
recovery after a native owner incarnation changes, with immutable history and
refusal of unsettled work. Older installed releases require an explicit upgrade.
See the [recovery contract and acceptance](docs/owner-recovery.md).

The [October 31 qualification pass](docs/native-qualification-results.md) checks
preview.11 on Snap's native 0.166.0 pair and records the preview.12 correction for
cancelled source errors in current watch attention. A separate review follow-up
qualifies ordinary endpoint setup and cancellation of a running observer. The
declared compatibility baseline remains unchanged.

| Capability | What is available |
| --- | --- |
| Watches | Quiet command/script observation, authenticated endpoint access, passive peer reads and configured MCP inspection. |
| Later checks | One-shot reassessment and model-selected continuation, with status and cancellation. |
| Returning to work | “What am I still waiting on?” combines this conversation's stored watches, reminder outcomes and outgoing receipts, with stale or missing evidence explained. |
| Peer coordination | Contextual independent-session discovery, attributed information/requests and handling receipts within one daemon. |
| Browser reports | Immutable static HTML, project catalog, four report MCP tools, a report skill and independent HTTP hosting. |
| Workers | Four native roles and seven worker workflows; explicit named tasks, selective Luna and primary-specific delegation. |

Command polling can stay quiet without a model turn per read. Configured MCP
checks use scheduled native model turns under normal authentication/approval;
each check has model cost. Explicit stop cancels selected observation without
stopping the observed work. Esc interrupts the foreground turn and leaves
independent registrations within their bounds.

Bounded synthetic native qualification is separate from real-source reliability,
credential/provider recovery, long unattended operation and personal UX acceptance.
Cross-host native messaging,
a recurring calendar and native `/exit` confirmation interception are outside
this preview. Use the [soak checklist](docs/soak-checklist.md) to collect actual-use
evidence without manufacturing workloads.

<details>
<summary>Managed deployment details: Snap, Starship and Carbon</summary>

Use `codex` for Snap OSS and `codex-work` for work, including their `agents`
subcommands. The old `codex-oss` compatibility entry point is retired. These are
separate homes and daemons; native `--profile` alone does not separate state.
See [multiple environments](docs/environments.md) for portable defaults and the
existing explicit Snap paths.

Managed configuration selects **v0.1.0-preview.30** for workers, monitoring and
reporting. Snap (default and Work) and Starship verified their installed worker
files. Fresh MCP processes on both hosts returned 17 monitoring tools and four
reporting tools. Carbon was offline during rollout. Its last verified release
was preview.29.

The [delivery receipt](docs/reliability-packaging-results.md#preview30-worker-workflow-fixes)
separates publication, managed files and runtime evidence. New private studies record versions per episode; an explicit policy update
lets an existing study continue across model upgrades with its history and
original bounds intact. See the [observation procedure](docs/routing-diagnostics.md)
and [implementation handoff](docs/implementation-handoff.md).

</details>

## Guides and evidence

| HTML guide | For | Markdown source |
| --- | --- | --- |
| [Install & manage](https://dev.byebyebryan.com/codex-plus/manage/) | Give your agent one guide for the installation lifecycle. | [Source](docs/manage-agent.md) |
| [Get started](https://dev.byebyebryan.com/codex-plus/start/) | Choose components and follow the right setup path. | [Source](docs/getting-started.md) |
| [Watches and reminders](https://dev.byebyebryan.com/codex-plus/daily-use/) | Watch a run, ask for a timed check, see what is pending or stop a watch. | [Source](docs/daily-use.md) |
| [Session communication](https://dev.byebyebryan.com/codex-plus/sessions/) | Find another open session, send a message and check its receipt. | [Source](docs/session-communication.md) |
| [Worker workflows](https://dev.byebyebryan.com/codex-plus/workers/) | Choose a named worker or delegate adaptively. | [Source](docs/workers.md) |
| [Multiple environments](https://dev.byebyebryan.com/codex-plus/environments/) | Home selection, separate stores and same-daemon boundaries. | [Source](docs/environments.md) |
| [How it works](https://dev.byebyebryan.com/codex-plus/architecture/) | Components, permissions, costs, receipts and Claude-workflow coverage. | [Source](docs/architecture.md) |
| [Monitoring installation](https://dev.byebyebryan.com/codex-plus/installation/) | Immutable releases, MCP loading, managed setup and rollback. | [Source](docs/runtime-distribution.md) |
| [Browser reports](https://dev.byebyebryan.com/codex-plus/reports/) | Publication, catalog, storage and independent hosting. | [Source](docs/html-report-usage.md) |
| [Daily-use trial](https://dev.byebyebryan.com/codex-plus/soak-checklist/) | Record real outcomes and friction during ordinary work. | [Source](docs/soak-checklist.md) |

For development and qualification, see the
[implementation handoff](docs/implementation-handoff.md),
[managed activation results](docs/managed-activation-results.md),
[source-access results](docs/source-access-pass-results.md) and
[technical watch reference](docs/watch-candidate.md).
The [presentation notes](docs/presentation.md) and
[Pages deployment guide](docs/pages-deployment.md) explain authoring and publication.

This repository was previously Codex Worker Kit. Compatible agent/skill paths
remain in place. Current GitHub documentation tracks main; documentation changes
do not repin qualified installed artifacts or update managed source archives.
The [implementation plan](docs/codex-plus-plan.md) labels completed contracts and
current work; [Claude context](docs/claude-monitoring-context.md) retains the
historical usage study. Active sessions supplied passive evidence; experimental
messaging/delivery used owned synthetic sessions. Agent Observer is not a runtime
dependency.

## Worker workflows

Preview.15 adds one optional escalation target to the two adaptive workflows
and packages `astra-xhigh`. The [qualification and limits](docs/worker-escalation-results.md)
separate native execution evidence, conditional Terra routes and ordinary-use acceptance.

Reusable workers and execution workflows keep your native user-selected primary
with selective Luna Max delegation. The primary owns decisions, integration, review, and
acceptance. Adaptive workflows keep work in the primary when the benefit of a
handoff is uncertain. Workflows preserve the selected primary model.

## Models and responsibilities

| Role | Model | Reasoning | Responsibility |
| --- | --- | --- | --- |
| Current primary | Selected by you in Codex | Selected by you | Decisions, difficult portions, integration, and acceptance |
| Cheaper worker `luna-max` | `gpt-6-luna` | `max` | Clear, bounded investigation and implementation with practical verification |
| Optional worker `sol-xhigh` | `gpt-6.1-sol` | `xhigh` | Configured escalation from Terra or explicitly assigned independent execution |
| Optional worker `astra-xhigh` | `gpt-6-astra` | `xhigh` | Escalation from Sol/Terra or explicitly assigned work |

Delegate to Luna when the objective, responsibility boundary, and acceptance
check are clear and expected savings justify packaging, review, and possible
corrections. Confidence concerns the assignment and verification; the primary
need not solve every implementation detail first. A substantial specified
migration or focused investigation can qualify. Evolving diagnosis, shared
decisions, and small remainders often fit primary execution better.

Explicitly invoke an adaptive workflow to make Astra XHigh available when a
known Sol or current Terra primary has a good reason to
escalate. The primary still decides whether to call it. A Terra primary can use
Sol XHigh instead when explicitly requested. Choose a Luna workflow when Luna
should be the only delegated model. See the [worker guide](docs/workers.md#optional-escalation).

Escalation requires evidence: an unresolved decision, contradictory observations,
a verification gap, or repeated failure without new evidence. Cross-module work,
migrations, concurrency, security, file count, or unfamiliarity alone do not
exclude Luna. A worker may reason about options; the primary retains authority
over decisions outside the execution contract.

## Workflows

| Workflow | Scope | Delegation |
| --- | --- | --- |
| `$luna-task` | One bounded task; no goal management | Luna only; primary handles difficult portions |
| `$luna-goal-loop` | A substantial goal across cohesive assignments | Luna only; primary handles difficult portions |
| `$adaptive-task` | One bounded task; no goal management | Primary, selective Luna, or a justified worker for the selected primary |
| `$adaptive-goal-loop` | A substantial goal, routed per assignment | Primary, selective Luna, or a justified worker for the selected primary |
| `$sol-task` | One bounded task; no goal management | Exact Sol XHigh worker; primary accepts the result |
| `$astra-task` | One bounded task; no goal management | Exact Astra XHigh worker; primary accepts the result |
| `$terra-task` | One bounded task; no goal management | Configured current Terra XHigh worker; primary accepts the result |

The named tasks preserve your primary and need no automatic escalation setting.
Review and investigation return evidence without source fixes. For example:

```text
$sol-task Review the current changes and run appropriate validation.
Return findings and evidence; leave source fixes to the primary.
```

These three skills first shipped in preview.18. For installation or upgrade,
follow the [release selection guide](docs/manage-agent.md#resolve-and-verify-one-published-release).
See the [named-task contract and examples](docs/workers.md#choose-sol-or-astra-explicitly-source-candidate).
The current Terra task uses a distinct `terra-6-1-xhigh` role; the legacy task of
the same name remains GPT-5.6-only. Install only the deliberately selected variant.

Preview.17 removes `$worker-task` and `$worker-goal-loop`. Update old prompts to
the corresponding adaptive name; no alias or forwarding layer remains. The
four canonical workflow instructions, Luna names and native model roles are
unchanged. Managed upgrades remove the retired installed directories explicitly.

The Luna workflows preserve the explicit worker choice without requiring a
workflow switch when the primary needs to help. The adaptive workflows choose
whether delegation helps and which worker to use. An unavailable optional worker
returns work to the primary; an explicitly requested unavailable Luna worker is
reported without silently substituting another model.

Inspect actual native tool declarations before reporting worker unavailability.
Collaboration controls are called directly in their declared namespace; an empty
Code Mode `ALL_TOOLS` search does not establish their absence. Select Luna with
`agent_type="luna-max"` and `fork_turns="none"`. The
[availability guide](docs/workers.md#native-delegation-and-availability) separates
missing controls, spawn failures and worker/model execution errors.

Activate adaptive workflows with `$adaptive-task`, `$adaptive-goal-loop`, or an
explicit request to use the named skill. A generic "goal loop" uses the ordinary
workflow. Discussing or editing a skill does not activate it. The adaptive skills
disable implicit invocation in their metadata. Skills are enabled by default
when installed; an existing local disable preference must be changed separately.

Give each worker a cohesive assignment and each change a single owner. Keep
context compact, reuse workers for related corrections and transfer ownership
before taking over. If a failure repeats without new evidence, the primary
diagnoses it.

## Installation

Use the [agent lifecycle guide](docs/manage-agent.md) as the primary setup and
maintenance procedure. Choose components in the [setup overview](docs/getting-started.md). The
[worker installation steps](docs/workers.md#installation) install four agents and
seven worker workflows; the HTML report skill is a separate optional addition.
The [runtime guide](docs/runtime-distribution.md) and
[report guide](docs/html-report-usage.md) cover their independent artifacts.
With a dotfile manager, update its source and published pins through that owner.

Bryan's chezmoi distribution uses `.chezmoiexternals/codex-plus.toml.tmpl` with pinned
Codex Plus URLs and checksums. It retains `~/.local/share/codex-worker-kit` as the
managed archive location for compatibility; native skill and agent paths remain
ordinary managed files. This upgrade does not activate a watcher or change
worker routing.

Select the primary separately in your client or configuration:

```toml
model = "gpt-6.1-sol"
model_reasoning_effort = "xhigh"
```

Each installed custom agent pins a concrete model and reasoning effort.
The table above lists packaged seed models; setup/refresh may select a newer
compatible version from the same family for that account. The client and
account must support these models, custom agents, and skills. A task label alone
does not select a model; workflows use the named custom agent with a compact
execution contract and minimal inherited context. See the official
[custom agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

### Existing Terra installations

GPT-5.6 Terra compatibility files under `legacy/` retain the deprecated
`terra-xhigh`, `$terra-task` and `$terra-goal-loop` identities. They do not alias
the current GPT-6.1 role `terra-6-1-xhigh`. Preview.17 contains only the legacy
Terra variant; preview.18 includes the current variant by default.

Both task variants use the `$terra-task` invocation. Select one deliberately;
do not install both into discoverable skill roots or recursively merge their
directories. Identify an existing variant from its retained manifest and exact
role pin before any migration. Preserve local edits and restrictions, and use
the owning configuration manager for reviewed replacement or removal. Never
blanket-delete `terra-task`: it may be the chosen current workflow. Check both
supported personal skill roots if earlier installations used different ones.
Publish a new release before updating managed URLs/checksums or installed files.

## Validation and tuning

Run `scripts/check` after changing the kit. It validates the default and legacy
inventory, agent model/effort selections, skill metadata, and explicit-only
adaptive invocation policies. It does not prove
routing quality or runtime model availability.

Run `python3 -B tests/test_check.py` for metadata regression checks. The validator
accepts the kit's two-level `interface` and `policy` mappings, quoted strings,
and lowercase booleans. Unsupported YAML forms are rejected; extend the validator
deliberately before adding other metadata formats or fields.

Review representative behavior as well:

- A specified migration with clear boundaries and useful checks can suit Luna.
- An unclear failure stays in the primary until a useful investigation can be
  confidently assigned and verified.
- A deeply coupled design decision stays in the primary, which may delegate
  resulting implementation when the savings justify the handoff.
- A useful independent review or demanding slice can use the configured target;
  explicit requests for separate native workers retain their own authority.
- An ordinary failed test goes back for correction; repeated failure without new
  evidence returns to the primary.
- An explicit Luna workflow delegates only to Luna, even when escalation is allowed.

Compare total primary-plus-worker usage, corrections, elapsed time, and accepted
results on representative tasks. Use runtime cost data when available; do not
infer savings from the number of Luna assignments or from token rates alone.

## Historical design references

[HTML report design](docs/html-report-design.md) and the
[v1 implementation plan](docs/html-report-plan.md) retain the original defaults,
interfaces, publication recovery and staged acceptance. The implemented and
installed behavior is described in the [usage guide](docs/html-report-usage.md)
and [report results](docs/html-report-results.md).

[Worker routing design](docs/worker-routing-design.md) records selective Luna
delegation, the separate purpose of Sol workers, and the rollout plan.
[Worker routing research](docs/worker-routing-study.md) reviews the evidence,
its limits, and a lightweight policy to assess in practice.
The active workflow instructions above describe the current implementation.
