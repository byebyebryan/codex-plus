---
name: terra-task
description: Delegate one bounded task to GPT-6.1 Terra XHigh only when the user invokes $terra-task or explicitly asks to use this named skill. Skill discussion does not activate it.
---

# Terra Task

Use this workflow only when the user explicitly invokes `$terra-task` or asks to
use this named skill. A direct native worker request without this skill is a
separate action. A generic task request, automatic escalation choice, or
discussion or editing of this skill does not activate it. Select Terra without
primary-model metadata or adaptive escalation opt-in, while honoring applicable
restrictions and native permissions. Keep the current primary, thread, native
owner, and model unchanged. Do not create or manage a goal. This invocation
authorizes only the requested task; it creates no persistent escalation
preference.

This current workflow selects GPT-6.1 Terra. The separate legacy `terra-task`
selects GPT-5.6 through `terra-xhigh`; do not load both skill variants or treat
the legacy role as a substitute. If the chosen variant is unclear, resolve
that choice before delegating.

## Set the assignment

Follow the mode selected by the user's request:

- **Review or validation:** report findings and evidence without implementation
  or source fixes. Validation may create ordinary temporary or build outputs
  under inherited native permissions; do not claim a read-only sandbox.
- **Investigation:** return findings, evidence, and useful options without
  implementation edits or source fixes.
- **Implementation:** require explicit write ownership. Include the owned files
  or responsibility, observable outcome, acceptance check, relevant context,
  invariants, and non-goals in the assignment.

Do not expand the user's scope or infer write authority from a review,
validation, or investigation request. Settle material permission or task-choice
ambiguity before delegation. A bounded investigation can gather missing facts;
the primary need not solve the question before assigning it.

For every mode, give the worker a compact, self-contained contract with the
mode, objective, observable outcome, responsibility boundary, relevant
authoritative context, invariants, non-goals, acceptance check, and unresolved
conditions. Preserve concurrent edits. For implementation, state the exact
files or responsibility the worker may change; do not infer write ownership.

## Delegate to Terra XHigh

Inspect the declared native collaboration controls and available custom-agent
roles before deciding delegation is unavailable. Call native controls directly
in their declared namespace, outside `functions.exec`; collaboration controls
are not exposed through Code Mode's `tools.*` namespace or `ALL_TOOLS`, so an
empty registry is not evidence that they are missing. A working control does
not prove the requested role or model can run.

Select exactly `terra-6-1-xhigh`, with its existing pinned model and reasoning effort,
and pass a compact, self-contained assignment using native
`collaboration.spawn_agent` with `agent_type="terra-6-1-xhigh"` and
`fork_turns="none"`. Do not infer role availability from the skill name. If the
role is absent or its pin differs from `gpt-6.1-terra` with `xhigh` reasoning,
do not attempt a substitute; report that no delegation was attempted and why.
If the actual spawn is rejected, report the spawn failure. If a worker starts
but encounters an execution error, report that separately. Check available
native result metadata for the selected role, model, and effort; report a
reroute or unavailable evidence accurately rather than relying on the worker's
self-description.

Never silently replace Terra with another worker, perform a second Codex launch,
switch provider or billing, change native permissions or MCP configuration, or
recommend a daemon restart as a workaround. The child receives no authority to
delegate onward.

## Review and finish

Check available native completed-turn state and inspect the actual worker
result, changes, outputs, and validation evidence before claiming the task ran
or completed. A successful spawn or available role alone is not completion
evidence. Reuse the same worker for bounded corrections within the original
assignment. The primary owns decisions, integration, and acceptance. It may
take over implementation only within the user's original write authority, and
must disclose that takeover. If Terra does not complete a requested review,
validation, or investigation, report that named assignment as unmet; separate
primary checks must be labeled and do not satisfy the named-worker request.
Accept the result or report the evidence, validation, actual role/model
information available, and any remaining uncertainty. Do not claim Terra
execution from static skill or archive validation alone.
