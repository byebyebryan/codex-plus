# Browser walkthrough

The [self-contained walkthrough](presentation/index.html) explains current
capabilities with three illustrative scenes: an endpoint watch, coordination
between independent sessions, and a later MCP inspection followed by a report.
Open the HTML locally or use the published browser link recorded in the
[documentation pass results](documentation-pass-results.md).

The scene controls reveal a request, setup, useful update and stop/handoff. They
only change the page; they do not run commands, create watches, send messages or
control a session. Dialogue is authored illustration, not a captured native run.
Technical proof is linked separately to the committed acceptance reports.

The page includes the component map, tool-check cost comparison, lifecycle FAQ,
Claude-workflow coverage, limits and a downloadable private-use soak-note
template. Prompt copy controls have a plain-HTTP fallback for SSH/mesh-hosted
reports. It uses inline assets and JavaScript with no third-party dependencies.

## Authoring and publication

Edit `docs/presentation/index.html`. Keep every asset embedded or inside a
dedicated export directory. Verify desktop/mobile layouts, keyboard controls,
scene state, copy/download controls and absence of browser errors before publishing.

Publish only the finished HTML:

```sh
rtk proxy codex-plus-report --json publish --source /absolute/codex-plus/docs/presentation/index.html --title "Codex Plus: daily use and workflow guide" --project codex-plus --check-delivery
```

Read the receipt: a stored snapshot, configured URL, verified HTTP bytes and
browser acceptance are separate facts. Changed content gets a new immutable
URL. Keep previous reports unless the user selects deletion. The shared report
server remains independently managed; publication reuses it when healthy.

The daily quickstart and reference material remain readable without a browser:
[daily use](daily-use.md), [architecture and comparison](architecture.md), and
[soak checklist](soak-checklist.md). This presentation does not change installed
runtime bytes, managed release pins or worker invocation behavior.
