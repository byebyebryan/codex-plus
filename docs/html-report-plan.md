# HTML report v1 implementation plan

Planning checkpoint, 2026-10-13, source baseline `6a04536`. Read the
[design](html-report-design.md) for product intent and the hosting/index choices.
This plan supplies defaults, interfaces, recovery semantics and execution gates.
See [execution evidence](html-report-results.md) for implementation and qualification.

## Scope and finish line

Deliver a report publisher usable from ordinary agent sessions on Starship, Snap
and Carbon. A completed static bundle becomes a durable, host-addressed link;
its optional browser catalog and lifetime do not depend on the agent session.
The user opens the link locally. Client-side JavaScript is supported; automatic
browser opening and applications with a running backend are outside v1.

First execution finish: implemented and tested core/CLI/catalog, qualified agent
integration and a verified report-component artifact, with a reviewable chezmoi
installation change. Real service provisioning and fleet apply require deployment
scope. Desktop acceptance and offline hosts remain separately recorded gates.
Do not activate the existing watch preview to make report publishing work.

## Decisions for this plan

| Decision | Baseline |
| --- | --- |
| Repository | codex-plus; standalone report component |
| Hosting | One persistent Tailscale Serve endpoint per publishing host |
| Returned URL | User-selected short MagicDNS HTTP hostname; never `localhost` |
| Port/path | Dedicated configured port, proposed 8787; prefix `/reports/` |
| Catalog | Optional static page; proposed host profile enables it |
| Storage | XDG user data, default `~/.local/share/codex-plus/reports` |
| Revision links | Immutable, provisionally; changed output receives a new link |
| Repeated publish | Identical bundle and public metadata reuse the same snapshot |
| Retention | Explicit deletion; no automatic TTL, pruning or eviction |
| Required agent integration | Provider-neutral `html-report` skill and CLI |
| Optional integration | Report-only local stdio MCP and plugin packaging |

The user confirmed static bundles, manual local opening and short HTTP hostnames
for the Snap/Starship mesh. Immutable revision semantics remain the recommended
baseline. Remaining entries are implementation
defaults for review, not claims that deployment has been approved.

## Current host evidence and prerequisites

Read-only planning checks found:

- Starship: Tailscale 1.104.1; Serve configuration empty; port 8000 already has a
  listener on `0.0.0.0`. Tailscale operator user is unset.
- Snap: Serve configuration empty; no listener on proposed port 8787. Its resolver
  resolves `starship` to `100.84.31.64` through the tailnet.
- Port 8787 was also absent from Starship's listener inspection. These are
  observations, not port reservations; recheck immediately before provisioning.
- Carbon is offline in the observed tailnet inventory and remains unqualified.
- Canonical chezmoi currently selects the worker archive at `56b7158`. The newer
  supervision runtime is a separately published preview with rollout deferred.

Initial execution found Starship's short hostname resolved to `127.0.1.1` locally
while its full MagicDNS name resolved to its tailnet address. The user subsequently
selected short HTTP URLs. Starship's local host mapping selects its Tailscale
address; short names must resolve and reach the endpoint on publishing and viewing
hosts. This host-side mapping remains outside chezmoi. A temporary direct
Serve route delivered HTTP 200 to Snap and Chrome; a plain Python listener bound
to the tailnet address did not pass that peer route check. Persistent serving,
reboot behavior and Carbon remain separate deployment gates.

