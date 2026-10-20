# Using the HTML report component

The source implementation supplies durable static snapshots, a static catalog,
standalone CLI, provider-neutral skill and optional local report MCP. Publishing
does not start Codex or a browser. With `server_autostart = true`, CLI/MCP publish
starts or reuses `codex-report-server` under its config-specific tmux ownership.
The server stays running after publication; there is no idle shutdown or report cleanup timer.

## Use it from Codex

With reporting configured in your current environment, ask: “Make a browser
report of the results, including the risks.” Codex prepares the HTML and intended
assets, publishes them under a stable project label and returns the report link.
You can ask to find earlier reports for that project or inspect a selected
report's delivery result. The CLI reference below supports setup and diagnosis;
ordinary use does not require a report ID or command recipe from you.

For a new installation, start with [component setup](getting-started.md#set-up-reporting)
and the [artifact and MCP steps](#verified-artifacts-and-optional-mcpplugin-loading).
GitHub Pages hosts this project's public documentation. The report component
publishes independent snapshots to your configured endpoint; it does not deploy
them to GitHub Pages.

## Publish and find reports

With the component installed on PATH:

```sh
rtk proxy codex-plus-report --json publish --source /absolute/report-export --title "Run comparison" --project "descent-lab" --check-delivery
rtk proxy codex-plus-report list
rtk proxy codex-plus-report --json list --project "descent-lab"
rtk proxy codex-plus-report get FULL_REPORT_ID --check-delivery
rtk proxy codex-plus-report doctor --check-hosting
```

Use `scripts/codex-plus-report` for a source-local invocation. Directory exports
default to `index.html`; `--entrypoint` selects another relative HTML file.
One HTML file must be self-contained. Include intended assets in a dedicated
directory; symlinks, escaping paths and special files are rejected.

The receipt separates publication, catalog and delivery. A configured hostname
URL is not proof that serving is ready. `--check-delivery` verifies actual HTML
bytes and records its check location; it does not open or validate a desktop
browser. Unconfigured/unreachable hosting retains the snapshot. Subsequent
configuration can supply a URL for an initially unconfigured report.
Automatic server startup has its own receipt. Startup failure retains the stored
report and explains the unavailable hosting; it does not take over a foreign
tmux session or listener. Read-only get/list/doctor commands do not start a server.

Unchanged content/title/project reuses a snapshot. Changed content gets a new
immutable link. Files are copied into the selected store, defaulting to
`~/.local/share/codex-plus/reports` for the conventional home. Deleting/moving the
source does not affect the published copy. Reports remain stored until selected deletion, subject to
configured capacity limits that refuse new reports rather than evict old ones.

The catalog groups reports by project, with counts and publication dates. Groups
with the latest activity come first, and reports within each group are newest
first. The project selector and title/project search combine; Clear filters
returns to the complete library. Labels are exact and case-sensitive. Use the
same stable repository name across sessions and hosts. Omitted labels appear
under Uncategorized; the publisher does not infer a label from an export path.

Project views have shareable URLs such as
`http://starship:8787/reports/#project=cubey`. Search state is also stored in the
fragment, so bookmarks and browser Back restore the view. Missing projects show
zero results, and `#uncategorized=1` selects unlabeled reports without reserving
that name as a real project. CLI/MCP publication, get and list receipts add
`catalog_url` and `project_url`; both are null when hosting is unconfigured or
the catalog is disabled. They identify a current mutable catalog view, while
`url` still identifies the immutable report. Existing snapshots are not moved
or rewritten, and older report links remain valid. Catalogs cover their own host.

For an update, use project-filtered inventory to find relevant prior reports and
include their descriptive links in the new HTML. Return its project catalog link
when useful. Open earlier and later reports in separate browser tabs to compare
them. A shared label groups related work; it does not imply an automatic revision
chain or select one report as its replacement.

```sh
rtk proxy codex-plus-report delete FULL_REPORT_ID
rtk proxy codex-plus-report repair
rtk proxy codex-plus-report repair --apply
rtk proxy codex-plus-report catalog-rebuild
```

Repair previews by default. Applying it finishes verified prepared publications,
retries exact interrupted deletion and removes positively identified abandoned
staging. It also releases an unpublished prepared record when no public snapshot
or active publisher remains. Active copy processes and unknown directories are preserved. Catalog
failure leaves the prior index and stored report intact; rebuild repairs it.
If physical trash removal is interrupted, retry the same delete or apply repair
to finish that exact cleanup. Republishing that identity is refused until cleanup
finishes, including when deletion completes during another copy. Remaining trash
continues to reserve payload/report capacity. Source files and other reports are
preserved.

## Configuration and hosting

The conventional home defaults to `~/.config/codex-plus/report.toml`, respecting
`XDG_CONFIG_HOME`. Alternate `CODEX_HOME` values derive separate config and data
paths; `CODEX_PLUS_REPORT_CONFIG`, `--config` and `--data-root` can preserve
explicit existing paths. A missing explicitly selected config refuses fallback.
See [the environment contract](environments.md) before mixing CLI and MCP calls.

On Snap the work MCP explicitly uses `report-work.toml` and port 8788; OSS uses
`report.toml` and port 8787. For a standalone work report command, select the same
work home and pass that existing config explicitly; setting `CODEX_HOME` alone
would select the derived default instead of this managed override.
The [implementation plan](html-report-plan.md#configuration-and-serving-ownership)
shows the supported schema and initial tunable limits.

Serve only the store's `public` subtree at the configured URL prefix. Host profiles
select `http://HOST:8787/reports/`, using `starship`, `snap` and `carbon`; Starship
already has a listener on port 8000. Short names must resolve to the serving host's
Tailscale address from both the publishing host and viewing desktops. Starship's
local host mapping addresses its earlier loopback alias. This host-side setting
stays outside chezmoi and needs rechecking after re-enrollment. Full MagicDNS URLs
remain configurable. HTTPS is supported and requires the full MagicDNS hostname
when using Tailscale-managed certificates. The publisher and HTTP server do not
require Tailscale; these machine names use the existing mesh's DNS/network.

```sh
rtk proxy codex-report-server start
rtk proxy codex-report-server status
rtk proxy codex-report-server attach
rtk proxy codex-report-server restart
rtk proxy codex-report-server stop
```

`start` initializes an owned store if needed and starts one detached tmux session
named **codex-report-server** for the conventional config, window **http**.
Other config paths get stable config-specific session names, so independent
stores/endpoints can coexist. An explicitly managed service can own serving
instead; Snap work uses its existing service with autostart disabled.
A repeated start reuses the healthy owned server. The session starts in the configured report data root, consistently
across callers and hosts. This display directory does not determine publication
or serving: the publisher uses `data_root`, and HTTP serves its `public` subtree.
HTTP reads the public subtree at the URL prefix; publishing new
reports needs no server restart. The bind address defaults to the configured URL
hostname; `server_bind` can select another local address. Only HTTP is built in;
HTTPS can use an external server.
Management explicitly selects tmux's default socket and clears inherited client
attachment variables. Starting, inspecting or attaching from another tmux socket
therefore manages the same shared server. The explicit `--tmux-socket` option
continues to select a separate socket for isolated checks.

`server_autostart` defaults to false for standalone/external installations.
Chezmoi enables it for default-home configs; Snap work uses its separate service. Publish starts a missing server, reuses a healthy
one and replaces an exited owned pane. It leaves an unhealthy live server or a
foreign session alone. Explicit `--data-root` overrides require matching store
settings in the selected config file for automatic hosting.

The session survives TUI closure, SSH disconnect and terminal closure. Tmux does
not survive host reboot: the next publish starts it again, or run
`codex-report-server start` to restore access before publishing. Chezmoi's
scoped installation starts it through an idempotent apply script. `stop` and
`restart` revalidate the owned session, configuration and actual process; foreign
same-named sessions and added user panes are refused. Stopping preserves reports.
`--config` supports another explicit configuration; `--tmux-socket` isolates tests
from regular sessions. HTTP hosting needs the chosen port reachable through the
host's firewall. `doctor --check-hosting` verifies HTTP catalog bytes with any
configured server and executes no Tailscale commands.

Entrypoints named `index.html` return the containing directory URL. The built-in
server supports both explicit index filenames and directory URLs, including
nested reports. Other entrypoint filenames remain explicit. Delivery rejects redirects except the same
origin's exact index-to-directory canonicalization and verifies the returned bytes.
Completed snapshot files and directories may use `.write-*` names. Only the
store's own temporary index files at the public root are hidden over HTTP.

The optional index is generated from public title/project/date/link fields.
Private source/provenance/hash records are outside the served tree. Disabling the
catalog leaves a non-listing landing page; direct report URLs still work. The
serving host must be online. When using an SSH TUI in Kitty, Ctrl+Shift-click opens
the link in the local desktop browser. HTTP report controls need fallbacks for
HTTPS-only browser APIs such as clipboard writing.

## Verified artifacts and optional MCP/plugin loading

The report component is packaged separately from supervision and worker artifacts:

```sh
rtk proxy scripts/codex-plus-report-package build --output /absolute/outside/repo/report.tar.gz
rtk proxy scripts/codex-plus-report-package verify /path/report.tar.gz --sha256 EXPECTED_SHA256
rtk proxy scripts/codex-plus-report-package install /path/report.tar.gz --prefix /absolute/install --sha256 EXPECTED_SHA256
rtk proxy scripts/codex-plus-report-package activate --prefix /absolute/install --revision FULL_SOURCE_REVISION
rtk proxy scripts/codex-plus-report-package mcp-config --prefix /absolute/install --config /absolute/report.toml
```

Build requires committed, clean source. The artifact declares exact hashes/modes,
source revision and Linux/Python compatibility without a native agent owner.
Installations keep immutable releases; selection changes only `current`. Data and
config are outside that prefix. Wrappers resolve their real release before import.
Use these commands for isolated/unmanaged validation; chezmoi owns Bryan's fleet.

The artifact includes portable and Codex compatibility plugin manifests exposing
the shared skill. The skill needs the installed CLI or independently configured
report MCP. The generated MCP config selects the installed stdio entry point and
retains write approval policy. There are four tools: publish, get, list and delete.
They require no native thread metadata; discovery creates no store or daemon.

Bryan's managed configuration enables report MCP by default on supported hosts
when the report component is enabled. It keeps required=false and explicitly
approves report_publish/report_delete under the current never-approval policy.
Tool availability does not authorize publication or deletion without user intent.
Existing explicit opt-outs, disabled tools and custom approval preferences are
preserved. A report-only Codex-config apply uses `htmlReportOnly=true` to preserve
unrelated settings. Fresh native sessions load the tools without restarting or
globally refreshing active daemons.
Plugin hosting/browser behavior still depends on the configured report endpoint.
