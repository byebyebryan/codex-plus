# Worker routing design

Date: 2026-10-06. Status: implemented in the adaptive skills. This note records
the design, candidate validation, and rollout plan. See the
[worker routing study](worker-routing-study.md) for evidence and its limits.

The adaptive workflows should keep more work in the GPT-6.1 Sol XHigh primary
and delegate to GPT-6 Luna Max when the assignment is clear and the expected
savings justify the handoff. A Sol worker serves a separate execution purpose;
it is not a capability escalation when Luna is unsuitable. Keep the design
light enough to generalize across repositories and task shapes.

## Context and motivation

The earlier setup used a Sol primary, Terra for more demanding delegated work,
and Luna Max for cheaper work. Terra is no longer part of the current default
bundle. Replacing that worker tier with another Sol agent preserves the names
of the routing options without preserving their original rationale.

The user's working premise is that GPT-6.1 Sol is now more affordable while
Luna remains substantially cheaper. These are preferences for the routing
design, not a measured price comparison in this repository. With a smaller
perceived cost penalty for primary execution, context transfer, review,
corrections, and coordination deserve more weight.

The earlier adaptive instructions repeatedly said "Luna by default." That can
encourage delegation before its benefit is established. The intended shift is
toward delegating work we can confidently assign and verify, while keeping
uncertain or closely connected work in the primary.

## Preserve the Luna workflows

Keep the `luna-max` agent, `$luna-task`, and `$luna-goal-loop` model choices and
basic behavior. An explicit Luna workflow expresses the user's preference
for Luna delegation. The primary still resolves decisions and difficult
portions, reviews the result, and may finish a small remainder directly.

Any polish should improve clarity without importing the adaptive workflow's
new threshold for delegation or silently introducing another delegated model.

## Adaptive routing

Use this as the core policy for `$worker-task` and `$worker-goal-loop`:

> Keep work in the primary when the benefit of delegation is uncertain.
> Delegate to Luna when the objective, responsibility boundary, and acceptance
> check are clear, and the expected savings justify packaging, review, and
> possible corrections. Reassess each assignment independently.

Confidence concerns the assignment and verification. Luna can choose ordinary
implementation details and investigate a well-defined question. The primary
does not need to solve the task before delegating it, and substantial work can
qualify when its outcome and boundaries are sound. If preparing a handoff would
require doing most of the task, the primary can finish directly.

Useful examples, rather than a fixed classification scheme:

| Assignment | Likely route and reason |
| --- | --- |
| Localized fix with a reproducer and a clear acceptance check | Luna can complete and verify a bounded slice. |
| Specified migration or repeated edits following an established pattern | Luna can save effort while preserving explicit invariants. |
| Focused investigation with a specific question and evidence to return | Luna can gather facts without being authorized to implement. |
| Evolving diagnosis or closely connected decisions and changes | The primary retains the context and resolves uncertainty. |
| Unclear verification or a small remainder already understood by the primary | The primary can finish without adding a handoff. |

Estimate the cost of reaching an accepted result, including primary and worker
effort. Do not hardcode a price ratio, a delegation quota, or a task-size cutoff.
Complexity labels, file count, migrations, or unfamiliarity alone do not decide
the route.

## Sol workers as an execution choice

Separate model selection from the decision to create another execution context.
When Luna is not a confident fit, the normal route is primary execution. Another
Sol agent with the same model and reasoning effort does not add a stronger
model tier.

Keep `sol-xhigh` available when independent execution has a concrete benefit:
parallel work with separable responsibilities, an investigation whose large
intermediate output can be distilled, or a deliberately independent review.
Each still incurs a handoff and primary acceptance work. Separate files can
still depend on shared decisions, so file ownership alone does not establish
independence. An independent review is an additional perspective, not a
guarantee against shared model errors; findings should point to actual evidence.

Difficulty alone should not spawn a Sol worker. Merely invoking an adaptive
worker workflow should not imply a request for parallel execution. Sol-worker
uses belong in a separate, secondary part of the workflow rather than the
ordinary primary-versus-Luna routing menu.

## Explicit activation

Activate the adaptive skills through `$worker-task`, `$worker-goal-loop`, or an
explicit request to use the named skill. Generic requests for a "task," "goal,"
or "goal loop" should use the ordinary workflow. Discussing or editing a skill
does not activate its execution workflow.

