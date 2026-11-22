# Luna workers and task workflows

Your current primary keeps decisions, integration and acceptance. Choose an
explicit Luna workflow when Luna should be the only delegated model. Choose an
adaptive workflow for primary-specific delegation. Astra can use Sol on opt-in.

## Model versions

Worker names stay stable across model releases. The native role TOML records
the concrete model selected during the last requested setup/refresh. The default
preference is **latest available stable version in that family**, supporting
XHigh for Sol/Astra/current Terra or Max for Luna. An exact-model preference
keeps a deliberate older version. The same routing policy applies across
supported versions of each family.

For example, one account's catalogue can resolve Sol to `gpt-6.2-sol`, while
another resolves to `gpt-6.1-sol`. Both use `$sol-task`. No `sol-latest` provider
alias is assumed. Refresh happens during authorized setup/update, not at each
assignment or while a child is running. Catalogue presence is candidate
evidence; verify actual execution separately. An unavailable model is reported,
not silently replaced after an execution failure.

Ask your installation agent to refresh worker model selections using the
[management guide](https://dev.byebyebryan.com/codex-plus/manage.md). It reads the
selected native home's catalogue and applies concrete roles through the existing
configuration owner. Workers alone include a stdlib-only offline resolver:

```sh
rtk proxy python3 -B WORKERS/scripts/codex-plus-workers resolve --catalog CATALOG.json --preferences PREFERENCES.toml
```

`WORKERS` is the verified retained worker release; the files are operator inputs,
not user copy/paste parameters. Preferences are optional. For example:

```toml
[models.sol]
version = "latest-available"
[models.astra]
version = "gpt-6-astra"
```

The resolver writes only its JSON plan to stdout. Review unavailable roles before
applying any model changes. With monitoring installed,
`codex-plus-context --models` (daemon-default provider; add
`--model-provider NAME` for a configured provider override) reads a complete bounded catalogue from an existing
owner. A workers-only agent can supply the equivalent native catalogue; no new
component or daemon is required. Keep prior selections when discovery is unavailable.

## Choose a workflow

| What you want | Invoke | What happens |
| --- | --- | --- |
| One bounded task with Luna | `$luna-task` | Delegate one cohesive investigation or implementation to Luna; the primary reviews it. |
| A substantial goal with Luna | `$luna-goal-loop` | Use Luna across useful bounded assignments until the goal and its checks are complete. |
| One task with selective delegation | `$adaptive-task` | The primary chooses direct work, useful Luna delegation, or justified escalation. |
| A substantial goal with selective delegation | `$adaptive-goal-loop` | The primary routes each assignment and owns integration and acceptance across the goal. |
| One named Sol task | `$sol-task` | Use Sol XHigh for the requested review, validation, investigation or implementation. |
| One named Astra task | `$astra-task` | Use Astra XHigh for the requested review, validation, investigation or implementation. |
| One named current-Terra task | `$terra-task` | Use the configured current Terra XHigh for the requested bounded task. |

Preview.17 removes `$worker-task` and `$worker-goal-loop`; update old requests to
the corresponding adaptive name. There are no aliases. The canonical
workflow identities and invocation boundaries remain unchanged. Generic task/goal wording and
discussion activate no worker workflow.

Check the selected release manifest for the workflow identities it contains.
Older releases may not include the three named tasks; select and verify a
compatible release through the [installation procedure](#installation). See the
[Sol/Astra examples](#choose-sol-or-astra-explicitly-source-candidate) and
[current Terra task](#choose-current-terra-explicitly-source-candidate).

Task workflows do not create or manage a goal. Goal-loop workflows use available
goal tools for an explicitly requested substantial outcome. A generic “go for a
goal loop” uses the ordinary primary workflow; an explicit natural-language
request to use Luna for a goal loop activates `$luna-goal-loop` even without the
skill token. Mentioning or discussing a skill does not activate it.

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

You can also ask directly: “Use Luna for a goal loop to complete the CSV importer
migration in the approved plan, reviewing each result against the compatibility
and integration checks.”

The primary owns the goal, selects assignments and reviews the results. Luna
can investigate or implement within a clear responsibility boundary. Ordinary
defects go back for correction; an unresolved decision, missing verification or
repeated failure without new evidence returns to the primary. The primary can
resolve a difficult portion and then give Luna the next suitable assignment.

Use `$adaptive-task` or `$adaptive-goal-loop` for the same task or goal when you want
the primary to choose whether delegation is useful for each assignment.

In preview.27, the adaptive workflows close with a short summary of who did what.
When native usage is available, the summary can include per-model token counts
for the current run. Contributions can still be reported on a workers-only
install. [How usage is scoped](routing-diagnostics.md#current-run-usage).

### Working in parallel

An ordinary request to either adaptive skill is enough for the primary to look
for work that can run at the same time. Each assignment needs the inputs to
start and a result the primary can verify. The primary chooses a model for each
assignment and can do one itself. Use this behavior in preview.29 and later.

For a review or research report, several workers can investigate separate
questions. For implementation, workers can make changes at the same time when
each owns its edits and the interface between them is settled. For example, two
exporters can be built against the same agreed record format. If the format
still needs a decision, settle it first. The primary checks the combined result.

```text
$adaptive-task Review this project's error handling and documentation for gaps.
```

```text
$adaptive-goal-loop Add CSV and JSON exporters for the published record format
and verify that both preserve every field.
```

<a id="choose-sol-or-astra-explicitly-source-candidate"></a>

### Choose Sol or Astra explicitly

Adaptive workflows let the primary choose how to delegate. A named task lets
you choose the worker for one assignment, including an independent review while
Terra remains the primary:

```text
$sol-task Review the current changes and run appropriate validation.
Return findings with file references and evidence; leave source fixes to the primary.
```

For an Astra second opinion:

```text
$astra-task Check the migration design for data-loss and recovery gaps.
Return findings and uncertainties; do not implement changes.
```

| Named skill | Exact worker | Scope |
| --- | --- | --- |
| `$sol-task` | `sol-xhigh`: configured Sol version, `xhigh` | One explicitly assigned review, investigation or implementation. |
| `$astra-task` | `astra-xhigh`: configured Astra version, `xhigh` | One explicitly assigned review, investigation or implementation. |

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

<a id="choose-current-terra-explicitly-source-candidate"></a>

### Choose current Terra explicitly

`$terra-task` uses the same bounded review, validation, investigation or
implementation contract as the named tasks above. It selects exactly
`terra-6-1-xhigh`: the configured current Terra version with `xhigh` reasoning. It preserves your
primary and needs no automatic escalation preference or primary detection.

```text
$terra-task Investigate the media import failure and return the cause and
validation evidence. Do not change source files.
```

The release adds a distinct role because legacy `terra-xhigh` still pins
GPT-5.6 Terra. Both skill variants use the `$terra-task` name: select one
deliberately, and never install both into discoverable skill roots. Identify an
existing copy from retained installation provenance before a reviewed replacement
through its configuration owner; preserve local changes and restrictions. Do not
delete a chosen current task as part of blanket legacy cleanup.
Also reconcile any manager rule that still declares `terra-task` retired before
installing the current variant; otherwise it may be removed during convergence.

Terra is available by explicit assignment. In a [native test of all three named
tasks](worker-escalation-results.md#current-named-task-source-qualification-2026-11-21),
the current Terra worker completed a review and its parent verified the finding.
On a host where the selected role cannot run, the primary reports the missing
control, incompatible role, spawn failure or execution error.

## Which agent does the work?

Packaged compatibility seeds are listed below; managed refresh can select newer
supported versions while preserving each native role name and effort.

| Agent | Package selection | Role |
| --- | --- | --- |
| Current primary | Selected separately by you, including Sol, Terra or Astra | Decisions, difficult portions, integration, review and acceptance. |
| `luna-max` | `gpt-6-luna`, reasoning effort `max` | Bounded investigation, implementation and validation with a practical acceptance check. |
| `sol-xhigh` | `gpt-6.1-sol`, reasoning effort `xhigh` | Optional configured escalation from Terra, or explicitly assigned independent execution. |
| `astra-xhigh` | `gpt-6-astra`, reasoning effort `xhigh` | Escalation from Sol or current Terra in an adaptive workflow, or explicitly assigned work. |
| `terra-6-1-xhigh` | `gpt-6.1-terra`, reasoning effort `xhigh` | Explicit bounded task only; distinct from legacy GPT-5.6 Terra. |

The Luna workflows use Luna as their only delegated model. If Luna is unavailable,
the primary explains that limitation rather than silently substituting a paid
worker. Difficult portions can stay with the primary. Adaptive workflows can
also escalate under the policy below.

Delegate when the objective, ownership boundary and acceptance check are clear,
and expected savings justify the handoff and review. A specified migration or
focused investigation can suit Luna. Evolving diagnosis or a small remainder
may be easier to finish in the primary. File count or unfamiliarity alone does
not decide the route. Compare total primary and worker usage plus corrections;
the package does not promise a universal cost saving.

## Optional escalation

In **preview.26**, explicitly invoking either adaptive skill makes
Astra XHigh available for justified escalation from a known Sol or current
Terra primary. Preview.25 requires an opt-in.

| Initiating primary | Default eligible target | Compatible explicit alternative |
| --- | --- | --- |
| Supported current Terra family | Astra XHigh | Sol XHigh |
| Supported Sol family | Astra XHigh | None |
| Supported Astra family | None | Sol XHigh for delegated work on opt-in |
| Luna, another or unknown model | None | None |

```text
$adaptive-task Review the importer migration and fix any confirmed defects.
```

From an Astra primary, the default is to keep work in Astra or hand a
verifiable assignment to Luna. In preview.28 you can permit Sol for one
request with either adaptive skill.

```text
$adaptive-task Review the importer migration. You may delegate to Sol if useful.
```

Sol is a good fit when the acceptance check is clear but the worker must make
consequential local decisions. Astra keeps cross-cutting decisions and accepts
the result. If Luna could meet the same check with comparable supervision,
prefer Luna. For a review that specifically requires Sol, use `$sol-task`.
An operator can also open a bounded [Astra-primary daily study](routing-diagnostics.md#astra-primary-daily-study).

The primary escalates only when a concrete issue, demanding slice, or useful
second opinion justifies the handoff and review. For cost-sensitive work, use
`$luna-task` or `$luna-goal-loop`. The primary also honors a request to rule
out escalation for a particular run. An enrolled [Sol/Luna baseline](routing-diagnostics.md)
keeps its study policy. For a Terra primary, an explicit Sol request replaces
Astra as the one escalation target. Native role files still pin model and
effort. There is no new setting, automatic Sol-to-Terra route, or escalation chain.

Resolve the initiating primary from reliable loaded-thread metadata at each
assignment boundary. The read-only `codex-plus-context --primary`
mode reports configured selection, not completed inference. Worker-only setups
need no monitoring runtime: if no reliable native selection is exposed, continue
primary/Luna work and hold automatic escalation. An explicit named-worker
request remains possible. Host defaults and model self-descriptions are not
identity evidence. When the selected target is unavailable, continue in the
primary or with useful Luna work. Existing workers retain their contracts and
ownership until completion or an explicit stop or handoff.

The [preview.15 qualification](worker-escalation-results.md) records native
evidence for the earlier opt-in policy.

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
Each change has one owner. The adaptive skills can [run independent work in parallel](#working-in-parallel).

The [peer tools](architecture.md#discovery-and-messaging) coordinate independent
sessions in the same daemon. Ordinary peer discovery excludes child agents.
A request to “tell the packaging session” uses that peer workflow; an explicit
`$luna-task` asks your primary to delegate work to its own worker. The worker
skills do not automatically register a watch or reminder.

## Installation

Use the [agent lifecycle guide](manage-agent.md#install-or-upgrade-through-the-configuration-owner)
for the complete procedure. Select and verify the current release using its
[release selection and verification procedure](manage-agent.md#resolve-and-verify-one-published-release),
then install the four native roles and seven workflow skills from that release's
worker archive. Preserve your configuration
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
you configure the report component; the seven worker skills above do not install
that skill or either runtime.
The installed adaptive skills determine when `astra-xhigh` is eligible.
Installing the role alone changes neither skill policy nor an already loaded
conversation. Your client and account must support the selected models,
custom agents and skills.

When upgrading an installation that predates the named tasks, select a verified
release whose manifest contains the requested skills and roles.
Upgrade through the configuration owner, including both files per skill, the
required roles and synchronized pins. Reconcile any retired Terra-task
declaration before applying. Verify native discovery separately from actual
model execution; do not graft moving-main files into a pinned older release.

Workers do not require the monitoring or reporting runtime. Those components
have their own [monitoring setup](runtime-distribution.md) and
[reporting setup](html-report-usage.md). Existing managed worker identities and
explicit invocation remain the same.

The [routing design](worker-routing-design.md) explains the policy; the
[routing study](worker-routing-study.md) records its evidence and limits.

## Optional private routing observations

The [routing diagnostics guide](routing-diagnostics.md) describes the opt-in
seven-day/eight-goal Sol/Luna readiness window. The adaptive goal skill enrolls
only into an already opened private study. Normal routing, named tasks and
Luna-only invocation stay unchanged; no Terra comparison is enabled.
