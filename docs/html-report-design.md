# HTML report design and implementation plan

Design baseline, 2026-10-13, against source `6a04536`. The standalone component
is now implemented and qualified in isolated installations; fleet activation
remains separate. See the [usage guide](html-report-usage.md) and
[execution evidence](html-report-results.md). The existing watch/peer runtime
preview and its deployment gates remain independently owned.

Read the [v1 implementation plan](html-report-plan.md) for concrete configuration,
interfaces, retry/recovery semantics, proposed limits and execution gates. Its
decision table supersedes provisional implementation details in this overview.

## Everyday outcome

Ask an agent to explain findings, compare options or present a result. When HTML
helps, it creates a report, publishes it and returns a short, clickable link.
The same link opens from the desktop whether the agent runs locally, over SSH,
inside tmux or without an attached TUI. Opening the report requires no per-report
port selection, tunnel setup or knowledge of its filesystem location.

The agent chooses the presentation: narrative, tables, diagrams, plots or
client-side controls. A skill supplies delivery guidance and optional examples;
it does not impose a dashboard template or make every answer an HTML report.
Chat retains a brief explanation of the useful result and a descriptive link.

Bryan selected these first-version boundaries:

- Return a reliable link that he opens locally. Automatic browser opening is later.
- Publish static HTML with its assets. Client-side JavaScript, SVG, JSON data,
  filtering and interactive charts fit this scope.

Live development servers, backend APIs, websocket streams and remote browser
control are later capabilities. The first publisher copies existing output; it
does not run a build, execute uploaded code on the host or start a report server
for each agent invocation.

## Proposed defaults

| Decision | Proposed first-version behavior |
| --- | --- |
| Source | One HTML file or an explicitly prepared report directory |
| Hosting | One shared report endpoint per host; Tailscale Serve can serve files directly |
| Network | Host-addressed tailnet URLs; v1 URL mode is recorded in the implementation plan |
| Publication | A separate immutable snapshot and URL for each publish |
| Retention | Keep snapshots until explicitly deleted |
| Discovery | Bounded local inventory; URL identifies its publishing host |
| Browser catalog | Optional static index at `/reports/`, covering that host's published reports |
| Opening | User opens the returned URL through the local terminal/browser |
| Agent integration | Shared skill and CLI; a thin, independent report MCP adapter |
| Distribution | A report component in codex-plus, installed through chezmoi |

These defaults describe the implementation baseline. The two
scope selections above are the user's confirmed choices.

## Consolidation and optional index

Use one shared serving endpoint on each host for all projects and agent sessions.
Project A and project B publish into separate report directories under the same
store and serving route. Publication does not allocate a port, create a server
process or tie report availability to its originating session. With direct
Tailscale file serving, the existing Tailscale daemon supplies the serving process.
An ordinary managed static server could fulfill the same contract if a different
backend is selected later.

Existing per-project development servers remain relevant to live applications.
They are independently owned; adopting the report publisher is not permission to
stop them or migrate their running content. Static report exports use the shared
endpoint when created through this capability.

Recommend a small optional index at the report service's root, `/reports/`:

- Descriptive title, optional project label, publication date and report link.
- Newest first, with client-side search/filtering when useful.
- Generated from committed report metadata on publish/delete, using a host-local
  lock and atomic index replacement so concurrent publishers do not lose entries.
- A host setting controls whether the catalog is shown. Direct report links
  remain usable when it is disabled; a minimal non-listing landing page prevents
  a fallback to raw filesystem directory listings.

The index exposes only the intended catalog fields. Original paths, conversation
IDs and private registry details stay outside the served tree. It is a static
read-only library, without browser-side deletion or an API backend. If generation
fails, preserve the previous complete index, disclose stale catalog state and
retain the independently valid report publication. Doctor should identify that
state and an explicit rebuild can repair it.

On a dedicated report port, an optional landing page at `/` can link to
`/reports/`. When sharing an existing HTTPS endpoint, leave its unrelated root
route alone. The first index covers its own host; aggregating other hosts is a
separate feature.

## Components and ownership

```mermaid
flowchart LR
    A[Agent creates HTML and assets] --> S[html-report skill]
    S --> C[Report CLI]
    M[Optional report MCP tools] --> P[Shared publisher core]
    C --> P
    P --> D[Durable report snapshots]
    T[Tailscale Serve] --> D
    B[Local desktop browser] --> T
```