Both adaptive skills already set `policy.allow_implicit_invocation: false` in
`agents/openai.yaml`, and their descriptions already require explicit use.
The installed copies on Snap matched those policies during the context review.
The reported unintended activation is therefore not explained by a missing
flag in the inspected files. Reinforce the descriptions and opening rules,
validate the policy, and check behavior in fresh sessions before calling the
runtime issue resolved.

Candidate testing also exposed implicit Luna activation on a generic goal-loop
request. The Luna goal-loop description and opening rule now explicitly require
a Luna request. Its supported invocation forms and implicit-discovery setting
remain unchanged; a request for a loop with Luna can still select it.

## Keep orchestration light

The user has previously tried OMC/OMA-style heavy orchestration and found that
increasing prescription harmed generalization. This refinement should use a
few decision rules, compact assignments, proportionate verification, and clear
ownership. Preserve room for the primary and workers to exercise judgment.
Compact assignments should carry sufficient context and point to authoritative
artifacts. Review the decomposition as well as individual worker results.

Avoid turning these skills into a workflow engine with fixed role graphs,
scoring systems, mandatory handoffs, or long task-classification playbooks.
Research may justify a narrow refinement; it should not become a reason to
accumulate instructions for every observed edge case.

## Research and acceptance

Study existing work on selective model routing, the overhead and benefits of
multi-agent execution, context isolation, independent review, and simple agent
designs. Distinguish controlled experiments, practitioner experience, official
product behavior, and our own design inferences. Translate useful findings into
a small number of rules that fit this kit.

Before implementing, assess representative cases: a clear Luna slice, evolving
diagnosis, a substantial but specified migration, a small primary remainder,
separable parallel work, and noisy investigation. For activation, distinguish
a generic goal-loop request, an explicit adaptive invocation, an explicit Luna
invocation, and a discussion about refining a skill.

Static validation can cover inventory, metadata, and invocation policy. Actual
routing quality, activation behavior, cost, and elapsed time require runtime
evidence; the online study does not substitute for those checks.

## Implementation and deployment plan

Planning baseline on 2026-10-06: the kit is at published commit `75eef78` with
the design, research, README, and inventory changes still uncommitted. Snap and
Starship both select the same published kit and GPT-6.1 Sol XHigh defaults.
Snap's live Codex config disables all four current skills through local
`skills.config` entries; Starship has no such entries. Those entries are local
state preserved by the chezmoi modify template, rather than shared defaults.
The user subsequently authorized enabling all four on Snap. Keep installed
skills enabled by default without overriding unrelated local disable preferences;
adaptive invocation remains explicit-only.

Snap's chezmoi branch also has two unpublished Agent Observer commits
(`3afe42e` and `66fbdd3`), while Starship's source checkout has unrelated worktree
changes. Preserve their history and edits. Refresh this baseline before release.

### Refine the kit

Update `skills/worker-task/SKILL.md` and
`skills/worker-goal-loop/SKILL.md` together. Make primary execution and selective
Luna delegation the ordinary choices. Move Sol-worker use into a separate
section with a concrete independent-execution benefit. Keep assignment,
ownership transfer, proportionate correction, and primary acceptance clear.

Align the two adaptive descriptions and `agents/openai.yaml` prompts with that
policy. Put the explicit named-skill trigger first and distinguish ordinary
goal loops and discussions of the skill. Preserve the existing
`allow_implicit_invocation: false` policy.

Polish the Luna workflows only where clearer context or review wording helps;
preserve their model choice and activation semantics. Clarify the
`sol-xhigh` agent description around independent execution. Keep the current
agent names, model and effort pins, and legacy compatibility boundary.

Update README routing guidance and the design status to match the resulting
behavior. Keep the research available as supporting material; do not require
every task to load it.

### Validate the candidate

Extend `scripts/check` to validate the adaptive invocation policy and the named
skill in each UI default prompt, without testing exact prose or adding a new
dependency. Run the repository gate, relevant skill validation, and
`git diff --check`; review the complete intended patch.

Use a small set of isolated fresh-session probes for activation and behavior.
Include ordinary goal-loop wording, discussion of a skill, explicit adaptive
invocation, and explicit Luna use. For routing, include a substantial clear
slice, a focused investigation, evolving diagnosis, a small primary remainder,
and work with shared decisions. Verify actual selected models when a worker
runs. A justified primary route is acceptable when handoff overhead dominates;
the probes should not enforce a delegation quota.

