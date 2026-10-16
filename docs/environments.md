# Multiple Codex environments

Implementation contract: native Codex owns its homes and daemons. Codex Plus
resolves one environment from CODEX_HOME, keeps default-home legacy paths, and
uses stable canonical-home namespaces for alternate homes. Native --profile is
not an environment selector. Credentials, MCP admission, migration and wrapper
names remain outside Codex Plus.

Explicit CLI paths take precedence over corresponding CODEX_PLUS_* environment
overrides, then home-derived defaults. Display labels are not storage identity.
Missing selected daemons fail without fallback or automatic startup. Existing
frozen daemon-incarnation bindings remain authoritative.

Monitoring, report MCP/CLI and read-only context
inspection share this contract. Reports can host concurrently on independently
configured endpoints with namespaced tmux ownership. Existing legacy report
config paths retain their session name; explicit existing storage is preserved.
No existing data or active intent is moved or restored automatically.

Acceptance includes offline resolution/override/legacy checks, two-home report
CLI/MCP inventories, isolated concurrent tmux servers with independent lifecycle,
missing-owner refusal, package inventory/install checks and existing regressions.
The original source pass performed no live deployment or owner restart; the
subsequent Snap deployment is recorded below.

## Daily selection and diagnosis

On Snap, `codex` / `codex agents` select default OSS (`~/.codex`), and
`codex-work` / `codex-work agents` select work (`~/.codex-work`). The temporary
`codex-oss` entry point is retired. Peer discovery/messages never cross these
native daemons. Both share an account and Unix user; this is best-effort config
separation rather than filesystem isolation.

Inspect the selected paths with `codex-plus-context`; it does not contact or
start a daemon. The CLI describes only its own environment/arguments, not the
settings hidden in another MCP process. For Snap's managed work setup:

```sh
rtk proxy env CODEX_HOME=/home/bryan/.codex-work codex-plus-context --state-root /home/bryan/.local/state/codex-plus-work --report-config /home/bryan/.config/codex-plus/report-work.toml
```

For OSS, use `~/.codex`, `codex-plus-oss` and `report.toml` instead. These are
existing Snap overrides, not portable default names. Preserve them when using
standalone monitoring/report commands, or pass the exact native MCP arguments.

## Selection and overrides

The canonical absolute Codex home is the storage identity. The environment key is
its SHA-256 prefix (24 hexadecimal characters). Symlink aliases of one home select
one namespace. Native `--profile` settings inside that home share its namespace.
There is no global selected-environment switch, profile registry or new daemon.

| Resource | Default Codex home | Alternate Codex home |
| --- | --- | --- |
| Monitoring | `$XDG_STATE_HOME/codex-plus` | `$XDG_STATE_HOME/codex-plus/environments/KEY` |
| Report config | `$XDG_CONFIG_HOME/codex-plus/report.toml` | `$XDG_CONFIG_HOME/codex-plus/environments/KEY/report.toml` |
| Report data | `$XDG_DATA_HOME/codex-plus/reports` | `$XDG_DATA_HOME/codex-plus/environments/KEY/reports` |

Unset XDG paths use their conventional home-relative defaults. The conventional
home is `~/.codex`, including when CODEX_HOME explicitly names it. CODEX_HOME and
XDG overrides must be absolute; parent traversal is rejected. Resolution and
`codex-plus-context` create no directories or processes and contact no daemon.
The diagnostic reports the configured report data root and URL when the selected
config exists; it does not prove that a server is running. It describes its own
arguments/environment, not overrides hidden inside native MCP configuration. Pass
those same overrides when comparing a manually configured MCP process.

Precedence is explicit argument, matching environment override, then derived path:

- Monitoring: `--state-root`, `CODEX_PLUS_STATE_ROOT`, environment default.
- Reports: `--config`, `CODEX_PLUS_REPORT_CONFIG`, environment default.
- Native endpoint: `--socket`, `CODEX_PLUS_SOCKET`, native status-only discovery
  for monitoring/peer commands.

Explicit report `--data-root` overrides its config; the config's `data_root`
overrides the home-derived default. A missing explicitly selected report config
refuses fallback unless a data-root override deliberately supplies an isolated
store. An absent derived default supports an unconfigured local store in that
same environment. No other home's report config is consulted. Explicit paths can
intentionally share data; environment selection is not an OS security boundary.

