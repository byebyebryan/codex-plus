<a id="luna-workers-and-task-workflows"></a>

# Worker workflows

Your primary is the agent in your current conversation. It can give Luna a
well-defined change to keep costs down or ask Astra to review a difficult
decision. The primary checks the result and carries on with the larger task.

- **Name a worker.** In a Sol-led session, try `$astra-task Review the CSV importer for compatibility with the old format.` Astra reviews that change. Sol uses the findings and carries on with the migration.
- **Let Codex choose.** Try `$adaptive-task Check the CSV importer and update its examples.` Your primary decides what to handle itself and what to delegate, then verifies the result.

## Choose a workflow

| What you want | One assignment | Through a substantial goal |
| --- | --- | --- |
| Let the primary choose what to do itself and whom to involve | `$adaptive-task` | `$adaptive-goal-loop` |
| Use Luna as the only delegated model | `$luna-task` | `$luna-goal-loop` |
| Choose a particular XHigh worker | `$sol-task`, `$astra-task` or `$terra-task` (current Terra) | Name the assignment and worker in your adaptive goal request. |

Invoke the skill explicitly. “Use Luna for a goal loop” also works. A generic
request for a task or goal loop stays with the ordinary primary workflow.
Discussing a skill leaves it inactive. Task skills handle one outcome.
Goal-loop skills can use native goal tools to track an explicitly requested
goal through acceptance.

## Working in parallel

1. **Agree on the record format.** Both exporters take the same reading list with titles, authors and record order.
2. **Build the two exporters in parallel.** Give each writer its own files and tests.
   - **Markdown** writes one table row per record.
   - **Plain text** writes each record on one line.
3. **Verify both through the CLI.** The primary connects the exporters to the command, runs both on the same input and checks the fields and order.

```text
$adaptive-task Add Markdown and plain-text export for the agreed reading-list
format. Keep the existing CLI behavior and verify both exports.
```

