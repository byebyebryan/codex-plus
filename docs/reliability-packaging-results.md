# Everyday reliability and native packaging results

Completed 2026-10-31 under the [selected plan](codex-plus-plan.md#completed-pass-everyday-reliability-and-native-packaging).
The [review correction](#review-correction-release-claim-boundaries) completed
2026-11-01 and supersedes the initial source-equality guide check.
The reviewed reliability work repairs current-release documentation consistency
and adds readable output to the existing doctor. Native plugins are a **partial
fit**; retain component archives and chezmoi distribution. Representative real-work
follow-up remains an open acceptance item.

The separately authorized [preview.13 publication and managed rollout](#preview13-publication-and-managed-rollout)
completed on 2026-11-01. Earlier local-candidate receipts below retain their dated
scope: the initial code candidate `bceda12e3dd652bab5659ab3bcc2d1e37f28f246`
used the unchanged preview.12 constant only for private qualification and did not
replace that published tag or its assets.

The [plugin installation follow-up](#plugin-installation-follow-up-isolated-cli-and-lifecycle-gates)
completed on 2026-11-01. Native CLI installation works in an isolated home;
cache pruning and the lack of a qualified private installation scope on the
existing owner keep production plugin migration deferred.

## Documentation consistency

The setup and architecture guides incorrectly called preview.11 current after
the preview.12 rollout. Both claims are corrected. The initial Pages builder
gate compared 15 identified current-release claims against the source version and
checked that the worker guide names all four worker workflows and the separate
reporting skill. It fails before rendering when a required claim is missing or
stale. Historical release evidence remains valid.

Five regressions cover stale setup and managed-release claims, missing current
claims, named workflow coverage and legitimate historical versions. The stale
setup claim failed before correction. These focused matchers need deliberate
updates if current-claim wording changes; they are not a general prose audit or
proof of publication, installed adoption or complete semantic accuracy.

## Review correction: release-claim boundaries

Completed 2026-11-01 under the
[correction plan](codex-plus-plan.md#planned-pass-release-claim-boundaries-and-candidate-readiness).
Reviewed local candidate `b45728b` corrects the gate and its test entry point.
Fresh private copies reproduced both false rejections before the fix: source
preview.13 with published/managed preview.12, and published preview.13 with
managed preview.12. Direct `python3 -B tests/test_pages.py` also failed because
the test imported the runtime `VERSION` without the repository on its import
path; unittest discovery alone had hidden that entry-point failure.

The existing README declarations now independently anchor published-release
and managed-selection guide claims. Source `VERSION` still owns all component
artifact versions; the checker does not import it or use it to assert publication
or deployment. Each anchor must be unique and well formed. Contradictions report
their domain, file, actual version and expected anchor. No ledger, service,
runtime API or CI workaround was added.

Self-contained documentation fixtures exercise aligned versions, candidate lag,
rollout lag, combined lag, rollback and differing version bases. Negative cases
retain released/managed claim checks, release link label/target and all three
archive checks, missing/duplicate/malformed anchors and named-workflow coverage.
Historical evidence remains accepted. The installation guide explains the
separate authorities and the check's offline limits.

- All **369 tests** pass on Python **3.11.10** and **3.14.8**. Both direct Pages
  invocation and discovery pass all **28 Pages tests** without `PYTHONPATH`.
  The Pages workflow's five inventory tests also pass. These are local checks of
  the existing CI commands; no remote CI run or public deployment was triggered.
- Three complete external builds cover the unchanged published/managed baseline
  and both formerly rejected transitions. Each builds the walkthrough and eight
  guides, validating **234 links/assets/anchors** and **15 current claims**.
  A contradictory published claim still fails before output creation. Fixture
  preview.13 pages are private test output, not a new published release.
- Actual Chromium checks cover landing, setup, architecture and installation
  pages for all three variants at 1440px and 390px: **24 page checks**, with no
  page errors or horizontal overflow. They verify the released link and managed
  text independently. Desktop/mobile installation screenshots were inspected.
- The clean **130-file inventory**, worker metadata and whitespace checks pass.
  All files in the 18-file worker, 25-file monitoring and 21-file reporting
  source inventories remain byte-identical; both canonical bytecode files are
  preserved. This gate correction changes no packaged file, so the earlier
  artifact qualification is retained rather than repeated.

The local correction is ready for a separate release/publication decision.
The source version, published preview.12 assets, managed selections and active
native processes were not changed. This pass starts no native actors, watches
or messages and adds no field-soak or compatibility qualification. Fleet
preservation counts later in this record belong to the initial pass; this
correction did not re-audit those hosts. Unified plugins remain deferred.

## Readable diagnosis

From this checkout:

```sh
rtk proxy scripts/codex-plus-doctor --human
```

The formatter uses the existing diagnostic result. It reports the selected
environment and paths, component versions/revisions and manifest integrity,
enabled MCP configuration, native client/owner qualification and reported MCP
version evidence. It adds no probe, store, MCP tool or background service.
Terminal control characters in metadata are escaped.

JSON remains the default with its existing schema and exit behavior. Missing
optional components or unavailable metadata retain their existing successful
diagnostic exit status; invalid configuration or payloads still return failure.
The tests cover alternate homes, mixed and invalid selections, unavailable or
unqualified native versions, reported mismatches, unknown metadata and both CLI
formats. Preview.13 publishes this flag; older preview.12 archives retain their original CLI.

A read-only check of the development conversation supplied a useful real
example: all selected component manifests verify preview.12, while its connected
monitoring and reporting MCPs both report preview.11. The client and owner report
0.166.0; the declared qualification baseline remains 0.162.1. Both output modes
retain those distinctions. Nothing was refreshed or reloaded to make the values
agree. Reported versions do not attest loaded payload bytes.

## Selected use evidence

The bounded review used the existing private observation-note format. It did not
scan transcripts broadly or manufacture a production workload.

| Evidence | What it supports | Classification and limit |
| --- | --- | --- |
| The development conversation's selected/reported MCP-version mismatch | Diagnosis distinguishes installed selection from a still-connected older server. | Retain the distinction and document the readable command. No follow-up latency, continuation or stop was measured. |
| The already documented [owner-change incident](owner-recovery.md#incident-and-product-boundary) | Caller recovery and recipient recovery are separate boundaries; accepted handling can retain an unknown native turn outcome. | Retain the existing explicit recovery/history contract. This is a retrospective record, not a new recovery trial or proof of a live owner replacement. |

Bounded outgoing-message, watch-history and reminder-history reads returned no
recorded entries in the current conversation state. The latter two report an
offline coordinator and potentially stale cached receipts. That does not prove
that every incarnation, conversation, home or host has no pending work.
No suitable independent-session follow-up, real endpoint/log transition or
configured-MCP monitoring episode was available in this selected evidence.
Their useful update, quiet behavior, continuation, recap, effective stop,
latency and cost remain unobserved. Earlier synthetic qualification is unchanged.

The deferred quiet-source `starting` label still needs a supported positive
native startup receipt. This pass adds no heartbeat or silence-based liveness
claim. No new watch, message, reminder, worker or native model turn was started.

## Native plugin spike

The official [packaging guide](https://developers.openai.com/plugins/build/plugins)
describes portable root `plugin.json`, `mcp.json` and skills, with an optional
Codex compatibility overlay. The [local-server guide](https://developers.openai.com/plugins/deploy/desktop-only#configure-a-local-mcp-server)
documents stdio commands and `${PLUGIN_ROOT}`. These are packaging capabilities,
not proof that an installed client preserves our entire workflow.

Installed Codex 0.166.0 exposes `plugin add` and local/Git marketplace commands.
Its generated experimental schema includes plugin discovery/read/install. The
packaging guide also describes plugin-scoped MCP configuration. CLI help and
schema support do not themselves prove successful installation. The official
[app-server API](https://developers.openai.com/codex/app-server#api-overview)
marks plugin list, read and install as under development.

A private local marketplace fixture outside the checkout contained a portable
candidate with 50 unchanged source files, two manifests, all five current skills
and the two agent TOMLs as reference files. Read-only `plugin/list` and
`plugin/read` on the existing owner discovered it without marketplace registration
or installation. The returned summary was uninstalled and disabled.

| Gate | Observed result |
| --- | --- |
| Manifest and discovery | Native parsing discovers five skills and both MCP server declarations, `codex_plus` and `html_report`. |
| Existing invocation names | Fails the unchanged-name gate: native discovery returns `codex-plus-spike:luna-task`, `codex-plus-spike:luna-goal-loop`, and similarly prefixed worker/report skills. The source skill names and instruction bytes were unchanged. |
| Custom agent registration | Not established. The inspected portable components and native plugin detail schema expose no custom-agent component; copying the two TOMLs does not register native worker roles. Keep the existing agent installation. |
| Relocation and protocol | A byte-identical relocated candidate initializes both stdio servers, retains their instructions and lists 17 monitoring/four report tools. A monitoring call without native caller metadata refuses before product state creation. |
| Native plugin execution and caller identity | Not qualified. The harness expands `${PLUGIN_ROOT}` itself; native expansion and verified caller `_meta` injection require an installed-plugin call. Discovery is not that call. |
| Policies and environment separation | Existing fixtures and archive behavior remain unchanged. Plugin-specific approvals, duplicate legacy/plugin server avoidance and installed-plugin OSS/work isolation were not exercised. |
| Optional components and upgrades | Not qualified by this combined private candidate. Component preferences, captured running code, upgrade retention and immutable rollback need installation evidence. |

The protocol probe created no Plus journal, report store or native home. RTK
created its ordinary private metrics database in the probe's isolated data root;
the initial overbroad no-files assertion was corrected to distinguish that
launcher bookkeeping from product state. Raw candidate and native receipts stay
outside source.

The reporting archive already supplies optional skill-only plugin manifests.
They are unchanged. This spike does not make them a bundled-MCP installation or
replace the existing monitoring, reporting or worker paths.

**Decision: partial fit; defer unified plugin distribution.** Native discovery
works and the code relocates, but invocation names change and worker registration
is unproven. Adoption currently adds installation work rather than removing it.
No compatibility adapter, new installer, marketplace registration or production
plugin setting was added. A later packaging-only trial would need a supported
private installation scope, native server startup and a verified caller-bound
operation, followed by policy, duplicate-server, environment and rollback checks.
It should first decide whether changed invocation names are acceptable.

## Plugin installation follow-up: isolated CLI and lifecycle gates

Completed 2026-11-01 under the
[plugin distribution-fit plan](codex-plus-plan.md#planned-pass-native-plugin-installation-and-distribution-fit).
This is a finite packaging qualification with a **defer migration** result.
It changes no product runtime code, worker invocation or production installation.
Native installed-plugin execution remains unqualified; the dependent actor trials
did not start. The isolated CLI and maintenance probes below are actual execution,
not inferences from help or discovery.

### Scope and candidate

The installed CLI and existing Snap OSS owner are 0.166.0. The generated
experimental schema, installed CLI help and matching upstream tag were inspected.
The native [plugin manager](https://github.com/openai/codex/blob/rust-v0.166.0/codex-rs/core-plugins/src/manager.rs)
installs into its selected home's store and calls `set_user_plugin_enabled`.
Its [store](https://github.com/openai/codex/blob/rust-v0.166.0/codex-rs/core-plugins/src/store.rs)
derives cache/data roots from that home. The inspected API and
[plugin configuration](https://github.com/openai/codex/blob/rust-v0.166.0/codex-rs/config/src/types.rs)
offer no qualified per-thread installation-home override. Source inspection
explains the write boundary; the isolated CLI probe verifies its concrete writes.

A private `CODEX_HOME`, marketplace, data/config/state roots and report store were
created outside the checkout. No authentication file or credentials were copied,
no daemon was started there, and no real-home marketplace or plugin setting was
written. The existing owner was used only for passive fixture discovery. No
native synthetic conversation, model turn, message, watch or reminder was started.

Both candidates reuse the exact 40-file union of the existing monitoring and
reporting source inventories. They include the report skill and exclude worker
skills/agent TOMLs. Preview.12 comes from release source `f6ec874`; preview.13
comes from `5e6c9dd`. Each keeps that release's product version and adds only
portable `plugin.json` and `mcp.json`, for **42 plugin files**. The trial identity
is `codex-plus-trial@codex-plus-private-trial`, with `codex_plus` and `html_report`
server declarations. Discovery returns `codex-plus-trial:html-report`.

The stdio trial manifest supplies explicit private fixture configuration. A
separate portable preview.13 candidate removes those host/fixture paths and
inherits normal environment/config selection. Native CLI installation of that
portable candidate preserves all 42 file bytes and modes. Two deterministic
candidate archives are identical. The prepared archive, checksum, provenance,
reproduction scripts and raw receipts remain private research artifacts outside
source; no new installer, public artifact or supported distribution is introduced.

### Observed gates

| Gate | Result and limit |
| --- | --- |
| Native CLI installation | Pass in the isolated home. `plugin marketplace add`, `plugin add` and `plugin list --json --available` report preview.13 installed and enabled. Registration creates the private `config.toml`; installation changes it and creates 42 cached files. The CLI warns that PATH aliases cannot be created under `/tmp`; installation still succeeds and no such helper is created. |
| Existing-owner installation scope | Not qualified. Passive `plugin/read` on the existing owner discovers both server declarations and the prefixed report skill, but reports this plugin uninstalled and disabled, both before and after private-home installation. The owner identity is unchanged. Installing into another home does not install into this owner; its `plugin/install` surface has no home argument. No real-home installation was attempted. |
| Installed payload protocol | Pass for manual stdio launches of the actual isolated installation: preview.13 reports 17 monitoring/four reporting tools. The harness expands `${PLUGIN_ROOT}`; native plugin startup/expansion and caller injection are still unqualified. |
| Metadata boundary | A monitoring `watch_list` call without native metadata refuses before creating the fixture state root. No metadata was fabricated or validation weakened. A successful native caller-bound operation remains gated. |
| Reporting functionality | A manual stdio call publishes one 75-byte owned HTML fixture, updates its private catalog and retrieves it. Autostart is disabled, the URL is unconfigured and delivery is unchecked. This establishes stored bytes, not HTTP delivery, native approval or browser rendering. |
| Rollback and upgrade | Selecting preview.12 in the local fixture catalog and reinstalling succeeds; selecting preview.13 again also succeeds and restores identical payload bytes. Each switch removes the prior cached version. This qualifies explicit local-catalog selection/reinstallation, not a first-class rollback command or automatic rollback policy. |
| Captured processes | Both already-running manual stdio servers continue to report preview.13 after its cache directory is removed. The reporting server can still retrieve the fixture. The removed version's `scripts/codex-plus-watch` path no longer exists, and a direct Python launch fails with exit 2. Some captured code keeps working; this does not qualify safe native live upgrades. |
| Removal and data | Native `plugin remove` removes the trial cache; marketplace removal clears its registration. The isolated config returns to empty. The report snapshot, catalog and original HTML survive, and captured reporting can still retrieve the snapshot before its process exits. No real journal existed in this fixture, so journal preservation is not established. |
| Permissions, duplication and environment isolation | Native installed-plugin approvals, denial paths, effective MCP names, duplicate legacy/plugin behavior, component enablement and OSS/work separation remain unqualified. No work-home or fleet trial occurred. |

The first report probe omitted the required `schema = 1` in its fixture config
and was correctly rejected before report creation. The fixture was corrected and
only the affected private protocol/lifecycle probe repeated. Product code did not
change. Both manual stdio processes were closed after their probes.

### Why migration remains deferred

The private CLI installation gate is closed successfully; a desktop app is not
needed for that bounded operation on this CLI. It does not close the different
gate of installed plugin execution on the existing daemon. Completing that gate
would need an explicitly scoped native-home installation or another supported
scope that actually belongs to that owner. A project enablement setting alone
does not isolate installation writes. Do not create a second daemon, copy a
cache into the live home or install globally to manufacture a passing result.

Cache pruning is an observed retention mismatch with today's immutable archive
installation. `codex_plus.cli.ensure_coordinator` derives its helper wrapper from
the captured module path; reporting server control also derives a source wrapper.
Native cache updates remove those paths. Whether native refresh behavior safely
replaces affected servers/helpers needs actual native acceptance; the manual
stdio result neither proves all running tasks fail nor proves upgrades are safe.
Do not add a private code-retention service, installation hook or compatibility
layer merely to make plugins appear equivalent to existing delivery.

The next acceptance scope would first qualify real native installation and
caller-bound reads, then A-watches-B/stop, approvals and coexistence, and finally
an active native update with helper continuity. Preserve native workers during
that run. The existing doctor assumes top-level legacy server names and archive
selections; assess any necessary diagnostics against observed plugin inventory
instead of treating its current output as plugin acceptance.

Official [local-MCP directory submission](https://developers.openai.com/plugins/deploy/desktop-only)
has an additional approved-partner/organization-allowlisting gate; our eligibility
is unknown. The [local/Git marketplace route](https://developers.openai.com/plugins/build/plugins)
is separate. Neither public-directory eligibility nor custom-agent registration
needs to be solved to run the narrower monitoring/reporting experiment, but both
remain relevant to a complete replacement.

**Recommendation:** retain preview.13 archives/chezmoi and the current worker
installation. Keep the prepared native plugin as a research candidate. The
syntax and CLI route work; full adoption has not demonstrated a simpler, equally
robust lifecycle. Revisit when a controlled native installation trial is in scope
and the active-update retention gate can be exercised without disturbing work.

All **596 protected paths** and all **13 baseline native/report process
identities** match before/after the local trials, including both existing
untracked bytecode files. Existing selections and owners remain intact. The
private installation is removed, its configuration is empty, and it has no auth
file or daemon directories. Private report evidence and prepared candidates are
retained for review. No publication, push, managed apply or global MCP refresh
occurred.

All **55 focused tests** pass: 28 Pages, 21 existing package and six reporting
MCP tests. The clean tracked-file candidate passes the 130-file inventory and
separate worker/skill validation; `git diff --check` passes. All 40 candidate
product files also match the canonical release source bytes. No new runtime
test or broader native compatibility claim follows from these checks.

## Validation and preservation

- All **364 tests** pass on Python **3.11.10** and **3.14.8**. Doctor changes add
  five tests; the Pages gate adds five. Worker validation remains separate from
  watch behavior.
- Two complete private builds from `bceda12` produce identical bytes for all
  three component archives, `release.json` and `SHA256SUMS`. All five verify.
- Relocated monitoring and reporting installs run both JSON and human doctor
  modes against verified component manifests. Watch/peer CLI help and fresh
  17/four-tool MCP discovery pass. These are protocol checks, not model turns.
- The final clean tracked-file candidate passes the explicit 130-file inventory,
  worker metadata checks and whitespace validation. Canonical inventory retains
  its known two extra bytecode files, both byte-identical to baseline.
- The external Pages build and actual browser checks cover all eight guides and
  60 walkthrough states at desktop, tablet and phone widths, with no page errors
  or horizontal overflow. They establish local candidate behavior only.

| Private candidate component | SHA-256 |
| --- | --- |
| Workers | `7874569f4511ca76e33d104fd2454441149e9455c699270d5264d266c7a9f1dd` |
| Monitoring | `8bc60aa67abe42c71cedfb372e0a4e365f50baa4c445e78b908f980e980bdbb9` |
| Reporting | `bb3757c1512acbdaad20d90eecba531a8d7968cbcac4d76d821c3a82a77762d7` |

Before/after checks match all **1,349 protected paths** and **26 recorded
native/report process identities**: Snap 541/13, Starship 482/10 and Carbon 326/3.
Configuration, worker identities, old/current payload bytes and modes, selected
symlinks and report HTTP results are unchanged. Snap OSS/work and Starship retain
their HTTP baseline; Carbon reporting remains unavailable. Carbon audit used the
trusted Starship-to-`carbon` route after the alternate `carbon.lan` route timed
out. No native owner was started or restarted; managed report servers are
unchanged. The fixture suite's temporary HTTP servers are separate test resources.

The source changes are local commits. No remote push, release/site publication,
chezmoi edit/apply, global MCP refresh or fleet migration occurred. The next
release can carry the documentation gate and doctor formatter through the
existing publication and managed-rollout gates. Representative daily-use
evidence and any future plugin adoption remain separate decisions.

## Preview.13 publication and managed rollout

Completed 2026-11-01 after Bryan approved release and scoped deployment. Immutable
source `5e6c9dde392e8fa3e33b6901c0afe68116c77d94` supplies unified
**v0.1.0-preview.13** workers, monitoring and reporting. It includes the readable
doctor, independent published/managed guide checks and explicit preview.12
verification and rollback support. Bumping the version first reproduced unsupported
preview.12 errors in both installers; the expanded regressions pass after the fix.
No worker agent/skill payload or workflow identity changed.

All **369 tests** pass on Python **3.11.10** and **3.14.8**; direct Pages invocation
passes all **28 tests** without `PYTHONPATH`. The clean **130-file inventory**,
worker metadata and whitespace checks pass. Two complete builds reproduce all
**five assets** byte for byte. Every downloaded GitHub asset matches those builds;
the unified verifier checks exact inventories, modes, versions, source revision
and checksums. The new tooling also verifies the actual prior preview.12 archives.
Relocated installations pass both doctor formats and MCP initialize/tools-list
checks with **17 monitoring** and **four report tools**, without creating state.
Release CI passes Python 3.11/3.14 independently of local qualification.

The guide build validates **234 local links/assets/anchors** and **15 current
claims**. Browser qualification covers **60 scene states** and **24 guide loads**
at desktop, tablet and mobile widths, with no page errors or horizontal overflow.
Publication initially retained managed preview.12 claims; managed claims advanced
only after the following host acceptance. CI and actual public delivery remain
separate checks.

Dotfiles pin `29d4d1d` (rollout receipt `8b191e6`) advances component URLs, source revision, fetched checksums,
selectors and dedicated/umbrella validators together. The focused update was
published from an isolated upstream checkout. All three canonical sources received
scoped commits preserving their divergent histories and unrelated changes: **25**
paths on Snap, **zero** on Starship and **two** on Carbon. The default source's
scoped diff is empty on every host. Plus, split-home and report validators pass;
report qualification includes isolated installation on all three supported profiles.

Each host's reviewed status/diff/script-excluded dry-run contains only two new
immutable payloads, two selectors and the worker version manifest. Payload
verification precedes selector apply. Exact installed inventory/hash/mode checks
pass for **25 monitoring**, **23 reporting** and **18 worker files** per host.
Fresh installed MCP commands report preview.13 with 17/four tools in Snap OSS,
Snap work, Starship and Carbon. Both installed doctor formats verify aligned
components and enabled MCP configuration in all four contexts.

Of **1,349 protected paths**, **1,346** remain byte/mode/link identical; only the
three worker version/provenance manifests advance. All **26 recorded native/report
process identity tuples** remain present. Private config/auth, agents/skills,
report configuration and every pre-existing immutable release are preserved.
The three healthy report endpoints remain HTTP 200 with identical catalog bytes;
Carbon was unavailable before rollout and remains so. Carbon uses the trusted
Starship SSH hop without bypassing host-key checks. No daemon/report-server
restart, global MCP refresh, native configuration apply, recovery or intent replay
occurred. Existing processes reconnect normally.

The development conversation's read-only doctor demonstrates the boundary:
selected files verify preview.13 while connected monitoring/reporting metadata
still reports preview.11. Native client and owner are 0.166.0; the declared
qualification baseline remains 0.162.1. Protocol discovery and bounded earlier
native trials do not establish blanket native compatibility or long operation.

Passive current watch, reminder and outgoing-message receipts contain no ordinary
follow-up episode in this conversation. No workload was manufactured and no real
session was messaged or interrupted. Real-work follow-up, long unattended operation
and personal UX acceptance remain open; native plugin distribution stays deferred.
Private rollout evidence remains outside source in a mode-0700 workspace.

The full dotfiles `scripts/check` passes the Plus pins/materialized workers,
split-home and preference-preservation gates, then fails in the unchanged OpenCode
block because the installed binary rejects `--pure`. That block is byte-identical
to upstream baseline `28d3655`; this rollout preserves its unrelated retirement
work. Dedicated reporting qualification passes independently of that early exit.

## Preview.14 worker discovery publication and rollout

Completed 2026-11-01 under Bryan's review/publish/deploy request. Immutable
source `dc19a8260f99b4a621899f0d1d45868c10133134` supplies unified
**v0.1.0-preview.14** workers, monitoring and reporting. The release was assembled
from published main with the four worker skill corrections and shared guidance;
the separate selected-primary/Terra candidate remains outside published source.
Native controls are discovered from actual declarations and called directly,
with explicit `luna-max` / `fork_turns="none"` selection and distinct discovery,
spawn and execution failures. Invocation metadata, model pins and routing are
preserved. Runtime/report changes retain actual preview.13 upgrade/rollback
support after the product version advances.

The focused source passes **376 tests**, all four skill validators, the clean
**132-file inventory** and whitespace checks. The final guide build checks 299
local links/assets/anchors and 15 release claims. An owned headless Chrome pass
checks 18 guide loads and 40 interactive scene states across desktop/mobile
widths, with no horizontal page overflow. GitHub run `41391747929` independently
passes Python **3.11** and **3.14**. Two full builds reproduce all **five assets**;
every downloaded published asset matches. Actual published preview.13 runtime
and reporting archives install, upgrade and roll back in private controls. The
earlier one-worker native probe confirms Luna/Max metadata and a completed
read-only handoff; unavailable/spawn-error/execution-error classifications were
tabletop reviews, not actual failure injection or full goal-loop trials.

Published dotfiles pin `59a889a` advances URLs, source revision, fetched checksums,
selectors and dedicated/umbrella validators. Scoped canonical commits preserve
divergent histories and concurrent work on Snap (`4b8152c`), Starship (`dc6a322`)
and Carbon (`beb5e34`). Plus and split-home checks pass; reporting qualification
covers exact isolated installation, CLI/MCP and convergence on all three host
profiles. The full dotfiles gate passes its Codex/worker/split/provider checks,
then fails because the installed OpenCode rejects `--pure`. That failing block
is byte-identical to the published-parent baseline and is preserved here.

The script-excluded rollout staged and verified immutable payloads before
selecting them and updating the managed worker files. Installed hashes, modes,
inventories and scoped diffs pass in Snap OSS/work, Starship and Carbon. Fresh
MCP initialize/tools-list reports preview.14 with **17 monitoring** and **four
report tools** in all four contexts; file-only doctor reports aligned verified
components. These fresh probes do not establish the versions already loaded by
other conversations.

Of **1,516 protected paths**, **1,476** remain identical. The **40** intended
changes are worker skill bodies, worker provenance/design and current selectors.
Private config/auth, agent definitions, invocation metadata and all pre-existing
immutable releases are preserved. Native daemon process identities remain
unchanged. Starship Python monitoring/reporting MCP connections ended during the
rollout and subsequent verification; their cause was not localized. These were
identified by matching their captured command hashes to the MCP programs, not
by treating arbitrary missing Python processes as acceptable. No lifecycle
command or global MCP refresh was issued. Starship's configured report URL returns
HTTP 200. Do not describe the connection exits as proven unrelated or claim that
every process stayed alive.
The original Starship conversation was not messaged or interrupted for a trial.
Private snapshots, process identifiers and raw probe captures remain outside Git.

## Preview.15 worker policy and guide publication

Published 2026-11-02 as [v0.1.0-preview.15](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.15)
from immutable source `0767e91c582653ec0c4c89e7a85d8cab5c68ec62`, using the personal
`byebyebryan` github.com account. Workers, monitoring and reporting share that
version/revision. The fetched five release files verify against their complete
manifests and checksums. Python 3.11 and 3.14 CI passed on the release tag and
published main; the source suite has 385 tests and four worker skill validators.

The [public guides](https://dev.byebyebryan.com/codex-plus/) include the three
roles, four workflows, instruction-based opt-in/default-off policy and revocation
examples. The new worker chooser creates natural requests and is labelled as an
illustration, not agent execution. Desktop/mobile checks cover all nine guides,
five four-step scenes and worker-choice/copy states: 18 guide loads and 54
interactive states, with no horizontal page overflow. Pages run `41548928349`
published the release-source edition; public browser checks and exact served
`manage.md` bytes verify separately from source rendering. Later documentation
receipts do not modify the release artifacts.

Public dotfiles commit `6eaf5fcd133e2c4f895f463bb701ff08d177368e` updates only seven
Codex Plus pin/validator files from a current-origin isolated checkout. Archive
URLs, checksums, source revision, the new Astra role, worker documentation scope,
private payload inventory and selectors advance together. Canonical integration
commits are `2dd19d0` on Snap, `11b8d2e` on Starship and `3407354` on Carbon.
Carbon received the same scoped patch after it returned online. Existing divergent history,
private preferences and unrelated dirty source remain preserved. Concurrent
checker edits outside the unchanged Codex pin block were retained; only the
published patch hunks were staged.

| Context | Selected components | Verification |
| --- | --- | --- |
| Snap OSS | Preview.15, source `0767e91` | Exact inventories, bytes, modes, three native role files, four skills, immutable selectors and empty scoped chezmoi diff. |
| Snap work | Preview.15, same artifacts | Same role/skill payloads and aligned doctor, preserving its separate native home/config. |
| Starship | Preview.15, same artifacts | Same complete installed checks and empty scoped diff. |
| Carbon | Preview.15, same artifacts | After connectivity returned, a fresh baseline confirmed unchanged source/installed state. The same manifest, role/skill, selector, doctor, MCP and empty scoped-diff checks passed; both pre-existing process identities were preserved. |

All three staged component manifests were verified before selectors/skills
advanced on each host. Existing worker/role/skill backups and older
runtime/report releases are retained. Across all three hosts, 1,666 protected
installed paths were checked; 50 intended existing paths changed, plus the new
Astra roles, qualification document and immutable release trees. Native owner
identities are unchanged. Two existing Snap MCP processes and six Starship MCP
processes exited during the pass; no lifecycle action was issued and their cause
was not localized. Remaining pre-existing process identities were preserved.

Fresh stdio initialization/tool listing reports preview.15 with 17 monitoring
and four report tools in Snap OSS/work, Starship and Carbon. This proves the selected
entrypoints' protocol/version, not code loaded by every existing conversation.
The installed Snap `codex-plus-context --primary` reads the active Sol/XHigh
selection successfully. No model turn, native owner restart, global MCP refresh,
report publication or existing-session input was used for deployment verification.
Native model/effort availability on other accounts and actual Terra-primary
execution retain the [worker qualification limits](worker-escalation-results.md).

Scoped Codex Plus, report artifact and managed-preference checks pass. The full
dotfiles gate passes the Codex checks, then reaches the existing OpenCode
`--pure` rejection. The failing OpenCode block is byte-identical to the published
parent and its command reproduces the same failure independently; it is outside
this release. The product checkout retains its two pre-existing untracked
bytecode files, outside the clean 135-file source gate. Private host captures,
backups and session/process identities are not committed.


## Adaptive-name migration qualification

The 2026-11-03 rename makes `$adaptive-task` and `$adaptive-goal-loop` canonical.
Both `$worker-*` identities remain explicit-only compatibility entries with one
relative link to their corresponding canonical instructions. Their invocation
satisfies that workflow's explicit activation boundary without a second request.
The copied policy bodies differ only by identity/activation references; native
role files and both Luna workflows remain byte-identical to the goal baseline.
No routing, escalation permission, primary selection or model pins changed.

The clean 139-file candidate passes 387 tests, six affected skill validators,
metadata/inventory checks and Pages verification (302 local links/assets/anchors,
15 current-release claims). Relocated real worker archives retain the canonical
instructions and both compatibility links; metadata regressions reject implicit
activation for all four names. These checks establish package/discovery structure,
not new native model decisions. Historical routing trials retain their original
worker names and evidence limits. Publication and installed state are recorded
separately after verification; preview.15 assets remain immutable.

## Preview.16 publication and managed rollout

Published 2026-11-03 as [v0.1.0-preview.16](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.16)
from source `b13cc66497569d3bb3f625d227095edab4a2b571`, through the personal
`byebyebryan` GitHub account. All five uploaded/downloaded release files match
the validated local build and full unified verifier. Release-tag CI run
`41677463762`, main CI `41677706717` and Pages `41677706788` pass. Both Python
3.11/3.14 CI lanes exercise the complete suite and build/verify the release.
Public browser checks cover all nine guides and 54 interactive states, including
canonical adaptive request generation; earlier preview assets are unchanged.

Dotfiles commit `928da79` publishes seven pin/validator files from current-origin
source. Eleven externals include all six workflow/compatibility entries; raw
role pins, archives, selectors, hashes and validators advance together. Canonical
integration commits are `013b9b8` on Snap and `d95b412` on Starship. Only reviewed
patch hunks were staged; divergent history and unrelated edits remain preserved.

| Context | Selected components | Evidence |
| --- | --- | --- |
| Snap OSS | Preview.16, source `b13cc66` | Exact manifests, roles, six skill entries, selectors and empty scoped diff; native read-only discovery sees all six enabled without errors. |
| Snap work | Preview.16, same artifacts | Exact installed checks and fresh stdio MCP smoke pass. Its native control socket is absent; no daemon was started for discovery. |
| Starship | Preview.16, same artifacts | Exact installed checks, empty scoped diff and native read-only discovery of all six enabled entries without errors. |
| Carbon | Last verified preview.15; apply pending | Fresh snapshot/preflight found no role overrides, canonical-name conflicts or disabled workflow conflicts. It then went offline before backup/integration/apply; trusted SSH timed out and the LAN route was unreachable. |

Snap and Starship retained worker/role/skill backups and older immutable releases.
Across their 1,342 protected installed paths, 28 intended existing paths changed,
plus new canonical skill files and immutable release roots. All 51 pre-existing
native/helper process identities were preserved through selection and smoke.
Native role files and Luna workflow bytes are unchanged. No daemon restart,
global MCP refresh or real-session input was issued.

Fresh stdio initialization/tool listing in Snap OSS/work and Starship reports
preview.16 with 17 monitoring and four reporting tools; doctor alignment passes.
Native `skills/list` used `forceReload=false` on existing owners only. Discovery
does not prove model invocation, compatibility forwarding in a model turn, or
that existing conversations reloaded their instructions. No model turn or worker
spawn was run for this rename; unchanged routing retains the previous bounded
qualification and Terra/provider/lifecycle limits.

Scoped Codex Plus, report artifact, exact worker inventory, preference preservation
and master external-pin gates pass. The full dotfiles gate passes Codex checks,
then fails at the pre-existing OpenCode `--pure` rejection. That failing source
block is byte-identical to the published parent and the baseline command fails
independently. Private captures, host snapshots and process/session identifiers
remain outside Git; the two pre-existing product bytecode files are retained.
