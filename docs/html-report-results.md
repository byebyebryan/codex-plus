# HTML report implementation evidence

## Managed MCP default: 2026-10-14

Bryan selected enabling report MCP by default. Published dotfiles 965f041 changes
supported-host availability and explicitly approves report_publish/report_delete
under the existing never-approval policy. Existing explicit opt-outs, disabled
and enabled tool lists, custom approval tables and machine overrides are tested
and preserved. A tested htmlReportOnly apply mode changes only this MCP entry.

The config-only change was applied on Snap and Starship from the same clean
published source. No report/runtime release, data, hosting configuration, worker
or other native setting was changed. Both existing daemons and report servers
remain running; canonical dirty bytes and local history are preserved.

On each host, a fresh ordinary native TUI session loaded all four tools from
managed configuration and successfully called report_list. A second fresh session requested report-argument overrides for an isolated store,
but native receipts show the override was not applied: the prepared synthetic
report was published in each normal configured catalog. All four tools executed
successfully under the managed policy. Only the new synthetic report was deleted,
using its exact returned identity; no pre-existing report was selected for deletion.
Before/after inventory counts match and the pre-existing sampled reports remain.
The shared servers were reused. This corrects the initial claim of isolated native
writes; configured-store write acceptance passed, and private-store isolation was
not proved by that launch. The unused private config also lacked schema=1, caught
by a subsequent CLI check. No additional trial or global reload was used.
The four owned test actors are archived with no pending input or viewers.

Both canonical chezmoi checkouts also received targeted local integration commits,
so their older off default cannot undo activation on a later apply. Their existing
branch history and unrelated pending edits were preserved; only the new report
fixture hunk was staged from Starship's already modified full validator. The
authoritative managed policy is published on main as 965f041.

Full dotfiles and component validators, source inventory and six report-MCP tests
passed. Runtime/artifact pins remain unchanged. A fresh session sees the new
capabilities; no daemon restart or global MCP refresh was performed.


Preview 7 explicitly starts the report tmux session in its configured data root.
The displayed directory is consistent across launch contexts; publication and
the HTTP public root continue to use the existing configured paths. This change
is isolated from the concurrent native runtime work and preserves report URLs.

Current project-browsing edition: preview 6 adds counted project groups, combined
project/search filters, bookmarkable navigation and project catalog links in
CLI/MCP receipts. The skill uses stable labels and links relevant earlier reports
when presenting updates. Existing snapshot files, identities and URLs are
unchanged. Validation and rollout evidence for this edition is under
`~/.local/state/codex-plus/report-projects/20261013/`; historical qualification
records below retain their original release/test counts.
The complete suite passes 258 tests, including five project history, catalog
escaping, receipt and provider-neutral MCP regressions. Skill and source gates
pass; browser acceptance and fleet installation have separate evidence records.

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

Live rollout completed on Starship and Snap using the published
`reports-v0.1.0-preview.2` artifact at source `c36e9f1`. The published/downloaded
archive matched the reproduced SHA-256
`1da07c2193a0dbdc9b11aa816657e6c083b8cf5cb25c8919200731d06011208b`.
Canonical chezmoi installs only report code/links/config/skill and starts the
code-report-server tmux session. Installed payload checks, source/target
convergence and local catalog/report HTTP byte checks passed on both hosts.
All five sample HTML/CSS/JS/JSON/SVG files matched in each peer direction.
Chrome opened the live Snap catalog/report, loaded the relative assets, filtered
rows and exercised the HTTP copy fallback. The launcher and SSH command exited
while both detached servers continued running.

The only firewall changes were runtime/permanent IPv4 TCP 8787 allowances from
100.64.0.0/10 in Starship's public zone and Snap's tailscale zone. Existing rules
were retained; no firewall reload, Serve reset or native daemon restart occurred.
Both existing project servers and Snap's Codex Plus checkout remained untouched.
The 138 unrelated source files and prior check-script edits on each host retained
their protected bytes. Carbon was offline and is not activated. Native terminal
modifier-click remains user acceptance beyond browser automation. Tmux requires
starting the server again after host reboot.

Live evidence and browser screenshot:
`~/.local/state/codex-plus/report-http/20261013-tmux/` on the participating hosts.

## Review gap closure

Preview 5 closes the three reproduced review findings. Ordinary management pins
tmux's default socket and clears inherited attachment variables, including for
attach. Completed snapshot entrypoints and asset directories may use `.write-*`
names, while root index-write temporaries remain hidden over HTTP.

Deletion retains its exact trash identity until physical cleanup finishes.
Publication checks that state before admission and again after copying, so a
concurrent completed-but-uncleaned deletion cannot be overwritten. Exact delete
retry and explicit repair share the cleanup path; remaining trash reserves both
payload and report capacity. The source suite passes 253 tests, including six new
regression cases for the review findings and their recovery/quota consequences.

The refined source preserves the unrelated worker/runtime files. Its artifact,
upstream integration and live rollout have separate qualification records under
`~/.local/state/codex-plus/report-goal-closure/20261013/`. Carbon's live rollout
still requires the offline host to become reachable.
