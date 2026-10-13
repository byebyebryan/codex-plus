# Using the HTML report component

The source implementation supplies durable static snapshots, a static catalog,
standalone CLI, provider-neutral skill and optional local report MCP. It does not
start Codex, a browser or a web server. Real fleet installation/serving is separate
from source and isolated package validation.

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
propose `http://HOST.tail223cf3.ts.net:8787/reports/`; Starship already has a listener
on port 8000. Full names avoid Starship's local loopback alias for its short name.
Use the actual DNS name reported by each host's Tailscale inventory. Short aliases
require separately qualified resolution and reachability. HTTPS is also supported.
Provision a persistent Tailscale Serve
route through its operator; doctor can inspect and print the proposed command
without applying it. Preserve existing routes, servers and tailnet settings.

Entrypoints named `index.html` return the containing directory URL. Tailscale
Serve's file handler redirected an explicit index filename incorrectly during
qualification; directory URLs passed both delivery and browser checks. Other
entrypoint filenames remain explicit. Delivery rejects redirects except the same
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
