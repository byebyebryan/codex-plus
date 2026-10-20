# Codex Plus

Watches, later checks, peer communication and browser reports around the native
Codex CLI/TUI. Keep your continuing conversation and its existing daemon; ask
for useful follow-up in ordinary language.

## Start here

Open a fresh ordinary Codex session on Snap or Starship and say, for example:

- “Watch the session doing the packaging work and tell me when it is ready.”
- “Tell that session the handoff should include the risks.”
- “Watch this run and tell me if it stalls or fails.”
- “Check this endpoint again later.”
- “Stop watching it.”
- “Make a browser report of what we learned.”

The model selects the source, filtering, cadence and continuation. It discovers
independent peers from context and clarifies ambiguity; no UUID, exact title,
JSON prompt or polling recipe is required from you.

Read the [daily-use guide](docs/daily-use.md), open the
[browser walkthrough](docs/presentation.md), or see
[how the package works](docs/architecture.md).

The [public HTML guides](https://dev.byebyebryan.com/codex-plus/) publish the
walkthrough and seven readable guides through GitHub Pages. See the
[Pages deployment guide](docs/pages-deployment.md) for source/build details.

## Current status

Use `codex` for Snap OSS and `codex-work` for work, including their `agents`
subcommands. The old `codex-oss` compatibility entry point is retired. These are
separate homes and daemons; native `--profile` alone does not separate state.
See [multiple environments](docs/environments.md) for portable defaults and the
existing explicit Snap paths.

Desktop notification delivery and terminal customization are outside Codex Plus.
Native Codex alerts remain selected. Notification enrichment and lifecycle
inspection are parked; [native terminal formatting](https://github.com/byebyebryan/dotfiles/blob/main/docs/kitty-notifications.md)
is managed with Kitty/chezmoi.

Snap now selects monitoring runtime **v0.1.0-preview.3** and reporting
**v0.1.0-preview.8**, including native multi-environment support, through chezmoi.
Both work and OSS entry points pass fresh MCP checks without replacing their
native daemons. Starship retains its prior installed runtime preview.2/report
preview.7 until a separate apply. See the [environment contract and deployment](docs/environments.md).

| Capability | What is available |
| --- | --- |
| Watches | Quiet command/script observation, authenticated endpoint access, passive peer reads and configured MCP inspection. |
| Later checks | One-shot reassessment and model-selected continuation, with status and cancellation. |
| Peer coordination | Contextual independent-session discovery, attributed information/requests and handling receipts within one daemon. |
| Browser reports | Immutable static HTML, project catalog, four report MCP tools, a report skill and independent HTTP hosting. |
| Workers | Existing two agents and four worker workflows, with unchanged identities and explicit invocation. |

Command polling can stay quiet without a model turn per read. Configured MCP
checks use scheduled native model turns under normal authentication/approval;
each check has model cost. Explicit stop cancels selected observation without
stopping the observed work. Esc interrupts the foreground turn and leaves
independent registrations within their bounds.

The preview is ready for daily-use trials. Bounded synthetic native qualification
is separate from real-source reliability, credential/provider recovery, long
unattended operation and personal UX acceptance. Cross-host native messaging,
a recurring calendar and native `/exit` confirmation interception are outside
this preview. Use the [soak checklist](docs/soak-checklist.md) to collect actual-use
evidence without manufacturing workloads.

## Guides and evidence

| Read this | For |
| --- | --- |
| [Daily use](docs/daily-use.md) | Natural requests, expected follow-up, stopping and reports. |
| [Luna and worker workflows](docs/workers.md) | Luna tasks and goal loops, adaptive delegation, agent roles and installation. |
| [Multiple environments](docs/environments.md) | Home selection, explicit overrides, separate stores and same-daemon boundaries. |
| [Architecture and Claude-workflow coverage](docs/architecture.md) | Components, permissions, costs, discovery, receipts and limits. |
| [Browser walkthrough](docs/presentation.md) | Three illustrative scenes and the published presentation. |
| [Runtime distribution](docs/runtime-distribution.md) | Immutable monitoring artifact, loading, managed installation and rollback. |
| [HTML report usage](docs/html-report-usage.md) | Publication, catalog, storage and separate hosting. |
| [Managed activation results](docs/managed-activation-results.md) | Independent installed/native acceptance on Snap and Starship. |
| [Source-access results](docs/source-access-pass-results.md) | Endpoint/MCP permissions, executed continuation and stop evidence. |
| [Technical watch reference](docs/watch-candidate.md) | Low-level CLI diagnostics and historical synthetic recipes. |
| [Implementation handoff](docs/implementation-handoff.md) | Current continuation state and earlier implementation history. |

This repository was previously Codex Worker Kit. Compatible agent/skill paths
remain in place. Current GitHub documentation tracks main; documentation changes
do not repin qualified installed artifacts or update managed source archives.
The [implementation plan](docs/codex-plus-plan.md) labels completed contracts and
current work; [Claude context](docs/claude-monitoring-context.md) retains the
historical usage study. Active sessions supplied passive evidence; experimental
messaging/delivery used owned synthetic sessions. Agent Observer is not a runtime
dependency.

## Existing worker bundle

Reusable workers and execution workflows for a Sol XHigh primary with selective
Luna Max delegation. The primary owns decisions, integration, review, and
acceptance. Adaptive workflows keep work in the primary when the benefit of a
handoff is uncertain. Workflows preserve the selected primary model.

## Models and responsibilities

| Role | Model | Reasoning | Responsibility |
| --- | --- | --- | --- |
| Recommended primary | `gpt-6.1-sol` | `xhigh` | Decisions, difficult portions, integration, and acceptance |
| Cheaper worker `luna-max` | `gpt-6-luna` | `max` | Clear, bounded investigation and implementation with practical verification |
| Optional worker `sol-xhigh` | `gpt-6.1-sol` | `xhigh` | Separable parallel work, context-isolated investigation, or independent review |

Delegate to Luna when the objective, responsibility boundary, and acceptance
check are clear and expected savings justify packaging, review, and possible
corrections. Confidence concerns the assignment and verification; the primary
need not solve every implementation detail first. A substantial specified
migration or focused investigation can qualify. Evolving diagnosis, shared
decisions, and small remainders often fit primary execution better.

A Sol worker needs a concrete benefit from another execution context. Difficulty
beyond Luna normally stays with the primary; the same-model worker is not a
stronger tier. Separate files may still depend on shared decisions. An independent
review adds a perspective, and its findings still need evidence. Terra and Astra
are outside automatic routing.

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
| `$worker-task` | One bounded task; no goal management | Primary or selective Luna; Sol for independent execution |
| `$worker-goal-loop` | A substantial goal, routed per assignment | Primary or selective Luna; Sol for independent execution |

The Luna workflows preserve the explicit worker choice without requiring a
workflow switch when the primary needs to help. The adaptive workflows choose
whether delegation helps and which worker to use. An unavailable optional worker
returns work to the primary; an explicitly requested unavailable Luna worker is
reported without silently substituting another model.

Activate adaptive workflows with `$worker-task`, `$worker-goal-loop`, or an
explicit request to use the named skill. A generic "goal loop" uses the ordinary
workflow. Discussing or editing a skill does not activate it. The adaptive skills
disable implicit invocation in their metadata. Skills are enabled by default
when installed; an existing local disable preference must be changed separately.

Use one cohesive assignment and one writer by default. Reuse workers for related
corrections, keep context compact, and transfer write ownership before taking
over. Ordinary defects usually call for corrections. Failed attempts without
new evidence call for primary diagnosis rather than repeated worker cycling.

## Installation

For the worker bundle, clone the repository and install its two custom agents
and skills (four worker workflows plus the additional HTML report skill):

```sh
git clone https://github.com/byebyebryan/codex-plus.git
mkdir -p ~/.codex/agents ~/.agents/skills
cp codex-plus/agents/*.toml ~/.codex/agents/
cp -R codex-plus/skills/. ~/.agents/skills/
```

This copy example installs agents/skills, not the monitoring or reporting
runtimes. Follow the [runtime guide](docs/runtime-distribution.md) and
[report guide](docs/html-report-usage.md) for those separate components.

The example uses `~/.codex/agents` for custom agents and `~/.agents/skills`
for user skills. If your client supports another personal skills directory,
install the same skill directories there. With a dotfile manager, update its
source and published pins instead of copying over managed targets.

Bryan's chezmoi distribution uses `.chezmoiexternals/codex-plus.toml` with pinned
Codex Plus URLs and checksums. It retains `~/.local/share/codex-worker-kit` as the
managed archive location for compatibility; the installed agent and skill paths
also stay the same. The repository rename does not activate a watcher or change
worker routing.

Select the primary separately in your client or configuration:

```toml
model = "gpt-6.1-sol"
model_reasoning_effort = "xhigh"
```

Each custom agent pins both its model and reasoning effort. The client and
account must support these models, custom agents, and skills. A task label alone
does not select a model; workflows use the named custom agent with a compact
execution contract and minimal inherited context. See the official
[custom agent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents).

### Existing Terra installations

GPT-5.6 Terra compatibility files live under `legacy/` and are deprecated. They
retain the `terra-xhigh`, `$terra-task`, and `$terra-goal-loop` identities and do
not alias Sol. Install them separately only to preserve an explicit Terra workflow:

```sh
cp codex-plus/legacy/agents/terra-xhigh.toml ~/.codex/agents/
cp -R codex-plus/legacy/skills/. ~/.agents/skills/
```

Copying the current default bundle does not remove previously installed Terra
files. When migrating, retire the old agent and both Terra skill directories
through the configuration manager or installation method that owns them. Check
both supported personal skill roots if an earlier installation used a different
one. For archive consumers, publish the kit before changing external URLs and
checksums; do not point a deployment at an unpublished checkout.

## Validation and tuning

Run `rtk proxy scripts/check` after changing the kit. It validates the default and legacy
inventory, agent model/effort selections, skill metadata, and explicit-only
adaptive invocation policies. It does not prove
routing quality or runtime model availability.

Run `rtk proxy python3 -B tests/test_check.py` for metadata regression checks. The validator
accepts the kit's two-level `interface` and `policy` mappings, quoted strings,
and lowercase booleans. Unsupported YAML forms are rejected; extend the validator
deliberately before adding other metadata formats or fields.

Review representative behavior as well:

- A specified migration with clear boundaries and useful checks can suit Luna.
- An unclear failure stays in the primary until a useful investigation can be
  confidently assigned and verified.
- A deeply coupled design decision stays in the primary, which may delegate
  resulting implementation when the savings justify the handoff.
- Separable parallel work or a noisy investigation can use Sol when another
  execution context helps.
- An ordinary failed test goes back for correction; repeated failure without new
  evidence returns to the primary.
- An explicit Luna workflow never silently creates a Sol or Terra worker.

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
