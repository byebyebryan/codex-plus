# Everyday reliability and native packaging results

Completed 2026-10-31 under the [selected plan](codex-plus-plan.md#completed-pass-everyday-reliability-and-native-packaging).
The local candidate repairs current-release documentation consistency and adds
readable output to the existing doctor. Native plugins are a **partial fit**;
retain the existing component archives and chezmoi distribution. Representative
real-work follow-up remains an open acceptance item.

This pass publishes no release or site and changes no managed installation.
Preview.12 source `f6ec874` remains selected. The reviewed code candidate is
`bceda12e3dd652bab5659ab3bcc2d1e37f28f246`; its private test artifacts retain the
unchanged preview.12 version constant and are not replacements for that published
tag or its assets. A later release must select a new immutable version.

## Documentation consistency

The setup and architecture guides incorrectly called preview.11 current after
the preview.12 rollout. Both claims are corrected. The existing Pages builder
now checks 15 identified current-release claims against the source version and
checks that the worker guide names all four worker workflows and the separate
reporting skill. It fails before rendering when a required claim is missing or
stale. Historical release evidence remains valid.

Five regressions cover stale setup and managed-release claims, missing current
claims, named workflow coverage and legitimate historical versions. The stale
setup claim failed before correction. These focused matchers need deliberate
updates if current-claim wording changes; they are not a general prose audit or
proof of publication, installed adoption or complete semantic accuracy.

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
formats. Published preview.12 archives do not have this new source-only flag.

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
