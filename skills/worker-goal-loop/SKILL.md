---
name: worker-goal-loop
description: Use only when the user invokes $worker-goal-loop or explicitly asks to use the worker-goal-loop skill. Run a substantial goal in the primary, selectively delegating clear, verifiable assignments to Luna. Sol workers need an independent execution benefit. A generic goal loop or discussion of the skill does not activate it.
---

# Worker Goal Loop

Activate only through `$worker-goal-loop` or an explicit request to use this
named skill. A generic "goal loop" uses the ordinary workflow; discussing or
editing this skill does not activate it.

Keep the current primary responsible for decisions, integration, and acceptance;
the intended setup is Sol XHigh with selective Luna Max delegation. Route each
assignment independently. This skill does not change the primary model.

## Establish readiness and the goal

Inspect the requested outcome, repository instructions, worktree, authoritative
design, invariants, and exit gate. Resolve ordinary technical decisions in the
primary within the user's scope. Ask the user only for a missing preference,
product choice, or authorization that materially affects the work.

When facts are missing, use bounded investigation to trace code, reproduce a
failure, or propose options. Specify the question and evidence needed; an
investigation does not authorize implementation edits. Start an implementation
writer only when the slice's intended behavior and invariants are settled.
Individual coding steps need not be predetermined.

When execution is ready and goal tools are available, create the explicitly
requested goal or continue a matching active goal. Report a conflicting active
goal instead of replacing it. Do not invent a token budget.

## Route each assignment

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
not decide the route. Do not require a failed Luna attempt before using the
primary, or impose a delegation quota. Reassess each assignment on its own merits.

## Use Sol workers for independent execution

Use `sol-xhigh` only when another execution context has a concrete benefit:
separable parallel work, an investigation with large intermediate output that
can be distilled, or an independent review. State that benefit and account for
handoff and acceptance effort. Difficulty beyond Luna normally stays in the
primary; another Sol worker is not a stronger model tier.

Separate files may still share decisions. Establish independence before parallel
writes, and require review findings to point to evidence rather than treating
another same-model opinion as verification. Invoking this workflow does not by
itself request parallel execution. Do not route automatically to Terra or Astra.

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

## Package and delegate

Choose the largest cohesive assignment that one worker can complete within its
decision boundary and that can be independently reviewed. Give it a compact,
self-contained contract containing:

- investigation or implementation mode, objective, and observable outcome;
- owned files or responsibility, with unrelated changes to preserve;
- invariants, non-goals, and authoritative context to inspect;
- the acceptance check and proportionate validation; and
- unresolved decisions or conditions to return to the primary.

Call the declared native spawn control directly, explicitly selecting the
named role: for Luna, use `agent_type="luna-max"` and `fork_turns="none"` for the
self-contained contract. Select `sol-xhigh` only under the existing independent-
execution rule. Honor the declared client schema and role/model rules; a task
label is not role selection. Use one writer by default and
reuse it for related corrections. Do not duplicate its implementation. Use parallel
assignments only when independent responsibilities justify their overhead.

## Review and recover

At meaningful boundaries, inspect actual findings or diffs and focused
validation. Review invariants, integration behavior, failure paths, unrelated
changes, and test gaps. Send ordinary defects back as bounded corrections.

If the same failure repeats without new evidence, or a decision or verification
gap emerges, have the primary diagnose or take over the difficult portion.
Before changing write ownership, obtain the handoff or stop the writer and
inspect partial changes. Preserve useful work. A subsequent Sol assignment
still requires a benefit from separate context or independent work; avoid
cycling between workers. Return clear remaining work to Luna when useful.

Reassess the next slice independently; earlier primary or worker use does not
dictate later routing. Continue the authorized goal without
pausing merely to ask the user to choose another workflow.

## Close the loop

Perform an overall contract review after integration. Complete remaining fixes
and resolve verification gaps, including in work done by the primary. Run the
repository's required final gate. Avoid repeated full-suite runs
unless a change or unresolved risk justifies them. Keep commits, pushes,
deployment, and roadmap changes within existing authorization.

Mark the goal complete only when the outcome and exit gate are satisfied with
no required work remaining. Otherwise follow the goal tool's blocking rules;
do not mark an active goal paused without a user request. Report the outcome,
routing rationale, worker and primary contributions, validation, remaining
uncertainty, and repository state. Include total usage or cost only when the
runtime provides it.
