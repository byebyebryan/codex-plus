# HTML report implementation evidence

2026-10-13. Source lives on `feat/html-report`, separate from Snap's scheduling
and communication checkout. The report component has no native Codex owner,
daemon, thread, watch or peer dependencies. Existing worker/runtime files remain
unchanged; report discovery does not start an agent or create a store.

Implemented: immutable copied static bundles, unchanged-output reuse, optional
escaped static catalog with search, bounded inventory/deletion, inspectable
prepared/deleting/staging recovery, standalone CLI, report-only stdio MCP,
provider-neutral skill and independent reproducible artifact with plugin manifests.
Source and isolated-package validation do not mean fleet deployment is complete.

## Qualification

- The full Python suite passes: 209 tests, including the existing 177 native,
  runtime and worker tests. Report checks cover source edits, concurrent publishers,
  integrity refusal, interrupted publication/deletion, catalog failure, active vs
  abandoned staging, capacity and metadata bounds, path/symlink safety and HTTP
  entrypoint byte verification.
- MCP tests discover/call the independent adapter without native agent metadata,
  retain truthful stored-but-unavailable receipts and reject oversized requests.
- Package tests verify reproducible bytes, relocated CLI/MCP operation without the
  source tree/native executable, exact payload/modes/checksums, unsafe archives and
  immutable release selection. The packaged plugin exposes the shared skill;
  report MCP configuration uses an explicit installed executable path.
- A five-file synthetic export (HTML, CSS, JavaScript, JSON and SVG) was published
  from an isolated installation. A temporary foreground Tailscale Serve route
  exposed only that fixture store's public directory on port 34483.
- Snap retrieved the fixture over the host's full MagicDNS URL with HTTP 200.
  Chrome loaded the report and relative assets, rendered the SVG, filtered data,
  exercised the HTTP clipboard fallback, searched the catalog and opened its link.
  A screenshot is retained with the local qualification artifacts.
- Short `starship` resolves to a loopback alias locally. Explicit `index.html`
  URLs also triggered a misdirected Serve redirect. Full MagicDNS names and
  directory entrypoint URLs passed actual checks. Hosting inspection recognizes
  foreground/persistent routes and validates transport, port, mount and data path.
- The owned foreground Serve route was stopped after qualification; Serve status
  returned to its original empty configuration. The test tab was closed. Existing
  sessions, servers, native daemons and network policy were left untouched.

Local evidence directory:
`~/.local/state/codex-plus/report-goal/20261013T204043Z/`.

The user subsequently selected short HTTP URLs for Snap/Starship use. Candidate
profiles now return `http://HOST:8787/reports/`. Starship's single local hostname
mapping was changed from loopback to its Tailscale address, with a guarded backup,
so its local browser and delivery probes can use the same short URL. Original
returned URLs remain unchanged; no existing reports were republished.

With owned temporary Serve routes on port 8787, exact HTTP 200 fixture bytes were
verified on all four routes: Starship local, Snap local, Snap to Starship and
Starship to Snap. The installed publisher's short-URL delivery probe and route
inspection passed. Both temporary routes were removed, restoring each host's
original empty Serve state. `localhost` still resolves to loopback. Follow-up
evidence is under `~/.local/state/codex-plus/report-url/20261013-short-http/` on
each host; Starship's root-owned hosts backup is
`/var/backups/codex-plus-report/20261013-short-http/hosts`.

## Deployment boundary

Chezmoi integration is prepared in a separate `feat/html-report-install` worktree.
It is disabled until a published artifact URL is selected with its exact revision
and checksum. Local fixture rendering/dry-run checks qualify that integration;
they do not replace a published release or a scoped fleet apply.

The user then selected plain HTTP in tmux instead of Tailscale Serve. This edition
includes `code-report-server` start/status/attach/restart/stop, generic HTTP hosting
inspection and separate lifecycle controls. The session is explicitly named
code-report-server, with an http window, and does not attach or start a native agent.
HTTP and isolated tmux tests cover assets, HEAD/Unicode/nested index URLs, private
path and symlink refusal, parallel idempotent starts, launcher-exit persistence,
owned restart/stop, foreign named sessions and added user panes. Tailscale is not
required by publishing, HTTP serving or hosting checks.
The combined source suite passes 244 tests after incorporating the separately
published upstream runtime work; the 67 unrelated native/runtime/worker files
match the post-merge protected hashes. Source inventory and whitespace gates pass.

Pending deployment gates: publish the reviewed component, choose/enable the exact
artifact pin, scoped chezmoi apply, start the owned HTTP tmux server,
recheck port/DNS/access on each host and qualify persistence after launcher exit. Carbon
was offline and is not qualified. Native terminal modifier-click and user desktop
acceptance remain separate from browser automation. HTTP controls needing secure
browser APIs must retain fallbacks or use a separately configured HTTPS profile.
