# Product page and interactive walkthrough

[Open the public browser walkthrough](https://dev.byebyebryan.com/codex-plus/).
GitHub Pages also serves the setup, daily-use, worker, architecture, environment,
soak, reporting and installation guides. Use **Guides** in the page header for
the complete directory, **Get started** for setup or **GitHub** for the source
repository. The README links the site prominently and offers both HTML and
Markdown editions of each guide. See the [Pages deployment guide](pages-deployment.md).

The [immutable report edition](http://snap:8787/reports/293fdc3828d80409edd88861719fa5d376df1afa4bbdf5fae6a569d8f12aaa17/)
is the historical 2026-10-14 edition retained on Snap and requires access to its report endpoint. The [Codex Plus project catalog](http://snap:8787/reports/#project=codex-plus)
contains related reports. Publication, HTTP-byte checks from both hosts and
browser interaction/layout checks passed; see the
[documentation pass results](documentation-pass-results.md).

The [self-contained authoring file](presentation/index.html) also opens locally.
Its source now has five illustrative scenes: a Luna investigation, an endpoint
watch, coordination between independent sessions, a later MCP inspection followed
by a report, and returning to unfinished work. All five workflows are available
in **preview.10 and later**. The catch-up scene uses preview.10's recap/history improvements;
see [feature availability](getting-started.md#released-and-source-features).
A separate environment selector illustrates personal and
work contexts with example Codex homes. It only updates the page; it does not
create a home, change config or contact a daemon.

The scene controls reveal a request, setup or recap, useful update and stop/handoff. They
only change the page; they do not run commands, create watches, send messages or
control a session. Dialogue is authored illustration, not a captured native run.
Technical acceptance records remain in the repository guides rather than the
landing page.

The catch-up example distinguishes an acknowledged reminder from a completed
follow-up, identifies an accepted message by purpose, and closes attention on
a failed callback through explicit cancellation. It explains that the recap is
cached and conversation-scoped. Its dialogue does not claim that a native run
or fresh source check occurred.

The page leads with use cases, everyday benefits, setup links and an interactive
first-watch checklist. A dedicated Luna section compares the four worker
workflows and links to the [worker guide](workers.md) for examples and setup.
It includes a model-call illustration, lifecycle FAQ and
a downloadable quickstart checklist. Host-specific deployment status, comparison
research and validation records stay in the technical guides. Prompt copy
controls have a plain-HTTP fallback for SSH/mesh-hosted reports. It uses inline assets and JavaScript with no third-party dependencies.

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
[daily use](daily-use.md), [architecture and comparison](architecture.md),
[setup](getting-started.md), [workers](workers.md) and the
[soak checklist](soak-checklist.md). This presentation does not change installed
runtime bytes, managed release pins or worker invocation behavior.
