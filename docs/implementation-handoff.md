# Implementation handoff

Updated 2026-10-12 for Bryan's continuation on Snap in
`/home/bryan/code/codex-plus`. The agreed research-to-local-candidate loop is complete;
its corrective unattended pass is also complete. Human acceptance and installation
remain subsequent scope.
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

## Next pass after review

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
