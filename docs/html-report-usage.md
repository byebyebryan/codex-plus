# Using the HTML report component

The source implementation supplies durable static snapshots, a static catalog,
standalone CLI, provider-neutral skill and optional local report MCP. Publishing
does not start Codex or a browser. With `server_autostart = true`, CLI/MCP publish
starts or reuses `codex-report-server` in its shared tmux session. The server stays
running after publication; there is no idle shutdown or report cleanup timer.

## Publish and find reports

With the component installed on PATH:

```sh
rtk proxy codex-plus-report --json publish --source /absolute/report-export --title "Run comparison" --project "descent-lab" --check-delivery
rtk proxy codex-plus-report list
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
immutable link. Files are copied into XDG data, default
`~/.local/share/codex-plus/reports`; deleting/moving the source does not affect
the published copy. Reports remain stored until selected deletion, subject to
configured capacity limits that refuse new reports rather than evict old ones.

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

## Configuration and hosting

Configuration defaults to `~/.config/codex-plus/report.toml`, respecting
`XDG_CONFIG_HOME`. `--config` and `--data-root` support explicit isolated tests.
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
rtk proxy tmux attach -t codex-report-server
rtk proxy codex-report-server restart
rtk proxy codex-report-server stop
```

`start` initializes an owned store if needed and starts one detached tmux session
named **codex-report-server**, window **http**. A repeated start reuses the healthy
owned server. HTTP reads the public subtree at the URL prefix; publishing new
reports needs no server restart. The bind address defaults to the configured URL
hostname; `server_bind` can select another local address. Only HTTP is built in;
HTTPS can use an external server.

`server_autostart` defaults to false for standalone/external installations.
Chezmoi enables it on this fleet. Publish starts a missing server, reuses a healthy
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
Plugin hosting/browser behavior still depends on the configured report endpoint.
