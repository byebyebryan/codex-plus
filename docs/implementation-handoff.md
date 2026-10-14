# Implementation handoff

Updated 2026-10-13 for Bryan's continuation on Snap in
`/home/bryan/code/codex-plus`. The operational source-access/refinement loop is
complete, including published preview and pushed managed distribution. The two-host managed rollout is now executing; a real-source pilot and personal
UX acceptance remain separate scope.

## Current pass: managed activation on both hosts

Bryan selected the [two-host rollout plan](codex-plus-plan.md#next-pass-managed-installation-and-activation-on-snap-and-starship)
and required preserving active work with no daemon restart. Host-scoped managed
availability and nine control approvals are published as dotfiles fa6c9c0. A tested
`codexPlusOnly` apply option preserves unrelated live config values, including
Starship's pending legacy cleanup. Full/component validators passed.

The five runtime/config target groups are installed on Snap and Starship from the
existing preview.2 release. Both payloads match the fetched checksum, manifest,
19-file inventory and modes. Ordinary fresh native TUI sessions found all 15 tools
and successfully called the installed watch_list without per-thread MCP injection,
a global reload or owner replacement. Snap's pre-existing state root required
permissions narrowed from 0755 to 0700; its contents were preserved.

Acceptance writes target fresh owned synthetic actors only. Snap's first broader
batch stopped at a provider-capacity error before messaging or observation began;
its two actors and fixture process were closed without replay. Starship's independent
bounded scenes are in progress. Its canonical divergent/dirty checkout remains
outside the clean pinned deployment worktree. New concurrent Snap Observer edits
are preserved. No prior allowance or closed study actor is reused.

## Current source-access and distribution pass

Bryan selected an ordinary goal loop from 8900175 to remove the blanket offline
restriction and qualify his endpoint/MCP monitoring workflows. The
[execution report](source-access-pass-results.md) records permission tests,
installed native acceptance, corrected findings and separate distribution gates.
Workers retain their identities and explicit invocation; no worker skill was
activated and no delegation was used.

Command sources inherit the exact loaded caller's effective native permissions,
including existing networking and authorized private cache writes. Read-only and
network-off choices narrow access; network-required checks an existing grant.
Periodic short commands and continuing scripts can observe without inference per
poll. MCP checks use scheduled native model turns under normal tool permissions;
direct calls are excluded after controlled qualification exposed an approval bypass.
Each MCP check therefore has model cost.

Installed endpoint acceptance passed authenticated reads, quiet filtering, useful
handling, foreground/earlier-human ordering, draft preservation and natural stop.
Scheduled MCP acceptance passed an executed slower-cadence successor and stop.
Timed reassessment performed an actual configured inspection. Missing approval and
in-flight cancellation have explicit native evidence. Named profiles retain offline
coverage; real authentication/provider failures and long operation remain separate.

The final runtime candidate is v0.1.0-preview.2 at
`2274f4b54817fae88c3762c39c1284b8b1eb2695`, with 19 files plus its manifest.
All 206 offline tests and the 69-file inventory pass. Publication and fetched-byte
verification passed. Focused chezmoi wiring is
validated and pushed as 1bac126, including full/component checks and scoped dry-run.
All 21 owned actors/helpers/viewers/fixture services are closed; the combined batch
used 31 turns (29 completed, two cleanup interruptions), nine automatic events,
54 HTTP fixture calls and ten MCP fixture calls. Original owner/requester remain
preserved. At that pass's finish, canonical dotfiles stayed at 271b35d with seven
concurrent files unchanged; published main contained the rollout. The subsequent
checkout reconciliation below supersedes that working-checkout state.
The selected finish leaves live apply/enablement deferred. The source/tag revision
identifies qualified runtime bytes; later documentation commits do not repin them.

The isolated dotfiles worktree reconciles the surviving 1c17dd5 integration onto
current published history 271b35d. Preserve concurrent canonical SSH, Claude and
Codex edits. Existing real conversations and the original daemon remain untouched;
experimental writes use fresh owned actors. Earlier native allowances remain closed.

## Checkout reconciliation after HTML report integration

Bryan subsequently requested reconciling published HTML-report work and the
canonical checkouts' pending edits. Source main was fast-forwarded to bad5565,
which includes both report PRs and all earlier monitoring work. The watch runtime
files, existing worker files and immutable preview.2 pins remain unchanged.

Canonical chezmoi main was rebased onto published history. All five local report
commits were skipped because equivalent patches were already upstream. The pending
Observer/Mesh selection and launcher edits matched published main and resolved
without a residual diff. Original commits and pending-file recovery copies were
retained privately before reconciliation.

The remaining source changes are committed and pushed separately: e5d5842 manages
shared SSH COLORTERM forwarding while preserving local config, and 5806533 retains
idle Codex threads for one hour and enables Claude's left-arrow agent navigation.
The SSH validator is included in the full dotfiles check. Full/component checks,
SSH parsing/preservation checks and scoped status/diff/dry-run passed. No live apply
or daemon restart was performed. Codex/SSH live targets remained unchanged; active
Claude runtime state was preserved rather than restored from a stale snapshot.

The sections below retain completed-pass and historical planning evidence.

The earlier review/refinement/packaging/distribution loop completed. Its
[final report](distribution-pass-results.md) records the published
[v0.1.0-preview.1 runtime](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.1)
at `f4db934`, 177 passing tests and 65-file source inventory, verified fetched
runtime/source bytes, 12 deliveries / 42 native turns (40 completed, two cleanup
interruptions) and the retained native requalification limits. The runtime includes
formal event receipts, outgoing message cancellation and complete timer controls.
Its readable event frame retains one compact receipt hint; native hidden-output
delivery remains unqualified for the established ordering contract.

The isolated dotfiles rollout is prepared as `1c17dd5` on local branch
`codex-plus-preview-n91wsqir`, with full/component validators and scoped dry-run
passing. It is not merged/applied; the runtime is optional and disabled by default,
preserving local preferences. All 17 experimental actors/helpers/viewers are closed,
and the original daemon/requester are preserved. The final report separates current
release facts from the historical checkpoints below. The runtime artifact/tag stays
at `f4db934`; subsequent main-branch handoff edits do not repin tested runtime bytes.

The review/refinement/packaging/distribution plan has now been selected for an
ordinary goal loop from `755855e`. The [execution report](distribution-pass-results.md)
records prioritized findings, refinement and separate release/install gates.
Selected finish: publish a verified preview and prepare validated managed rollout;
live apply is deferred. The prior native batches remain closed. Preserve concurrent
dotfiles edits and use fresh owned actors within the new 24-delivery/48-turn ceiling.

Bryan has now requested planning a substantial **review/refinement/packaging/
distribution** loop. The [new loop contract](codex-plus-plan.md#next-loop-review-refinement-packaging-and-distribution)
starts with a prioritized review, completes stoppable model-facing timer controls,
qualifies installed guidance/tool loading, and verifies the package independently
of this checkout before publication. Default finish: published preview plus a
validated managed-rollout change; live apply is deferred unless the deployment
finish line is selected. This is a planning checkpoint, not a new execution goal.

Current local candidate is `01c1c70`; freshly queried GitHub main and this host's
chezmoi manifest/checker still select `56b7158`. Preserve the existing archive and
worker identities. Concurrent dotfiles edits include the portable Codex template
and validator, so isolate release work and preserve unrelated source/live drift.
The proposed fresh native ceiling is 24 deliveries / 48 turns across all stages;
the previous 7-delivery/24-turn batch remains closed. Runtime upgrade protection,
installed-path activation and rollback are explicit gates. Real sessions remain
read-only sources; experimental writes use fresh owned actors.

The completed local interaction pass is
[natural requests and readable peer communication](codex-plus-plan.md#next-pass-natural-requests-and-readable-peer-communication).
Bryan has now assessed the controlled walkthrough as hard to follow: watch prompts
exposed timing/condition recipes, sending depended on an exact destination title,
and JSON event prompts cluttered the conversation. Technical lifecycle evidence
stands; everyday interaction acceptance has not passed. Bryan subsequently requested
execution as an ordinary goal loop with the established incremental-commit practice.
The [current pass report](interaction-pass-results.md) records qualification,
implementation, native acceptance and the closed combined experiment allowance.

The pass qualified a reusable model-facing interface, contextual independent-peer selection,
readable attributed delivery and separate observation/information/request meaning.
Installed 0.162.1 schemas include standalone tool output and dynamic tools, but
native rendering and ordering/control compatibility were gates before adoption.
Native qualification now selects a session-local stdio MCP interface and readable
text through the qualified queue. Standalone tool output joined an active foreground
turn despite earlier queued human input, so it is not selected for this coordinator.
Caller thread/turn metadata was observed; sender identity and acknowledgements must
use verified native context. Requests within the receiver's existing task are the
recommended first scope; new-task delegation is a separate pending scope choice.

The source-local interface is implemented in `codex_plus/model.py` and
`codex_plus/model_server.py`, with `scripts/codex-plus-model` and readable queued
events. All 162 offline tests and the 59-file inventory pass. Contextual references,
native caller/turn binding and distinct handling outcomes have regression coverage.
Fresh native actors selected a peer from ordinary work context, handled one useful
watch callback with a fresh read and native-context acknowledgement, preserved an
unsent draft through readable information delivery, accepted/declined existing-task
requests, checked cached handling without ping-pong, and stopped a pronoun-selected
watch. Read-only callers used accurate tool hints and explicit fixture-only approval
settings; no global configuration or filesystem-sandbox relaxation was required.

The combined recipe closed at 7 deliveries / 24 turns (23 completed, one qualification
cleanup interruption), with zero provider failures. All eight experimental actors,
owned sources/coordinators/bridges/viewers are closed; the original owner and this
requesting conversation remain preserved. The report distinguishes harness errors,
partial watch-draft capture and carried-forward lifecycle evidence. A
[primary-driven fresh demonstration](watch-candidate.md#current-primary-driven-interaction-demonstration)
is prepared for Bryan's assessment; it needs a new allowance and new actors. See the
[model interface guide](watch-candidate.md#session-local-model-interface) and current
pass report for attachment scope. Nothing is installed or globally enabled; everyday
UX acceptance and broader new-task delegation remain pending.

Read this first, then the [implementation plan](codex-plus-plan.md). The plan
defines milestones; this handoff explains why they were chosen and what the
research does and does not establish. Recheck live versions, endpoints and Git
state at the start of implementation.

The latest [Claude monitoring context](claude-monitoring-context.md) records the
design correction and selected Snap history inspection. It broadens the earlier
JSON-snapshot-only proposal into monitoring plus model-controlled wakeups; the
local surface is now implemented in `codex_plus/` with
`scripts/codex-plus-watch`. Read [the candidate guide](watch-candidate.md) and
[current evidence](coordinator-loop-results.md) before using it. Published and
installed worker files remain unchanged; this helper is local source only.

## Discovery and peer watches: automated pass complete

Bryan's latest planning direction is to use inter-session coordination as the
next watch acceptance case: **session A observes session B and follows up, with
both existing, loaded sessions inside the same owning daemon**. Either may be
idle or busy. The subsequent ordinary goal loop delivered the local surface and
closed its bounded synthetic native recipes. See the
[discovery and peer-watch plan](codex-plus-plan.md#next-pass-discovery-and-peer-watches).

Bryan has now requested execution as an ordinary goal loop with incremental
commits. The [peer-watch report](peer-watch-results.md) records qualification,
implementation, review and native acceptance. All 128 tests and the 52-file inventory
pass. Combined native usage was 8 admissions / 14 turns with zero provider failures;
the report distinguishes the first harness timing failure from the passing targeted
recipe. All owned fixtures/coordinators were settled; the original owner and requester
were freshly verified preserved. Human TUI acceptance remains pending.

A subsequent controlled native TUI walkthrough is now complete. Bryan watched
Snap's A/B viewers over SSH from Starship and requested primary-driven controls.
The fresh recipe used 8 admissions / 16 turns: 15 completed, one interrupted with
Esc, zero failures. Native draft preservation, post-Esc follow-up, scoped stop while
B kept working, viewer detach/reattach and shutdown preview/cleanup passed. A setup
message also exposed a scope boundary: delivery could not override A's earlier
direct instruction not to start a watch. See the
[walkthrough evidence](peer-watch-results.md#controlled-native-tui-walkthrough).
All helpers and the event keeper are stopped; only idle synthetic viewers remain
for inspection. Personal UX assessment, human input ordering and independent-peer
task assignment authority remain open; native `/exit` protection is not implemented.

Bryan explicitly permits monitoring/watching existing active sessions with no
writes or interruptions. Passive discovery and bounded reads may use those sessions;
messages, queued follow-ups, goal changes, interruption and other state-changing
checks use task-owned synthetic sessions. A synthetic A may watch a real B, provided
all experimental delivery goes to synthetic A and B remains read-only. Raw session
data stays private. This permission refines the active execution recipe.

Carry forward the ordinary-session message/reply evidence. The original follow-up
note records successful independent-session replies and a discovery correction:
query the actual daemon's loaded inventory, then bounded metadata, instead of
searching saved names. The later watch batch also found a CLI-created thread
reported as `source=vscode`; a CLI-only source filter missed it. The newer native
task-tool facade was inspected/listed but not fully exercised. Qualify only the
remaining facade or integration gaps rather than repeating basic transport research.

Ordinary "tell agent B" discovery selects independent sessions. Delegated child
threads stay out of normal peer matching; explicit hierarchy inspection can show
them under their parent. Use native delegation provenance/relationships, keep
unknown classification visible, and distinguish independent forks from delegated
children. Native parent-child orchestration remains responsible for child results.

The implemented slice supplies passive peer discovery/read, exact resolved native
message registrations and selectable peer snapshots through the existing coordinator.
Current command sources cannot be assumed to access the daemon socket or native
MCP tools under their restricted policy. Freeze B's observation identity separately
from A's delivery identity; both must refer to the same positively verified owner.
Use selected peer progress/result/input-needed evidence, not idle or child completion
as a universal task-completion signal. Model-selected signals, cadence and follow-up
remain choices. Human draft/TUI acceptance stays explicitly pending when unattended.
The [peer TUI checklist](watch-candidate.md#deferred-peer-tui-walkthrough) now has
controlled technical evidence; Bryan's assessment and remaining authority/UI
questions precede separately scoped packaging/installation. Native child/fork lifecycle
and the newer task-tool facade are not newly qualified by the source implementation.

## Completed lifecycle pass after review

Read-only post-loop review reproduced two additional gaps in the current candidate:
renewing a lost source can leave `replacing` pending beyond expiry, and cancellation
skips queue reconciliation when start state is `unknown`. The existing 64 tests
still pass; they do not cover these combinations. The earlier native results
remain scoped evidence, not proof that these newly reproduced cases are correct.

The [next-pass plan](codex-plus-plan.md#next-pass-lifecycle-correctness-and-native-tui-acceptance)
proposes regressions and lifecycle fixes first, then a fresh bounded native batch
and a TUI walkthrough with Bryan. Renewal should reject an already-lost source
without mutating intent; owner loss during renewal must settle a bounded attempt
without claiming an unconfirmed stop. Cancellation/shutdown should reconcile exact
owned pending input independently of an uncertain start outcome. A real-source
pilot follows acceptance; its source is not selected. Bryan has now requested an
ordinary goal loop with incremental commits, completing as much as possible
unattended and deferring manual steps. Its objective covers the automated slice,
cleanup and prepared human/pilot handoff; direct human acceptance remains pending.
The prior goal and native batches remain closed.

The corrective automated slice now resolves those gaps, plus bounded/inspectable
renewal attempts and retries, pagination-aware withdrawal, shared shutdown cleanup
and late deadline boundaries. All 94 tests pass. Its fresh native batch closed
at 4 admissions / 5 turns with no capacity failures, and task-owned cleanup and
original-owner preservation were verified. See the
[corrective evidence](coordinator-loop-results.md#corrective-unattended-pass-automated-acceptance-complete)
and [prepared manual handoff](watch-candidate.md#deferred-tui-walkthrough-and-real-source-pilot).
Earlier paragraphs preserve the planning/review sequence; they are not unresolved
implementation findings. Manual TUI acceptance and real-source selection remain
deferred at Bryan's request, outside this completed unattended objective.

## Accepted direction and preferences

**Native Codex CLI/TUI, background follow-up first, coordination next.** Preserve Bryan's
planning without plan mode followed by goal-loop work, long-lived inspectable
conversations and normal human input. Add small capabilities; leave task
strategy with the model. He dislikes opinionated workflow packs and does not
want a replacement frontend or another mandatory planning process.

Bryan's explicit tenet is to give the model control and options for setup, using
rigid rules only when robust and broadly generalizable. Start from Claude Code's
Monitor and adaptive scheduling, checked against his actual usage. Let the model
choose sources, scripts, filtering, cadence, renewal and follow-up within the
existing scope. Keep exact binding, process ownership, resource bounds,
cancellation and truthful receipts in the runtime.

Pi was an earlier preferred foundation, but Bryan has not personally used it.
It is now a longer-term exploration. OpenCode remains a light reference.
Claude remains a native tool outside new customization requirements; removal
of its existing Observer support has not been authorized.

The desktop app was inspected and overlaps in scheduling, remote access and
coordination. Its installed app-server and the CLI daemon were separate owners,
with an explicit writer-conflict UI. Bryan chose to stay with the CLI for now.
There is no remaining desktop comparison gate before the first watch.

Agent Observer, Mesh, Agent Plus and physical displays remain separately owned
projects. The first watcher binds an explicitly selected native thread without
an Observer dependency. Revisit Observer's public discovery/freshness contract
when coordination or fleet use actually needs it. Keep passive state publication
separate from operational actions.

## First deliverable and execution history

The completed loop qualified the full-access Linux/native `0.162.1` path and
delivered a reviewed local coordinator. Native checks cover actual event handling,
model-selected continuation, goal-held source observation, post-Esc delivery,
linked renewal, coordinator-crash recovery, explicit cancellation and bounded
one-shot wakeups. All 64 tests and the explicit 46-file inventory pass. Two batches
closed at 17 follow-up admissions and 30 started native turns, with no capacity
failures. Task-owned sources/coordinator/viewer were stopped, the synthetic goal
and queue cleared, and only the temporary trust entry restored. The original
daemon and requesting conversation were positively verified preserved.

The paragraphs below retain the research sequence. Their earlier pending claims
describe those checkpoints; the current report is authoritative for this pass.

On 2026-10-12 Bryan requested a research/spike plan first and selected simulated
work for initial tests while Claude Code handles the actual work. The plan's
[research and spike pass](codex-plus-plan.md#research-and-spike-pass) describes
the simulator controls, draft calls/receipts, phased native/offline recipes,
experiment bounds and decision criteria. Bryan clarified that Esc interrupts
the current turn, while stopping monitoring requires an explicit message.
Independent monitors remain registered; native post-interruption processing and
explicit cancellation still need qualification. Bryan subsequently
requested an ordinary goal loop to execute the pass. The
[initial results](monitoring-spike-results.md) record native source/queue/timer
evidence and a source-level prototype. Two event handling turns failed with
provider capacity errors; active-goal coexistence, executed adaptive renewal,
human TUI acceptance and daily recovery remain unqualified. The initial native
admission batch is closed; further checks need a new bounded recipe for a named gap.

The [next-spike proposal](codex-plus-plan.md#next-spike-conversation-control-and-complete-supervision)
now gives those gaps concrete cases and acceptance checks: ordinary CLI-created
thread qualification, active/stopped goals and human control first; complete
event handling and executed adaptation second; calling permissions and Bryan's
direct TUI acceptance third. The proposed batch permits twelve follow-up
admissions and twenty started model turns overall. It remains a planning draft,
with Esc interruption separated from explicit supervision stop; no new trials
have been launched. The initial helper's pause-on-interruption study guard does
not establish the desired product behavior.

Bryan also reports Claude's confirmation before exit kills background shells/tasks.
The latest [exit-protection note](claude-monitoring-context.md#exit-protection-reported-2026-10-12)
records the evidence boundary and required lifecycle distinction. Qualify native
Codex exit controls; viewer detach, explicit supervision stop and destructive
owner shutdown are separate actions. Do not silently kill background work on
viewer closure or assume the helper can intercept native `/exit`.

Bryan is now planning a substantial overnight ordinary goal loop and selected
research gates followed by a reviewed local coordinator candidate if they pass.
The [large-loop execution contract](codex-plus-plan.md#large-goal-loop-research-to-a-reviewed-local-candidate)
defines staged qualification, conditional implementation, recovery/review work,
productive fallback, two finite native batches and the morning report. It permits
24 follow-up admissions and 40 started native test turns overall, with the existing
short source/timer/protocol bounds. Bryan subsequently requested execution and
incremental commits. That pass has now delivered the local candidate; the
[current evidence report](coordinator-loop-results.md) records native results
and implementation status. The planning/first-spike baseline is committed at
`8f3b380`; preserve later concurrent changes.
Human TUI acceptance, real-source supervision and installation remain later scope.

The implemented candidate first slice is
**one host, one existing Codex thread, a model-selected read-only event source
and a model-controlled one-shot wakeup**. Deliver useful events and timed
follow-ups to the same native thread, with status, cancellation, expiry and
bounded source/delivery errors. Direct human TUI acceptance and real-source
qualification are the next checks, followed by separately scoped installation.

A model-prepared script can decide what to emit. Bounded JSON snapshot projection
is one helpful mode, not a requirement for every source. Source-specific polling,
thresholds and completion/renewal policy should remain selectable by the model.

The everyday example is: “Watch this run; tell me when it finishes or fails.”
Quiet observation avoids accidental watch-triggered turns. A useful result
produces a follow-up with normal TUI input preserved. A deliberately scheduled
reassessment can run even without a new source event; account for it separately.
The watcher observes and notifies; it does not restart or repair the job.

Use the plan's staged sequence: finish planning, end-to-end follow-up, daily reliability, then
helper/skill packaging and chezmoi installation. Python and the native queue
route are the proposed starting point. MCP can wrap a working interface later;
neither MCP nor a skill supplies background lifetime automatically.

## Evidence already available

| Evidence | What it establishes | Limit |
| --- | --- | --- |
| Original 62-trial ledger | 46 passed, 15 failed, one user-cancelled; no recorded running trial | Closed disposable study, not a product success rate |
| Codex/Pi operational cycles | Both passed scoped 45-minute cycles; Codex also passed an existing six-hour trial | No full six-hour Pi pass; further overnight study was withdrawn |
| Codex owned-runtime probes | Same-thread delivery, selected-field filtering, watches, peers and selected recovery | Several approval, interruption and cold-thread cases were mock-only |
| Ordinary-session follow-up | Correlated replies from Starship `system` and Snap `agent-observer` reached the requesting session | Native queue/SSH mechanics, not an installed peer toolkit |
| Cross-host TUI attachment | Starship TUI rendered the existing Snap thread and prompt through temporary SSH forwarding | No prompt submitted through that test client; live editing/approvals/drafts untested |
| Current native task tool surface | Desktop inspection exposed list/read/send/wait tools in the CLI; listing succeeded | Sending/waiting through those tools and fleet scope were not qualified |
| Latest Claude/Snap inspection | Current docs, installed Claude 2.1.296 and four selected main histories show model-prepared scripts, renewed monitors and explicit wakeup/stop choices | Mechanisms and selected usage patterns, not an audited production outcome or chosen Codex Plus API |

The live follow-ups are outside the 62-trial ledger. Historical mock results,
automated TUI captures and human daily acceptance must remain distinct.
Failures and cancellation are evidence, not reasons to silently rerun the study.

## Binding and delivery details

The last local CLI check returned **0.162.1**. Its queue command accepts an
explicit endpoint, exact thread ID and bounded text. The current calling
environment exposes `CODEX_THREAD_ID`; validate it and the owning endpoint
instead of copying a prior thread ID, PID, socket path or role name.

Useful read-only startup checks are `rtk proxy codex --version`,
`rtk proxy codex queue --help` and
`rtk proxy codex app-server daemon version`. The last command reports local and
running-owner versions; it is not a daemon start/restart operation. The tested
delivery syntax is `codex queue --remote <owning-endpoint> --thread <thread-id>
--message <event-text>`. Actual identity and endpoint discovery still need a
supported implementation; do not turn these placeholders into fixed defaults.

For live delivery, reuse the owner of the visible conversation. Do not create
another app-server writing the same history. The archived adapter deliberately
creates disposable owners and threads; that launch path is not the product
binding path. The TUI is a client in the tested daemon mode, so a closed viewer
does not necessarily mean a dead runtime.

Positive loaded-thread membership can validate a current binding. Idle is a
work phase, not evidence of a stopped session. Saved inventory or absence from
one loaded-list response must not be treated as a complete live census. Freeze
host/namespace/thread identity after selection and preserve unknown/unavailable
facts on failed or stale reads.

Busy delivery normally waits for the active turn to finish. **Do not keep a
turn busy polling for its own queued follow-up.** Let it settle and process
the event in the next turn. Earlier busy-wait failures are preserved in the
study; its ordinary coding probe succeeded with the settle-first sequence.

In a mock interruption probe, direct `thread/queue/add` admitted later input
without starting it until `thread/queue/start`. Requalify the chosen native CLI
route rather than assuming every admission wakes immediately. Do not override
a human or budget stop automatically.

Native enqueue is not a processing acknowledgement, and acknowledgement is
not proof of an external effect. Use stable event IDs and explicit receipt
states; native consumed queue IDs did not guarantee deduplication. Keep
ambiguous delivery inspectable and do not blindly replay it. Cancel/expiry
stop future admission but cannot promise to retract already queued input.

## Reuse the prototype selectively

On Starship, the research archive is the sibling folder `../agent-harness-research`.
It is a local archive, not a Git checkout or a runtime dependency. It is not
currently present on Snap. The Claude context note carries the latest planning
evidence; retrieve a specific Starship reference only when needed. Do not copy
or execute the entire study.

| Local archive path | Useful reference | Product adaptation needed |
| --- | --- | --- |
| `spikes/codex-tui/ops.py` | Event IDs, receipt states, selected-field projection and watch lifecycle | Synthetic roles/tools; baseline is saved before event admission, so a product must commit baseline and pending event together to avoid a crash gap |
| `spikes/codex-tui/native.py` | Initialization, `thread/queue/add`, same-thread handling and bounded transport | Starts a dedicated owner, creates threads and disables inherited capabilities; do not transplant that into ordinary-session binding |
| `spikes/common/command_observer.py` | Finite subprocess observation, timeout/output/error bounds | Restricted synthetic Python program, fixed poll count and permissive truncated-output result; complete JSON snapshots need stricter validation and owned-child cancellation |
| `spikes/common/watch_projection.py` | Quiet irrelevant-field churn, one material event and missing-field failure | Model-driven fixture driver, not a production source adapter |
| `spikes/common/watch_edges.py` | Event limits, cancellation/error and busy/unavailable cases | Synthetic peer/role setup and old launch recipes |
| `spikes/codex-tui/recovery.py` | Uncertain dispatch, processing receipts and duplicate toy effects | Demonstrates bounded mechanics, not transactional infrastructure exactly-once behavior |

Treat atomic baseline/event recording, owned subprocess cleanup and uncertainty
handling as implementation requirements, not properties automatically inherited
from the samples. Adapt the mechanics into small production modules and new
offline tests. Do not copy fixture policies, study counters or raw journals.

## Distribution and working-tree state

The GitHub repository and local checkout were renamed from codex-worker-kit to
codex-plus. Published rename commit: `56b7158a0c1019212fd51fd3f3436d29b5b0e8a1`.
The existing worker agents/skills are still the implemented bundle.

Canonical chezmoi source is `/home/bryan/.local/share/chezmoi`:

- `.chezmoiexternals/codex-plus.toml` has seven entries selecting that published
  commit. The archive checksum is
  `3abfa2c60c8b878bb00e23023b99f21f767c04094c18d5f1da03df13e6eea3a6`.
- Dotfiles migration commit: `7aa31ff60df354bc37af108e575f928eb2815b72`.
- The managed archive location remains `~/.local/share/codex-worker-kit` for
  compatibility. Agent and skill identities/install paths remain unchanged.
- The migration was published and a scoped dry-run passed; no live apply was
  performed in that rename step. Unrelated Kitty source work remains modified.
- Publish a real release before repinning. Update manifest, revision/URLs,
  checksums and matching `scripts/check` expectations together, then validate
  the requested installation scope and actual installed bytes.

The read-only continuation check on 2026-10-12 found this host's chezmoi source
still using `.chezmoiexternals/codex-worker-kit.toml` and matching checker
expectations at `ee9894f`. Its installed 21-file archive matches that revision
exactly; the two current agents and four skills match this checkout. The earlier
published rename state above is not this host's managed source state. Preserve
its unrelated source edits; the spike does not require a pin migration or apply.

**The planning and first-spike additions were checkpointed at `8f3b380`.** They
include `README.md`, `scripts/check`, `AGENTS.md`, the plan/Claude context/handoff,
`spikes/monitoring/`, separate spike tests and the initial results. Preserve them
and any newer concurrent edits. Bryan requested
source/doc synchronization to Snap, including
updating and moving its clean old `codex-worker-kit` checkout to `codex-plus`.
Continue in that checkout; a fresh clone or worktree based only on published
main will not contain these drafts. Recheck status and bytes on the current host.

The explicit inventory checker now includes these documents. Adding runtime
files requires deliberate inventory updates; keep worker metadata validation
and watch behavior tests separate. Planning checks are not watch acceptance.

## Remaining decisions and checks

The first test source will be simulated local work, as requested on 2026-10-12.
An actual local job and its host-readable status command have not been selected;
qualify one after the synthetic mechanisms are useful. Do not launch an expensive
evaluation just to manufacture a pilot.

The local surface implements source/output modes, configurable bounds, renewal,
failure and explicit-stop policy. Runtime invariants remain separate from
model-selectable task policy. Coordinator recovery has bounded native evidence;
longer operation, native-daemon restart and installed lifecycle remain later work.
A separate service does not
automatically inherit all managed MCP credentials or Codex execution controls.

Company OpenRouter access, rates, sanctioned tools, model-quality parity and
hard provider charge caps remain unqualified. The study did not prove a cost
winner. Quiet acceptance counts watch-triggered turns, separately from other
ongoing goal/tool work or research overhead.

Use short offline state-transition checks and a bounded native TUI pilot. The
original research goal is complete; do not revive it or add overnight research
gates. This handoff does not authorize controlling other running sessions,
changing provider support or deploying unrelated projects.

## Reference index

All paths below are relative to the Starship research archive. They are additional
references, not required local files on Snap:

- `docs/current-direction.md`: governing decisions and scope.
- `docs/personal-workflow-and-harness-preferences.md`: preferences and their
  evolution; older Pi-first sections are historical.
- `notes/2026-10-11-codex-daily-workflow-follow-up.md`: ordinary-session replies,
  discovery correction, command center and remote attachment limits.
- `notes/2026-10-11-codex-desktop-app-overlap.md`: desktop ownership, native task
  tool discovery and the distinction between mobile/app remote and remote TUI.
- `docs/runtime-lifecycle.md` and `notes/2026-10-10-runtime-interfaces.md`:
  ownership, transport and interruption boundaries. Old agent-tree messaging
  restrictions do not describe every newer task-control tool.
- `docs/measurement-contract.md`: quiet/event accounting, receipt meanings and
  limits of request/token/cache observations.
- `reports/spike-coverage.md` and `reports/spike-completion-audit.md`: original
  scoped evidence, real/mock distinctions and closure.
- `docs/account-tool-integration-map.md`: local versus company access limits.
- `docs/document-map.md`: broader history if a specific question requires it.

## Suggested opening instruction

> Read AGENTS.md, docs/implementation-handoff.md and docs/codex-plus-plan.md.
> Read docs/claude-monitoring-context.md for the latest direction and evidence.
> Review the local candidate and current evidence on Snap. Use Claude's model-controlled
> monitoring and wakeup choices as the reference, preserving native CLI/TUI
> ownership and the worker bundle with no initial Agent Observer dependency.
> Plan the human TUI walkthrough and a cheap accessible real-source pilot.
> Keep installation separate; do not restart the closed research batches.
