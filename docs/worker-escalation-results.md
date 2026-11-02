# Worker escalation candidate qualification

Local candidate qualified 2026-11-02 on native Codex 0.166.0. This is source and
private artifact evidence, not a published release or installed policy.
Published and managed selections remain preview.14 from `dc19a82`.

## Implemented policy

The [selected design](worker-routing-design.md#selected-design-primary-luna-and-one-escalation-target)
and [implementation plan](https://github.com/byebyebryan/codex-plus/blob/295ed24061d058067e8d2a18ee39a3f55d610067/docs/codex-plus-plan.md#selected-plan-primary-luna-and-optional-escalation)
keep the native user-selected primary, useful Luna assignments and one opt-in
escalation target. Terra can select Sol or Astra; Sol can select Astra. Defaults
are none. Reviews and demanding implementation use the same option. There is no
new preference file, custom native setting, router service, automatic Sol/Terra
cost substitution or recursive escalation ladder.

Only `worker-task` and `worker-goal-loop` gain the selection policy. The native
`astra-xhigh` role pins `gpt-6-astra` / `xhigh`; `sol-xhigh` remains
`gpt-6.1-sol` / `xhigh`. The Luna role and both explicit Luna skills, including
invocation metadata, remain byte-identical to the goal baseline. Generic goal
requests and skill discussion activate no worker skill. Explicit named native
worker requests retain their separate authority.

The existing source `codex-plus-context --primary` helper supplies qualified
loaded-thread selection. It does not prove a backend inference identity, guess
from host defaults or revive an unloaded thread. Worker-only installs remain
useful without the helper or monitoring: unknown primary identity holds automatic
escalation and preserves primary/Luna work. Native role pins, account eligibility,
completed execution and accepted work remain distinct evidence.

## Source and artifacts

The reviewed plan is committed as `f40b32a`; implementation is `295ed24`, followed
by local validation/documentation refinements. The 135-file clean candidate
passes `scripts/check`, all 383 repository tests on Python 3.14, the four worker
skill validators and whitespace checks. Artifact tests inspect native model/effort
pins and exact worker skill bytes; they do not match routing prose or claim to
prove model decisions. Existing context tests cover fresh selection, child and
unloaded callers, missing/partial metadata, owner failure and no fallback.

The complete unified private build and verifier pass. Two builds from `295ed24`
produce identical bytes for all five release files. The new Astra role is in the
explicit source and worker artifact inventories. The candidate retains the
existing version solely for private qualification; these files are not replacement
preview.14 release assets. Publication needs a new selected release/version and
synchronized managed pins/checksums/validators. No asset was published.

The candidate Pages build checks the walkthrough and nine guides, 301 local
links/assets/anchors and 15 current-release claims. Guides label the new policy
as a local candidate and retain the published preview.14 installation boundary.
The strict working-checkout inventory still rejects the same two pre-existing
bytecode files; they are preserved. The clean committed source is the acceptance
input, not a checkout with generated runtime files removed.

## Native execution and acceptance

All trials use newly owned fixtures under the existing daemon. Project-scoped
native role files expose the candidate without copying into installed personal
roles, reloading global MCP servers or restarting the owner. The pilot ceiling
is eight worker starts and 32 native conversation turns, including settlement;
two distinct provider/access failures would stop it. A native conversation turn
can include multiple model/tool rounds and is not an API-request or billing unit.

| Trial | Observed result | Evidence limit |
| --- | --- | --- |
| Default adaptive task with no escalation | Sol primary kept a small CSV fix, preserved embedded LF/CRLF and passed three tests; no worker started. | One ordinary bounded task, not a delegation-rate benchmark. |
| Sol primary with Astra opt-in | Direct native spawn selected `astra-xhigh`, `fork_turns="none"`; loaded worker selection was `gpt-6-astra` / `xhigh`; its turn completed without error. | Completed native execution with matching selection; no independent backend identity or general capability ranking. |
| Read-only Astra review | Found two real defects in an owned handoff fixture; the primary independently reproduced both, checked seven controls and verified unchanged fixture bytes. | Sequential fixture behavior, not real concurrent worker termination. |
| Explicit Luna with Astra permitted for adaptive work | Direct native spawn selected `luna-max`, no forked history; loaded selection `gpt-6-luna` / `max`, completed without error. Luna implemented the two fixes in its assigned files; the primary reviewed and accepted all ten tests, including regressions that failed the original implementation. | An explicit Luna task, not automatic adaptive Luna selection or cost-savings proof. |
| Collaboration genuinely unavailable | A fresh thread with native agents disabled completed a small `worker-goal-loop` in the primary. It reported missing controls, no attempted delegation and no substitute process/worker. | Does not exercise a rejected spawn or a post-start model error. |
| Independent Sol policy evaluation | Explicitly requested `sol-xhigh`, no forked history; loaded `gpt-6.1-sol` / `xhigh`, completed without error. Evaluator and primary agreed on all 18 conditional cases and left fixture files unchanged. | Named-role control and policy interpretation, not a Terra-primary run. |
| Native role pin conflict | A fresh thread exposed an intentionally invalid fixture `astra-xhigh` pinned to Sol XHigh. The final candidate skill reported the exact conflict, attempted no spawn, preserved files and finished useful primary review. | Tests preflight conflict handling, not an actual backend reroute. |
| Empty Code Mode registry | A real `ALL_TOOLS` lookup exposed zero collaboration controls; a directly declared native `collaboration.list_agents` call succeeded. Pilot workers also used direct native spawn calls. | A successful list call alone would not prove spawning; the separate completed role trials do. |

The pilot used three worker starts and nine native conversation turns, with no
provider/access failure. All four owned primary fixtures and three children
settled with completed error-free turns, then were archived and unloaded.

The 18 policy cases cover Terra defaults and both optional targets, Sol/Astra,
unsupported mid-tier offload, Astra/unknown primaries, missing controls/roles,
empty registry, explicit Luna, generic goal wording, a prohibited child chain,
request-level disable, active-owner preservation, wrong pins, rejected spawn and
post-start model failure. Hypothetical metadata and errors are explicitly fixture
inputs; no hypothetical route was launched. An explicit null target means disable
in that private fixture encoding, not a new public configuration schema. A pin
mismatch without timing cannot honestly be classified as preflight versus a
post-start reroute. No actual child spawned a descendant.

## Remaining limits and deployment boundary

Local Terra-primary inference remains unavailable from the earlier native spike
and was not retried. Terra-to-Sol/Astra is supported policy with conditional
fixture coverage; neither path has actual Terra-primary execution proof here.
Actual provider rejection, model errors, primary/settings changes while a writer
is active and long-running unattended recovery are not established by these
small trials. No universal ranking, cheaper accepted-task result or exact spend
enforcement is claimed.

No release, push, Pages publication, managed policy apply, fleet deployment,
installed worker patch or existing-session interruption belongs to this pass.
The native owner automatically added trust entries for the three private fixture
directories. After settlement, a version-checked native config batch removed only
those owned entries with no runtime reload; the original config hash was restored.
All 17 protected installed/config paths match their baseline bytes/modes and the
native daemon identity is unchanged. Private prompts, captures, session identifiers, raw configuration
and toy implementation files remain outside committed source.
