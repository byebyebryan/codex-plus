# Luna workers and task workflows

Preview.17 includes three native custom agents and four worker workflows. Your
current primary keeps decisions, integration and acceptance. Choose an explicit
Luna workflow, or let an adaptive workflow use direct work, useful Luna delegation
and one optional escalation target without changing your primary model.

## Choose a workflow

| What you want | Invoke | What happens |
| --- | --- | --- |
| One bounded task with Luna | `$luna-task` | Delegate one cohesive investigation or implementation to Luna; the primary reviews it. |
| A substantial goal with Luna | `$luna-goal-loop` | Use Luna across useful bounded assignments until the goal and its checks are complete. |
| One task with selective delegation | `$adaptive-task` | The primary chooses direct work, useful Luna delegation, or one configured escalation target. |
| A substantial goal with selective delegation | `$adaptive-goal-loop` | The primary routes each assignment and owns integration and acceptance across the goal. |

Preview.17 removes `$worker-task` and `$worker-goal-loop`; update old requests to
the corresponding adaptive name. There are no aliases. The four canonical
instructions and native role pins are unchanged. Generic task/goal wording and
discussion activate no worker workflow.

The current source candidate adds `$sol-task` and `$astra-task`, bringing the
source inventory to six workflows with the same three roles. These two skills
are **unreleased**; preview.17 archives and installed homes still contain the
four workflows above. See the [explicit named-task examples](#choose-sol-or-astra-explicitly-source-candidate).

Task workflows do not create or manage a goal. Goal-loop workflows use available
goal tools for an explicitly requested substantial outcome. A generic “go for a
goal loop” uses the ordinary primary workflow. Mentioning or discussing a skill
does not activate it.

### One bounded task

For example, in your Codex conversation:

```text
$luna-task Investigate why the CSV importer drops quoted newlines. Return a
reproduction, the cause and a proposed fix; keep this pass read-only.
```

The primary defines a useful investigation and acceptance check, then delegates
it to `luna-max`. Luna returns evidence and any unresolved decision. Investigation
alone does not authorize implementation. For a settled fix, you can instead ask:

```text
$luna-task Fix the quoted-newline case in the CSV importer and verify it with
the existing parser tests. Preserve the other edits in this checkout.
```

### A substantial goal

```text
$luna-goal-loop Complete the CSV importer migration described in the approved
plan. Use Luna for cohesive implementation slices, review each result, and
finish when the compatibility and integration checks pass.
```

The primary owns the goal, selects assignments and reviews the results. Luna
can investigate or implement within a clear responsibility boundary. Ordinary
defects go back for correction; an unresolved decision, missing verification or
repeated failure without new evidence returns to the primary. The primary can
resolve a difficult portion and then give Luna the next suitable assignment.

Use `$adaptive-task` or `$adaptive-goal-loop` for the same task or goal when you want
the primary to choose whether delegation is useful for each assignment.

### Choose Sol or Astra explicitly (source candidate)

Adaptive workflows let the primary choose how to delegate. A named task lets
you choose the worker for one assignment, including an independent review while
Terra remains the primary:

```text
$sol-task Review the current changes and run appropriate validation.
Return findings with file references and evidence; leave source fixes to the primary.
```

For an Astra second opinion, after installing a release containing this skill:

```text
$astra-task Check the migration design for data-loss and recovery gaps.
Return findings and uncertainties; do not implement changes.
```

| Source-candidate skill | Exact worker | Scope |
| --- | --- | --- |
| `$sol-task` | `sol-xhigh`: `gpt-6.1-sol`, `xhigh` | One explicitly assigned review, investigation or implementation. |
| `$astra-task` | `astra-xhigh`: `gpt-6-astra`, `xhigh` | One explicitly assigned review, investigation or implementation. |

The request determines the mode. Review/validation and investigation return
findings and evidence without source fixes; implementation requires assigned
write ownership. Ordinary test/build outputs may still be produced under the
inherited native permissions. A review instruction is not a separate enforced
read-only sandbox. The primary checks the result and decides how to act on it.

Named tasks do not create goals, change your primary, require primary-model
detection, or enable a persistent escalation preference. An explicit choice is
independent of adaptive routing eligibility and still honors applicable user
restrictions and native permissions. Missing controls/roles, incompatible pins,
spawn rejection and worker/model errors are reported without silently selecting
a different worker. Installing a role alone does not establish model access.

For a larger goal, use the existing adaptive loop and assign a named review:

```text
$adaptive-goal-loop Complete this migration. Use Sol XHigh specifically for
independent review before final acceptance. Keep implementation in the primary
or suitable Luna assignments.
```

That instruction authorizes the requested review only; it does not enable Sol
for unrelated automatic escalation. No model-specific goal-loop skills or
mandatory review stage are added. Generic goal wording or discussion of either
new skill does not invoke it. Existing Luna-only workflows stay Luna-only.

## Which agent does the work?

| Agent | Package selection | Role |
| --- | --- | --- |
| Current primary | Selected separately by you, including Sol, Terra or Astra | Decisions, difficult portions, integration, review and acceptance. |
| `luna-max` | `gpt-6-luna`, reasoning effort `max` | Bounded investigation, implementation and validation with a practical acceptance check. |
| `sol-xhigh` | `gpt-6.1-sol`, reasoning effort `xhigh` | Optional configured escalation from Terra, or explicitly assigned independent execution. |
| `astra-xhigh` | `gpt-6-astra`, reasoning effort `xhigh` | Optional configured escalation from Sol or Terra, or explicitly assigned work. |

The Luna workflows use Luna as their only delegated model. If Luna is unavailable,
the primary explains that limitation rather than silently substituting a paid
worker. Difficult portions can stay with the primary. The adaptive worker
workflows use the optional policy below; escalation is off when unset.

Delegate when the objective, ownership boundary and acceptance check are clear,
and expected savings justify the handoff and review. A specified migration or
focused investigation can suit Luna. Evolving diagnosis or a small remainder
may be easier to finish in the primary. File count or unfamiliarity alone does
not decide the route. Compare total primary and worker usage plus corrections;
the package does not promise a universal cost saving.

## Optional escalation

Choose your primary normally in Codex. In explicitly invoked adaptive workflows,
use primary/Luna by default, or configure one target for that primary:

| Initiating primary | Optional automatic target | Default |
| --- | --- | --- |
| GPT-6.1 Terra | Sol XHigh OR Astra XHigh | None |
| GPT-6.1 Sol | Astra XHigh | None |
| Astra, Luna, another or unknown model | None in V1 | None |

For example, with a Sol primary:

```text
$adaptive-task Review the importer migration and fix any confirmed defects.
Allow Astra XHigh escalation for this task when a useful independent review
or unresolved issue warrants it. Keep Luna available for bounded work.
```

Or put a soft default in existing user guidance, through the owner of that file:

> In explicitly invoked adaptive worker workflows, allow Sol XHigh when the
> initiating primary is GPT-6.1 Terra, and Astra XHigh when it is GPT-6.1 Sol.
> Otherwise use no automatic escalation.

This example installs no preference. Native role files still pin model and
reasoning effort; no extra TOML setting or Plus preference file is needed.
The permission is a natural-language instruction interpreted by the primary,
not a parsed configuration flag or an enforced spending limit.
Enabling a route starts no work or skill and permits suitable assignments within
the authorized task without approval for every spawn. A current request can
change a soft default; native restrictions and permissions remain effective.
Reviews and implementation share that single target. There is no automatic
Sol-to-Terra cost offload, default Terra-to-Sol escalation or child-to-child
escalation chain. The primary keeps acceptance responsibility.

Resolve the initiating primary from reliable loaded-thread metadata at each
assignment boundary. The read-only `codex-plus-context --primary`
mode reports configured selection, not completed inference. Worker-only setups
need no monitoring runtime: if no reliable native selection is exposed, continue
primary/Luna work and hold automatic escalation. An explicit named-worker
request remains possible. Host defaults and model self-descriptions are not
identity evidence. Existing workers retain their contracts, settings and write
ownership when the primary or policy changes; disabling a target prevents new
assignments rather than silently cancelling active work.

To revoke permission before the next assignment, say:

> Disable automatic escalation for the next assignment. Continue suitable Luna work.

That prevents new target assignments, including reuse of an existing target
worker for new work. Active workers keep their contracts and ownership until
completion or an explicit stop/handoff. In the matched native fixture, permission
omitted, enabled for Astra and revoked produced Luna, Astra and Luna respectively.
This is bounded instruction-following evidence, not a hard spending control.

The [qualification](worker-escalation-results.md) separates source,
artifact, native execution and the unavailable local Terra-primary paths.

## Native delegation and availability

The primary checks the actual native tool declarations and the custom roles they
expose. Native collaboration controls are separate from Code Mode: they are not
in `functions.exec`'s `tools.*` namespace or `ALL_TOOLS`. An empty registry search
does not establish that delegation is unavailable.

When declared, call controls directly in their native namespace. For example,
use `collaboration.list_agents` for a read-only control check, then
`collaboration.spawn_agent` with `agent_type="luna-max"`, `fork_turns="none"`
and the self-contained assignment. A task name containing "Luna" does not select
the role. A successful list call does not prove that spawning or Luna execution
will succeed. Follow the actual declared schema for the client in use.

| Observation | Report and next step |
| --- | --- |
| No native spawn control or selected role is exposed | Name the missing control/role; no delegation was attempted. An installed agent file does not establish callable controls. |
| The direct spawn call returns an error | Report a spawn failure and its actual error; no successful worker execution is established. |
| A spawned worker returns a model/task error | Report the execution failure and any partial result; use the workflow's normal primary review/takeover rules. |

Keep the explicit invocation boundaries and routing above. Do not replace the
selected worker, launch a separate Codex process, or recommend daemon restarts
to work around the registry discovery mistake. Once a worker runs, confirm its
native model/effort metadata and inspect the returned work; installation and a
successful control call alone do not establish execution.

## How workers fit with watches and peers

Workers are child agents assigned by the primary through native agent tools.
The primary gives each worker a compact contract, preserves concurrent edits,
reviews its actual findings or diff, and checks the result before accepting it.
One cohesive assignment and one writer are the default.

The [peer tools](architecture.md#discovery-and-messaging) coordinate independent
sessions in the same daemon. Ordinary peer discovery excludes child agents.
A request to “tell the packaging session” uses that peer workflow; an explicit
`$luna-task` asks your primary to delegate work to its own worker. The worker
skills do not automatically register a watch or reminder.

## Installation

Use the [agent lifecycle guide](manage-agent.md#install-or-upgrade-through-the-configuration-owner)
for the complete procedure. Install the three native roles and four workflow
skills from a verified preview.17
worker release archive. Preserve your configuration
owner, local changes and skill disable preferences. Remove the two retired
worker-name directories through that owner after retaining any local edits;
verify they are absent from installed inventory and native discovery. The human
[setup overview](getting-started.md) explains component selection.

For an unmanaged conventional home, native agents live under `~/.codex/agents`
and user skills under `~/.agents/skills`. The official
[custom agent](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
and [local skill](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
references describe discovery. Confirm supported locations for alternate homes;
user skills can be shared. If chezmoi owns these paths, update its source and
published pins through that owner. Copying from moving main is a source-development
choice, not the released installation procedure.

The bundle also contains the separate `skills/html-report` skill. Add it when
you configure the report component; the four worker skills above do not install
that skill or either runtime.
The `astra-xhigh` role is available for permitted escalation; installing it does
not opt in to automatic use or update an already loaded conversation. Your client and account must
support the selected models, custom agents and skills; installation does not
prove runtime model availability.

Preview.17 does not contain `sol-task` or `astra-task`. Do not copy their files
from moving main into a managed preview.17 installation. A future release must
include both skill files per new workflow, update its manifest and managed pins,
and verify native discovery separately from actual model execution.

Workers do not require the monitoring or reporting runtime. Those components
have their own [monitoring setup](runtime-distribution.md) and
[reporting setup](html-report-usage.md). Existing managed worker identities and
explicit invocation remain the same.

The [routing design](worker-routing-design.md) explains the policy; the
[routing study](worker-routing-study.md) records its evidence and limits.
