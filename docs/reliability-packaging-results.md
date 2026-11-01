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
