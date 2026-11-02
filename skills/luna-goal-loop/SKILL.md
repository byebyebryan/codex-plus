---
name: luna-goal-loop
description: Use when the user invokes $luna-goal-loop or explicitly requests a loop with Luna. A generic goal loop without a Luna request does not activate this skill. Run a substantial goal with luna-max for bounded investigation and implementation; the primary owns decisions, difficult portions, and review. Luna is the only delegated model.
---

# Luna Goal Loop

Activate through `$luna-goal-loop` or an explicit request for a loop with Luna.
A generic "goal loop" without a Luna request uses the ordinary workflow.
Discussing or editing this skill does not activate its execution workflow.

Keep the current primary responsible for decisions, integration, and acceptance;
the intended setup is Sol XHigh. Use Luna Max for useful bounded investigation
and implementation throughout the goal. This skill does not change the primary
model. Do not start a goal loop implicitly for a trivial task.

## Establish readiness and the goal

Inspect the requested outcome, repository instructions, worktree, authoritative
design, invariants, and exit gate. Resolve ordinary technical decisions in the
primary within the user's scope. Ask the user only for a missing preference,
product choice, or authorization that materially affects the work.

If facts are missing, a bounded Luna investigation can trace code, reproduce a
failure, or propose options. Specify the question and evidence needed; an
investigation does not authorize implementation edits. Start an implementation
writer only when the slice's intended behavior and invariants are settled.
Individual coding steps need not be predetermined.

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

If Luna genuinely cannot be used, report that limitation without claiming a Luna
assignment or loop ran; do not silently substitute another delegated model.
When execution is ready and goal tools are available, create the explicitly
requested goal or continue a matching active goal. Report a conflicting active
goal instead of replacing it. Do not invent a token budget. If the user has not
requested a goal, do not create one merely because this skill was discovered.

## Package each assignment

Choose the largest cohesive assignment with a practical acceptance check that
one worker can complete without an unresolved product or architecture decision.
Bound it by reviewable behavior and responsibility, not a small file count.
Give the worker a compact, self-contained contract containing:

- investigation or implementation mode, objective, and observable outcome;
- owned files or responsibility, with unrelated changes to preserve;
- invariants, non-goals, and authoritative context to inspect;
- the acceptance check and proportionate validation; and
- unresolved decisions or conditions to return to the primary.

Call the declared native spawn control directly with `agent_type="luna-max"`
and `fork_turns="none"` for the self-contained contract. Honor the declared
client schema and role/model rules; a task label alone does not select Luna. Use one writer by default, reuse
it for related corrections, and do not duplicate its implementation. Use parallel
assignments only when independent responsibilities justify their overhead.

## Review and resolve difficulty

At meaningful boundaries, inspect actual findings or diffs and focused
validation. Review invariants, integration behavior, failure paths, unrelated
changes, and test gaps. Send ordinary defects back as bounded corrections.

Return an unresolved decision, missing verification, contradictory evidence, or
repeated failure without new evidence to the primary. Migrations, concurrency,
security, cross-module behavior, or file count alone do not disqualify Luna.
The primary may resolve or implement the difficult portion and hand clear
remaining work back to Luna, or finish the slice directly when another handoff
adds no value. Explain the takeover and continue the authorized goal; do not
pause merely to ask the user to select another workflow.

Before the primary edits worker-owned files, obtain the handoff or stop the
writer and inspect partial changes. Preserve useful work. Luna remains the only
delegated model; do not introduce a Sol, Terra, or Astra worker under this skill.
Reassess the next slice independently so a primary takeover does not displace
Luna from later suitable work.

## Close the loop

Perform an overall contract review after integration. Complete remaining fixes
and resolve verification gaps, including in work done by the primary. Run the
repository's required final gate. Avoid repeated full-suite runs
unless a change or unresolved risk justifies them. Keep commits, pushes,
deployment, and roadmap changes within existing authorization.

Mark the goal complete only when the outcome and exit gate are satisfied with
no required work remaining. Otherwise follow the goal tool's blocking rules;
do not mark an active goal paused without a user request. Report the outcome,
Luna and primary contributions, validation, remaining uncertainty, and repository
state. Include total usage or cost only when the runtime provides it.
