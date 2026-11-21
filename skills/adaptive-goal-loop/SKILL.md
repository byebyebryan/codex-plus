---
name: adaptive-goal-loop
description: Use only when the user invokes $adaptive-goal-loop or explicitly asks to use the adaptive-goal-loop skill. Run a substantial goal in the primary, selectively delegating clear, verifiable assignments to Luna. Sol/Terra primaries can escalate to Astra. An Astra primary can delegate to Sol on opt-in. A generic goal loop or discussion of the skill does not activate it.
---

# Adaptive Goal Loop

Activate only through `$adaptive-goal-loop` or an explicit request to use this
named skill. A generic "goal loop" uses the ordinary workflow; discussing or
editing this skill does not activate it.

Keep the current primary responsible for decisions, integration, and acceptance.
Use Luna Max for suitable handoffs. The primary-specific policy below may allow
one additional worker for a justified assignment.
Route each assignment independently. This skill does not change the primary model.

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

For a known Sol primary, if `codex-plus-diagnostics` is installed, run
`codex-plus-diagnostics enroll --if-open --routing-not-started` before routing a new goal. This is a no-op without an
already opened private study; never start or extend one implicitly. If enrolled,
retain the returned episode identity and keep the Sol/Luna baseline for that
episode. A separately authorized exception is recorded as a policy deviation.
Use the helper's `link` command to record
meaningful retained work, Luna attempts (including missing controls or failed
spawns), native thread/turn identities and private contract/review references.
An exact returned native task path can use `link --worker`; ambiguity requires
explicit identities instead of guessing.
Record first-result review separately from final acceptance. At closure, use
`outcome` for actual review, repair/takeover and user intervention; attest child
coverage only after checking it. Missing evidence stays unknown. These records
change no routing permission. For an enrolled goal, keep useful work moving and
report gaps if the helper or telemetry becomes unavailable. Read subcommand `--help` or the
[operator guide](https://dev.byebyebryan.com/codex-plus/routing-diagnostics/)
only for an enrolled goal.

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

## Resolve worker eligibility

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
| Supported Astra family | None | Sol XHigh delegation under the opt-in below |
| Luna, other or unknown | None | None |

With an Astra primary, direct work and Luna are the default. Allow Sol only
when the user permits this route for the current scope or an eligible private
study assignment returns arm B. Apply direct-only, Luna-only, named assignments,
exclusions and study restrictions first. An explicit named review covers that
review and its corrections. Recheck permission at each new assignment.

Give Sol a cohesive outcome and acceptance check when consequential local
decisions remain and independent judgment is likely to save Astra execution
or repair. State which decisions Sol owns and which it should return. Prefer
Luna if it can meet the same check with comparable supervision. Keep work in
Astra if the finding could change the goal or if acceptance would repeat the
investigation. Sol can take the first assignment. Astra accepts the result.

For ordinary unrestricted work with a known Astra primary and the diagnostics
helper installed, run this before decomposition or routing. Supply the actual
acceptance check.

```sh
codex-plus-diagnostics astra-study assign --workflow goal --check "prospective acceptance check"
```

Skip setup, probes, replays, already-routed work and requests
that prescribe a worker or policy. Keep continuations in their existing study
and arm, including through a primary change. Never count one context in both
studies. In the Astra study, A permits Astra/Luna. B also permits Sol. If no assignment is returned,
use the normal request policy. A closed or unavailable helper grants no new
permission. For a continuing B context, recheck its assignment before a new
Sol handoff after a pause. A final outcome or expired follow-up ends study
permission. Keep later overrides and failed attempts in the assigned arm.

In an enrolled context use `codex-plus-diagnostics astra-study note --text "…"`
at routing and first return. Add `--final` to the closing outcome note.
Record owner and reason, the alternative to a Sol handoff,
observed role/model/effort, first return, repairs, takeover, final acceptance
and any user rescue. Include the scoped usage snapshot or a private reference
when available. Keep missing evidence unknown. See the
[operator guide](https://dev.byebyebryan.com/codex-plus/routing-diagnostics/#astra-primary-daily-study).

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

## Package and delegate

Choose the largest cohesive assignment that one worker can complete within its
decision boundary and that can be independently reviewed. Give it a compact,
self-contained contract containing:

- investigation or implementation mode, objective, and observable outcome;
- owned files or responsibility, with unrelated changes to preserve;
- invariants, non-goals, and authoritative context to inspect;
- the acceptance check and proportionate validation; and
- unresolved decisions or conditions to return to the primary, including an
  explicit prohibition on nested delegation.

An investigation or review returns findings and evidence without implementation
edits. Implementation requires explicit write ownership. Call the declared
native spawn control directly, explicitly selecting the
named role: for Luna, use `agent_type="luna-max"` and `fork_turns="none"` for the
self-contained contract. For an opted-in Astra-to-Sol handoff select `sol-xhigh` with
`fork_turns="none"`. For escalation select exactly `sol-xhigh`
or `astra-xhigh` as resolved above, also with `fork_turns="none"`. Honor the
declared client schema and role/model rules; a task label is not role selection. Use one writer by default and
reuse it for related corrections. Do not duplicate its implementation. Use parallel
assignments only when independent responsibilities justify their overhead.

## Review and recover

Check completed-turn state and available native worker model/effort metadata
before claiming the selected target ran. Keep unavailable selection evidence
explicit while reviewing any useful result; role installation alone is not
completed execution.

At meaningful boundaries, inspect actual findings or diffs and focused
validation. Review invariants, integration behavior, failure paths, unrelated
changes, and test gaps. Send ordinary defects back as bounded corrections.

If the same failure repeats without new evidence, or a decision or verification
gap emerges, have the primary diagnose or take over the difficult portion.
Before changing write ownership, obtain the handoff or stop the writer and
inspect partial changes. Preserve useful work. A subsequent escalation still requires the selected
target and a concrete benefit; avoid cycling between workers. Return clear
remaining work to Luna when useful.

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
validation, remaining uncertainty, and repository state. Briefly say what
the primary and each worker actually did and why delegation was useful. Use
observed model/effort where available and label unknown attribution. For
primary-only work, a short line is enough.

When available, take one `codex-plus-diagnostics usage` snapshot near finish.
Pass `--worker PATH` for each exact native collaboration task path used under
the current native root. Add observed per-model token counts when useful.
Label partial counts, including the active primary turn. If the goal spans
several native roots, identify the snapshot as current-root usage. Use broader
counts only when their scope is verified, for example from an enrolled episode.
Cached input is part of input. Treat counts as tokens only. The snapshot needs
no study. If telemetry is unavailable, finish with the contribution summary.
