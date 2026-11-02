---
name: worker-task
description: Use only when the user invokes $worker-task or explicitly asks to use the worker-task skill. Complete one bounded task in the primary, selectively delegating clear, verifiable work to Luna. Escalation uses one opt-in target for the initiating primary. Generic task or goal-loop requests and discussion of the skill do not activate it; no goal management.
---

# Worker Task

Activate only through `$worker-task` or an explicit request to use this named
skill. Generic task or goal-loop requests and discussion or editing of the skill
do not activate it.

Keep the current primary responsible for decisions, integration, and acceptance;
selectively use Luna Max and one opt-in escalation target when useful. This
skill does not change the primary model or create or manage a goal.

## Define and route the task

Inspect the request, repository instructions, worktree, and enough authoritative
context to define the outcome, ownership boundary, and acceptance check. Resolve
ordinary technical decisions within the user's scope. Ask the user only for a
missing preference, product choice, or authorization that materially affects
the work. Start implementation once intended behavior and invariants are settled;
individual coding steps need not be predetermined.

Keep work in the primary when the benefit of delegation is uncertain. Delegate
to `luna-max` when the objective, responsibility boundary, and acceptance check
are clear, and expected savings justify packaging, review, and possible
corrections. Confidence concerns the assignment and verification; Luna can
choose implementation details or investigate a well-defined question without
the primary solving it first.

Keep evolving diagnosis, shared decisions, and difficult portions in the primary.
If preparing a handoff would do most of the work, or only a small remainder is
left, finish directly. A substantial specified migration or focused investigation
can still suit Luna. Complexity labels, file count, or unfamiliarity alone do
not decide the route. Do not require an unsuccessful Luna attempt before using
the primary, or impose a delegation quota.

## Resolve optional escalation

Keep the user's native primary and its reasoning setting. At each new assignment
boundary, read reliable loaded-thread metadata for the initiating primary. When
available, `codex-plus-context --primary` provides that read-only selection;
`status="known"` is configuration evidence, not proof of completed inference.
Do not infer identity from a host config default or a model's self-description.
If reliable metadata is unavailable, keep primary/Luna work useful and hold
automatic escalation; worker-only installs need no runtime or new service.
An explicit user assignment to a named worker remains a separate native action.

Resolve one optional target from the current request or applicable user guidance;
otherwise use none. A request may override a soft default, but never restrictions
or native permissions. Valid automatic routes are:

| Initiating primary | Optional target | Named role |
| --- | --- | --- |
| `gpt-6.1-terra` | Sol XHigh OR Astra XHigh, exactly one | `sol-xhigh` OR `astra-xhigh` |
| `gpt-6.1-sol` | Astra XHigh | `astra-xhigh` |
| Astra, Luna, other or unknown | None | No automatic escalation |

Do not guess between conflicting targets. Hold escalation until that choice is
clear; continue useful primary/Luna work. Do not automatically offload Sol work
to Terra or escalate Terra to Sol without opt-in. Explicit Luna workflows keep
Luna as their only delegated model regardless of this setting.

Use the configured target for a concrete unresolved issue, demanding slice or
useful second opinion whose benefit justifies handoff and review. Reviews and
implementation use the same target; no separate review switch or mandatory
review stage. Higher price alone does not prove a capability improvement.
Do not require a failed Luna attempt or a diagnostic probe before the first
useful assignment to a compatible exposed role.

One target is a model choice, not a one-call quota; bounded corrections may reuse
it. Children return unresolved gaps to the initiating primary and receive no
nested-delegation authority. A Terra-to-Sol child must not reapply a Sol-to-Astra
default. Policy or primary changes affect the next assignment only: preserve
active children's contracts, settings and write ownership. Disabling a target
admits no new target assignments; handle active work under explicit stop and
ownership instructions. Enabling a target starts no work, invokes no skill and
needs no approval per suitable assignment within the authorized task.

## Discover native delegation

Inspect the actual native tool declarations and their exposed custom-agent roles
before deciding delegation is unavailable. Native collaboration controls are
called directly in their declared namespace (for example,
`collaboration.spawn_agent`), outside `functions.exec`. They are intentionally
absent from Code Mode's `tools.*` namespace and `ALL_TOOLS`; an empty registry
search is not evidence that native controls are missing. A directly declared
`collaboration.list_agents` can check that control, but does not prove that a
role, spawning or model execution works.

Select the exact named role with its fixed model/effort. Honor native pin
precedence and requirements; an override does not retune a pinned role. A
missing role or incompatible pin holds that route. Do not silently alias it.
Distinguish missing controls/roles (no delegation attempted), a rejected spawn,
post-start worker/model errors, and an observed model reroute. Report the actual
observation and useful partial work honestly; do not claim the requested target
ran if the observed selection differs. Preserve the parent's provider,
permissions and MCP environment. Do not substitute another target, change
billing/provider, launch a separate Codex process or recommend a daemon restart.
If the selected route cannot run, continue in the primary where feasible or
report the unresolved gap. Do not invent an automatic fallback ladder.

State the chosen route and brief rationale without asking the user to route it.
Retain resource constraints and do not promise exact billing enforcement when
telemetry cannot establish it.

## Delegate when useful

Give the selected worker a compact, self-contained contract containing:

- investigation or implementation mode, objective, and observable outcome;
- owned files or responsibility, with unrelated changes to preserve;
- invariants, non-goals, and authoritative context to inspect;
- the acceptance check and proportionate validation; and
- unresolved decisions or conditions to return to the primary, including an
  explicit prohibition on nested delegation.

An investigation or review returns findings and evidence without implementation
edits. Implementation requires explicit write ownership. Call the declared
native spawn control directly, explicitly selecting the named role: for Luna,
use `agent_type="luna-max"` and `fork_turns="none"` for the self-contained
contract. For configured escalation select exactly `sol-xhigh` or `astra-xhigh` as
resolved above, also with `fork_turns="none"`.
Honor the declared client schema and role/model rules; a task label is not role
selection. Prefer one cohesive assignment over parallel microtasks. Do not
duplicate the worker's implementation while it runs.

## Review and recover

Inspect actual findings or diffs and validation evidence. Reuse the worker for
clarifications and bounded corrections. An ordinary failed test is usually a
correction. If the same failure repeats without new evidence, or a decision or
verification gap emerges, have the primary diagnose or take over the difficult
portion. Do not require an unsuccessful Luna attempt before choosing the primary
for work already known to need it.

Before changing write ownership, obtain the handoff or stop the current writer
and inspect partial changes. Preserve useful work. A subsequent escalation still
requires the configured target and a concrete benefit; avoid cycling between
workers. Reassess clear remaining work for Luna when useful.

## Finish

Review integration behavior, failure paths, unrelated changes, and test gaps.
Resolve verification gaps before acceptance, including work done by the primary.
Run checks appropriate to the assignment and repository-required gates; broaden
checks only for an unresolved risk. Complete corrections within the original task without
silently expanding scope or creating a goal.

Keep commits, pushes, deployment, and other external actions within existing
authorization. Report the outcome, routing rationale, worker and primary
contributions, validation, remaining uncertainty, and repository state.
