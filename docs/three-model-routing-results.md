# Primary-aware three-model routing spike

Date: 2026-11-01. Status: selected-primary inspection qualified as a local
candidate; three-model routing deferred behind a native execution gate. See
the [execution contract](codex-plus-plan.md#selected-spike-primary-aware-three-model-worker-routing).

## Decision and scope

Keep Sol XHigh, Terra XHigh and Luna Max as the proposed selections, with the
user choosing the primary. Preserve the Luna agents/workflows, explicit skill
activation and current adaptive routing. No new Terra agent or changed worker
policy is included in this candidate.

The user-approved direction remains useful: a Sol primary could delegate to
Terra or Luna; a Terra primary could delegate to Luna and use Sol for a focused
reasoning or implementation escalation. The continuing primary would retain
integration and acceptance. Direct primary work would remain available without
a required cascade, failed cheap attempt, routing score or mandatory reviewer.

The existing adaptive instructions assume Sol primary and describe a Sol worker
as another execution context rather than a stronger tier. That distinction
must be revisited before advertising Terra-primary escalation. The old
`legacy/agents/terra-xhigh.toml` selects GPT-5.6 Terra and is not a substitute for
GPT-6.1 Terra. Those files are unchanged.

## Native findings

The selected existing owner and schema generator both use native Codex 0.166.0.
Its generated `Thread` schema exposes `model` and `reasoningEffort` as the current
configured values when loaded and latest persisted values when unloaded. The
schema explicitly excludes per-turn execution telemetry. Native
`thread/read` returns those fields; the inspected TUI `read_thread` tool omits
them. A model's self-description or a home config default is therefore not an
adequate replacement for the native read.

Two owned durable control threads each completed four short turns: Sol/XHigh,
Luna/Max, an inherited Luna/Max turn, then Sol/XHigh again. All eight metadata
observations matched the expected model and effort. The second thread also
passed four reads through the candidate context helper. After archival, native
metadata reported `notLoaded` and the helper returned `unknown` without resuming
the thread. A read of the real caller's selection reported Sol/XHigh.

These are metadata/protocol controls, not representative coding tasks or model
quality benchmarks. Six of eight acknowledgment messages matched the expected
bare token; two included a terminal period. The prompt itself ended with a
period after the requested token. Preserve that formatting observation rather
than reporting eight exact-output passes. No reroute notification was observed;
absence of that notification is not independent backend identity proof. Native
usage counters were collected, but no Terra cost/quality comparison was possible.

## Terra execution gate

The existing owner's complete hidden-inclusive model inventory omitted
`gpt-6.1-terra`. Starting an owned durable thread with that exact model and
`xhigh` returned the requested configuration successfully. Its first actual turn
then failed with `modelNotFound`:

> The 'gpt-6.1-terra' model is not supported when using Codex with a ChatGPT account.

Configured selection and a successful thread start did not establish execution.
The failed thread retained Terra/XHigh metadata and entered `systemError`.

Read-only inspection found that the managed local catalog also omits this model,
while the installed binary's bundled catalog includes it. Official
[catalog documentation](https://learn.chatgpt.com/docs/model-catalogs)
states that a local `model_catalog_json` takes precedence over remote discovery.
This establishes a local catalog discrepancy, not the cause of the inference
failure.

A second owned fixture used a thread-scoped override pointing to a private
catalog copy containing the exact native bundled Terra entry. It failed with
the same inference error. The owner's normal catalog still omitted Terra after
the retry. This does not establish that the long-lived owner's cached catalog
was refreshed by the override. Account eligibility, owner caching and upstream
availability remain unlocalized. Do not claim a universal ChatGPT limitation,
that a global catalog edit will fix it, or that a daemon restart is required.
No other provider or authentication route was substituted.

Both failed fixtures and both successful control fixtures are archived and
unloaded. Only those four newly owned actors received input or lifecycle
operations. No child-worker or peer-message trial was started.

## Native catalog repair candidate

The subsequent 2026-11-01 goal loop qualifies a local fix in the canonical
chezmoi provider integration. This is separate from the Codex Plus runtime
candidate, product version and the deferred three-tier worker behavior.

Both production homes still select the same managed snapshot lacking Terra.
Removing an output key from a managed template alone would retain the old live
key during merge. The candidate therefore:

- omits `model_catalog_json` for the OpenAI default and its ChatGPT profile,
  restoring native discovery rather than periodically copying a bundle;
- retires only the integration's exact old catalog paths, preserving custom
  catalog paths and explicit machine overrides;
- provides a catalog-only apply that preserves all other settings and refuses
  a provider transition; Plus/report-only scopes retain their boundaries;
- retains Ori's OpenRouter catalog, complete metadata and worker aliases; and
- handles an optional OpenRouter default separately, since native profiles
  overlay the base config and cannot unset its catalog.

That last case needs a subscription compatibility snapshot. The refresh helper
uses native `debug models` in separate empty staging homes, references each
selected home's existing native credential file without copying or interpreting
its tokens, and requires a newly written, current-version, identity-scoped native
cache. A successful command with silent bundled fallback is rejected. Default
and Work account catalogs remain separate. Explicit offline fallback exports the
installed native bundle and records that source; it never uses Ori's stale native
snapshot. Publication remains atomic, preserves earlier generations and rejects
foreign paths. There is no background or launch-time refresh. Compatibility
snapshots require manual refresh when models or account selection change.

The current compatibility exporter supports file-backed ChatGPT login;
keyring-only export is not qualified and fails closed. Normal native discovery
keeps its native authentication behavior. Native inference access remains
unproven by these metadata tests.

Validation uses synthetic credentials and a loopback catalog, with no real
account request, shared daemon or inference turn. Native 0.166.0 fetches a
new fixture entry absent from the stale Ori snapshot, preserves its complete
metadata, distinguishes two account identities, rejects failed-online fallback,
and selects the correct instructions in all eight combinations of root provider,
explicit billing profile and native home. Managed tests cover exact-path
migration, custom/machine choices, byte convergence, narrow apply preservation,
Luna/Max metadata, malformed/missing exports, freshness/version/identity failures,
foreign publication paths and failure preservation.

`check-codex-openrouter --native /opt/openai-codex/bin/codex` passes. The full
chezmoi check passes its relevant Codex/worker/split/provider gates, then fails
in the existing Claude/OpenRouter fixture because its temporary home lacks
staged Niri components. The pre-change baseline reproduces the same failure;
it is not repaired or bypassed here. Codex Plus's clean 133-file inventory and
40 existing check/Pages tests pass; the pre-existing untracked bytecode is
preserved outside that clean candidate.

Actual-config dry runs on Snap pass for both native homes. Their semantic
config delta contains exactly one removed key, `model_catalog_json`; both
rendered ChatGPT profiles also omit it. Eleven protected live config/profile,
auth and catalog paths retain their original bytes/modes/targets. Both owners
predate this goal and remain running; their complete inventories still omit
Terra and still select the old snapshot. This confirms preparation without
claiming installation or loaded acceptance.

The candidate changes seven chezmoi paths: three shared config/profile templates,
the Work ChatGPT profile wrapper, the existing refresh helper, its existing check
script and provider documentation. Those paths overlap uncommitted provider work
in a divergent tree, so keep the baseline and focused patch separate before any
commit/publication there. No production helper/config/catalog, auth, worker,
release selection or daemon restart is part of preparation. Apply the reviewed
catalog-only delta and the two explicit profiles at a later authorized boundary,
verify the effective config and loaded inventory independently, then qualify
exact Terra/XHigh inference before continuing three-tier worker work.

## Scoped Snap repair applied

Bryan subsequently authorized applying the fix on 2026-11-01. The reviewed
catalog-only chezmoi apply changed exactly four targets: the root config and
ChatGPT profile in each of Snap's default and Work homes. Each file's semantic
delta is removal of `model_catalog_json`; installed bytes match the freshly
reviewed renders and all four retain mode 0600. Private preimages and receipts
are retained for rollback. Credentials, OpenRouter profiles, worker/skill files,
the installed refresh helper and managed catalog generations are unchanged:
128 protected paths match the before snapshot. Chezmoi repository status and HEAD are
unchanged, retaining the divergent history and overlapping source work.

Both existing daemon identities remain unchanged. Their disk-effective
`config/read` results select OpenAI with no catalog override, while complete
`model/list` results still omit Terra. No lifecycle operation was issued.

A bounded native `codex debug models` query outside the shared owners then
succeeded separately for each home, using the existing native ChatGPT login
and built-in OpenAI endpoint defaults. Both wrote freshly fetched,
identity-scoped 0.166.0 caches. Each returned nine models, with no exact
`gpt-6.1-terra`; this was current account metadata rather than silent bundled
fallback. Only the normal native caches were refreshed, without publishing a
replacement managed catalog generation. No credential copied or changed, real
conversation resumed, or inference request issued during this validation.

This additional result means a daemon restart alone is not the remaining
remedy for Terra availability. The stale local override is repaired, but the
current account-facing catalog also omits Terra. Distinguish that observation
from a proven account-tier restriction or universal product limitation; account
eligibility versus upstream rollout is not yet localized. Preserve active
owners and investigate that availability gate before another exact-model trial.
The optional compatibility exporter remains a local source candidate, and no
fleet publication or deployment is established by this Snap-only apply.

## Supported local implementation

`codex-plus-context --primary` exposes the qualified read through the existing
CLI. Its ordinary path-only behavior remains offline. The optional mode:

- requires the caller's native thread identifier;
- uses the selected environment and existing socket override rules;
- verifies listener ownership and positive loaded-thread inventory;
- reads only that thread, rejects subagent/unloaded/error/partial metadata and
  returns `unknown` instead of consulting defaults or another home;
- reports configured model, provider and effort with
  `execution_verified: false`; and
- reads fresh metadata each time, without a cache, hook, new MCP tool or daemon.

The worker bundle remains independent of monitoring. The candidate helper is
not installed or made a mandatory worker dependency, and none of the current
agent or skill payloads changes. See the [source usage notes](environments.md#local-candidate-inspect-the-selected-primary).

## Continuation when model execution is available

1. Recheck the actual selected owner and complete model inventory. Obtain one
   successful exact Terra/XHigh inference through the intended native account,
   with the effective catalog provenance recorded. Preserve active owners and
   the existing configuration manager; do not infer permission to restart.
2. Verify Terra-primary selection through the helper, a user model switch and
   inheritance on the following turn. Keep configured-selection and actual
   execution evidence separate.
3. In owned fixtures, qualify Sol-primary delegation to Terra/Luna and
   Terra-primary Luna delegation plus a focused Sol escalation. Check actual
   child model/effort selections, ownership, corrections and primary acceptance.
4. Compare a routine fix, planned change, ambiguous diagnosis and documentation
   task from identical starting material with equal acceptance criteria. Keep
   Luna/Max fixed, initially match primary reasoning effort and record complete
   primary/worker usage, elapsed time, missed requirements and repair work.
   Tune effort only after that comparison; retain counts rather than publishing
   a universal savings percentage.
5. Refine the existing adaptive task/goal-loop skills and package a current Terra
   role only if those gates pass. Preserve the Luna workflows and explicitly
   handle unknown primary context, unavailable agents and nonmatching models.
   A Sol worker under Sol primary still needs an independent-execution benefit;
   under Terra primary it can have a focused escalation purpose.

## Validation and preservation

All 382 existing/new tests pass under Python 3.14, including six new context
tests (16 environment tests in total). They cover opt-in behavior, missing
caller/owner, listener binding and read-only methods, stale/subagent/partial or
mismatched metadata, fresh selection after a change, selected-endpoint use and
deadline failure without fallback. The clean 133-file source candidate passes
the repository inventory, agent/skill metadata and model/effort checks.
`git diff --check` passes.

The working checkout's inventory check still rejects exactly the two
pre-existing untracked bytecode files. They are preserved, not deleted or added
to the public inventory. All 375 protected file hashes/modes/links match the
baseline, including those bytecode files. The existing owner identity matches;
all four owned actor records report `notLoaded`. All current agent and skill
payload files remain unchanged.

Committed candidate `4fe5ae6` passes the clean inventory check and a complete
three-component release build/verification. A checksum-verified monitoring
archive installs under a private temporary prefix; its relocated context CLI
successfully reads the real caller's selected Sol/XHigh configuration. All 18
worker payload files match the prior source byte-for-byte. These private build
checks use the current source version; they are not new published release assets
or an installation into a production prefix.

Raw events, private actor identifiers, catalog copies and local evidence paths
remain outside committed source. This pass does not publish, deploy, change
production configuration or restart a daemon. The research spike is complete
with the Terra execution gate unresolved; the continuation above is required
before implementing or claiming the three-model adaptive workflow.