Both adaptive skills look for independent work when you invoke them. The
primary can take one assignment itself or give several assignments to eligible
workers. If one change depends on another’s output, it completes them in
sequence. This behavior shipped in preview.29.
[See the illustrated handoff](https://dev.byebyebryan.com/codex-plus/walkthrough/#scenes).

A review can split along independent questions in the same way. For example,
one worker can check error handling while another checks the examples in the
documentation. The primary collects their evidence and decides what to change.

## Example requests

### One bounded task

```text
$luna-task Investigate why the CSV importer drops quoted newlines. Return a
reproduction, the cause and a proposed fix. Keep this pass read-only.
```

The primary assigns the investigation to `luna-max` and checks Luna’s evidence.
If you want an implementation, give it write ownership and a way to verify
the fix.

```text
$luna-task Fix the quoted-newline case in the CSV importer and verify it with
the existing parser tests. Preserve the other edits in this checkout.
```

### A substantial goal

```text
$luna-goal-loop Complete the CSV importer migration in the approved plan.
Use Luna for implementation and finish when the compatibility and integration
checks pass.
```

The primary owns the goal. It can send a defect back to Luna for correction,
take over an unresolved decision, or handle a difficult portion itself. An
assignment with missing verification returns to the primary for review.

Adaptive workflows close with a short account of who did what. The primary
can credit a finding to the assignment that returned it. For a claim that
Luna completed the work, preview.30 requires a completed native turn, the
returned work and evidence of the selected role, model and effort. The primary
reports attribution gaps and conflicting evidence. A usage summary can also
show observed tokens for this run. [How usage is scoped](routing-diagnostics.md#current-run-usage).

<a id="choose-sol-or-astra-explicitly-source-candidate"></a>

### Choose Sol or Astra explicitly

Adaptive workflows let the primary choose how to delegate. A named task lets
you choose the worker for one assignment, including an independent review while
Terra remains the primary.

```text
$sol-task Review the current changes and run appropriate validation.
Return findings with file references and evidence. Leave source fixes to the primary.
```

For a second opinion on a design, give Astra the decision to examine.

```text
$astra-task Check the migration design for data-loss and recovery gaps.
Return findings and uncertainties. Keep this pass read-only.
```

The named skills select the configured `sol-xhigh` or `astra-xhigh` role
with `xhigh` effort. Your request sets the mode.

- **Review or investigation** returns findings and evidence. Source fixes need a separate implementation assignment. Tests and builds may produce ordinary outputs under the worker’s inherited native permissions.
- **Implementation** gives the worker explicit write ownership. The primary checks the result and decides whether to accept it.

A named assignment keeps your primary in charge. It needs neither
primary-model detection nor a persistent escalation preference. User
restrictions and native permissions still apply. An unavailable or incompatible
role or a failed attempt is reported for the worker you chose.

For a larger goal, assign a named review inside the adaptive loop.

```text
$adaptive-goal-loop Complete this migration. Use Sol XHigh specifically for
independent review before final acceptance. Keep implementation in the primary
or suitable Luna assignments.
```

Here Sol’s assignment covers this review and its corrections. Later work uses
the goal’s existing worker policy.

<a id="choose-current-terra-explicitly-source-candidate"></a>

### Choose current Terra explicitly

`$terra-task` uses the same bounded review, validation, investigation or
implementation contract. It selects `terra-6-1-xhigh` at the configured
current Terra version with `xhigh` reasoning.

```text
$terra-task Investigate the media import failure and return the cause and
validation evidence. Keep this pass read-only.
```

Legacy `terra-xhigh` pins GPT-5.6 Terra. Both generations have a skill named
`$terra-task`, so keep only the chosen variant in discoverable skill roots.
Identify any existing copy from its installation provenance. Make the change
through its configuration owner, preserve local edits and restrictions, and
update any rule that still declares `terra-task` retired.

In the preview.30 native check, current Terra returned a review finding and
its parent verified it. The same qualification covered Sol, Astra and Luna.
[Named-task results](worker-escalation-results.md#current-named-task-source-qualification-2026-11-21).

## Which agent does the work?

Each role has a stable name and reasoning effort. The table gives the model
shipped in the archive. A managed refresh can select a newer supported version.

| Agent | Package selection | Role |
| --- | --- | --- |
| Current primary | Selected separately by you, including Sol, Terra or Astra | Decisions, difficult portions, integration, review and acceptance. |
| `luna-max` | `gpt-6-luna`, reasoning effort `max` | Bounded investigation, implementation and validation with a practical acceptance check. |
| `sol-xhigh` | `gpt-6.1-sol`, reasoning effort `xhigh` | Bounded delegation from Astra on opt-in, explicitly selected escalation from current Terra, or a named Sol assignment. |
| `astra-xhigh` | `gpt-6-astra`, reasoning effort `xhigh` | Escalation from Sol or current Terra in an adaptive workflow, or explicitly assigned work. |
| `terra-6-1-xhigh` | `gpt-6.1-terra`, reasoning effort `xhigh` | Explicit bounded task using current Terra. The legacy role selects GPT-5.6 Terra. |

Give an assignment to Luna when the objective, ownership and acceptance
check are clear enough to justify briefing and review. A specified migration
or a focused investigation can fit. The primary can take a difficult portion,
an evolving diagnosis or a small remainder. When assessing cost, include both
agents’ usage and any corrections.

## Optional escalation

Either adaptive workflow can select **one additional worker role** for a
concrete problem or a useful second opinion. The primary chooses whether a
handoff is worth the review. Luna-only workflows keep Luna as the sole
delegated model and report when Luna is unavailable.

| Initiating primary | Additional role eligible by default | What you can opt into |
| --- | --- | --- |
| Supported current Terra | Astra XHigh | Sol XHigh in place of Astra |
| Supported Sol | Astra XHigh | — |
| Supported Astra | — | Sol XHigh |
| Luna, other or unknown | — | — |

Sol and current Terra gained default Astra eligibility in preview.26.
Preview.25 required an opt-in. Preview.28 added the opt-in Sol route for
Astra. You can also rule out escalation for a run. An enrolled Sol/Luna
baseline keeps its study restrictions. [Routing diagnostics](routing-diagnostics.md).

```text
$adaptive-task Review the importer migration. You may delegate to Sol if useful.
```

For an Astra primary, direct work and Luna are the default. Give Sol a bounded
assignment when its local decisions call for independent judgment and Astra
can check the result. Prefer Luna if it can meet the same check with comparable
supervision. Use `$sol-task` to require Sol for one review. A bounded private
study can also permit a Sol handoff. [Astra-primary daily study](routing-diagnostics.md#astra-primary-daily-study).

At each new assignment, the primary checks reliable loaded-thread metadata.
`codex-plus-context --primary` reports the configured native selection.
Execution evidence comes from the actual native turn. A worker-only setup can
use reliable native metadata directly. When that evidence is missing, or a
selected target is unavailable, automatic work stays with the primary or Luna.
An explicitly requested named assignment remains a separate choice. A host
default or model’s self-description cannot identify the loaded primary.

Existing workers keep their assignments until completion, explicit stop or
handoff. Each worker reports directly to the primary. This choice applies to the
assignment. [Earlier opt-in qualification](worker-escalation-results.md).

## Model versions

Worker names stay stable across model releases. The native role TOML records
the concrete model selected during the last requested setup/refresh. The default
preference is **latest available stable version in that family**, supporting
XHigh for Sol/Astra/current Terra or Max for Luna. An exact-model preference
pins a specific version. The resolver recognizes stable Sol and current Terra
IDs from 6.1 onward, and stable Astra and Luna IDs from 6 onward. The same
routing policy applies across supported versions.

For example, two accounts can both use `$sol-task` while their catalogues
select `gpt-6.2-sol` and `gpt-6.1-sol` respectively. Selection uses a concrete
model ID. An authorized setup or update can refresh it. A worker keeps its
selection through the assignment and reports a model-access failure for that
selection.

Ask your installation agent to refresh the worker selections using the native
home’s catalogue and its configuration owner. A workers-only installation includes an
offline resolver that uses the Python standard library. [Management guide](https://dev.byebyebryan.com/codex-plus/manage.md).

```sh
python3 -B WORKERS/scripts/codex-plus-workers resolve --catalog CATALOG.json --preferences PREFERENCES.toml
```

Here `WORKERS` stands for the verified, retained release. Supply the catalogue
file and, optionally, a preferences file. This example keeps the latest stable
Sol while pinning Astra.

```toml
[models.sol]
version = "latest-available"
[models.astra]
version = "gpt-6-astra"
```

The resolver writes only its JSON plan to stdout. Review unavailable roles before
applying any model changes. With monitoring installed,
`codex-plus-context --models` reads a bounded catalogue from the existing owner.
It uses the daemon-default provider unless you specify `--model-provider NAME`.
A workers-only agent can supply the equivalent native catalogue. Keep prior selections when discovery is unavailable.

## Native delegation and availability

The primary checks the native tool declarations and the custom roles they
expose. Call collaboration controls directly in their declared namespace.
They live outside Code Mode’s `functions.exec`, `tools.*` and `ALL_TOOLS`.

For example, `collaboration.list_agents` checks whether the listing control
works. To request Luna, use the declared `collaboration.spawn_agent` control
with `agent_type="luna-max"`, `fork_turns="none"` and a self-contained
assignment. The role argument selects the worker. Follow the actual client’s
declared schema.

| What happened | What the primary can report |
| --- | --- |
| The spawn control or selected role is missing, or its model/effort is incompatible | Identify the missing control, role or incompatible selection. The assignment hasn’t started. |
| The direct spawn call failed | Report the actual error. |
| A spawned worker returned a model or task error | Report the execution failure and any partial work. Follow the workflow’s correction or takeover rules. |
| A worker returned a result | Inspect the work, validation, native completion and available role, model and effort evidence. Report any missing fields or mismatch. |

Only native collaboration in the current client can establish that this worker
ran. Neither an installed role file nor a successful list call establishes
model access. A registry search, substitute worker, separate Codex process or
daemon restart cannot verify the requested handoff.

## How workers fit with watches and peers

A **worker** is a child of the primary in this conversation. Give each writer
a distinct responsibility and a concrete check. The primary reviews its diff
or findings. [Parallel assignments](#working-in-parallel).

A **peer** is an independent, loaded session in the same daemon. “Tell the
packaging session” uses peer messaging. Ordinary peer discovery excludes
child agents. Watches and reminders have their own registrations.
[Contact another session](session-communication.md).

## Installation

1. Ask your agent to [resolve and verify one published release](manage-agent.md#resolve-and-verify-one-published-release). Check the manifest for the skills and roles you need.
2. Through your configuration owner, install four native roles and seven workflows from its worker archive, including both files per skill. Preserve local edits, synchronized pins and skill-disable preferences. The client and account must support custom agents, skills and the selected models.
3. Confirm installed inventory and native discovery. Use completed native work to confirm access to a selected model. Freshly installed roles alone leave the policy of an already-loaded conversation in effect.

An unmanaged conventional home uses `~/.codex/agents` for native agents and
`~/.agents/skills` for user skills. Check alternate-home discovery, since
some skill roots can be shared. If chezmoi owns the files, update its source
and pins. Use verified release archives for installation. Moving-main files
are for source development. [Agent lifecycle guide](manage-agent.md#install-or-upgrade-through-the-configuration-owner) · [Custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents) · [Local skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

**Upgrading an older installation.** Preview.17 retired the worker-name aliases
`$worker-task` and `$worker-goal-loop`. Update old requests to the corresponding
adaptive skill. Retain local edits before removing the retired directories
through their owner, then check that installed inventory and discovery both
exclude them. Preview.18 added the Sol, Astra and current-Terra tasks. If you
use the current Terra variant, reconcile manager rules that still retire
`terra-task` before applying.

Workers run independently of monitoring and reporting. The bundle also
contains a separate `skills/html-report` skill to add with the reporting
component. [Choose components](getting-started.md#choose-what-to-install) · [Monitoring setup](runtime-distribution.md) · [Reporting setup](html-report-usage.md).

## Optional private routing observations

The opt-in Sol/Luna readiness study runs for up to seven days or eight goals.
An adaptive goal can enroll only in an already-opened private study. This
study covers the Sol/Luna policy. [Routing diagnostics](routing-diagnostics.md) · [Routing design](worker-routing-design.md) · [Study evidence and limits](worker-routing-study.md).
