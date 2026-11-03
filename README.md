# Codex Plus

Workers, watches, later checks, peer communication and browser reports around
the native Codex CLI/TUI. Keep your continuing conversation and its existing
daemon; choose explicit worker workflows or ask for useful follow-up in ordinary
language.

> **[Explore the interactive walkthrough and HTML guides →](https://dev.byebyebryan.com/codex-plus/)**
>
> [Get started](https://dev.byebyebryan.com/codex-plus/start/) ·
> [Luna & workers](https://dev.byebyebryan.com/codex-plus/workers/) ·
> [Daily use](https://dev.byebyebryan.com/codex-plus/daily-use/)

**Install or manage with your agent:** give it the
[agent guide](https://dev.byebyebryan.com/codex-plus/manage.md) and say
“Install Codex Plus” or “Upgrade my existing installation.” The
[HTML guide](https://dev.byebyebryan.com/codex-plus/manage/) has copyable requests
for inspection, configuration, rollback, cleanup and uninstall too.

## Start here

Use the [agent guide](docs/manage-agent.md) for installation and maintenance;
the [setup overview](docs/getting-started.md) explains workers, monitoring and
reporting for reference. With the relevant components installed, open an
ordinary Codex session and say, for example:

- “$luna-task Investigate the importer failure and return a reproduction.”
- “$luna-goal-loop Complete the approved importer migration and verify it.”
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

Workers, monitoring and reporting share **one Codex Plus version and release**.
Choose the component archives you need in the setup guide; an existing managed setup can use these requests
directly. The public site includes the walkthrough and nine HTML guides. Their
Markdown sources and technical evidence are linked below.

## Current status

The preview is ready for daily-use trials. Choose workers, follow useful changes
or publish a browser handoff around your existing Codex conversation.

**v0.1.0-preview.15** includes optional primary-aware escalation in the two
adaptive worker workflows, the `astra-xhigh` role, read-only primary selection
and graceful reporting-only metadata fallback. Escalation defaults off and uses
your request or existing instructions; explicit Luna workflows remain Luna-only.
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
| Workers | Three native roles and four worker workflows; selective Luna and one optional escalation target, with explicit invocation. |

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

**Preview.15 rollout:** Snap OSS/work and Starship now select all three components
at preview.15. Carbon went offline after preflight and remains last verified at
preview.14; its apply is pending. The
[delivery receipt](docs/reliability-packaging-results.md#preview15-worker-policy-and-guide-publication)
records exact scope, preservation and loaded-process limits.

The last completed common fleet receipt (2026-11-01) recorded:

> Snap, Starship and Carbon select **v0.1.0-preview.14** for workers, monitoring and
reporting from source `dc19a82` through chezmoi. The scoped rollout on 2026-11-01
verified exact payloads, doctor output and fresh MCP discovery in all four contexts.
Native owners, private configuration and old releases are preserved. Starship
MCP connection exits are recorded as an audit limitation in the
[rollout receipt](docs/reliability-packaging-results.md#preview14-worker-discovery-publication-and-rollout).
Existing conversations can retain older loaded versions until normal reconnect.
The [implementation handoff](docs/implementation-handoff.md) records source,
release and installed state.

Desktop notification delivery and terminal customization are outside Codex Plus.
Native Codex alerts remain selected. Notification enrichment and lifecycle
inspection are parked; [native terminal formatting](https://github.com/byebyebryan/dotfiles/blob/main/docs/kitty-notifications.md)
is managed with Kitty/chezmoi.

</details>

## Guides and evidence

| HTML guide | For | Markdown source |
| --- | --- | --- |
| [Install & manage](https://dev.byebyebryan.com/codex-plus/manage/) | Give your agent one guide for the installation lifecycle. | [Source](docs/manage-agent.md) |
| [Get started](https://dev.byebyebryan.com/codex-plus/start/) | Choose components and follow the right setup path. | [Source](docs/getting-started.md) |
| [Daily use](https://dev.byebyebryan.com/codex-plus/daily-use/) | Natural requests, useful follow-up, stopping and reports. | [Source](docs/daily-use.md) |
| [Luna & workers](https://dev.byebyebryan.com/codex-plus/workers/) | Tasks, goal loops, adaptive delegation and worker installation. | [Source](docs/workers.md) |
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
| Optional worker `astra-xhigh` | `gpt-6-astra` | `xhigh` | Configured escalation from Sol/Terra or explicitly assigned work |

Delegate to Luna when the objective, responsibility boundary, and acceptance
check are clear and expected savings justify packaging, review, and possible
corrections. Confidence concerns the assignment and verification; the primary
need not solve every implementation detail first. A substantial specified
migration or focused investigation can qualify. Evolving diagnosis, shared
decisions, and small remainders often fit primary execution better.

Automatic escalation defaults to none. In the adaptive workflows, Terra can
opt in to Sol XHigh OR Astra XHigh, and Sol can opt in to Astra XHigh. Set the
single target in the request or existing applicable user guidance. Reviews and
implementation share that target; children return gaps to the initiating primary
without an escalation chain. No automatic Sol-to-Terra offload is introduced.
Unknown primary metadata holds automatic escalation while primary/Luna work
remains useful. See [examples and configuration](docs/workers.md#optional-escalation).

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
| `$worker-task` | One bounded task; no goal management | Primary or selective Luna; one opt-in escalation target |
| `$worker-goal-loop` | A substantial goal, routed per assignment | Primary or selective Luna; one opt-in escalation target |

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

Use the [agent lifecycle guide](docs/manage-agent.md) as the primary setup and
maintenance procedure. Choose components in the [setup overview](docs/getting-started.md). The
[worker installation steps](docs/workers.md#installation) install three agents and
four worker workflows; the HTML report skill is a separate optional addition.
The [runtime guide](docs/runtime-distribution.md) and
[report guide](docs/html-report-usage.md) cover their independent artifacts.
With a dotfile manager, update its source and published pins through that owner.

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
