# Worker routing design

Updated 2026-11-05. Preview.15 implements the selected primary/Luna/optional
escalation policy below. Existing installations need an explicit upgrade. See the
[qualification record](worker-escalation-results.md) for native evidence and limits;
the [worker routing study](worker-routing-study.md) records the research history.

Preview.17 retains the canonical `$adaptive-task` and `$adaptive-goal-loop`
names and removes the worker-name compatibility entries introduced in preview.16.
The policy, Luna workflows and native role pins are unchanged.
Historical trial names and installation receipts below retain their original
identities; use the [current worker guide](https://github.com/byebyebryan/codex-plus/blob/main/docs/workers.md)
for release availability, the seven workflows and migration procedure.

## Explicit named tasks: preview.18

`$sol-task` and `$astra-task` select the existing `sol-xhigh` and `astra-xhigh`
roles for one bounded assignment. `$terra-task` extends the same contract using
the new `terra-6-1-xhigh` role, pinned to `gpt-6.1-terra` / `xhigh`. Legacy
`terra-xhigh` and its GPT-5.6 task remain unchanged under `legacy/`; choose only
one task variant because both use `$terra-task`. They are explicit-only task frontends, not
new routing tiers or automatic escalation policy. The request selects review,
investigation or implementation; review/validation returns evidence without
implementation edits, while implementation requires write ownership. The primary
retains decisions, integration and acceptance. Task invocation creates no goal.

An explicit named assignment needs neither reliable initiating-primary metadata
nor an automatic escalation grant. It works with any primary subject to native
permissions, exposed role pins and applicable restrictions. It authorizes only
that assignment and bounded corrections, not future automatic selection. Preserve
the provider/MCP environment and exact role selection, with no silent alternative,
nested delegation or restart/process workaround. Report missing controls/roles,
pin conflicts, rejected spawning, execution errors and observed reroutes distinctly.

Keep both skills self-contained, use direct native collaboration calls and
`fork_turns="none"`, and check completed-turn state and available selection
metadata before claiming the target ran. Review mode constrains the assignment;
it does not change inherited permissions or enforce a read-only sandbox.

No model-specific goal loops, review configuration switch, service or mandatory
review step is needed. Terra's versioned role prevents legacy role confusion;
it adds no automatic Terra routing option. Existing adaptive loops can receive an explicit
named-review instruction without granting implementation escalation. Preserve
all four existing skill bodies and native role files byte-for-byte. Preview.18
packages seven workflows and four current roles. Source, published archives,
managed installation and native execution must be verified separately. Use the
selected release's manifest rather than assuming an existing installation updated.
The new current-Terra role is not exposed in this session; do not infer execution
from its source pin or silently use legacy Terra, another worker or a process/
restart workaround. Migration must select a variant through the configuration
owner, preserving local edits and restrictions instead of merging skill roots.

## Selected design: primary, Luna and one escalation target

Use three operating tiers: high = Astra, mid = Sol/Terra, low = Luna. These are
workflow categories, not a proven universal capability ranking. The user picks
the native primary and its reasoning setting for the project. Routine adaptive
routing chooses direct primary work, a useful Luna assignment, or one explicitly
configured escalation target. No quality/balanced/economy selector belongs to V1.

### Routes and defaults

| Initiating primary | Optional automatic escalation target | Default |
| --- | --- | --- |
| GPT-6.1 Terra | Sol XHigh or Astra XHigh, exactly one | None |
| GPT-6.1 Sol | Astra XHigh | None |
| GPT-6 Astra | None in V1 | None |
| Luna, another model or unknown identity | None in V1; explicit user assignments remain separate | None |

Luna Max remains available for cohesive, bounded, verifiable assignments in
every supported workflow. Such work can be substantial implementation or
investigation; do not reduce it to tiny chores or require delegation when a
handoff adds little. An equivalent Luna primary/worker pair still needs a
benefit from separate execution. The continuing primary owns decisions,
integration and acceptance and never switches itself to the escalation model.

Do not automatically delegate Sol-primary work to Terra for nominal savings,
or escalate Terra-primary work to Sol by default. The user can enable the latter
when a second opinion or additional help is useful. Reviews, investigations
and demanding implementation slices all use the same escalation option; they
need no separate review toggle or obligatory review stage. Higher price alone
does not establish a capability improvement.

One target is a model choice, not a one-call quota. Reuse the selected worker
for ordinary bounded corrections when useful. A Terra-to-Sol selection grants
no implicit Sol-to-Astra chain: children return unresolved gaps to the original
primary and do not reapply their own model as a new primary policy. Only the
user's actual primary/configuration change can select a different route later.

### Configure through existing native instruction mechanisms

Keep [native agent files](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
authoritative for model/effort pins. Express the
optional escalation policy in an explicit adaptive request or applicable user
guidance, defaulting to none when unset. A current request can override a soft
default for its task; distinct restrictions, scope and native permissions still
apply. No new native TOML keys, preference file or configuration hierarchy are
needed for the first candidate. Later persistent instructions remain chezmoi
owned and are changed only in their canonical source within deployment scope.

An opt-in instruction example, not an installed setting:

> In explicitly invoked adaptive worker workflows, allow Sol XHigh escalation
> when the initiating primary is GPT-6.1 Terra, and Astra XHigh when it is
> GPT-6.1 Sol. Otherwise use no automatic escalation. Keep Luna available for
> useful bounded assignments.

Resolve policy for the actual initiating primary, rather than a guessed host
default. Re-read at new assignment boundaries. Existing children retain their
contracts, settings and write ownership when the user changes the primary or
guidance. Explicitly enabling a target authorizes suitable assignments within
the task without a permission question for every spawn; it starts no work and
does not itself invoke a skill. Disabling a target prevents new assignments,
while handling an active child follows the user's stop/ownership instructions.

Native loaded-thread metadata is the qualified primary source. The preview.15
read-only helper supplies loaded-thread selection; a config default or model
self-description is not an identity substitute. If trustworthy metadata is
unavailable, use primary/Luna and report automatic escalation as held. An
explicit user assignment to a named worker can still be honored within normal
constraints without pretending primary detection succeeded. Worker-only
installations keep their existing usefulness and gain no monitoring dependency.

### Native execution, availability and failure handling

The worker roles are `luna-max` (existing), `sol-xhigh` (existing), and
`astra-xhigh` (added in preview.15). Preserve the
existing named roles and legacy compatibility files. Terra remains a normal
supported native primary; this policy needs no automatic Terra worker role.
Role installation/declaration, account access and completed inference remain
different evidence. General Terra support is not removed by this host's failure.

Inspect actual native declarations, then call collaboration controls directly,
outside `functions.exec`/`ALL_TOOLS`. An empty Code Mode registry excludes no
native control. Select the exact configured role and `fork_turns="none"` with a
self-contained contract. Honor role pin precedence; do not pretend an override
changed a fixed model or effort. All children inherit the parent provider,
permissions and MCP environment, and receive no nested-delegation authority.

A compatible exposed route can receive its first useful authorized assignment
without a diagnostic probe. Keep missing controls/roles, an actual rejected
spawn, model errors and observed reroutes distinct. If the configured target
cannot run, preserve its error and useful partial work, then continue in the
primary where feasible or report the unresolved gap. Do not silently select a
different target, change billing/provider, launch another Codex process or
suggest a daemon restart. No automatic fallback ladder is part of this policy.

Keep compact assignments and proportionate review. Review mode normally asks
for findings and evidence without edits; implementation mode has explicit write
ownership and acceptance. Stop or obtain a handoff before transferring a live
writer's files. Escalation needs a concrete unresolved issue or useful second
opinion, not a failed cheap attempt or a model-price comparison alone.

Explicit `$luna-task` and `$luna-goal-loop` retain Luna as their only delegated
model regardless of the escalation policy. Only explicitly invoked adaptive
skills gain the new automatic selection rule. Direct user requests for a named
worker or independent parallel work remain separate native actions within their
existing authority. Generic task/goal-loop wording and skill discussions still
activate no worker skill.

### Qualification and implementation boundaries

| Case | Required result |
| --- | --- |
| Terra/Sol with no target | Primary/Luna only; no inferred Sol/Astra opt-in. |
| Terra with Sol selected | Sol can review or own a bounded slice; Astra is not implicitly authorized. |
| Terra with Astra selected | Use Astra when justified; Sol is not an automatic intermediate step. |
| Sol with Astra selected | Additional help can use Astra for a concrete reason; no Terra cost offload. |
| Astra primary | Direct work/Luna; no automatic mid-tier worker route. |
| Luna/other/unknown primary | Conservative primary/Luna path; no guessed escalation binding. |
| Exact worker identity/effort differs from the target | Report the conflict; do not silently retune, alias or claim the requested selection ran. |
| Native controls exposed despite empty Code Mode search | Discover and call the real native surface directly. |
| Missing control/role, failed spawn or failed model turn | Report the distinct observation and partial result; no concealed fallback target. |
| Configured Sol child sees a Sol-to-Astra default | It remains a child of the Terra task and returns its gap; no recursive chain. |
| Primary or policy changes during a goal | Resolve the next assignment afresh; preserve active workers' contracts and ownership. |
| Explicit Luna workflow or generic goal-loop wording | Keep current invocation and Luna-only delegation rules. |
| Target disabled after spawn | Admit no new target assignments; follow explicit instructions for any active work. |
| Unavailable cost telemetry or strict spend limit | Do not claim exact billing enforcement; retain stated resource constraints. |

These are policy acceptance cases; the [qualification record](worker-escalation-results.md)
identifies which have executed native evidence. The local implementation changes
the two adaptive skills, adds the Astra role and updates guidance/package
validation together. It preserves the Luna skill
identities and fixed selections. Qualify the existing selected-primary helper
and truthful worker-only degradation before making automatic routing claims.

The bounded pilot now uses three worker starts and nine native conversation
turns under the existing 0.166.0 owner. It qualifies Sol-primary/Astra review,
explicit Luna execution, an explicit Sol control, unavailable native controls
and a role-pin conflict. All owned fixtures are settled and archived. See the
[qualification record](worker-escalation-results.md) for accepted results and
which of the case-matrix paths remain conditional. Terra routing stays fixture
coverage until a real Terra primary can execute; another primary using the Sol
role does not prove Terra-primary routing. Known failed Terra access was not
retried. Private captures are outside source, and installed policy is unchanged.

Public capability evidence supplies provisional priors, so a new large local
ranking benchmark is unnecessary. Ordinary-use receipts can later check total
primary/worker effort, corrections and accepted integration. A later release
needs a new selected version and synchronized published-byte/managed-source
pins, preserving live work and chezmoi drift. No universal savings claim follows
from the protocol pilot.

## Shipped policy and earlier research context

The sections below retain the implemented policy and research chronology. The
selected design above is the preview.15 implementation. The sections below are
historical policy and research snapshots; they do not add routes to the selected
policy.

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

Use this as the core policy for `$adaptive-task` and `$adaptive-goal-loop`:

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

Activate the adaptive skills through `$adaptive-task`, `$adaptive-goal-loop`, or an
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

## Native control discovery

Availability is established from the actual native tool declarations and exposed
custom roles. Native collaboration controls are called directly, outside
`functions.exec`, `tools.*` and `ALL_TOOLS`. A Code Mode registry search returning
no matches is not evidence that these controls are missing. A declared native
list control can check that control, but does not prove role availability,
successful spawning or model execution.

For a Luna assignment, explicitly select `agent_type="luna-max"` and
`fork_turns="none"` in the declared native spawn control, with a self-contained
contract. Retain the independent-execution requirement for `sol-xhigh`. Keep
missing controls/roles, an actual spawn failure and worker/model execution errors
separate in the handoff. Report actual errors and partial results; use the
existing primary takeover policy. Do not substitute a different worker, launch
a separate Codex process or suggest a daemon restart as a workaround for this
discovery mistake. If a control or role is genuinely unexposed, report that
specific limitation without claiming an attempted spawn or a model failure.
The runtime still needs to demonstrate the selected worker's actual metadata,
result and handoff.

### Discovery correction validation: 2026-11-01

The four source skills and shared guides now inspect native declarations before
reporting availability and explicitly select the named Luna role with no forked
history. Existing skill frontmatter, invocation metadata, role/model pins and
routing policy are unchanged. No prose-matching regression test was added.

A native Code Mode registry inspection contained no collaboration controls,
while direct native list and spawn calls succeeded. One authorized read-only
Luna probe returned the expected handoff. Independently read native metadata
identified `luna-max`, `gpt-6-luna`, effort `max`, and a completed turn with no
error. The worker correctly classified empty-registry/native-available,
native-unavailable, rejected-spawn and worker-execution-error fixtures. The last
three were tabletop decisions, not injected runtime failures. No implementation
or goal-loop execution was exercised by this small probe.

The earlier combined local candidate passed all four skill validators, a clean
133-file inventory and 382 fixture tests. The focused release excludes the
separate selected-primary/Terra candidate and runs its own source/package gates.
The development checkout's two pre-existing untracked bytecode files remain
preserved. Runtime captures stay outside
committed source. These checks establish a source correction and one local
native handoff, independently of published artifacts and managed installed
skills. Publication and installation are reported separately.

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

## Draft: model-aware routing preferences, 2026-11-02

Superseded as an implementation direction by the
[selected design](#selected-design-primary-luna-and-one-escalation-target).
The quality/balanced/economy selector and general cross-mid-tier dispatch below
are retained as research history, not V1 requirements.

Status: research/design candidate, with no worker-skill, agent, installed-config
or runtime change. The [follow-up research](worker-routing-study.md#follow-up-model-facts-and-routing-preference-2026-11-02)
supports separating facts from preference, but does not qualify routing quality.
This draft supersedes the proposed fixed high/mid/low model assignments as the
next hypothesis to test. It does not replace the active Sol/Luna policy.

### Keep model facts and session choices separate

| Input | What it describes | Authority and limits |
| --- | --- | --- |
| Model profile | Exact provider/model, documented strengths, supported settings, dated cost basis and useful local evidence. | Native metadata supplies supported options; attributed guidance/local results supply strengths. Unknown facts stay unknown. |
| Native eligibility | Exposed controls/roles, current provider/account route, usable settings and any observed execution result. | Runtime/session scoped. A role declaration, catalog entry, successful spawn and completed model turn prove different things. |
| User configuration and preference | Supplied worker-model preferences/exclusions, role/effort pins, resource constraints and high/mid/low preference. | Honor explicit constraints and existing configuration precedence. Preference influences eligible worker choices; it grants no new task authority. Unset preference uses the proposed balanced default. |
| Initiating primary | The model/effort and active context of the conversation invoking the adaptive skill. | Read qualified native metadata. The primary keeps ownership, integration and acceptance; launching the skill does not switch it. |

The route is a choice among eligible model/effort configurations and continuing
in the primary. Keep the user-selected primary in place. Its active context,
remaining work and integration responsibility matter even when another model
has a lower rate. Do not infer the primary from a default config or the model's
self-description; use qualified native metadata or report it as unknown.

### Support four models, with session-specific eligibility

The general design includes GPT-6 Luna, GPT-6.1 Terra, GPT-6.1 Sol and GPT-6
Astra as normal supported model candidates. Current
[official availability guidance](https://learn.chatgpt.com/docs/pricing#feature-availability)
lists Terra for paid Work/Codex plans, with account/workspace and region limits.
Treat Terra availability as an expected supported case in the product design,
while discovering actual access for the invoking session. Bryan's current
Terra omission/failure is a local availability case, not a global exclusion or
evidence that Terra is generally unsupported.

Keep all four profiles in the proposed reference and packaging/validation
matrix. Terra's current model identity is `gpt-6.1-terra`; the preserved legacy
GPT-5.6 Terra role cannot stand in for it. Initial configurations are
Luna Max and Terra/Sol/Astra XHigh, validated against each native route. These
execution settings remain separate from the high/mid/low routing preference.

Build the eligible choices from the general supported candidates, the user's
constraints and current native evidence. A user exclusion, a missing native
role, an unsupported effort and an inference access failure have distinct
meanings; none should rewrite the global model profile. Preserve unknown
availability as unknown. Do not turn this environment's Terra absence into a
shipped universal disable or require every environment to have all four models.

A declared compatible native role/model can receive a real authorized assignment
without a past successful execution receipt. Label its access as unverified
until that assignment returns; the first actual assignment can establish access.
An unknown backend result is not the same as a missing control, an unsupported
model or a demonstrated access failure. No diagnostic inference or catalog
refresh is required before every ordinary task. Report a rejected first attempt
honestly and use primary takeover rather than probing through a model ladder.

### Route relative to the initiating primary

These are illustrative choices when each worker is available, permitted and
useful for the actual task. Model strengths and total accepted-result effort
still govern selection; the price ladder is not a required execution sequence.

| Initiating primary | Useful adaptive options |
| --- | --- |
| Astra | Continue demanding connected work directly; consider Sol, Terra or Luna for useful economical assignments. |
| Sol | Continue ordinary connected work directly; consider Terra or Luna where suitable, and Astra as a focused frontier alternative for a concrete unresolved gap. |
| Terra | Continue ordinary implementation or investigation directly; consider Luna for useful bounded work, or Sol/Astra for a concrete unresolved gap when the expected benefit justifies the handoff. |
| Luna | Continue within the primary's fit; the adaptive workflow can use Terra, Sol or Astra for a justified assignment while the continuing primary owns the task. |

User configuration can narrow or favor these choices. For example, excluding
Astra removes that option even under high preference; a fixed role's effort
pin remains effective; and a Sol primary does not need another Sol worker for
capability escalation. Another same-model context can still serve independent
execution. Changing the primary through the user's normal model selection
changes the next routing context without requiring a new skill identity.

Worker exclusions constrain new delegated assignments. They do not silently
replace an already selected primary outside that worker set. An explicit limit
on the whole workflow also constrains future primary work; report a conflict
with the current selection rather than claiming a worker setting changed it.
Re-read the primary and relevant instructions at each new assignment boundary.
An existing worker retains its original contract and actual execution settings;
new preferences never silently interrupt or retarget a writer.

Explicit `$luna-task` and `$luna-goal-loop` remain a separate low-cost choice:
their only delegated model is `luna-max`, regardless of the primary, available
higher-cost candidates or adaptive preference. Configuration and availability
checks preserve their honest failure reporting rather than silently widening
their model selection.

### Give high/mid/low useful semantics

| Setting | Proposed meaning | Effect on routing |
| --- | --- | --- |
| High: quality-first | Prefer additional reasoning capability or a useful frontier alternative when it plausibly improves the accepted result. | Seek justified additional help earlier for a concrete unresolved issue; clear cheap work can still use Luna. |
| Mid: balanced | Weigh likely improvement against handoff, latency and total usage. | Keep ordinary work in a capable primary; delegate useful slices and escalate a demonstrated gap. |
| Low: economy | Require a stronger reason to incur additional expensive execution. | Favor a credible economical route or direct primary completion; a difficult task can still justify additional frontier help. |

These are soft preferences, not a dollar ceiling, model allowlist or promise to
make the current primary cheap. Explicit resource limits remain hard constraints.
If satisfying the task would require exceeding such a limit, report the conflict
instead of quietly weakening the acceptance check. No setting requires a failed
cheap attempt, a particular delegation percentage, or a mandatory reviewer.

V1 provides no billing enforcement mechanism. When telemetry or the billing
basis is unavailable, do not promise an exact spend ceiling or fabricate a
remaining balance. A strict ceiling that cannot be honored with available
controls must be disclosed before additional paid worker execution; a soft
economy preference remains usable without a bill estimate.

### Keep the profile small and honest

A useful profile needs an exact native role binding when a fixed role is used,
provider/model identity, allowed effort choices from the native route, a dated
cost basis, brief documented strengths and an evidence label. Separate official
guidance, local protocol controls and accepted repository work. Record effective
context/modality/tool requirements only when relevant; a native catalog is not
a local performance benchmark.

Use all four normal candidates in the general profile set. The first native
pilot here can exercise Luna, Sol and Astra while Terra remains unavailable in
this environment. Exact Terra execution is a remaining local acceptance case,
not a prerequisite for documenting or implementing its supported routing path.
Test Terra-present and Terra-primary policy cases in isolated fixtures and label
them separately from actual Terra execution. It need not occupy the middle of
every task's ranking. An unknown model need not be assigned a speculative
cost/capability bucket.

For the first candidate, use native role files for execution pins and a compact
attributed worker reference for supplementary facts. Accept a preference in the
explicit adaptive-workflow request; otherwise use a default from applicable
user guidance, then balanced if none is supplied. Reuse native configuration
and existing instruction mechanisms for defaults and restrictions. A preference
override does not lift a separate worker exclusion, resource limit or native
permission. Explicit user changes to those constraints are distinct from merely
asking for high preference. Fixed agent files keep their native precedence;
an incompatible requested effort is reported rather than silently applied.

V1 adds no persistent Plus preference file, new native config keys or additional
configuration hierarchy. If actual usage later justifies persistence, give each
fact one owner and have chezmoi manage only the intended preference/role targets,
preserving local overrides. The selected-primary helper remains optional and
read-only: workers must not become dependent on the monitoring installation.
If reliable primary metadata is unavailable, continue in the primary or make a
justified permitted assignment, but do not claim comparative escalation from
an inferred primary identity.

### A short routing rule is sufficient for the first candidate

1. Honor the invoked workflow, task boundary, required tools/modalities and
   explicit model/resource constraints. Preserve investigation versus write
   ownership and the existing acceptance standard.
2. Read the initiating primary, supplied user constraints and preference, then
   inspect declared native controls and roles directly. Filter known-unavailable
   models and incompatible model/effort settings for this session only. Keep
   unknown availability explicit; do not run speculative probes during ordinary
   tasks or assume the host's default config identifies the active primary.
3. Consider direct primary work and useful bounded assignments. Use model
   strengths and relevant evidence to judge the likely benefit, including the
   cost of context transfer, review and repair.
4. Apply the preference among credible routes. Explain the chosen route in one
   sentence when delegation or escalation is material. A price difference alone
   does not establish task fit; an extra same-model worker needs an independent
   execution benefit rather than being called a capability escalation.
5. Spawn through the actual native declaration with a self-contained assignment
   and `fork_turns="none"` for an explicit model/effort choice. Respect fixed
   role precedence. Verify the observed model/effort and handoff; distinguish
   requested configuration from any available execution/reroute evidence.
6. Review the result, resolve concrete gaps and reassess the next assignment.
   Repeated failure without new evidence calls for diagnosis or primary takeover,
   not cycling through a compulsory model ladder. Transfer write ownership only
   after the writer hands off or stops, preserving useful partial changes.

Example with a Sol primary: an economical bounded extraction may suit Luna at
every preference. Ordinary implementation, configuration or investigation can
stay in Sol or form a useful Terra assignment when eligible and justified by
expected total effort. A hard unresolved design question can justify an Astra
assignment when there is a concrete reason to try that frontier alternative;
its higher price alone does not establish an upgrade from Sol. Terra is
a general worker candidate, not a standing destination for writing or visual
tasks. Advertised strengths alone do not establish an advantage over another
model on those tasks. These are examples for qualification, not dispatch rules
or proof of comparative quality.

### Preserve invocation and failure behavior

Only the explicitly invoked adaptive worker workflows would gain this policy.
`$luna-task`, `$luna-goal-loop`, `luna-max`, `sol-xhigh`, and legacy identities
retain their current meanings. Generic goal-loop requests and discussion of
these skills still activate no worker workflow. No primary model switch or
additional task authority follows from a preference.

Native collaboration controls stay outside `functions.exec`/`ALL_TOOLS`.
Preserve the recently corrected distinction between missing declarations or
roles, rejected spawns and worker/model errors after startup. An empty Code
Mode search excludes no native candidate. A genuinely missing control means no
delegation was attempted; never label that a model failure.

Terra unavailable in one session simply leaves that session's eligible pool;
its supported profile and other sessions' choices remain intact. If needed
help is unavailable, a capable primary may finish; otherwise disclose the unmet need.
Do not silently alias models, change provider/billing route, repurpose a pinned
role, launch another Codex process or recommend a restart as discovery repair.
After an actual worker failure, report the error and use the authorized takeover
policy. A different worker requires a justified new routing decision within the
adaptive workflow, not a concealed substitution for a failed named assignment.

### Qualify the design before implementing it

| Case | Required reasoning/result |
| --- | --- |
| Terra present and permitted | Include its current profile and settings as a normal candidate; do not carry over a global disable from this host. |
| Terra absent locally | Filter it for that session; keep other candidates and general Terra support intact, with no invented inference success. |
| Terra primary | Account for the initiating Terra context, appropriate Luna assignments and justified Sol/Astra help. |
| Astra, Sol or Luna primary | Reassess routes relative to the actual initiating model and context; no automatic primary switch. |
| User excludes a model or pins an effort | Honor that constraint under every routing preference; do not silently override the fixed role. |
| High preference, clear bounded slice | Luna remains a valid route when the handoff helps. |
| Economy preference, unresolved difficult question | Stronger help remains possible within explicit constraints; acceptance is unchanged. |
| Primary already resolved most of a small slice | Direct completion remains valid despite a cheaper candidate's token rate. |
| Visual task with relevant local evidence | Task-specific strength can outweigh a generic ordering; tool access is checked separately. |
| Equivalent model/effort in two labels | Do not claim capability escalation; justify separate execution if useful. |
| Unsupported effort, context or modality | Reject that configuration without silently substituting a setting. |
| Unknown profile, stale price or incomparable billing basis | State uncertainty; do not fabricate a precise ranking or saving. |
| Unknown primary, provider alias or stale home default | Avoid inferred primary identity and unverified comparative claims. |
| Empty Code Mode registry, native controls declared | Native delegation remains discoverable directly. |
| Genuinely absent controls or role | Report the specific missing surface without an attempted-spawn claim. |
| Spawn rejected, execution failed or model rerouted | Preserve distinct observations, actual settings and useful partial work. |
| Explicit Luna or generic goal-loop request | Preserve each workflow's existing invocation and model boundary. |
| Compatible declared model with no past execution | A useful authorized first assignment is possible; access is labeled unverified until its actual result. |
| Worker exclusion omits the selected primary | Apply it to new workers; do not switch the primary or misstate a workflow-wide restriction. |
| User changes primary/preference during the loop | Re-read at the next assignment boundary; retain existing workers' contracts and ownership. |
| Exact spend ceiling with unavailable billing telemetry | Disclose that enforcement is unavailable before additional paid workers; never claim guaranteed spend. |
| High preference conflicts with a worker exclusion or explicit Luna workflow | Keep the exclusion/workflow boundary; preference alone does not widen permission or model selection. |

First exercise these as policy cases and review the proposed prompts against
them; prose matching is not behavioral evidence. A later authorized isolated
pilot must qualify exact Astra/Sol/Luna execution, both Sol and Astra primary
contexts, useful handoffs, primary acceptance and failure handling. Compare
primary-only and adaptive execution from equal fixtures, including the cheaper
capable-primary baseline. Keep effort fixed initially, retain all reported token
categories, elapsed time and repair work, and call unobservable cost unknown.
Prefer a small accepted improvement over adding another policy mechanism.

The first candidate's design choices are settled for review; it is not runtime
qualified. Later decisions are whether usage justifies persistent preferences,
which task-specific evidence is useful enough to retain, and whether the pilot
shows any value beyond the existing primary/Luna policy. No trained router,
global score, automatic profile refresher, model benchmark service or per-turn
primary switching is necessary to test this hypothesis.

### Second research review: findings and readiness

The 2026-11-02 review checked all 22 policy cases above as tabletop decisions,
not model executions or tests of an implemented router. It resolved five gaps:
untried access versus missing controls, worker restrictions versus primary
selection, configuration scope/precedence, changes during an active loop, and
exact-spend claims without telemetry. These rules preserve the current native
execution and explicit invocation boundaries.

Fresh official sources confirm custom-agent pin precedence and inherited
provider/permissions/MCP configuration, caller-scoped model metadata, and the
separation of credit rates from subscription usage. The research supports the
architecture but supplies no task-quality threshold for these four model/effort
choices. The proposed next step is a bounded native protocol pilot, followed
by paired accepted-outcome comparisons if protocol viability passes. No actual
model, worker, catalog or owner lifecycle operation was run for this review.

### Capability evidence refinement after focused research

The [focused comparative study](worker-routing-study.md#focused-capability-evidence-astra-sol-and-terra-2026-11-02)
finds useful independent coding evidence, including native Codex runs. It
supports Sol as a strong general-purpose cost/quality choice, Terra as a real
general coding candidate, and Astra as a possible frontier alternative. It
does not support a universal Astra > Sol > Terra capability ladder. Preserve
the price order as a dated rate fact, separate from these conditional priors.

In particular, a Sol primary should not automatically delegate hard work to
Astra because Astra costs more. Seek a concrete benefit for the unresolved
question, account for handoff/review, and retain direct primary work. A Terra
assignment is an economical candidate, not a guarantee of savings: some public
tasks consume enough extra tokens to reverse the nominal price advantage.

Effort is part of the compared configuration. Public Terra Max results differ
materially across suites, and the current broad Codex comparison displays Sol
and Astra at Max rather than our proposed XHigh settings. Retain exact variants,
harnesses and evidence dates; do not promote a result from another effort or
benchmark version into an unqualified local profile. The first candidate's
existing effort choices remain provisional pending native fit checks.