The publisher core owns bundle validation, snapshot creation, metadata, listing
and removal. CLI and MCP adapters use the same implementation. Tailscale owns
the configured HTTP/HTTPS endpoint and serving lifetime. There is no background
report coordinator or model turn needed to keep a static report available.

The existing `model_server.py` calls `native_context`, resolves an existing Codex
socket and creates `ModelAPI` on every tool call. Its thread/turn checks protect
peer and watch operations. Reports must not require those operations or weaken
their checks. Use a separate report entry point that works without Codex running
and without Codex-specific caller metadata. Any recorded conversation label is
optional provenance, not an authentication or access-control identity.

Provider-neutral skill instructions and the CLI are the baseline integration.
A report-only MCP adapter can expose the same operations to Codex and Claude;
client configuration/loading is qualified separately. Plugin packaging bundles
that skill and adapter for convenient installation. A plugin does not supply
HTTP hosting or desktop browser access by itself.

## Publishing interface

Proposed CLI name: `codex-plus-report`. Proposed skill name: `html-report`.

```sh
rtk proxy codex-plus-report publish --source /absolute/path/report.html --title "SSH findings"
rtk proxy codex-plus-report publish --source /absolute/path/report-bundle --entrypoint index.html --title "Run comparison"
```

The equivalent MCP operation is `report_publish(source, title, entrypoint?, project?)`.
HTML is authored into files using the agent's ordinary tools; the call carries
paths and metadata, rather than embedding the whole report in tool arguments.
An optional project label is display metadata for the index, not a filesystem
path or an instruction to inspect conversation history.

| Operation | Behavior |
| --- | --- |
| `report_publish` | Validate and copy one explicit source into a new snapshot; return a publication receipt |
| `report_get` | Read a selected report's metadata and URL; optionally perform a bounded serving check |
| `report_list` | Return bounded local inventory, newest first, with title, date and URL |
| `report_delete` | Remove exactly the selected published snapshot and its registry entry; preserve source files |
| CLI `doctor` | Inspect installation, configured route and serving health without changing them |

Listing and metadata reads do not create state, start services or inspect agent
histories. Delete is a write/destructive operation; the adapter declares that
effect accurately and follows the calling client's existing authorization.
There is no automatic bulk cleanup or cross-host SSH control in these tools.

A receipt includes the report ID, title, entrypoint, origin host, local snapshot
location, expected URL when configured, bundle hash/count/size and serving-check
result. Routine chat shows the descriptive link and any material delivery limit,
without UUIDs, helper commands or raw JSON.

Successful storage and successful delivery are distinct facts:

- **Stored:** a complete local snapshot and its metadata exist.
- **URL configured:** a hosting route supplies its expected browser URL.
- **Serving checked:** a bounded request retrieved the expected entrypoint bytes.
  Record where that request ran; a check on the publishing host does not prove
  desktop connectivity or visual quality.

If hosting is unconfigured or unreachable, retain and report the stored snapshot
and the specific delivery problem. Do not substitute a remote `localhost` URL,
claim the browser opened, change the tailnet or invent a successful health check.

## Bundle and update semantics

A single-file source should be self-contained. A directory source must be a
dedicated report export, with an explicit entrypoint and its intended assets.
Publishing the current project directory implicitly is not an acceptable shortcut.

Use relative asset URLs so the bundle works below its report URL. The publisher
does not rewrite arbitrary HTML/JavaScript or silently collect files from parent
directories. Clearly missing local dependencies are reported. A bounded dependency
check is useful evidence; it cannot prove every runtime JavaScript fetch succeeds.
Prefer bundled dependencies; disclose any deliberate external dependencies.

Accept regular files and directories within configured size/count bounds. Reject
symlinks, path traversal, special files and an entrypoint outside the selected
bundle. Copy into staging outside the served root, validate the snapshot, and
expose it through an atomic directory rename. Never present partially copied
reports as successful publication. Failure/crash recovery must distinguish
incomplete staging, stored snapshots and committed receipts.

Each distinct bundle and public-metadata snapshot receives an opaque report ID.
Publishing identical output again reuses its verified snapshot and URL. Editing
the original files does not change an existing snapshot. Changed output produces
a new URL; the older link continues to identify the older result. Optional
predecessor metadata can connect revisions without a mutable `latest` alias.
Concurrent publishes cannot overwrite each other's files or metadata.