Use direct file serving in persistent `--bg` mode. No Python server or additional
web daemon is needed. Current Serve documentation describes HTTP ports, path
mounts and persistent restart behavior. In upstream 1.104.1 source, the
interactive certificate-enable path is conditional on HTTPS, so HTTP provisioning
does not need that HTTPS flow. Actual route qualification still remains a gate.
[Serve reference](https://tailscale.com/docs/reference/tailscale-cli/serve),
[1.104.1 mode handling](https://github.com/tailscale/tailscale/blob/v1.104.1/cmd/tailscale/cli/serve_v2.go#L462).

HTTP supports ordinary rendering and client-side controls. Some browser APIs,
including `navigator.clipboard.writeText`, require a secure context; use a usable
fallback or an explicitly configured HTTPS profile for reports needing those APIs.
Keep HTTPS supported without silently rewriting earlier returned URLs.
[Clipboard requirement](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText).

## Configuration and serving ownership

Proposed user configuration: `~/.config/codex-plus/report.toml`. Example host
profile, not a deployed configuration:

```toml
schema = 1
data_root = "/home/bryan/.local/share/codex-plus/reports"
base_url = "http://starship:8787/reports/"
catalog_enabled = true
max_bundle_bytes = 104857600
max_bundle_files = 2000
max_store_bytes = 5368709120
max_store_reports = 1000
```

These are proposed initial tunables: 100 MiB per bundle, 2,000 files, 5 GiB for
the store and 1,000 snapshots. Check representative reports before deployment;
reject excessive inputs clearly and never discard existing reports to fit them.
Missing configuration is an explicit delivery condition, not permission to invent
an endpoint. Validate an absolute owned data root and a host-addressed HTTP/HTTPS
base URL with no embedded credentials, query or fragment.

Metadata has an additional hard bound of 2 MiB per snapshot and 10,000 identities
including retained deletion records. Inputs/configuration that exceed these bounds
are refused before unreadable state is stored. These bounds preserve inspectability;
they do not prune reports or deletion history.

Chezmoi owns code selection, publisher configuration and skill/MCP discovery
wiring. Provision the host's Serve route as a separate operator action; its
privilege, HTTPS/account prerequisites and existing routes are checked first.
Do not set a global operator user, reset Serve or change unrelated network policy
as part of publication. Save existing route configuration and identify precisely
the route owned by this feature before installation/rollback. Tailscale state
itself is not copied into dotfiles.

The route maps `/reports/` to the store's `public` directory. Dedicated port
ownership isolates the report origin from unrelated host web applications.
Permitted tailnet clients can read published bundles; catalog visibility is a
discovery preference, not a per-report access boundary. The component assumes one
local user's trusted report store, not isolated tenants or untrusted uploads.

## Source, identity and on-disk contract

Agents finish a dedicated export before publication. Sources may follow a project's
artifact convention or live in a scratch directory. Accept one self-contained
HTML file, or a real directory with an HTML entrypoint and regular-file assets.
Directory entrypoint defaults to `index.html`; other relative entrypoints are
explicit. Reject symlinks, special files and path escapes. Support spaces and
Unicode filenames with correct URL encoding. Do not run builds, collect arbitrary
parent files or rewrite the report's HTML/JavaScript.

Report identity is the full SHA-256 digest of a versioned canonical snapshot
description: entrypoint, title, optional project label, and sorted relative file
paths with their content hashes. Timestamps, source paths and optional agent
provenance do not enter that digest. Unchanged retries reuse a snapshot; changed
output becomes a new immutable revision. The report ID is not an access token.

```text
reports/
  public/index.html          # generated catalog or non-listing landing page
  public/<report-id>/...     # immutable HTML/assets only
  metadata/<report-id>.json  # private publication state and provenance
  staging/<operation-id>/    # incomplete copies, never served
  trash/<operation-id>/      # interrupted deletion cleanup, never served
  publish.lock              # host-local commit/catalog lock
```

Bounded reads use metadata; optional integrity verification checks the selected
bundle. No database, native Codex history, watcher journal or model wakeup is
required. Private metadata is never copied into the served bundle.

## Publish, recover and delete behavior

1. Copy and hash the explicit source into bounded staging, outside the served tree.
   Detect observed source edits or growth and fail cleanly; this is not a filesystem
   snapshot of an actively edited project.
2. Compute the report identity. Under the host-local commit lock, verify whether
   the exact snapshot already exists. Reuse a verified match; never overwrite
   mismatching bytes or commit over an unknown directory.
3. Write an atomic private `prepared` record containing the snapshot description.
   Atomically rename the completed staged directory into `public/<report-id>`.
4. Commit the private `published` record and first-publication timestamp. Rebuild
   the catalog from committed records using atomic file replacement.
5. Return the receipt after a requested bounded HTTP check. Network or catalog
   failure does not destroy the stored report.

Before the rename, staging is unpublished. After the rename but before the record
commit, the complete bundle may be readable at its direct URL but is not yet
catalogued or reported as committed success. An explicit retry of the same publish
can verify and finish its own prepared record. Doctor/list do not mutate storage
to hide gaps. An explicit repair command previews prepared/orphaned records before
completing validated commits or removing abandoned staging; it never guesses what
an unrelated directory contains.

Delete first moves exactly the selected bundle outside the public root, then
records deletion and rebuilds the catalog. Cleanup removes only owned trash.
Interrupted deletion remains identifiable; original source files and other report
URLs remain intact. Successful deletion cannot erase browser/downloaded copies.
No operation resumes an agent, sends a peer message or automatically republishes
a report whose retention was explicitly ended.

The catalog uses title, optional project, date and URL, newest first. Escape text
and encode links; metadata cannot inject catalog HTML/scripts. Search/filtering
are client-side. The report-count bound caps generated catalog size. When disabled,
serve a non-listing landing page; direct links still work. Keep the prior complete
index on generation failure, disclose stale state and offer explicit rebuild.
Browser deletion is outside v1.

## CLI, MCP and receipts

CLI: `codex-plus-report publish|get|list|delete|doctor|repair|catalog-rebuild`.
The last two are explicit maintenance writes; repair defaults to a preview.
CLI output supports readable text and structured JSON for automation. Snapshot
operations use Linux filesystem locking; the initial compatibility is Linux and
Python 3.11 or newer, without a required Codex version.

Optional MCP adapter:

| Tool | Arguments | Effects |
| --- | --- | --- |
| `report_publish` | absolute `source`, `title`, optional `entrypoint`, `project`, `check_delivery` | Writes snapshot/catalog; requested bounded delivery check |
| `report_get` | exact `report_id`, optional `check_delivery` | Reads metadata; requested bounded network read |
| `report_list` | optional `limit`, `cursor`, `project` | Bounded local metadata read |
| `report_delete` | exact `report_id` | Removes one snapshot; destructive write |

Keep maintenance in the CLI initially. Initialization/tool listing perform no
native daemon calls, serving setup or storage writes. Read/write annotations
describe real effects and client authorization remains effective. Do not advertise
publication as universally idempotent when source paths can change between calls;
unchanged-snapshot deduplication has a narrower guarantee.

Receipt schema 1 contains `report_id`, `title`, `project`, `entrypoint`, `origin`,
`created_at`, `snapshot_path`, file/byte counts and independent status fields:

- `publication`: new snapshot committed or existing verified snapshot reused.
- `url`: configured URL or null; availability is not implied by the string.
- `catalog`: updated, disabled or stale, with a bounded explanation when needed.
- `delivery`: unchecked, verified or unavailable, with checked time/location and
  a bounded reason. Verification fetches expected entrypoint bytes.

MCP returns readable link text plus structured data. Routine chat presents the
useful result and visible URL, disclosing material delivery failures. Origin-side
HTTP success is not desktop reachability, rendering or user acceptance. Capacity,
path or copy failures return a clear error and operation identity when useful;
never invent success. Configuration changes do not rewrite earlier returned URLs
or alter existing snapshot content.

## Implementation boundaries and sequence

Use a small independent `codex_plus/reports/` package with store/publisher, catalog,
config/hosting checks and CLI modules. Proposed launchers: `scripts/codex-plus-report`
and, if selected, `scripts/codex-plus-report-mcp`. The report core uses Python
stdlib and does not import native caller/watch/peer control modules. Skill path:
`skills/html-report`. Keep catalog presentation simple.

| Slice | Deliverable | Acceptance before proceeding |
| --- | --- | --- |
| 1. Core and CLI | Config, snapshots, receipts, list/get/delete/doctor and recovery | Multi-asset HTML, unchanged retry, changed revision, path/size failure, concurrent commits and crash/delete recovery pass isolated tests |
| 2. Static catalog | Optional index, filtering, atomic rebuild, stale-state reporting | Concurrent publish/delete loses no entries; escaped titles and disabled mode work; direct URLs remain usable |
| 3. Hosting qualification | Reviewable route setup and readonly checks | Configured hostname/port serves exact HTML/assets from another host; unrelated routes/processes stay intact; persistence verified after publisher exit |
| 4. Agent surface | Skill, optional report MCP and client wiring | An ordinary report request produces a meaningful report and a working visible link; discovery/publication never touches native ownership |
| 5. Packaging | Report artifact/profile and thin plugin wrapper if useful | Fetched hashes, modes, exact inventory and isolated installed behavior pass; existing runtime/worker compatibility stays covered |
| 6. Managed rollout | Prepared scoped chezmoi change; requested fleet apply | Review drift/dry-run, verify installed bytes and endpoint ownership per host, record desktop acceptance and offline hosts as pending |

No new native watch study or monitoring experiment belongs in these checks.
Offline fixtures use isolated directories and bounded temporary servers. Live
checks preserve existing project servers, Serve routes, daemons and agent drafts.
Browser checks use the actual desktop, including SSH TUI and tmux paths; include
a table/filter, plot/image and relative JSON fetch. HTTP-only controls must work
without secure-context assumptions.

## Packaging and completion evidence

Create a report-specific artifact identity and compatibility declaration. Do not
inherit supervision's required Codex version/Unix owner, or repin the worker archive
just to install reports. Reuse verified packaging with an explicit report profile;
keep published preview bytes/tag intact. Data/config/Serve state never enter archives.

The required installation is CLI plus skill. Local stdio MCP and plugin wrappers
are convenience integrations, not another implementation or public remote service.
Select manifests supported by installed clients and test actual loading. Official
OpenAI documentation separates skill/MCP capabilities from their plugin package
and supports compatibility manifests; a public marketplace submission is not
needed for this personal fleet.
[Plugin packaging](https://developers.openai.com/plugins/build/plugins).

## Concurrent development and integration

Report work uses `feat/html-report` in Starship's checkout. Snap has its own
checkout and may continue scheduling/communication work independently; this
feature does not change its branch or working files. Separate host checkouts
already isolate edits and staging. A linked worktree is useful if another local
task needs the same checkout concurrently, but does not prevent merge conflicts.

Keep report implementation in new report modules, launchers, skill files and
report-specific tests/docs. Existing native scheduling, peer communication and
their caller/turn validation remain owned by the other work. Shared integration
points are `README.md`, `scripts/check` and package/release plumbing; edit these
narrowly and reconcile both inventories and features rather than replacing one
side. Separate report compatibility/version metadata avoids unnecessary edits to
the existing supervision version.

Push the feature branch when publication is requested. Before integration, fetch
fresh `origin/main`, merge it into a published feature branch (or rebase unpublished
local commits), resolve overlaps and review the combined diff. Run inventory,
report checks and the existing runtime regression suite on that integrated state.
Integrate branches into `main` one at a time with normal history-preserving pushes.
If `main` advances again, repeat reconciliation and appropriate checks; do not
force-push shared `main` or overwrite the other host's checkout to gain parity.
Same-file textual conflicts and semantic interactions still require review even
when Git merges cleanly.

Record source checks, artifact verification, network delivery and desktop acceptance
separately. This task changes documentation and inventory only. Before execution,
recheck upstream/dirty work, chosen URL/revision defaults and serving prerequisites.
Live apply, service changes, daemon restarts and source publication are not implied
by completing this planning document.
