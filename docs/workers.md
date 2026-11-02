# Luna workers and task workflows

The local worker candidate includes three custom agents and four explicitly
invoked worker workflows. Published preview.14 still has two agents and the
earlier Sol/Luna policy; this candidate is not released or installed. Your current primary agent keeps decisions, integration and final
review. A workflow can hand a useful assignment to a worker without changing
your primary model.

## Choose a workflow

| What you want | Invoke | What happens |
| --- | --- | --- |
| One bounded task with Luna | `$luna-task` | Delegate one cohesive investigation or implementation to Luna; the primary reviews it. |
| A substantial goal with Luna | `$luna-goal-loop` | Use Luna across useful bounded assignments until the goal and its checks are complete. |
| One task with selective delegation | `$worker-task` | The primary chooses direct work, useful Luna delegation, or one configured escalation target. |
| A substantial goal with selective delegation | `$worker-goal-loop` | The primary routes each assignment and owns integration and acceptance across the goal. |

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

Use `$worker-task` or `$worker-goal-loop` for the same task or goal when you want
the primary to choose whether delegation is useful for each assignment.

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

## Optional escalation in the local candidate

Choose your primary normally in Codex. In explicitly invoked adaptive workflows,
use primary/Luna by default, or configure one target for that primary:

| Initiating primary | Optional automatic target | Default |
| --- | --- | --- |
| GPT-6.1 Terra | Sol XHigh OR Astra XHigh | None |
| GPT-6.1 Sol | Astra XHigh | None |
| Astra, Luna, another or unknown model | None in V1 | None |

For example, with a Sol primary:

```text
$worker-task Review the importer migration and fix any confirmed defects.
Allow Astra XHigh escalation for this task when a useful independent review
or unresolved issue warrants it. Keep Luna available for bounded work.
```

Or put a soft default in existing user guidance, through the owner of that file:

> In explicitly invoked adaptive worker workflows, allow Sol XHigh when the
> initiating primary is GPT-6.1 Terra, and Astra XHigh when it is GPT-6.1 Sol.
> Otherwise use no automatic escalation.

This example installs no preference. Native role files still pin model and
reasoning effort; no extra TOML setting or Plus preference file is needed.
Enabling a route starts no work or skill and permits suitable assignments within
the authorized task without approval for every spawn. A current request can
change a soft default; native restrictions and permissions remain effective.
Reviews and implementation share that single target. There is no automatic
Sol-to-Terra cost offload, default Terra-to-Sol escalation or child-to-child
escalation chain. The primary keeps acceptance responsibility.

Resolve the initiating primary from reliable loaded-thread metadata at each
assignment boundary. The candidate's read-only `codex-plus-context --primary`
mode reports configured selection, not completed inference. Worker-only setups
need no monitoring runtime: if no reliable native selection is exposed, continue
primary/Luna work and hold automatic escalation. An explicit named-worker
request remains possible. Host defaults and model self-descriptions are not
identity evidence. Existing workers retain their contracts, settings and write
ownership when the primary or policy changes; disabling a target prevents new
assignments rather than silently cancelling active work.

The [candidate qualification](worker-escalation-results.md) separates source,
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
for the complete procedure. Published preview.14 installs its two agents and
four workflow skills from a verified worker release archive and preserves your configuration
owner, local changes and skill disable preferences. The human
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
The source candidate additionally packages `astra-xhigh`; its presence does not
opt in to paid escalation or update an installation. Your client and account must
support the selected models, custom agents and skills; installation does not
prove runtime model availability.

Workers do not require the monitoring or reporting runtime. Those components
have their own [monitoring setup](runtime-distribution.md) and
[reporting setup](html-report-usage.md). Existing managed worker identities and
explicit invocation remain the same.

The [routing design](worker-routing-design.md) explains the policy; the
[routing study](worker-routing-study.md) records its evidence and limits.