For authoring, follow the project's existing generated-report convention when
the report belongs with its artifacts. Otherwise a dedicated scratch export, for
example under `~/.cache/codex-plus/report-drafts`, keeps ad hoc reports out of the
project's source inventory. Authoring location is a model/project choice.

Published copies always go into a durable per-user store under
`$XDG_DATA_HOME/codex-plus/reports`, defaulting to this layout:

```text
~/.local/share/codex-plus/reports/
  public/                    # mapped to the URL prefix /reports/
    index.html               # optional catalog, or non-listing landing page
    <report-id>/
      index.html
      assets/...
  metadata/                  # private publication records
  staging/                   # incomplete copies, never served
```

Only the `public` subtree is served. The catalog can project title, project, date
and URL from registry records; original paths, conversation provenance and
internal hashes remain private. Published links continue working if the original
project is moved, its scratch directory disappears or its authoring session ends.
The report directory is runtime data, outside release archives and chezmoi's
managed `exact` trees. Same-user processes are the local trust boundary; a
conversation label does not create an isolated security principal.

## Hosting and browser behavior

Every returned URL names the publishing host, including when the agent and
browser currently run on that same host. Do not switch published links to
`localhost` based on the current viewer: it would change meaning when opened from
another desktop. Recommended HTTPS shape:

```text
https://<publishing-host>.<tailnet>.ts.net/reports/<report-id>/index.html
```

The short-hostname HTTP form is also a valid configured choice:

```text
http://starship:8000/reports/                         # optional catalog
http://starship:8000/reports/<report-id>/index.html   # one report
```

