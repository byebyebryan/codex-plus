# Codex Plus

Small augmentations around native Codex conversations and the TUI. This repository
was previously published as Codex Worker Kit; its existing worker agents and skills
remain available with the same identities and installation paths.

## Current scope and next step

The published/installed bundle remains the worker agents and skills described below.
This checkout also contains a tested **local watch coordinator candidate** for
monitoring and model-controlled wakeups into an explicitly selected existing
Codex thread. See [the candidate guide](docs/watch-candidate.md) and
[the research and acceptance report](docs/coordinator-loop-results.md).
It also includes same-daemon independent-session discovery, bounded passive peer
reads, correlated message registrations and peer watches through that coordinator.
See [the peer-watch acceptance report](docs/peer-watch-results.md) for the tested
scope and remaining human checks.
Claude Code's Monitor
and adaptive scheduling, informed by Bryan's actual usage, guide the design.
Give the model options for sources, scripts, filtering, cadence and renewal;
bounded JSON snapshot filtering is one useful option. Status, cancellation and
expiry are part of the candidate. It is not released or installed through chezmoi.
The [initial monitoring spike](docs/monitoring-spike-results.md) records native
source/queue/timer evidence, a research-only simulator/helper and the remaining
goal, stop and daily-use acceptance gates.

Same-daemon peer coordination now builds on watches without an Agent Observer
dependency. Reassess Observer's discovery/freshness contract when cross-host
coordination is needed.

The [implementation plan](docs/codex-plus-plan.md) records the proposed runtime,
same-thread delivery, daily-use acceptance and chezmoi packaging. The
[Claude monitoring context](docs/claude-monitoring-context.md) captures the latest
design correction, source-host history findings and open planning decisions.
Development continues on Snap. The qualified candidate uses the existing native
CLI daemon and leaves Codex CLI/TUI as the daily interface. Human TUI acceptance,
longer operation and installation remain subsequent work. Existing active sessions
have supplied passive observation evidence; all experimental messaging and delivery
used synthetic sessions.

For a new implementation thread, read [AGENTS.md](AGENTS.md) and the
[implementation handoff](docs/implementation-handoff.md) before the plan. They
summarize research evidence, reuse boundaries, distribution and local draft state.

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

Clone the repository and install the two current custom agents and four skills:

```sh
git clone https://github.com/byebyebryan/codex-plus.git
mkdir -p ~/.codex/agents ~/.agents/skills
cp codex-plus/agents/*.toml ~/.codex/agents/
cp -R codex-plus/skills/. ~/.agents/skills/
```

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
- Separable parallel work or a noisy investigation can use Sol when another
  execution context helps.
- An ordinary failed test goes back for correction; repeated failure without new
  evidence returns to the primary.
- An explicit Luna workflow never silently creates a Sol or Terra worker.

Compare total primary-plus-worker usage, corrections, elapsed time, and accepted
results on representative tasks. Use runtime cost data when available; do not
infer savings from the number of Luna assignments or from token rates alone.

## Design notes

[Worker routing design](docs/worker-routing-design.md) records selective Luna
delegation, the separate purpose of Sol workers, and the rollout plan.
[Worker routing research](docs/worker-routing-study.md) reviews the evidence,
its limits, and a lightweight policy to assess in practice.
The active workflow instructions above describe the current implementation.
