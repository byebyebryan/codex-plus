# Implementation handoff

Updated 2026-11-02. The owner-recovery work was isolated on Starship
in `/home/bryan/code/codex-plus-owner-recovery`, based on maintained main. Preserve
the older report checkout and the existing worktrees. Preview.14 is published and
selected on Snap OSS/work, Starship and Carbon; selected and loaded versions remain distinct.

## Local candidate: primary, Luna and one escalation target

Bryan's post-research decisions are reconciled in the
[selected design](worker-routing-design.md#selected-design-primary-luna-and-one-escalation-target)
and [next plan](codex-plus-plan.md#selected-plan-primary-luna-and-optional-escalation).
The user chooses the native primary; adaptive routing offers direct work, useful
Luna assignments and one opt-in escalation target. Terra can select Sol or
Astra; Sol can select Astra; defaults are none. Reviews and second opinions use
that same target, with no separate review flag or quality/economy selector.
The operational tiers are Astra / Sol+Terra / Luna, with no claim of a universal
capability ordering or automatic Sol/Terra cost substitution.

Only three worker roles are needed: existing Luna/Sol plus the candidate Astra
role. Terra is a normal primary and needs no automatic worker role. Escalation
configuration uses the request/existing user guidance, keeping native pins and
managed ownership. No recursive escalation, automatic primary switch or
concealed alternative target is authorized. Unknown primary metadata holds
automatic escalation; the source helper is still an unpublished candidate,
and worker-only installations retain direct/Luna use without monitoring.

Bryan selected the implementation goal loop after reviewing the plan. The five
planning documents are committed as `f40b32a`. The two adaptive skill bodies and
metadata, Sol role guidance, new Astra role, package inventory and worker guides
are being qualified as a local candidate. The explicit Luna skill files and
Luna model/effort stay unchanged. Installed preview.14 and current native owners
remain outside this pass. See the [qualification record](worker-escalation-results.md)
for source, package and runtime evidence; older proposals below retain their
historical limits.

## Research candidate: model facts and routing preferences

This earlier candidate is superseded by the selected proposal above; its
quality/balanced/economy selector is not part of V1.

The latest [focused capability research](worker-routing-study.md#focused-capability-evidence-astra-sol-and-terra-2026-11-02)
reviews independent Codex/agent evaluations and mixed first-person experiences.
It supports conditional priors rather than an Astra > Sol > Terra capability
ladder: Sol has strong coding value, Terra is a general coding candidate, and
Astra is a possible frontier alternative. Some Terra workloads reverse its
nominal token-price advantage; effort/harness choices matter. The
[draft refinement](worker-routing-design.md#capability-evidence-refinement-after-focused-research)
removes automatic Astra-as-upgrade language. Public CSV score arithmetic was
checked without running inference. Native access/fit and our own accepted-task
savings remain separate, unproved gates.
The focused research goal is complete as documentation/report work. A clean
export passes repository/skill validation and five validator fixtures; 117
documentation links and all 91 protected non-document source files verify.
The capability report's HTTP bytes and desktop/mobile data controls verify.
Planning edits remain local/uncommitted and preserve the prior research work;
native worker inference, implementation and deployment have not started.

The 2026-11-02 [research follow-up](worker-routing-study.md#follow-up-model-facts-and-routing-preference-2026-11-02)
and [draft design](worker-routing-design.md#draft-model-aware-routing-preferences-2026-11-02)
separate attributed model facts, native eligibility, user configuration and the
initiating primary. High/mid/low expresses a quality/balanced/economy preference
among credible task-specific routes without fixing a model or weakening
acceptance. The general design includes Luna, Terra, Sol and Astra, with live
eligibility scoped to each session. Terra's absence here does not exclude it
from supported profiles or other environments. Explicit Luna task/goal-loop
workflows keep their separate Luna-only contract.
Terra is a general worker candidate, including coding/configuration and
investigation. Its advertised writing/visual positioning is source context,
not an established task-routing advantage or a dedicated assignment bucket.
The current official Standard credit table puts Terra at half Sol's rates,
correcting the earlier opposite working premise; included subscription usage
and actual accepted-task cost remain separate questions.

The [next qualification plan](codex-plus-plan.md#research-pass-model-aware-worker-preferences)
can use Astra/Sol/Luna while Terra access remains unqualified here, with
Terra-present/absent and Terra-primary policy fixtures kept distinct from native
execution. The older Terra gate applies to this environment's execution, not
to general design support or all routing research. Source
selected-primary inspection and the prior Luna handoff are useful prerequisites;
they do not prove Astra execution or the new routing policy. This research
updated planning documentation and published a separate HTML review report.
It ran no model/worker trial, account catalog refresh, skill installation,
release/fleet publication or native-owner lifecycle action. Current skills,
native agent pins and invocation rules remain unchanged. The second research
review settles V1 on request/user-guidance preferences and native role pins,
with no new persistent configuration schema. All 22 documented policy cases
were reviewed as tabletop decisions, including first-use access, worker-only
exclusions, changing primary/preferences and unavailable billing telemetry.
See the [review findings](worker-routing-design.md#second-research-review-findings-and-readiness).

The initial research snapshot passed the clean 133-file repository gate,
382 existing fixture tests and all four worker skill validators. The subsequent
general-Terra/initiating-primary refinement passes the clean repository gate,
five existing validator tests, 110 local documentation links/anchors and
`git diff --check`; non-document source is unchanged. The working
checkout's strict inventory still rejects its two pre-existing untracked
bytecode files; they remain preserved. All 91 non-document source files match
HEAD. Research cases are a proposed qualification matrix, not executed routing
tests. No new functionality or savings claim follows from these checks.

The second review passes the clean repository gate, five validator fixtures,
all four worker skill validators, 112 local documentation links/anchors and
whitespace checks. The HTML report's published bytes verify over HTTP; both
local and published copies pass two viewport loads and 18 interactive states
in an owned browser. The report publisher started its configured shared report
server and left it running; this is separate from native agent ownership.
Review/report captures remain private and outside source. No worker-policy
implementation, source commit/push or managed deployment occurred in this pass.

## Preview.14 worker correction published and deployed

Bryan's confirmed native-control discovery fix is published as preview.14 from
`dc19a82`; dotfiles pin `59a889a` is published and scoped-applied on Snap OSS/work,
Starship and Carbon. The release excludes the separate selected-primary/Terra
research candidate. All four worker skill bodies now inspect actual declarations
and call collaboration controls directly with the explicit Luna role/no forked
history. Invocation metadata, model/effort pins and routing remain unchanged.

See the [publication/rollout receipt](reliability-packaging-results.md#preview14-worker-discovery-publication-and-rollout).
All 376 focused tests pass locally and in Python 3.11/3.14 CI; four skill validators,
reproducible fetched assets, prior-release rollback and installed inventories/modes
verify. Fresh MCP discovery reports 17/four tools at preview.14 in all four
contexts. The full dotfiles gate retains the unchanged OpenCode `--pure` failure.
Of 1,516 protected paths, only 40 intended worker/selector/provenance paths changed.
Native daemon identities remain unchanged. Starship MCP processes exited during
the rollout and subsequent verification; their cause is unlocalized. The
configured Starship report URL returns 200. No lifecycle action or global MCP
refresh was issued. Existing conversations can retain older loaded MCP metadata.

## Local candidate: native catalog ownership repair

The [repair results](three-model-routing-results.md#native-catalog-repair-candidate)
and [rollout plan](codex-plus-plan.md#planned-fix-native-model-catalog-ownership)
record the 2026-11-01 goal loop. During preparation, both native homes selected
the stale managed snapshot; the installed bundle includes Terra. Bryan then
authorized the scoped local repair. Both Snap homes' config and ChatGPT profile
files now omit the override; only that key changed semantically in each of the
four files. The canonical chezmoi candidate explicitly migrates only
integration-owned paths. `codexCatalogOnly` preserves every other live key
and rejects a provider transition. ChatGPT profiles drop their redundant catalog
line when the root uses OpenAI.

Native profiles cannot clear an inherited catalog. For the optional OpenRouter
default, the candidate keeps a compatibility snapshot refreshed by native Codex
for each home's account, with fresh-cache provenance and an explicit offline
fallback. Ori remains isolated from native credentials/history. No new catalog
service, launch refresh, worker identity or routing policy is introduced.

Focused managed checks and native 0.166.0 loopback tests pass, including eight
provider/profile/home combinations, distinct synthetic accounts, complete new
model metadata and rejected silent fallback. The full chezmoi gate reaches an
unrelated Claude fixture/Niri-staging failure reproduced on the pre-change
baseline. Preserve the divergent chezmoi history and overlapping provider edits;
this goal does not publish them. Source preparation is separate from installed
configuration, a loaded owner's inventory and backend inference acceptance.

The [applied repair evidence](three-model-routing-results.md#scoped-snap-repair-applied)
records exact rendered-byte/mode verification and 128 unchanged protected paths.
Both daemon identities are unchanged. Fresh native `debug models` reads now
successfully update each home's account-scoped cache to version 0.166.0, but
both server catalogs contain nine models and omit Terra. Restarting a daemon
alone does not address that result. Investigate account/upstream availability
before another Terra execution trial or three-tier worker changes. The optional
compatibility refresh helper remains a source candidate; no managed catalog
generation, worker payload, other host or daemon restart was part of this apply.

The subsequent [upstream check](three-model-routing-results.md#upstream-catalog-omission-localized)
confirms Bryan's restarted default owner still omits Terra. A minimal native home
and a direct authenticated OpenAI catalog GET both return the same nine models,
with HTTP 200 upstream and no Terra. Both homes select one ChatGPT account.
This excludes the repaired local config as the current omission's source;
account/workspace access, rollout and an upstream defect remain to distinguish.
Official guidance includes Terra on paid Codex plans and supports this CLI
version; the public status page reports no active incident. Keep the raw captures
and account details private, and use the prepared sanitized reproduction for
an account-specific support check when appropriate.

## Local candidate: three-model routing qualification

The 2026-11-01 [spike](three-model-routing-results.md) qualifies selected-primary
inspection through native loaded-thread metadata and an opt-in source
`codex-plus-context --primary` mode. Eight native control turns verify selection
changes/inheritance; the helper passes four live reads and rejects an archived
caller. Configured selection is explicitly distinct from execution telemetry.

Both exact Terra/XHigh inference attempts failed with `modelNotFound`, including
a retry with an owned thread's private catalog override. The managed catalog
omits Terra while the installed binary's bundled catalog includes it; the
remaining owner-cache/account/upstream cause is unresolved. Keep adaptive
routing, existing agents and Luna workflows unchanged. Both failed fixtures and
both successful controls are archived/unloaded. Follow the spike's continuation
gates before introducing a Terra worker or claiming Terra-primary escalation.

This is a local source candidate, not a release or deployment. Existing owners,
production configuration, installed selections and unrelated bytecode are
preserved. Candidate `4fe5ae6` passes 382 tests, a clean 133-file inventory and a
complete private release build/verification. The relocated context CLI works,
all 18 worker payload files are unchanged and all 375 protected files match.
The gated research pass is complete; final evidence is in the results.

## Lifecycle guide publication

Completed 2026-11-01 under Bryan's separate publish/deploy request. Reviewed
source `52ab312` and its preceding documentation commits are pushed to personal
github.com main. Pages build/deploy and Python 3.11/3.14 validation pass; each
Python job ran 376 tests and verified a complete release build. The deployed
14-file site matches the reviewed build, and all 13 served files return HTTP 200
with identical bytes. All 45 public browser checks pass. The agent guide is now
public at `/manage/` and its exact Markdown export at `/manage.md`.

See the [publication receipt](pages-deployment.md#agent-first-lifecycle-publication-2026-11-01).
This is a documentation deployment: no new product version/assets, runtime apply,
fleet mutation or daemon restart. Earlier fixture and native-acceptance limits
remain unchanged. The local-candidate sections below retain their dated scope.

## Lifecycle review and refinement

Completed 2026-11-01 against the local lifecycle candidate. The guide now routes
read-only and partial installations explicitly, pins the public GitHub host and
preserves custom monitoring bounds/allowlists as well as paths and policy. The
builder preserves attributed table cells, checks that all seven rendered action
requests appear exactly once and gives copy buttons distinct accessible names.

All 61 targeted tests and 45 browser checks pass. The three new regressions fail
against the previous builder. Released preview.13 generators pass five custom
configuration checks; a host-pinned metadata download succeeds with an inherited
enterprise host. The site still has nine HTML guides, an identical raw Markdown
export, 299 checked local links and 15 consistent current-release claims. See the
[review receipt](lifecycle-guidance-results.md#review-and-refinement-2026-11-01).

No new native actors, watches or messages were created, and the earlier idle
ephemeral fixture was not touched. Runtime sources, production configuration,
installed selections and active processes are unchanged. That review left a local
candidate; the publication receipt above records its subsequent deployment.

## Completed local pass: agent-first installation and maintenance

The [selected plan](codex-plus-plan.md#completed-local-pass-agent-first-installation-and-maintenance)
is complete as a local candidate. [The agent guide](manage-agent.md), `/manage/`
and its exact `/manage.md` export now provide seven short lifecycle requests.
README, landing and setup lead to that route; the human overview and component
references remain available. Existing archive installers and configuration owners
remain in place. Plugin migration is parked; its evidence below remains valid.

Candidate `e1b2d17` replaces moving-main worker setup with verified release
provenance and documents preservation/defer paths for cleanup and uninstall.
Both published preview.12/.13 artifact sets verify. Eighteen disposable lifecycle
checks, three failed-upgrade assertions and four synthetic manager assertions pass.
A fresh owned native actor completed read-only inspection from the short prompt;
agent-led installation and native MCP activation remain unqualified. The final
site passes 27 browser checks and all 58 relevant existing tests. See the
[full results and limits](lifecycle-guidance-results.md), including the corrected
first-trial collector failure.

The successful durable actor is archived/unloaded. One initial ephemeral test
thread remains loaded and idle: native archive/resume/delete reject its missing
persisted rollout, and unsubscribe from a new connection leaves it loaded. No
daemon restart was attempted. Owned preview servers and the manual MCP child are
stopped; all 596 protected paths and 13 baseline process identities match.

That preparation pass committed the candidate locally and performed no production
installation, watch, peer message, push, publication, deployment or restart.
The publication receipt above records its subsequent deployment without a runtime
release or fleet repin. The prior plugin documentation commits and existing
untracked bytecode files remain preserved.

## Plugin exploration: isolated installation works; migration deferred

The [plugin distribution-fit loop](codex-plus-plan.md#completed-exploration-native-plugin-installation-and-distribution-fit)
completed 2026-11-01 with a defer-migration recommendation. Native CLI 0.166.0
installs, lists, rolls back, upgrades and removes the private candidate without a
desktop app or new daemon. Forty unchanged release source files plus two portable
manifests form a reproducible local candidate; native installation preserves its
bytes/modes. Manual installed-payload stdio probes discover 17 monitoring/four
reporting tools and publish/retrieve a private report with hosting disabled.

Version changes delete the previous cache directory. Captured stdio servers keep
answering, but the removed version's helper path cannot be launched. Safe native
active updates are unqualified. The existing owner sees the private-home plugin
as uninstalled/disabled; no supported private installation scope on that owner
was qualified. Caller metadata, native policy/coexistence and the dependent
A-watches-B trials remain open. No native actor was created. See the
[full evidence and remaining scope](reliability-packaging-results.md#plugin-installation-follow-up-isolated-cli-and-lifecycle-gates).

All 596 protected paths and 13 baseline native/report process identities match.
The private install/marketplace are removed, both owned stdio processes closed,
and the private report/candidates retained. Workers, preview.13 managed selections,
production config and active owners are unchanged. Official local-MCP directory
submission separately requires partner allowlisting; our eligibility is unknown.
No runtime code, new installer, publication, push or managed deployment is part
of this research result.

## Preview.13 publication and rollout

Completed 2026-11-01 under the [selected plan](codex-plus-plan.md#completed-pass-preview13-publication-and-preservation-first-rollout).
Release source `5e6c9dd` and dotfiles pin `29d4d1d` (rollout receipt `8b191e6`) are published. Snap OSS/work,
Starship and Carbon select verified preview.13 workers, monitoring and reporting.
Both installed doctor formats and fresh MCP protocol discovery pass in all four
contexts. All 369 tests pass on Python 3.11/3.14; five fetched assets match two
reproducible builds and relocated qualification. Release CI and public guide
checks pass independently. See the [full receipt](reliability-packaging-results.md#preview13-publication-and-managed-rollout).

All 1,349 protected paths are preserved except the three intentional worker
version/provenance metadata updates; all 26 recorded native/report process
identities and HTTP baselines match. Canonical chezmoi sources have the scoped pin
commit and empty target diffs while preserving divergent history and 25/0/2
unrelated dirty paths on Snap/Starship/Carbon. No daemon/report-server restart or
global MCP refresh occurred. Loaded MCP processes reconnect normally; this
conversation still reports preview.11 against selected preview.13. Ordinary-use
follow-up acceptance remains open, and unified plugin distribution stays deferred.
The earlier local-candidate scopes below are historical.

## Current scope and entry points

The [release-claim boundary correction](reliability-packaging-results.md#review-correction-release-claim-boundaries)
completed 2026-11-01 under the
[selected plan](codex-plus-plan.md#completed-pass-release-claim-boundaries-and-candidate-readiness).
Candidate `b45728b` checks published and managed guide declarations independently
of source artifact versioning, accepting release/rollout lag and rollback while
rejecting contradictory claims. Self-contained fixtures repair the direct Pages
test invocation. All 369 tests pass on Python 3.11/3.14; both direct Pages tests
and discovery work without `PYTHONPATH`. Three external guide builds verify all
15 claims and 234 links/assets/anchors each; 24 focused browser checks pass.
The clean 130-file inventory and worker checks pass. All three component source
inventories and the two preserved bytecode files are unchanged. No native actors
or new artifact qualification were needed. Commits remain local; push, version
selection, publication and managed apply are separate actions. The earlier
364-test/artifact receipt below retains its original candidate and dated scope.

The [everyday reliability and native packaging pass](reliability-packaging-results.md)
is complete as a local candidate. Current-release claims are corrected and checked
by the Pages builder; the existing doctor adds opt-in `--human` while retaining
default JSON and its exit behavior. Code candidate `bceda12` passes 364 tests on
Python 3.11/3.14 and reproducible relocated archive checks. It retains the source
version constant only for private validation; it must not replace preview.12's
published assets. The final tracked-file inventory is 130 files.

Native plugin discovery works but prefixes skill names; worker registration and
installed-plugin caller metadata remain unqualified. The decision is partial fit:
retain archives/chezmoi and defer unified plugin distribution. Selected diagnostic
and historical incident evidence does not complete real-work follow-up acceptance.
This pass starts no native actors, model turns, watches or messages. All 1,349
protected paths and 26 recorded native/report process identities match baseline.
Preview.12 remains selected; publication, push and deployment are separate gates.

The separately authorized review follow-up closes ordinary endpoint setup and
live cancellation with three completed owned native turns on Snap OSS 0.166.0.
The source kept running after its one change callback and stopped only after the
explicit request, before expiry and below its event limit. A post-stop endpoint
change produced no reads or callbacks during 30.3 seconds. The fresh actor is
archived/unloaded and its endpoint/controller are closed. See the
[follow-up evidence](native-qualification-results.md#review-follow-up-ordinary-setup-and-live-cancellation).
Preview.12 source `f6ec874` includes the attention correction and explicit
preview.11 monitoring/reporting verification and rollback support. Publication
and scoped managed rollout completed on Snap OSS/work, Starship and Carbon.
All five fetched assets match two builds; 354 tests, Python 3.11/3.14 CI, public
Pages delivery and actual browser checks pass. Installed payloads and fresh MCP
protocol discovery verify preview.12. All 1,186 protected paths and 26 recorded
native/report process identities match baseline. Default chezmoi sources now
select this release while retaining unrelated edits and divergent local history.
The full dotfiles check passes Plus gates, then encounters the unchanged OpenCode
`--pure` failure. See the
[publication and rollout receipt](native-qualification-results.md#preview12-publication-and-managed-rollout).

The initial [native qualification and operational clarity pass](native-qualification-results.md)
completed 2026-10-31 within the [selected plan](codex-plus-plan.md#planned-pass-native-qualification-and-operational-clarity).
Two owned independent conversations used 17 native turns across the installed
preview.11 run and one affected repeat on the existing Snap OSS 0.166.0 pair.
Peer messages, blocker follow-up, normal MCP inspection, a reminder, fresh recap,
explicit stop, invented clean recovery/history and foreground interruption have
their scenario limits in the results. Both actors are archived/unloaded, queues
are empty and no fixture process remains. The observer's initial invocation
failure and conflicting fixture limits are retained; the repeat's command watch
was registered by the controller CLI, not by a natural-language actor request.

Correction `9804d99`, now released in preview.12, removes explicitly cancelled terminal source
errors from current watch attention while retaining history and unresolved
delivery. That pass passed 353 tests, a regression that failed before the fix, two
identical package builds and relocated CLI/MCP discovery. Native candidate
inspection confirmed zero current entries and preserved error history. All
139 protected local paths and 13 baseline native/report-related process
identities match baseline; selected releases, private configuration and the two
untracked bytecode files are preserved. Publication, release-version selection,
push and chezmoi rollout were outside that initial pass; the receipt above records
their subsequent completion.

The initial overview's read-only checks found Snap OSS's selected preview.11 manifests
valid and this conversation's two MCPs reporting preview.11. Both CLI and owner
reported native 0.166.0; general compatibility remains unestablished, with bounded
scenario evidence now recorded above. Snap OSS reporting now verifies over HTTP
200, and the public landing/architecture
pages return 200 with preview.11 content. This refreshes those local facts only;
it does not attest loaded payload bytes or re-audit Snap work, Starship or Carbon.
The October 29 rollout and native qualification records retain their dated scope.

That initial pass's final validation passed the clean **129-file inventory**, worker checks,
18 Pages tests, five inventory-check tests and whitespace checks. The external
walkthrough/eight-guide build verifies 234 local links/assets/anchors and public
metadata. The runtime's 353-test gate used Python 3.14.8; that initial pass started no new
CI or public deployment. Canonical `scripts/check` fails only on the two preserved
bytecode files; its clean tracked-file candidate passes. The earlier planning
gate's 128-file inventory and 234-link build remain documentation-only evidence.

The separately authorized 2026-10-29 release pass completed review corrections,
the 351-test source gate, Python 3.11/3.14 CI, reproducible/fetched artifact verification and
scoped managed rollout. Preview.11 source `5c9ec1d` includes strict boot-evidence
and journal classification checks added after the closed native sample. All four
installed contexts report 17 monitoring/four report tools in fresh protocol
discovery. All 252 protected paths and native Codex process identities are
preserved. HTTP baselines are unchanged, including already unavailable Snap OSS
and Carbon endpoints. See the [full receipt](owner-recovery.md#preview11-publication-and-managed-rollout).

Codex Plus supplies bounded observation, later checks, same-daemon peer
coordination and independent static reports around native Codex. Native Codex
owns its conversations, goals, execution policy and daemons. Worker workflows
remain explicitly invoked; a generic goal loop does not activate them.

The selected [owner-recovery pass](owner-recovery.md) follows the 2026-10-29
investigation. It implements explicit clean same-thread rollover, bootstrap
diagnosis and immutable inspectable history, while refusing live or uncertain
work. The initial source loop completed with
348 passing fixture tests, reproducible relocated packages and seven completed
owned native turns on 0.165.0. Two fresh messages were handled; old unknown turn
outcomes remained unknown. The actors/helpers are closed and the original owner
and real incident archives are preserved. No recovered incident
state was replayed; that source loop changed no existing owner or managed
installation. The recovery document records the qualified artifact revision and
evidence limits separately from the subsequent release/rollout above.

The earlier **preview.10 publication and managed rollout completed**. Release source
`078c630` supplied workers, monitoring and reporting under one tag; dotfiles main
`49cfc41` selected it on Snap (OSS/work), Starship and Carbon. All manifests verified,
scoped diffs converged and fresh MCP protocol discovery reported preview.10 with
15 monitoring/four report tools. All 39 recorded native/MCP/report processes,
265 protected paths and four HTTP report endpoints match the starting baseline.
No daemon/server restart, global MCP refresh or new native model trial occurred.
See the [full receipt](refinement-results.md#preview10-publication-and-managed-rollout).

The [documentation follow-up](site-polish-results.md#source-documentation-follow-up-2026-10-22)
completed 2026-10-22 after the recap fixes. It reconciles source/release availability
across the entry points and guides, and adds a fifth illustrative catch-up scene.
All 20 authored scene states pass actual candidate browser checks at desktop,
tablet and narrow mobile widths, alongside the eight guide routes and controls.
That local pass preserved runtime, worker and skill bytes. The authorized
publication packages the reviewed work as preview.10. Public delivery/browser
and managed rollout checks passed independently, with no historical trial replayed.

The [native alignment and natural follow-up pass](native-alignment-results.md)
completed 2026-10-22 after Bryan's project review and goal-loop request. Its source
candidate bounds reminder history, rediscovers outgoing receipts through the
existing tool, refines recap/quiet-follow-up guidance and adds native MCP version
metadata to the doctor. The 15-tool monitoring surface and native ownership stay
intact. Owned synthetic trials supply bounded 0.163.0 evidence; the candidate is
included in preview.10. Managed deployment remains outside that research pass.

The review follow-up fixes two recap gaps: acknowledged reminder callbacks stay
visible while their outcome is unknown or needs attention, and outgoing receipts
include the stored message kind and a bounded quoted purpose. Explicit reminder
cancellation closes known failure attention while preserving native work and
history. Five new regressions bring the fixture suite to 317; these fixes add no
new native-runtime qualification. See the [review results](native-alignment-results.md#review-corrections).

The completed refinement pass fixes status freshness, reminder expiry and bounded
watch history; adds full fixture CI and read-only installation diagnosis; and
unifies workers, monitoring and reporting under **v0.1.0-preview.9**. See
[the refinement results](refinement-results.md) for source/artifact/publication
acceptance and the subsequent scoped managed rollout. The documentation passes below are
completed context, not the current execution scope.

Start with [setup](getting-started.md), the [daily guide](daily-use.md), [worker workflows](workers.md), [architecture](architecture.md),
[environment contract](environments.md) and [public walkthrough](https://dev.byebyebryan.com/codex-plus/).
The [implementation plan](codex-plus-plan.md) records the selected scope and completed
contracts; the [reconciliation results](reconciliation-results.md) record the earlier
environment/documentation pass. The [historical checkpoints](implementation-history.md) preserve
older migration, notification, rollout and acceptance evidence.

The [site polish pass](site-polish-results.md) adds the component-based setup
path, a fourth illustrative scene for Luna and publication/navigation refinements.
Its source and publication acceptance remains separate from runtime qualification.
That pass is complete: eight HTML guides and 16 illustrative scene states passed
actual public delivery/browser checks at desktop, tablet and mobile widths.
The publication workflow uses pinned Pages actions on Ubuntu 24.04; its build and
deploy completed without annotations. Only the pre-existing untracked bytecode
remains outside committed source.

The repository-discovery follow-up makes the HTML site prominent in the README,
pairs all eight guides with their Markdown sources, and aligns guide/repository
navigation and GitHub metadata. Its plan and acceptance belong to the same
[polish results](site-polish-results.md). The follow-up is complete: Pages
deployed successfully without annotations, all 11 public pages/assets matched
the candidate bytes, and actual GitHub/Pages desktop and mobile checks passed.
Runtime, agent and skill files and the pre-existing bytecode are unchanged.
Continue with ordinary use and its evidence.

## Source, releases and installed state

| Layer | Release/rollout fact recorded 2026-11-01 |
| --- | --- |
| Published unified release | v0.1.0-preview.13, source `5e6c9dd`; one version, tag and release manifest, with optional worker/monitoring/report archives. All five fetched assets match two reproducible builds. |
| Managed upgrade | Dotfiles pin `29d4d1d` is published; scoped rollout and canonical source synchronization completed on all three hosts while preserving divergent history and unrelated work. |
| Earlier artifacts retained | Preview.12 source `f6ec874` and earlier runtime/report releases remain available for captured processes and rollback; new installers verify actual preview.12 archives. |
| Snap | All three preview.13 payloads, both doctor formats and fresh 17/four-tool MCP discovery verify in OSS/work; both HTTP endpoints retain identical 200 catalog bytes. |
| Starship | All three preview.13 payloads, both doctor formats and fresh MCP discovery verify; private configuration, native owners, old releases and HTTP bytes are preserved. |
| Carbon | All three preview.13 payloads, both doctor formats and fresh MCP discovery verify; private configuration and native owners are preserved; HTTP was already unavailable. |
| Native compatibility | Bounded earlier owned Snap OSS trials on 0.166.0; release baseline remains 0.162.1. Installed protocol discovery is separate from blanket compatibility or long operation. |
| Source | Readable doctor output and independent published/managed guide checks; preview.12 verification and rollback remain available. |
| Notification delivery | Native Codex to terminal. Formatting belongs to Kitty/chezmoi. Enrichment and the 349 inspector are parked/retired. |

Source documentation may advance beyond the selected immutable artifacts.
Existing MCP processes keep their captured code until normal reconnect. The
[runtime guide](runtime-distribution.md) and [report guide](html-report-usage.md)
explain optional component installation, serving and rollback under one release.
`scripts/codex-plus-doctor` checks selected manifests and native version evidence
without starting services. Preview.10 can also read reported MCP
versions for one positively loaded conversation. Selection or reported versions
do not establish loaded payload bytes; absent metadata remains unknown.

## Snap environment contract

| | OSS | Work |
| --- | --- | --- |
| Native command | `codex`, `codex agents` | `codex-work`, `codex-work agents` |
| Home | `~/.codex` | `~/.codex-work` |
| Explicit monitoring root | `~/.local/state/codex-plus-oss` | `~/.local/state/codex-plus-work` |
| Explicit report config | `~/.config/codex-plus/report.toml` | `~/.config/codex-plus/report-work.toml` |
| Report endpoint | `http://snap:8787/reports/` | `http://snap:8788/reports/` |
| Company MCPs | Omitted | Snap Bridge and gateway enabled |

The same account uses independent auth caches and native owners. This is
configuration separation under one Unix user, not a security boundary. Do not
recreate `codex-oss` or move the retained history. Private config and wrappers
belong to chezmoi; Codex Plus does not install a profile registry or migrate data.
Its canonical-home defaults apply only where explicit paths are absent. Pass the
actual overrides to `codex-plus-context` when diagnosing this managed setup.

## Acceptance and remaining work

The deployed environment pass verified both fresh MCP entry points, separate
stores, exact installed manifests, company-MCP admission and both HTTP endpoints.
The earlier native acceptance covers bounded watches, messages, inspections,
continuation and explicit stop on owned synthetic sessions. Those facts do not
establish provider recovery, long unattended reliability or personal UX.

The refinement release passes 303 fixture tests locally and in Python 3.11/3.14
CI, reproducible artifact verification, relocated CLI/MCP discovery, old-artifact
verification and public guide delivery/browser checks. Managed installation is
qualified in disposable Snap/Starship profile homes, including all three aligned
manifests, script-excluded apply and convergence. The subsequent user-authorized
rollout applied only selected Codex Plus targets on Snap and Starship, with
chezmoi scripts excluded. Payloads verified before selection; source edits,
private configuration, worker bytes, native/MCP processes and report serving were
preserved. All three report endpoints retained HTTP 200 and identical content.
See the [rollout receipt](refinement-results.md#managed-rollout-2026-10-22).
That managed rollout performed no service restart, global MCP refresh or new
native model trial.

The subsequent natural-follow-up source candidate, including review corrections,
passes 317 fixture tests.
Owned trials cover contextual peer choice, message handling, a known blocker, a
later configured MCP check, explicit stop, actual compaction and foreground
interruption that preserves observation. Helper loss is reported as uncertain;
expired recovery refuses. See the [results and limits](native-alignment-results.md)
before extending those claims.

Use the [soak checklist](soak-checklist.md) during ordinary work. No pending
historical trial, actor budget or wakeup should be replayed. Do not create a
watch, message, model workload or notification experiment merely to refresh docs.

## Continuation and validation

Commit directly to main, preserving concurrent edits. Prefix shell commands with
RTK. Run `scripts/check`, the meaningful test suite, `git diff --check`, and the
Pages builder outside the checkout. Presentation changes need actual browser
checks of scene state, environment selection, controls and desktop/mobile layout.
Public Pages deployment is separate from immutable report publication and from
managed runtime deployment. Retain source/artifact/installed/live evidence levels.
Do not restart native owners or report servers, repin workers, change credentials
or perform managed applies without a task that calls for those actions.
