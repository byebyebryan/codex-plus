---
name: adaptive-task
description: Use only when the user invokes $adaptive-task or explicitly asks to use the adaptive-task skill. Complete one bounded task in the primary, selectively delegating clear, verifiable work to Luna. Astra is available for justified escalation from a supported primary. Generic task or goal-loop requests and discussion of the skill do not activate it; no goal management.
---

# Adaptive Task

Activate only through `$adaptive-task` or an explicit request to use this named
skill. Generic task or goal-loop requests and discussion or editing of the skill
do not activate it.

Keep the current primary responsible for decisions, integration, and acceptance.
Use Luna Max for suitable handoffs and allow one escalation target when justified.
This skill does not change the primary model or create or manage a goal.

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

## Resolve escalation

Keep the user's native primary and its reasoning setting. At each new assignment
boundary, read reliable loaded-thread metadata for the initiating primary. When
available, `codex-plus-context --primary` provides that read-only selection;
`status="known"` is configuration evidence, not proof of completed inference.
Do not infer identity from a host config default or a model's self-description.
If reliable metadata is unavailable, keep primary/Luna work useful and hold
automatic escalation; worker-only installs need no runtime or new service.
An explicit user assignment to a named worker remains a separate native action.

Resolve at most one escalation target. Astra XHigh is the default for a
supported Sol or current Terra primary. Honor a compatible explicit choice or
a restriction on escalation in the request or applicable user guidance. The
default applies only inside this explicitly invoked workflow.

| Initiating primary | Default target | Compatible explicit alternative |
| --- | --- | --- |
| Supported current Terra family | Astra XHigh (`astra-xhigh`) | Sol XHigh (`sol-xhigh`) |
| Supported Sol family | Astra XHigh (`astra-xhigh`) | None |
| Astra, Luna, other or unknown | None | None |

Identify the family from the exact loaded model ID, using the installed
`codex-plus-workers classify --model MODEL` when useful. Supported stable IDs
are `gpt-M[.m]-sol` (6.1+), `-astra` and `-luna` (6+), and current `-terra`
(6.1+); aliases and other IDs stay unknown. Family recognition grants no
additional route. Native role files hold the concrete model and effort selected
at the last managed refresh; do not resolve or upgrade models during a task.

Hold escalation if instructions conflict or the selected target is unavailable.
Continue useful primary/Luna work without substituting another escalation
target. Sol does not automatically offload to Terra. Explicit Luna workflows
use Luna as their only delegated model.

Use escalation for a concrete unresolved issue, demanding slice, or useful
second opinion whose value justifies handoff and review. The default makes a
target available; it creates no routine review, automatic spawn, or requirement
to try Luna first. Reviews and implementation use the same target.

Reuse that target for bounded corrections when useful. Children return gaps to
the initiating primary and receive no nested-delegation authority. A policy or
primary change applies to new assignments. Active children retain their
contracts, settings, and ownership until completion or an explicit stop or handoff.

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
missing role, wrong family or incompatible effort holds that route. Verify the
actual declared selection against the requested family and effort; an exact
version preference remains binding. Do not silently alias or retune it.
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
contract. For escalation select exactly `sol-xhigh` or `astra-xhigh` as
resolved above, also with `fork_turns="none"`.
Honor the declared client schema and role/model rules; a task label is not role
selection. Prefer one cohesive assignment over parallel microtasks. Do not
duplicate the worker's implementation while it runs.

## Review and recover

Check completed-turn state and available native worker model/effort metadata
before claiming the selected target ran. Keep unavailable selection evidence
explicit while reviewing any useful result; role installation alone is not
completed execution.

Inspect actual findings or diffs and validation evidence. Reuse the worker for
clarifications and bounded corrections. An ordinary failed test is usually a
correction. If the same failure repeats without new evidence, or a decision or
verification gap emerges, have the primary diagnose or take over the difficult
portion. Do not require an unsuccessful Luna attempt before choosing the primary
for work already known to need it.

Before changing write ownership, obtain the handoff or stop the current writer
and inspect partial changes. Preserve useful work. A subsequent escalation still
requires the selected target and a concrete benefit; avoid cycling between
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