For example, a local launcher can set CODEX_HOME and export
CODEX_PLUS_REPORT_CONFIG to keep CLI use consistent with a report MCP configured
using an explicit `--config`. These variables select paths, not credentials.
`mcp-config --codex-home /absolute/home` on either package generator produces an
explicit home-bound MCP snippet. Home-bound snippets also clear inherited component overrides (monitoring
state/socket or report config), so the selected home does not accidentally reuse
a parent environment's resources. Supply explicit path arguments when needed. Explicit
CLI socket options remain authoritative. Existing explicit state/config paths
remain valid and need not adopt derived defaults.

## Concurrent report hosting and compatibility

Report configs retain explicit base URLs, bind addresses and ports. No automatic
port allocation or firewall changes occur. A nonlegacy config gets a tmux session
name keyed by its canonical config path. The conventional report config retains
`codex-report-server`. Fingerprint, process and pane ownership checks still apply.
An already-running legacy session is reused only when its recorded fingerprint
matches the selected store and endpoint; foreign legacy sessions are left alone.
Do not change an active config's storage or endpoint before stopping its owned
server. Distinct configurations require distinct listening endpoints.

Source supports runtime preview.3 and reports preview.8. Snap selects both;
Starship retains its earlier installed releases until a separate apply. Both
package inventories include the shared resolver and context CLI;
previous runtime previews .1/.2 and report preview.7 remain verifiable/selectable.
Component releases and deployment receipts remain independent. The notification
component and the 349 inspector are retired; terminal formatting belongs to
Kitty/chezmoi.

Snap's existing work/OSS overrides, data attribution and separate work report
service are preserved. Its explicit paths take precedence over home-derived
defaults; no store migration is required to adopt the new runtime. Chezmoi continues
to own wrappers, MCP admission, private configuration and host startup policy.
Observer's collection of multiple native homes is independent of Codex Plus.

## Source acceptance

The combined suite passes 326 tests, including ten environment tests. These
cover legacy/canonical-home defaults, explicit overrides, absent daemon/config
refusal, same-thread-ID monitoring separation, CLI/MCP report separation,
home-bound install snippets, real concurrent HTTP/tmux lifecycles on a private
socket, and legacy report-session reuse without restart. Existing foreign-session,
extra-pane, notification/agents and native-binding regression tests still pass.
The explicit 123-file inventory and guide build/link checks pass.

A read-only native check on Snap resolves each existing work/OSS owner and reads
its effective configuration without owner replacement. It confirms current
explicit monitoring roots are retained; it is not a model-turn or watch trial.
Existing runtime preview.2 and report preview.7 payloads verify in clean temporary
copies. The live runtime has pre-existing Python cache files outside its immutable
manifest; those files were neither removed nor treated as exact-install proof.
No goal, watch, wake, peer message, live report or native task was created for this
source acceptance. Report lifecycle tests own only disposable private tmux actors.

Runtime preview.3 and report preview.8 candidates built from source `478138b`
are byte-for-byte reproducible across two builds each. Both archives verify,
install and activate under temporary prefixes, and their relocated context CLI
and MCP inventories work without the source checkout. The relocated report
CLI and MCP also publish/list independently under two temporary homes. These
are candidate-package checks, not published releases or installed Snap upgrades.

## Snap multi-environment deployment: 2026-10-15

Published runtime [preview.3](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.3)
and reports [preview.8](https://github.com/byebyebryan/codex-plus/releases/tag/reports-v0.1.0-preview.8)
from source `c73c237c734eb7e20b46185cccd471edfc803520` and selected them through
chezmoi on Snap. Published downloads match the local artifact checksums; both
installed immutable inventories/modes verify. The 326-test suite passes.

Fresh MCP processes launched from both native homes' configured commands report
runtime preview.3 (15 tools) and report preview.8. Read-only report listing,
context resolution with the actual explicit overrides, native configuration
admission and HTTP health at both configured report endpoints pass. OSS and work
retain their separate state roots, report configs/stores, native owners and auth
files. Neither existing native daemon nor either report server was restarted.
Existing MCP processes retain their captured release until their normal reconnect;
this deployment does not claim to hot-replace already loaded processes.

`codex-plus-context` is installed for read-only diagnostics. Snap's existing
explicit monitoring roots and report configs remain authoritative; pass those
same overrides when inspecting them. No state was moved to derived defaults.
Workers and experimental notification helper retain their independent pins;
native notifications remain selected. Starship's installed selections were not
changed by this Snap deployment. Installed receipts are private host state,
not part of this source tree.