Judge accepted outcomes and observed routing, and retain usage and elapsed time
when the runtime supplies them. These smoke checks establish a small behavioral
sample, not a universal savings claim or a statistically optimized threshold.

### Publish the kit

Stage only the intended kit changes, inspect the staged patch and remote
divergence, then commit and publish the release. Download the archive and agent
files for the exact published commit. Verify their contents against the release
source and compute checksums from the fetched bytes.

### Update chezmoi

Use a clean release checkout based on the current published dotfiles branch
to prepare the pin update without bundling Snap's unpublished Observer commits.
Update `.chezmoiexternals/codex-plus.toml` and the matching expectations
in the dotfiles `scripts/check` together. All seven external entries should
select the published kit commit; archive and agent-file checksums should match
the fetched artifacts. Retain regular materialized files and directories.

Run the dotfiles gate, inspect the staged changes, and publish the focused pin
update. Integrate that update into each canonical source checkout while
preserving Snap's existing commits and Starship's unrelated edits. Do not reset
those checkouts or publish their unrelated work as part of this release.

### Deploy on Snap and Starship

Deploy on Snap first. Review scoped `chezmoi status` and `chezmoi diff`, refresh
the external cache, and perform a scoped dry-run. Apply only these kit targets
after the reviewed dry-run succeeds:

- `~/.local/share/codex-worker-kit`
- `~/.codex/agents/luna-max.toml` and `~/.codex/agents/sol-xhigh.toml`
- `~/.codex/skills/luna-task` and `~/.codex/skills/luna-goal-loop`
- `~/.codex/skills/worker-task` and `~/.codex/skills/worker-goal-loop`

Verify exact installed inventory and byte identity against the published
release, including the invocation metadata. Confirm the two agent model/effort
selections, skill discovery, and absence of skill-loading errors in a fresh
client. Make the targeted enablement change if the user chooses to re-enable
Snap's skills; preserve all unrelated skill-disable entries and local config.
Check that a subsequent chezmoi render preserves that selected runtime state.

Repeat the scoped rollout and installation checks on Starship, preserving its
source and live drift. Confirm both hosts select the same kit release and
expected activation rules. Do not apply unrelated Codex or desktop settings.

### Accept or roll back

Acceptance requires passing source checks, published artifact identity, matching
materialized targets on both hosts, and fresh-client activation evidence. Report
the behavioral sample and its limits separately from installation success.
Preserve active work and use fresh sessions for validation.

If a release gate fails, correct the candidate before advancing. If deployment
needs rollback, restore the prior external pin and checker expectations and
reapply the same scoped targets. Restore any enablement state changed by this
rollout. Report exact kit and dotfiles commits, host results, and remaining
repository divergence.

## Candidate verification

On 2026-10-06, the repository gate passed for the 20-file bundle, including
unchanged model/effort pins and legacy compatibility files. The three edited
skills passed skill validation. Isolated negative checks rejected enabled or
missing adaptive invocation policy, a policy placed in the wrong block, and
incorrect skill references in UI prompts. Repository Markdown links resolved.

Fresh-client discovery found all four candidate skills enabled with no skill
loading errors. Read-only behavioral smoke checks used a 600-event JSON fixture
with 85 failures and 200 events for each of three owners:

- Explicit `$worker-task` completed the audit in the primary and explained that
  this small assignment did not justify a handoff.
- A design discussion about `worker-goal-loop` returned advice without starting
  an execution workflow.
- The initial generic goal-loop request incorrectly selected `luna-goal-loop`.
  After narrowing its activation wording, a fresh repeat completed directly in
  the primary without selecting a worker skill or delegating.
- Explicit `$luna-task` delegated the audit and the primary verified the result
  and unchanged fixture. A persistent follow-up run recorded the primary as
  `gpt-6.1-sol` at `xhigh` and its `luna-max` child as `gpt-6-luna` at `max`.

The ephemeral goal-loop probes could not exercise persistent goal tools. Host
acceptance should check goal management in a persistent fresh session. This
small sample does not establish a general savings rate, an optimal routing
threshold, or performance on large implementation and parallel Sol assignments.
