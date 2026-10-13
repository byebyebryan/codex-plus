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

## Deployment boundary

Chezmoi integration is prepared in a separate `feat/html-report-install` worktree.
It is disabled until a published artifact URL is selected with its exact revision
and checksum. Local fixture rendering/dry-run checks qualify that integration;
they do not replace a published release or a scoped fleet apply.

Pending deployment gates: publish the reviewed component, choose/enable the exact
artifact pin, scoped chezmoi apply, provision the owned persistent Serve route,
recheck port/DNS/access on each host and qualify persistence after restart. Carbon
was offline and is not qualified. Native terminal modifier-click and user desktop
acceptance remain separate from browser automation. HTTP controls needing secure
browser APIs must retain fallbacks or use a separately configured HTTPS profile.
