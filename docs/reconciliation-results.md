# Reconciliation and presentation pass: 2026-10-16

The user requested an ordinary goal loop after multi-environment deployment and
notification retirement. This pass keeps native owners, installed release pins,
auth, histories, workers and live observation/hosting state unchanged.

## Findings and changes

- The large handoff opened with older installed facts. Its original text is
  retained in [implementation history](implementation-history.md); the current
  [handoff](implementation-handoff.md) now gives one continuation contract.
- Architecture and walkthrough still described runtime preview.2/report preview.7
  as current everywhere. They now distinguish Snap preview.3/preview.8 from
  Starship's installed preview.2/preview.7, confirmed by read-only inspection.
- Environment docs were not a public guide, and normal-use material omitted the
  work/OSS peer and report boundary. The six-guide site includes environments;
  the walkthrough has an illustrative Snap home selector with explicit paths.
- Report docs assumed one config and tmux name. They now explain home-derived
  defaults, explicit existing overrides, config-specific server ownership and
  Snap's separate work service. Standalone callers must select the same overrides
  as their MCP rather than silently switching stores.
- Notification delivery/enrichment and the 349 inspector remain retired. Native
  terminal formatting belongs to Kitty/chezmoi. Historical evidence is labeled.
- The site builder refuses duplicate IDs as well as missing/escaping links and
  fragments. Browser checks exposed GitHub’s attributed table markup bypassing
  the old exact-tag scroll wrapper; the builder now preserves table attributes
  while wrapping both ends correctly. Offline regression checks cover environment routing, historical
  references, unique headings, anchors and output containment.

## Validation and evidence boundaries

Source tests and authored scenes do not create new native/live reliability evidence. No watch, wake, peer
message, model task, notification trial or report snapshot is required for this
pass. GitHub Pages serves the updated presentation; old immutable report editions
remain intact and labeled as historical.

| Check | Result |
| --- | --- |
| Source inventory and worker metadata | 112 declared files; agent/skill validation passed. |
| Full source suite | 279 tests passed, including nine public-site regressions. |
| Public build | Walkthrough plus six guides; 86 local links/assets/fragments verified. |
| Browser interaction | 24 scene states, four home selections, slider, keyboard activation, copy fallback, note download and checklist passed. |
| Desktop/mobile | All six guide routes at 1440px and 390px; diagram loaded; no document overflow or browser errors. |
| Markdown references | 170 relative paths checked, no missing targets. |
| Preservation | 41 protected runtime/worker source files unchanged; tracked native config/auth/pins/selectors and process incarnations preserved. |

Actual browser checks use a disposable headless Chromium context and a private
loopback static server; neither a live user browser nor a shared profile is used.
Screenshots were visually reviewed at both widths. The existing GitHub Pages
workflow publishes main, now including the environment guide and offline page
regressions. The deployment run and fetched-byte/browser receipts are recorded
privately by commit; the public walkthrough is the current guide edition, while
the October 14 immutable report remains a historical edition.