Use a browser-resolvable hostname. Tailscale MagicDNS provides machine names and
fully qualified names; an alias that exists only in SSH configuration is not
browser DNS. Prefer the reported Tailscale name over guessing from the operating
system hostname. A live check on Snap resolved `starship` to `100.84.31.64` during
this planning pass. [MagicDNS naming](https://tailscale.com/docs/features/magicdns).

Tailscale Serve supports HTTPS file/directory serving and a configured path mount.
It also supports an HTTP port with short MagicDNS names. HTTPS mode requires
tailnet HTTPS setup; tailnet access rules apply to serving. This makes it a
candidate for a durable per-host report route without a separate application
server. [Serve reference](https://tailscale.com/docs/reference/tailscale-cli/serve),
[HTTPS and access prerequisites](https://tailscale.com/docs/features/tailscale-serve).

Changing a URL alone cannot expose a service bound only to loopback. The selected
serving endpoint must accept traffic over the tailnet, and the viewing desktop
must resolve/reach it. A loopback address is fine for an internal proxy backend;
the user-facing URL remains host-addressed. Port 8000 above is an example, not a
reserved endpoint; a later check found an existing Starship listener on that port,
so the implementation plan proposes dedicated port 8787. Roaming preserves the
URL as the
viewing device changes networks or desktops; it does not make an offline
publishing host available.

Configure the serving route once as an operator/deployment action. Ordinary
publish calls read its configuration and write report data; they never run
`tailscale serve reset`, overwrite unrelated routes, enable Funnel, change ACLs
or trigger account-wide HTTPS setup. Coexistence with existing Serve routes is
an installation check. Starship's read-only Serve inspection returned an empty
configuration during this planning pass; Snap and Carbon still need current
deployment inspection.

Per-host hosting avoids introducing a central upload service. It also means a
report cannot be fetched while its publishing host is asleep, offline or retired.
Stored files survive a reboot; serving depends on the host and Tailscale returning.
If reports must remain available while laptops are off, a central always-on report
host becomes a separate selected backend and adds upload/ownership work.

Reachability and browser launching remain distinct. Codex 0.162.1's ordinary
transcript click invokes the browser opener on the TUI host. Kitty's existing
Ctrl+Shift+left-click opens the link on the desktop running Kitty, including when
an application grabs mouse input. Visible URL hints provide a keyboard route.
The returned link should therefore include visible URL text, with a concise
modifier-click hint only when useful. [Matching Codex issue](https://github.com/openai/codex/issues/52766),
[Kitty mouse actions](https://sw.kovidgoyal.net/kitty/conf/#mouse-actions).

Automatic opening is deferred. A future desktop relay would need explicit
destination selection or pairing; neither SSH environment variables nor a remote
MCP process identify the intended browser reliably. Multiple desktops and nested
SSH must not result in broadcasting browser-open requests.

## Lifetime and removal

Reports persist until explicitly deleted. They are independent of turn activity,
TUI attachment, tmux, daemon thread unload timers and MCP process lifetime. A
hosting outage does not delete the snapshot or silently republish it elsewhere.

Do not evict older reports automatically to make a new publish succeed. Enforce
configured storage bounds and return a clear capacity error. Local inventory and
exact-report deletion provide the first cleanup controls. Choose initial storage
limits from representative report fixtures before installation.

No TTL or scheduled pruning is promised in v1. If retention is added later,
distinguish a cleanup schedule from a guaranteed access deadline: serving static
directories directly does not enforce expiry before a cleanup job removes them.
Deletion removes future server availability; it cannot retract browser-cached or
downloaded copies.

## Skill behavior

The skill applies when the user requests an HTML report, or the task benefits from
a substantial browser presentation. Ordinary concise answers remain concise.
It can be invoked explicitly and discovered normally; preserve the explicit-only
policies of unrelated worker skills.

The workflow is: author a dedicated report, check its meaningful interactions and
assets, publish it, assess the delivery receipt, and return the useful result with
the link. The model retains choice of structure, visuals and depth. Templates,
if supplied later, are optional starting points. Generating a report is not proof
that its underlying analysis is correct, or that its browser presentation passed.

## Repository and distribution plan

Keep implementation in codex-plus, with small report-core/CLI modules, an optional
report MCP entry point, `skills/html-report` and focused behavioral tests. Update
the explicit source inventory deliberately. Keep report tests separate from
native watch/peer acceptance.

Define the report component's own compatibility and package inventory. The current
runtime artifact declares Codex 0.162.1 and an existing native Unix daemon as
requirements; those requirements must not become report dependencies. Reuse
package verification and immutable-selection mechanics where they fit, without
changing the already published preview artifact/tag.

Qualify skill and MCP loading in each intended client. Plugin manifests are thin
distribution wrappers around the same skill/core, not alternative implementations.
For the fleet, chezmoi owns installed code selection, skill discovery wiring and
per-host application configuration. Tailnet HTTPS/access policy and Serve-route
ownership need an explicit deployment step after inspection; report publication
must not perform that setup. Preserve unrelated source and live configuration.

## Implementation slices and acceptance

1. **Publish core and CLI.** Dedicated file/directory exports, immutable snapshots,
   receipts, bounded list/get/delete and doctor. Verify single-file and multi-asset
   reports, concurrent publishers/index updates, interrupted copies, path escapes,
   capacity failure and deletion that preserves sources/other reports. No native daemon
   or MCP dependency is allowed in these tests.
2. **One-host hosting qualification.** Inspect Serve/HTTPS prerequisites and route
   ownership. Use isolated report content to qualify the configured route, relative
   assets, hostname resolution, configured HTTP/HTTPS mode, optional index behavior,
   exact fetched bytes and persistence after publisher/client exit. Installing
   a real route is a separately requested deployment action.
3. **Agent integration.** Add the skill and report-only MCP adapter where useful.
   Verify ordinary requests, honest unavailable-hosting receipts, readable links
   and the absence of native Codex owner calls during discovery/publication. Test
   the actual installed client versions; no model-study rerun or live peer actions.
4. **Desktop acceptance.** Open a report generated on another host, inspect its
   interactive controls/assets, and verify Kitty local opening from an SSH TUI.
   Cover the actual tmux path separately, especially hidden hyperlink handling.
   HTTP retrieval alone does not close this gate.
5. **Release and fleet installation.** Publish verified report-component bytes,
   prepare coordinated chezmoi pins/configuration/checks and scoped dry-runs, then
   apply the requested hosts and verify installed files and desktop delivery.
   Starship, Snap and Carbon require individual evidence; an offline host remains
   pending rather than inheriting another host's success.

The next pass should settle the proposed per-host backend, immutable URLs and
explicit retention, then execute the core/CLI slice. Automatic opening, live apps,
central hosting, mutable aliases, richer report-library UI and scheduled cleanup
can follow demonstrated need. This document authorizes no service activation,
tailnet change, deployment, daemon restart or source publication by itself.
