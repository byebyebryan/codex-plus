# Worker routing research

Date: 2026-10-06. Scope: published experiments, first-party engineering
experience, and current Codex documentation relevant to the
[routing design](worker-routing-design.md). Active workflows are unchanged.

The [2026-11-02 follow-up](#follow-up-model-facts-and-routing-preference-2026-11-02)
researches a broader candidate in which model facts and the user's routing
preference are separate. The original Sol/Luna findings below remain historical
evidence; the follow-up does not change the shipped workflows.

The latest [focused capability research](#focused-capability-evidence-astra-sol-and-terra-2026-11-02)
compares independent coding evaluations and first-person reports. It revises
the proposed capability priors without changing installed model selections.
The subsequent [selected design](worker-routing-design.md#selected-design-primary-luna-and-one-escalation-target)
uses that evidence for direct primary work, Luna and one opt-in escalation
target. The earlier three-preference draft is retained as research history.

Selective delegation and coordination overhead are established research topics.
The evidence supports keeping the adaptive workflows led by the primary,
delegating suitable work to Luna, and treating another Sol agent as a separate
execution choice. It does not establish an optimal threshold for our particular
Sol XHigh and Luna Max pairing. Keep the resulting policy short and evaluate
accepted outcomes rather than prescribing an elaborate process.

## Selective model use has a quality and cost tradeoff

[RouteLLM](https://arxiv.org/html/2406.18665v4), first submitted in June 2024
and revised in February 2025, learns whether the stronger model is likely to
outperform the weaker model, then varies a threshold to trade response quality
against strong-model usage. This is a controlled routing study using preference
data and answer benchmarks. Its signal is the comparative benefit of the
stronger model, rather than a fixed rule that every request should start cheap.
It does not measure the context transfer and acceptance costs of delegated
repository work.

[FrugalGPT](https://arxiv.org/abs/2305.05176), May 2023, is earlier work on
learned model cascades that reduces cost while preserving answer quality on
its evaluated tasks. It establishes that cheaper models can be useful within
a quality constraint; its historical savings and cascade structure are not
parameters for this kit.

[AgentRouter](https://arxiv.org/pdf/2609.22951), September 2026, studies routing
individual steps within agent trajectories. Its useful distinction is that a
weak output can affect later steps, so judging a step in isolation misses part
of the cost. The paper also reports degraded routing accuracy when transferred
to another orchestration framework. This is a recent, trained-router example,
not evidence to adopt its classifier, model tiers, or savings estimates here.

**Application to this kit:** base Luna delegation on a sound assignment and
credible verification, with a likely saving in total accepted-result effort.
Evaluate the whole task. A primary that has already resolved most of a slice
may have little left to save by handing off the remaining edits.

## Task structure matters more than an extra agent label

[Towards a Science of Scaling Agent Systems](https://arxiv.org/html/2512.08296v3),
first submitted in December 2025 and revised in April 2026, compares 260
configurations across six agentic benchmarks, five architectures, and three
model families. Results vary strongly by domain: decomposable work can benefit,
while sequential dependencies and communication can consume the reasoning
budget. The coding evaluations use 20-instance subsets; the tested models do
not include our GPT-6.1 Sol and GPT-6 Luna pair. Its reported saturation point
and architecture rankings should not become universal thresholds.

[Cognition's context-engineering account](https://cognition.com/blog/dont-build-multi-agents),
June 2025, identifies two practical hazards: losing relevant context during
handoff and allowing workers to make conflicting implicit decisions. Separate
file ownership does not settle shared decisions about behavior or integration.
This is engineering judgment from a coding-agent developer, rather than a
controlled demonstration that all multi-agent systems fail.

[OpenHands' single-agent account](https://www.openhands.dev/blog/dont-sleep-on-single-agent-systems),
September 2024, describes how fixed role divisions can restrict the tools or
context needed to solve a task. It favors a capable generalist where that
structure does not help. The historical article is a design argument, not a
current benchmark ranking.

**Application to this kit:** keep tightly connected reasoning in the primary.
Delegate across a meaningful responsibility boundary once shared invariants
are clear. Give the worker compact but sufficient context and access to the
authoritative artifacts; brevity alone is not a good handoff metric.

## Multi-agent gains can buy more work rather than cheaper work

[Anthropic's research-system account](https://www.anthropic.com/engineering/multi-agent-research-system),
June 2025, describes gains on an internal research evaluation, especially when
independent search directions can run in parallel and return compressed
findings. It also identifies substantial token usage and a poor fit for domains
with shared context and many dependencies, including much coding work. Its
15-times token figure compares multi-agent research with chat interactions;
it is not a measured 15-times penalty for adding one worker to a coding task.

[Anthropic's coordinator cookbook](https://platform.claude.com/cookbook/managed-agents-cma-plan-big-execute-small)
compares cheap reading workers with a solo frontier model under a matched
verification standard and meters actual bills. It reports a fixed setup cost
per worker and higher bills when briefs become too narrow. Both approaches
also verified facts within an incorrectly chosen set of parks: checking
subtask results did not validate the decomposition. The example demonstrates
an economic mechanism on a particular research workload, not a savings ratio
for coding. Its counterfactual price table contains an introductory rate with
an August 2026 expiry, so that table should not be reused as current pricing.

Current [Codex subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents#why-subagent-workflows-help)
also identifies isolated context and parallel read-heavy work as benefits, and
warns that parallel writes add conflicts and coordination.

**Application to this kit:** retain parallel execution and context isolation as
possible reasons for a Sol worker. A substantial, bounded reading or evidence
gathering task can also suit Luna. Preserve access to raw evidence when the
primary needs to judge its nuances, and review whether the decomposition covers
the user's actual request. Different files alone do not justify parallel work.

## Another same-model perspective is not proof of correctness

[The Cost of Consensus](https://arxiv.org/html/2605.00914v1), April 2026,
compares homogeneous debate with isolated self-correction on two difficult
reasoning benchmarks. Its main experiments use 7–8B models and find peer
conformity, destabilized correct reasoning, and added token cost. Those results
concern unguided debate; they do not directly test detached Sol code review.

The evidence is not uniformly against multiple reasoning paths.
[Multi-Agent Reasoning Improves Compute Efficiency](https://arxiv.org/html/2605.01566v1),
May 2026, finds some debate and mixture-of-agents configurations outperform
self-consistency under comparable estimated compute. It uses Llama models on
MMLU-Pro and BBH, with theoretical compute estimates and overlapping confidence
intervals for some configurations. Those are reasoning experiments rather than
end-to-end coding handoffs or billed Codex usage.

**Application to this kit:** preserve an optional independent review for a
specific question. Ask for findings tied to code, requirements, tests, or other
evidence. Treat agreement between agents as a judgment to inspect, and keep
actual acceptance checks. The papers do not justify mandatory reviewers or a
debate loop for ordinary work.

## Simple instructions still need clear boundaries and verification

[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents),
December 2024, recommends simple, composable patterns and adding complexity
when outcomes justify it. It distinguishes routing, parallelization, and
dynamic worker delegation, and emphasizes clear evaluation criteria. The page
notes that its tooling landscape has since changed. The useful enduring lesson
is simplicity with task feedback, rather than adopting its examples as a
mandatory sequence.

[OpenAI's guidance on revisiting skills](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra),
September 2026, cautions against broad descriptions, repeated guidance, and
elaborate itineraries, and encourages loading detail only when relevant. It is
specifically about GPT-6 Astra and explicitly notes that models can benefit
from different instructions. It supports auditing this kit's prompt size and
triggers; it does not prove that guidance useful to Sol or Luna can be removed.

[Why Do Multi-Agent LLM Systems Fail](https://arxiv.org/html/2503.13657v3),
first submitted in March 2025 and revised in October 2025, analyzes more than
1,600 traces across seven systems and identifies 14 failure modes grouped
around system design, agent coordination, and verification. Repetition, lost
context, wrong assumptions, and incomplete checks are useful failure categories
to recognize. The taxonomy should inform targeted corrections, not become
another role hierarchy or a universal prediction for newer models.

[AI Agents That Matter](https://arxiv.org/html/2407.01502v1), July 2024,
shows why agent evaluations need cost controls, simple baselines, and adequate
holdouts. Its HumanEval experiments find inexpensive baselines competitive
with more elaborate agents. Function-generation tasks and historical prices
limit direct transfer, but the evaluation principle applies: retain usage
counts so comparisons can be repriced, and report quality alongside expense.

**Application to this kit:** put the routing policy in a few sentences. Keep
the existing compact assignment, ownership, and review practices. Evaluate
several real task shapes, including cases different from the examples used to
write the instructions. These research notes are supporting material for
refining routing, rather than required reading before each task.

## Explicit activation remains a separate issue

Current [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills#optional-metadata)
says `allow_implicit_invocation: false` prevents implicit invocation while
allowing explicit `$skill` use. Both adaptive skills already have that policy
in the inspected source and local installation. Reinforce the named-skill
boundary in descriptions and opening instructions, but do not treat a prose
change as proof that the reported runtime misrouting has been fixed.

## Proposed policy after the study

These are design inferences for this kit, not experimentally optimized rules:

1. Keep adaptive work in the primary when delegation's benefit is uncertain.
2. Use Luna for a clear, reviewable assignment when its expected savings cover
   the handoff and acceptance effort. A focused investigation can qualify.
3. Keep difficult or closely connected reasoning in the primary. A Sol worker
   needs a separate benefit from parallel execution, isolated investigation,
   or independent review.
4. Supply sufficient context, preserve shared invariants, and verify both the
   assigned result and its fit within the user's overall request.
5. Keep explicit Luna workflows intact and adaptive activation explicit.

A candidate short routing paragraph:

> Keep work in the primary when delegation's benefit is uncertain. Delegate to
> Luna when the assignment and verification are clear and the expected savings
> justify the handoff. If Luna is not a confident fit, continue in the primary.
> Use a Sol worker only when independent execution offers a concrete benefit.

Avoid a trained router, numeric confidence scores, fixed role graphs, mandatory
cheap-first attempts, automatic Sol escalation, and routine debate. None is
necessary to apply the useful findings here.

## What a practical comparison should measure

Compare the current instructions, the proposed selective policy, and primary
execution on comparable task outcomes. Record accepted results, actual model
and reasoning settings, primary and worker usage, corrections or takeovers,
and elapsed time. Use billed cost when available and retain token categories
for later repricing. Keep success criteria equal across routes.

Include a clear bounded fix, specified migration, evolving diagnosis, small
remainder, substantial evidence gathering, and work with shared decisions.
Assess optional parallelism separately from the primary-versus-Luna choice.
Check activation in fresh sessions with generic goal-loop wording, named
adaptive and Luna workflows, and requests to discuss the skills.

The online evidence supports a lightweight refinement, but it supplies neither
an optimal delegation percentage for our models nor a diagnosis of the reported
activation issue. Those conclusions depend on actual kit behavior.

## Follow-up: model facts and routing preference, 2026-11-02

Bryan proposed separating model cost/capability descriptions from a high/mid/low
setting. This is a better research hypothesis than permanently assigning one
model to each tier: the setting can express a preference while task fit and
actual access determine the useful candidates. This conclusion is a design
inference, not a measured improvement to this kit. See the
[draft design](worker-routing-design.md#draft-model-aware-routing-preferences-2026-11-02)
and [qualification plan](codex-plus-plan.md#research-pass-model-aware-worker-preferences).

### What the current official sources establish

The current [OpenAI model guidance](https://learn.chatgpt.com/docs/models)
describes Astra for demanding work, Sol for complex long-running work at lower
cost, Terra for writing/visual/computer-use tasks, and Luna for focused work.
These are qualitative starting points. They are not measured head-to-head
results for our repositories, effort selections, or acceptance standards.
In particular, Terra's advertised writing/visual strengths do not reserve it
for those tasks or establish an advantage over Sol. The proposed policy treats
Terra as a general candidate for implementation, configuration and investigation;
task-specific preference needs evidence rather than a product-description label.

The [official availability guidance](https://learn.chatgpt.com/docs/pricing#feature-availability)
lists GPT-6.1 Terra for paid Work/Codex plans, subject to workspace/account and
region restrictions. The general candidate set should therefore include Terra
alongside Luna, Sol and Astra. Our environment's missing catalog entry and
failed inference do not establish general unavailability. Keep general product
support, user exclusions and observed session access as separate facts. Terra's
real execution remains unqualified here; Terra-present and Terra-primary
fixture coverage can still exercise the general routing design honestly.

The [Codex pricing table](https://learn.chatgpt.com/docs/pricing#token-rates),
retrieved 2026-11-02, gives these Standard credit rates per million tokens:

| Model | Input credits | Cached-input credits | Output credits |
| --- | --- | --- | --- |
| GPT-6 Astra | 250 | 25 | 1,250 |
| GPT-6.1 Sol | 50 | 2.5 | 250 |
| GPT-6.1 Terra | 25 | 1.25 | 125 |
| GPT-6 Luna | 2.5 | 0.25 | 12.5 |

This corrects the earlier working premise that Terra costs twice Sol: these
published Standard credit rates put Terra at half Sol. They are neither an
account-specific bill nor a conversion of included subscription allowance into
tokens. API prices are a separate rate card. Context, caching, reasoning, speed
mode and retries can change actual task usage; retain the billing basis and
check date rather than treating these numbers as permanent tier definitions.

Reasoning effort is a separate execution setting. The official model pages for
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[Terra](https://developers.openai.com/api/docs/models/gpt-6.1-terra), and
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) document supported
efforts and modalities. The native route still determines usable options and
effective limits. For example, the Sol API page lists a 1.05M context window
while Codex guidance specifies a 500K default. Copying API limits into a worker
profile would therefore be insufficient. Equal effort labels across models do
not establish equal compute, latency, cost, or capability.

Native [model-catalog guidance](https://learn.chatgpt.com/docs/model-catalogs)
separates metadata from inference access and requires caller/version-scoped
catalogs. It does not supply an empirical capability ranking or local task
success rate. Keep the native catalog authoritative for supported settings;
supplement it only with small, attributed cost/strength notes. Do not create a
second catalog or reintroduce the repaired local catalog override.

Native [custom-agent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
already supports per-agent model and effort settings. File pins take precedence
over spawn overrides; provider, permissions and MCP configuration come from the
parent. A model's documented tool support cannot establish that a particular
session exposes a tool or authorizes its use. Existing `luna-max` and `sol-xhigh`
identities must retain their meanings.

### What the routing research adds

| Primary source | Finding relevant to this proposal | Limit on transferring it here |
| --- | --- | --- |
| [RouteLLM](https://arxiv.org/html/2406.18665v4), revised February 2025 | Separates an estimate of comparative model benefit from a configurable cost/quality threshold. | Primarily two-model answer routing; its trained scores and savings do not qualify native coding handoffs. |
| [FrugalGPT](https://arxiv.org/abs/2305.05176), May 2023 | Demonstrates learned combinations of models under quality/cost objectives. | Historical models and evaluated datasets; no basis for requiring a cheap-first cascade in this kit. |
| [Agent-as-a-Router](https://arxiv.org/html/2606.22902v3), June 2026 | Finds that task-specific performance information helps routing and that model strengths differ across coding dimensions. | Its router, memory and benchmark are different; the agentic evaluation uses a 40-step cap and cache hits are not observable for its cost estimates. |
| [Towards a Science of Scaling Agent Systems](https://arxiv.org/html/2512.08296v3), revised April 2026 | Shows that coordination benefits depend on task and architecture. | Coding evaluations use 20-instance subsets and older model families; no universal benefit from adding another worker. |
| [AI Agents That Matter](https://arxiv.org/html/2407.01502v1), July 2024 | Evaluates agent accuracy together with cost and simple baselines. | Different workloads and historical prices; supports the evaluation method, not a current model ranking. |

The new coding-router paper is particularly relevant to the idea of model
specifications: documented features and prices are insufficient to predict
success on a repository task. Use task-specific evidence when available and
mark unknowns. Its stronger routing results do not establish that this project
needs a learned router, persistent memory module, or per-turn model switching.

### Design implications and evidence limits

The useful separation is attributed model facts, current native eligibility,
user configuration/preference and the initiating primary's actual model/context.
Hard task requirements and explicit constraints filter candidates; the
preference influences the choice among credible routes. Capability notes
remain multidimensional and qualitative until comparable local evidence exists.
Cost categories, if displayed, are summaries of a dated rate card rather than
the model's identity. A model can be attractive for visual work without being a
general escalation for coding.

Consider total effort to reach an accepted result: primary planning, context
packaging, worker input/output/reasoning, review, corrections and takeover. A
cheaper token rate does not guarantee a cheaper accepted task; choosing the
existing primary can avoid a redundant handoff. Record elapsed time separately
because parallel token totals do not add up to wall-clock latency.

High/mid/low should initially mean quality-first/balanced/economy preferences,
not fixed models, reasoning efforts, or weaker acceptance requirements. These
are proposed semantics. The exact supported effort remains explicit, and the
initial local comparison should retain Sol/Astra XHigh and Luna Max so effort
tuning does not confound the routing comparison. Later effort experiments can
use the same acceptance checks. General Terra support starts with Terra XHigh;
its actual use depends on the intended environment's native settings/access.

This pass fetched current official documentation and primary papers and
reviewed the local source. It started no worker or model trial and refreshed no
account catalog. The prior qualified Luna handoff and selected-primary helper
remain separate evidence. Astra/Sol/Luna are selectable in this conversation's
declared native spawn schema, which is not an execution receipt for a new
Astra worker. The earlier Terra inference failure remains the last local Terra
execution evidence; its absence no longer needs to block a different candidate
pool's qualification. No cost saving, capability ordering or improved routing
behavior has been proved by this documentation pass.

### Second research review: test the assumptions, 2026-11-02

The design was reviewed again against current
[custom-agent precedence](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents),
[native configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence),
and [model-catalog scope](https://learn.chatgpt.com/docs/model-catalogs). The
review distinguishes a declared usable execution route from past execution
proof: an authorized first real assignment can test access, without a mandatory
diagnostic inference. Its result still needs honest configuration/access/error
reporting. The proposed worker exclusion applies to delegated assignments;
the existing selected primary stays explicit. Native requirements and fixed
role settings remain effective.

[TwinRouterBench v5](https://arxiv.org/html/2605.18859v5), revised October 2026,
adds a useful evaluation distinction: static routing diagnostics and live
end-to-end execution answer different questions. It accounts for routing
overhead, cache effects and unresolved tasks. Its reported dynamic evaluation
is a locked 100-task Astropy/Django subset, not a random sample of the full
suite. Its model pool, per-call switching and bills differ from this kit's
bounded native workers. Borrow the separation of design checks and accepted
outcomes, not its tier prices, labels, savings or architecture.

The resulting candidate keeps preference in the explicit request or existing
user guidance, with balanced as the proposed fallback. No new persistent config
schema is needed initially. Re-evaluate at assignment boundaries, preserve an
active worker's contract, and avoid exact-spend claims without usable telemetry.
All 22 documented policy cases were inspected as tabletop decisions. That
review closes the design ambiguities identified here; it proves neither native
access for all models nor better coding outcomes. The next gates remain native
protocol viability and paired accepted-task comparisons, including the capable
Sol primary baseline and failed/partial attempts in the accounting.

## Focused capability evidence: Astra, Sol and Terra, 2026-11-02

### Question and evidence standard

Bryan identified capability assumptions as the largest unresolved routing lever.
Research the exact `gpt-6-astra`, `gpt-6.1-sol` and `gpt-6.1-terra` variants,
including effort and harness, rather than deriving capability from price or
product positioning. Luna's explicit low-cost workflows remain in place.

Prefer evaluator-owned measurements with methods and artifacts. Use detailed
first-person reports to identify hypotheses, retaining mixed experiences and
configuration uncertainty. Benchmark aggregators, copied launch numbers and an
LLM-generated discussion summary are not additional independent measurements.
All sources below were accessed 2026-11-02; published snapshots can change.

### Independent evaluator evidence

**Artificial Analysis, current native Codex evaluation.** Its
[Coding Agent Index v2.0 comparison](https://artificialanalysis.ai/agents/coding-agents/comparisons/codex-vs-opencode)
reports these variants. Index points are not success probabilities:

| Codex model/effort | Index | API cost/task | Minutes/task |
| --- | --- | --- | --- |
| Astra Max | 55 | $7.04 | 24.8 |
| Sol Max | 54 | $1.50 | 23.7 |
| Terra XHigh | 48 | $0.69 | 16.4 |
| Terra Max | 48 | $1.24 | 26.1 |
| Luna Max | 31 | $0.16 | 21.3 |

This supports Sol's strong coding value and Terra's useful middle position in
this setup, not an invariant ranking or significant one-point Astra advantage.
The current displayed Sol/Astra rows are Max, not our proposed XHigh presets.

The [methodology](https://artificialanalysis.ai/methodology/coding-agents-benchmarking)
uses 290 tasks, three attempts each, and equal weights for FrontierCode v1.1,
Terminal-Bench 4.0 and SWE-Atlas-QnA-AA. It combines code changes, terminal tasks
and repository Q&A; some grading is rubric/model-based and some tasks are
private. Costs are pooled API-price attempt averages, with missing telemetry
excluded, rather than included ChatGPT-plan consumption or our accepted-task
bills. Its terminal component overlaps Vals' dataset, although the runs/harnesses
differ; the two evaluators are not two independent sets of terminal challenges.

**Vals, two different coding workloads.** The October 29
[Terminal-Bench 4.0 board](https://www.vals.ai/benchmarks/terminal-bench-4)
and [Vibe Code Bench v1.1 board](https://www.vals.ai/benchmarks/vibe-code)
give the following source-reported results:

| Model | Terminal score, Mini-SWE-agent | Terminal cost/test | Web-app score, OpenHands |
| --- | --- | --- | --- |
| Astra | 59.60% | $9.58 | 89.59% |
| Sol | 55.05% | $1.72 | 88.93% |
| Terra | 49.49% | $2.16 | 84.00% |

All three model pages list Max as the default effort, with per-benchmark
provider/parameter caveats: [Astra](https://www.vals.ai/models/openai_gpt-6-astra),
[Sol](https://www.vals.ai/models/openai_gpt-6.1-sol),
[Terra](https://www.vals.ai/models/openai_gpt-6.1-terra).
The terminal board shows a concrete reversal of token-price intuition: Terra
costs more per test than Sol while scoring lower, with much greater token use.
The web-app scores put Astra and Sol close, without establishing equivalence or
a statistically reliable ordering. Neither harness is native Codex.

**VulcanBench, a small Codex effort sweep.** The October 30
[Terra report](https://vulcanbench.com/benchmarks/swe-v4-gpt61-terra-v329.html)
tests 23 legacy-program rewrites once per effort. Terra passes 16/23 at XHigh
and 23/23 at Max; combined scores are 83.68 and 90.00. At Max it is comparable
to the reported Astra/Sol columns, contradicting a universal large capability
gap. This is a narrow suite, its combined score includes 33% model-judged code
quality, and comparison columns come from separate reports/versions. Costs
are solver-only API-equivalent estimates. Public CSV aggregates reproduce its
five weighted scores to rounding; this arithmetic check does not independently
verify task execution, hidden tests or model identity. Do not infer that Terra
Max is universally better, or dismiss AA's contrasting effort result.

### Corroboration, conflicting reports and exclusions

The September 29 [AA Sol analysis](https://artificialanalysis.ai/articles/gpt-6-1-sol-replaces-gpt-6-sol-after-just-7-days-with-near-astra-intelligence)
reported Sol XHigh above Astra in its then-current coding index and above Sol
Max. The index has since changed. This is evidence against an assumed monotonic
model/effort ladder, not a value to mix into today's v2.0 table.

The public [joonlab Sol benchmark](https://github.com/joonlab/gpt-6.1-sol-benchmark)
reports near-ceiling Sol/Astra accuracy on small task sets. It publishes data
but not the harness, hidden tests or full responses; its own ceiling and
confidence limits prevent a fine capability ranking. It contains no Terra run.
Endor Labs' [Astra security-coding study](https://www.endorlabs.com/learn/gpt-6-astra-on-codex---the-biggest-codex-leap-to-date)
compares against GPT-5.6 Sol, not GPT-6.1 Sol; it cannot establish the current
three-model ordering.

First-person launch-week reports are mixed:

- A [Terra Max code-review report](https://www.reddit.com/r/codex/comments/1xguuah/i_made_a_huge_set_of_code_changes_for_the/)
  describes useful unique findings on one patch. The author also describes weak
  implementation persistence and says Astra was not included in that experiment.
  It motivates a review hypothesis, not a specialist-worker rule or an Astra win.
- A [long-document Work report](https://www.reddit.com/r/codex/comments/1xgcsh8/gpt61_terra_repeated_instructionfollowing/)
  describes repeated procedural interruptions at Medium and maximum effort.
  This concerns Work orchestration, not a controlled Codex coding comparison;
  the author explicitly leaves session/rollout causes open.
- In the [role discussion](https://www.reddit.com/r/codex/comments/1xgmzda/what_is_the_role_of_gpt61_terra/),
  direct users describe useful fast ordinary/multirepo work. The top automated
  summary is not a measured consensus. Different
  effort, speed mode and tasks make these reports unsuitable for pooled scores.

OpenAI's [Terra launch evaluation](https://openai.com/index/introducing-gpt-6-1-terra/)
reports meaningful coding results and a scientific-terminal workload where
Terra Max exceeds Sol, while recommending Sol/Astra for complex coding. It
supports workload dependence, but remains vendor-run evidence. Separately,
[Vals SRE Bench](https://www.vals.ai/benchmarks/srebench) means software reverse
engineering, not site-reliability operations; its Astra/Sol results must not
be relabeled as evidence about homelab administration. Terra is unmeasured there.

### Revised capability priors and design consequences

These are provisional routing priors, not measured universal tiers:

| Model | Evidence-supported working prior | Boundary |
| --- | --- | --- |
| Sol | Strong general-purpose coding value; often close to Astra in tested coding setups. | No guarantee of matching Astra on every difficult task or effort. |
| Terra | Genuine general coding candidate with useful cost/speed tradeoffs; outcomes depend strongly on effort/workload. | No dedicated writing/visual/review bucket and no guarantee of lower task cost. |
| Astra | Frontier alternative that can add value on some demanding tasks. | Higher price does not establish a capability upgrade from a Sol primary. |
| Luna | Preserve the explicitly chosen inexpensive worker path. | This pass does not change its role, effort or invocation. |

Revise the draft accordingly. A Sol primary needs a concrete expected benefit
before seeking Astra; describe the route as a focused frontier alternative
unless comparative evidence warrants stronger language. Terra can own ordinary
implementation/investigation when eligible and reviewable. Compare actual
model/effort/harness variants, maintain evidence date/version, and keep uncertain
cost/quality effects explicit. The first candidate may retain its proposed
XHigh settings, but they are provisional choices rather than established optima.

This research can replace a large local model-ranking exercise. The remaining
local pilot should prove native access, correct settings, handoff, ownership,
instruction persistence and accepted integration. Small matched ordinary-use
samples can test fit without promising a universal ranking or building a new
benchmark service. No local inference, skill change, catalog repair, installation
or deployment was performed for this research goal; public captures and CSVs
remain outside source.

### Focused research validation and delivery

The clean 133-file export passes the repository gate, five existing validator
fixtures and all four worker skill validators. All 117 local documentation
links/anchors checked across the five planning documents resolve, and whitespace
checks pass. All 91 protected non-document source files match the starting
snapshot. The working checkout's strict inventory still rejects the same two
pre-existing untracked bytecode files; they were preserved.

The separate capability report is published through the configured report
service with verified HTTP bytes. Local and served copies each pass desktop
and mobile loads, three dataset selections and three evidence disclosures per
viewport, including exact table values and no horizontal page overflow. Owned
browser/check servers are closed; the existing report server was reused and
left running. No new product release, source commit/push, managed apply, native
worker trial or native-owner lifecycle action is part of this completed research
goal. These delivery checks do not qualify the proposed routing implementation.

### Policy reconciliation after the capability research

Bryan groups Astra as high, Sol/Terra as mid and Luna as low for operating
purposes, while retaining the user's native primary choice. This does not assert
that the research proved absolute intelligence tiers. The selected policy avoids
routine cross-mid-tier cost routing: the primary and Luna remain the ordinary
choices, with one configured escalation target when useful. A Terra primary
can explicitly select Sol or Astra; Sol can select Astra; defaults are none.
Sol second opinions use that same option rather than another review flag.

The native role/effort precedence checked in the official documentation still
applies. Only a new Astra worker role is needed in the candidate; Terra can be a
supported primary without a worker role. Existing instruction mechanisms can
express the opt-in mapping, avoiding a new configuration schema. Children do
not apply a new primary-based escalation mapping to themselves. Unknown primary
metadata holds automatic escalation, preserving worker-only usefulness and
honest runtime limits. The selected design's case review is planning evidence;
no new model trial was run to validate these decisions.
