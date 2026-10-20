# Luna workers and task workflows

Codex Plus includes two custom agents and four explicitly invoked worker
workflows. Your current primary agent keeps decisions, integration and final
review. A workflow can hand a useful assignment to a worker without changing
your primary model.

## Choose a workflow

| What you want | Invoke | What happens |
| --- | --- | --- |
| One bounded task with Luna | `$luna-task` | Delegate one cohesive investigation or implementation to Luna; the primary reviews it. |
| A substantial goal with Luna | `$luna-goal-loop` | Use Luna across useful bounded assignments until the goal and its checks are complete. |
| One task with selective delegation | `$worker-task` | The primary decides whether to work directly, use Luna, or use Sol when a separate execution context helps. |
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
| Current primary | Selected separately by you; intended setup is Sol XHigh | Decisions, difficult portions, integration, review and acceptance. |
| `luna-max` | `gpt-6-luna`, reasoning effort `max` | Bounded investigation, implementation and validation with a practical acceptance check. |
| `sol-xhigh` | `gpt-6.1-sol`, reasoning effort `xhigh` | Optional worker for separable parallel work, a context-isolated investigation or independent review. |

The Luna workflows use Luna as their only delegated model. If Luna is unavailable,
the primary explains that limitation rather than silently substituting a paid
worker. Difficult portions can stay with the primary. The adaptive worker
workflows can also use Sol when another execution context has a concrete benefit.

Delegate when the objective, ownership boundary and acceptance check are clear,
and expected savings justify the handoff and review. A specified migration or
focused investigation can suit Luna. Evolving diagnosis or a small remainder
may be easier to finish in the primary. File count or unfamiliarity alone does
not decide the route. Compare total primary and worker usage plus corrections;
the package does not promise a universal cost saving.

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

For an unmanaged conventional Codex home, clone the repository and copy the
two agents and four worker skills. Run these commands from the parent directory
where you want the checkout:

```sh
git clone https://github.com/byebyebryan/codex-plus.git
mkdir -p ~/.codex/agents ~/.agents/skills
cp codex-plus/agents/*.toml ~/.codex/agents/
cp -R codex-plus/skills/luna-task codex-plus/skills/luna-goal-loop codex-plus/skills/worker-task codex-plus/skills/worker-goal-loop ~/.agents/skills/
```

The paths follow the official [custom agent](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
and [local skill](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
documentation. For another Codex home, use its agent directory and the skill
location supported by your client. If chezmoi owns these paths, update its
source and published pins through that installation method.

The bundle also contains the separate `skills/html-report` skill. Add it when
you configure the report component; the four worker skills above do not install
that skill or either runtime.
Your client and account must support the selected models, custom agents and
skills; installation does not prove runtime model availability.

Workers do not require the monitoring or reporting runtime. Those components
have their own [monitoring setup](runtime-distribution.md) and
[reporting setup](html-report-usage.md). Existing managed worker identities and
explicit invocation remain the same.

The [routing design](worker-routing-design.md) explains the policy; the
[routing study](worker-routing-study.md) records its evidence and limits.
