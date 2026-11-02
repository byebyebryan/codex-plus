---
name: worker-task
description: Use only when the user invokes $worker-task or explicitly asks to use the worker-task skill. Complete one bounded task in the primary, selectively delegating clear, verifiable work to Luna. Sol workers need an independent execution benefit. Generic task or goal-loop requests and discussion of the skill do not activate it; no goal management.
---

# Worker Task

Activate only through `$worker-task` or an explicit request to use this named
skill. Generic task or goal-loop requests and discussion or editing of the skill
do not activate it.

Keep the current primary responsible for decisions, integration, and acceptance;
the intended setup is Sol XHigh with selective Luna Max delegation. This skill
does not change the primary model or create or manage a goal.

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

## Use a Sol worker for independent execution

Use `sol-xhigh` only when another execution context has a concrete benefit:
separable parallel work, an investigation with large intermediate output that
can be distilled, or an independent review. State that benefit and account for
handoff and acceptance effort. Difficulty beyond Luna normally stays in the
primary; another Sol worker is not a stronger model tier.

Separate files may still share decisions. Establish independence before parallel
writes, and require review findings to point to evidence rather than treating
another same-model opinion as verification. Do not route automatically to Terra
or Astra.

Inspect the actual native tool declarations and their exposed custom-agent roles
before deciding delegation is unavailable. Native collaboration controls are
called directly in their declared namespace (for example,
`collaboration.spawn_agent`), outside `functions.exec`. They are intentionally
absent from Code Mode's `tools.*` namespace and `ALL_TOOLS`; an empty registry
search is not evidence that native controls are missing. A directly declared
`collaboration.list_agents` can check that control, but does not prove that the
Luna role, spawning, or model execution works.

Distinguish missing native controls or roles (no delegation attempted), an error
from the actual spawn call (spawn failed), and model/task errors after a worker
starts (worker execution failed). Report the observed limitation or error and
any partial result honestly. Do not substitute another worker, launch a separate
Codex process, or recommend a daemon restart to work around this discovery
mistake. Retain this workflow's existing primary takeover and routing rules.

If the selected worker genuinely cannot be used, disclose the specific reason
and continue in the primary. State the chosen route and a brief rationale
without asking the user to route it.

## Delegate when useful

Give the selected worker a compact, self-contained contract containing:

- investigation or implementation mode, objective, and observable outcome;
- owned files or responsibility, with unrelated changes to preserve;
- invariants, non-goals, and authoritative context to inspect;
- the acceptance check and proportionate validation; and
- unresolved decisions or conditions to return to the primary.

An investigation does not authorize implementation edits. Call the declared
native spawn control directly, explicitly selecting the named role: for Luna,
use `agent_type="luna-max"` and `fork_turns="none"` for the self-contained
contract. Select `sol-xhigh` only under the existing independent-execution rule.
Honor the declared client schema and role/model rules; a task label is not role
selection. Prefer one cohesive assignment over parallel microtasks. Do not duplicate
the worker's implementation while it runs.

## Review and recover

Inspect actual findings or diffs and validation evidence. Reuse the worker for
clarifications and bounded corrections. An ordinary failed test is usually a
correction. If the same failure repeats without new evidence, or a decision or
verification gap emerges, have the primary diagnose or take over the difficult
portion. Do not require an unsuccessful Luna attempt before choosing the primary
for work already known to need it.

Before changing write ownership, obtain the handoff or stop the current writer
and inspect partial changes. Preserve useful work. A subsequent Sol assignment
still requires a concrete benefit from separate context or independent work;
avoid cycling between workers. Reassess clear remaining work for Luna when useful.

## Finish

Review integration behavior, failure paths, unrelated changes, and test gaps.
Resolve verification gaps before acceptance, including work done by the primary.
Run checks appropriate to the assignment and repository-required gates; broaden
checks only for an unresolved risk. Complete corrections within the original task without
silently expanding scope or creating a goal.

Keep commits, pushes, deployment, and other external actions within existing
authorization. Report the outcome, routing rationale, worker and primary
contributions, validation, remaining uncertainty, and repository state.
