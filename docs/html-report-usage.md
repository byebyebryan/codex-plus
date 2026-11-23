<a id="using-the-html-report-component"></a>

# Publish an HTML report

Choose the report address from the reader’s side. Use `localhost` if your
browser runs on the Codex machine. If you run Codex over SSH and read on
your laptop, use a hostname the laptop can reach. Set it once and the report
skill uses it for each new publication in that environment.

## Use it from Codex

> Show the same book in both export formats side by side. Publish the
> comparison with my other reading-list reports and give me the link.

With reporting configured in this environment, Codex prepares the export and
returns the report link. Ask “Find the earlier reading-list reports” to browse
the project catalog or “Check delivery for this report” to inspect its receipt.

## From export to browser

1. **Prepare the export.** Codex creates the HTML and collects its assets.
2. **Publish a snapshot.** The publisher stores a copy under a stable link. A project label groups related reports.
3. **Check delivery.** Codex can compare the served HTML with the saved copy.
4. **Open the report.** Follow the link from a browser that can reach the report host.

[Set up reporting](getting-started.md#set-up-reporting) · [Agent installation guide](manage-agent.md) · [Verified artifacts and MCP](#verified-artifacts-and-optional-mcpplugin-loading).

## Publish and find reports

### Publish an export

```sh
codex-plus-report --json publish --source /absolute/report-export --title "Exporter comparison" --project "reading-list" --check-delivery
```

Use `codex-plus-report` when it is on PATH, or `scripts/codex-plus-report`
from source. A directory export uses `index.html` by default. Select another
relative HTML file with `--entrypoint`. Include only intended files. The
publisher rejects symlinks, escaping paths and special files.

Publishing the same files, entrypoint, title and project reuses the snapshot.
Changing any of them creates a new immutable link. The conventional store is `~/.local/share/codex-plus/reports`.
Moving or deleting your export leaves the stored copy accessible. Reports stay
until you select them for deletion. When capacity is exhausted, the publisher
refuses new reports.

### Read the receipt

| Result | What it tells you |
| --- | --- |
| Publication | The store holds the snapshot. If hosting is unconfigured or unreachable, the copy is still there. A later configuration can supply its URL. |
| Catalog | An enabled index links the report under its project. A catalog update failure preserves the previous index and the stored report. |
| Server startup | When enabled, automatic startup records whether the publisher started or reused its server. A startup failure leaves the snapshot in place and reports the hosting problem. |
| Delivery | `--check-delivery` verifies the HTML bytes and identifies the check location. Open the link separately on your viewing desktop. |

### Find and share earlier reports

```sh
codex-plus-report list
codex-plus-report --json list --project "reading-list"
codex-plus-report get FULL_REPORT_ID --check-delivery
codex-plus-report doctor --check-hosting
```

Use the **report link** (`url`) for an immutable snapshot. Use the **project
link** (`project_url`) for a current view of one project or the **catalog link**
(`catalog_url`) for this host’s whole collection. CLI and MCP publish, get and
list receipts expose the catalog links when hosting and the catalog are
configured. Otherwise those fields are null.

The catalog shows project counts and publication dates. Projects with recent
activity come first and reports are newest first within each group. Filter
by project and search by title or project together. **Clear filters** restores
the whole library.

Use one exact, case-sensitive label across sessions and hosts. Omitted labels
appear under **Uncategorized**. Each host lists its own reports. For example,
`http://starship:8787/reports/#project=reading-list` opens one project on
Starship. Search and filters live in the URL fragment, so bookmarks and Back
restore the view. A missing project shows zero matches. `#uncategorized=1`
selects unlabeled reports while leaving that name available as a project label.

For a comparison, link earlier reports in the new HTML and open the snapshots
in separate tabs. Reports that share a label remain individual snapshots with
their original links. You choose which reports to compare.

### Delete and repair

```sh
codex-plus-report delete FULL_REPORT_ID
codex-plus-report repair
codex-plus-report repair --apply
codex-plus-report catalog-rebuild
```

- **Delete** selects one report. If physical trash removal is interrupted, retry that deletion or apply repair. Remaining trash reserves capacity, and the store refuses republication of that identity until cleanup finishes, including during another copy.
- **Repair** previews the changes. Applying it finishes verified prepared publications, retries exact interrupted deletions and clears positively identified abandoned staging. It releases an unpublished prepared record once both the public snapshot and active publisher are absent. Active copies, unknown directories, source files and other reports are preserved.
- **Rebuild the catalog** to restore the index from stored reports after an indexing failure.

## Configuration and hosting

### Choose the config and store

The conventional home uses `~/.config/codex-plus/report.toml` and respects
`XDG_CONFIG_HOME`. Alternate `CODEX_HOME` values derive separate config and
data paths. `CODEX_PLUS_REPORT_CONFIG`, `--config` and `--data-root` select
explicit paths. A missing explicitly selected config stops the command.
[Environment contract](environments.md) · [Configuration schema and limits](html-report-plan.md#configuration-and-serving-ownership).

On Snap, the work MCP uses `report-work.toml` and port 8788. OSS uses
`report.toml` and port 8787. For a standalone work command, select the work
home **and** pass its existing config explicitly. Setting `CODEX_HOME` alone
selects the derived default.

### Choose a reachable endpoint

Serve the store’s `public` subtree at the configured URL prefix. The managed
host profiles use `http://HOST:8787/reports/` with `starship`, `snap` or
`carbon`. Starship already has a listener on port 8000.

- The short hostname must resolve to the serving host’s Tailscale address on both the publisher and viewing desktops. Starship’s host-side mapping corrects its earlier loopback alias. This mapping lives outside chezmoi and needs rechecking after re-enrollment.
- A full MagicDNS URL also works. Tailscale-managed HTTPS certificates require the full MagicDNS hostname. The report software can run on other networks.
- Allow the serving port through the host’s firewall. `doctor --check-hosting` verifies HTTP catalog bytes from any configured server without calling Tailscale.

### Manage the built-in server

```sh
codex-report-server start
codex-report-server status
codex-report-server attach
codex-report-server restart
codex-report-server stop
```

**Start.** The first start initializes an owned store if needed and starts a
detached tmux session with an `http` window. The conventional config names
the session `codex-report-server`. Other configs get stable, distinct names.
Starting again reuses a healthy owned server. Its pane starts in the configured
report data root, and HTTP serves that store’s `public` subtree.

**Publish.** New reports appear without a server restart. With
`server_autostart = true`, publication starts a missing server, reuses a
healthy one or replaces an exited owned pane. A foreign session or listener
and an unhealthy live server are left alone. An explicit `--data-root`
override needs matching store settings in the chosen config for autostart.
Read-only get, list and doctor commands leave the server as they find it.

**Stop and restart.** Both commands verify session ownership, configuration
and the actual process. A foreign same-named session or extra user panes block
the operation. Stopping the server preserves the reports. TUI closure, SSH
disconnect and terminal closure leave the tmux session running. After a reboot,
run `codex-report-server start` or let the next autostart-enabled publish start
it. The server has no idle shutdown or report cleanup timer.

**Defaults and overrides.** Standalone installs default to
`server_autostart = false`. Chezmoi enables it for default-home configs
and its scoped apply starts the server idempotently. Snap work uses its
existing service with autostart disabled. The bind address defaults to the URL
hostname. Set `server_bind` to use a different local address. The built-in
server speaks HTTP. An external server can provide HTTPS.

Use `--config` for another configuration. Server management uses tmux’s
default socket and clears inherited attachment variables, even when you
call it from another socket. Use `--tmux-socket` to select a
separate socket explicitly.

### Open a report URL

An `index.html` entrypoint gets a directory URL. The built-in server accepts
the index filename or its directory, including nested reports. Other HTML
filenames stay in the link. Delivery checks accept only the same origin’s
exact index-to-directory redirect and verify the returned bytes.

The optional index contains public titles, projects, dates and links. Private
source, provenance and hash records live outside the served tree. Disabling
the catalog leaves a non-listing landing page and working direct URLs.
Completed snapshots may include files and directories named `.write-*`.
Only temporary index files at the public root are hidden over HTTP.

From an SSH TUI in Kitty, Ctrl+Shift-click opens the link in your local
desktop browser. When authoring interactive reports for HTTP, give controls
like clipboard copy a fallback for APIs that require HTTPS.

## Verified artifacts and optional MCP/plugin loading

Reporting is an optional archive in the single Codex Plus release, sharing its
version and source commit with workers and monitoring. See
[release verification](runtime-distribution.md#one-codex-plus-release).
For a standalone install, build or verify the archive before selecting its revision.

```sh
scripts/codex-plus-report-package build --output /absolute/outside/repo/report.tar.gz
scripts/codex-plus-report-package verify /path/report.tar.gz --sha256 EXPECTED_SHA256
scripts/codex-plus-report-package install /path/report.tar.gz --prefix /absolute/install --sha256 EXPECTED_SHA256
scripts/codex-plus-report-package activate --prefix /absolute/install --revision FULL_SOURCE_REVISION
scripts/codex-plus-report-package mcp-config --prefix /absolute/install --config /absolute/report.toml
```

A source build requires a clean, committed checkout. The archive records hashes,
modes, source revision and Linux/Python compatibility. Selecting an immutable
release updates `current`. The store and config live outside that prefix.
Each wrapper resolves its real release before importing code. Use the component
installer for unmanaged or isolated installations. Chezmoi owns the managed fleet.

**Skill and MCP.** The portable and Codex compatibility plugin manifests
expose the same provider-neutral skill. It can use the installed CLI or a
separately configured report MCP. The generated MCP config points to the
installed stdio entrypoint and retains the write approval policy. Its four
tools publish, get, list and delete reports. Discovery needs neither a store
nor a daemon. Operations run independently of native thread metadata.

**Managed loading.** On supported hosts, enabling reporting enables its MCP
by default. It sets `required=false` and explicitly approves `report_publish`
and `report_delete` under the configured never-approval policy. Publication
and deletion still require user intent. Explicit opt-outs, disabled tools and
custom approval settings take precedence.

A report-only Codex config apply uses `htmlReportOnly=true` to preserve
unrelated settings. Open a fresh native session to load the tools. The
configured report endpoint handles serving and desktop access.
