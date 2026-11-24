# Overview and interactive walkthrough

The [site overview](https://dev.byebyebryan.com/codex-plus/) shows what you can
ask for in a Codex conversation and what each request returns. Go directly to
[watches and timed checks](daily-use.md), [HTML reports](html-report-usage.md),
[communication between sessions](session-communication.md), or
[named and adaptive worker assignments](workers.md). The opening includes
the install request. The task chooser shows one request and its guide at a time.
Beneath it, a CSV importer example connects a worker review, a handoff between
sessions, a CI watch and an HTML report.
Setup and reference material are in the
[guide directory](https://dev.byebyebryan.com/codex-plus/#guide-directory).

## Walkthrough content

The [interactive walkthrough](https://dev.byebyebryan.com/codex-plus/walkthrough/)
opens with six invented conversations. The adaptive example shows which files
each writer owns, when the primary can integrate the exporters and how it can
credit the work. The primary checks both formats through the CLI. One worker’s
executed model is unconfirmed. The
[release qualification](reliability-packaging-results.md#preview30-worker-workflow-fixes)
contains the native execution records and their limits.

The other examples cover a Luna investigation, a watched peer session, quiet
endpoint polling, a one-shot MCP inspection followed by a report, and catching
up on unfinished work. Each interactive step reads the corresponding
JavaScript-free transcript. Readers can expand the transcripts for the complete
conversations.

The worker request builder illustrates a bounded task or goal loop for the
selected primary. Changing the primary resets the additional worker to its
eligible default. The selected permission appears in the generated request.
The [worker guide](workers.md) explains the seven workflows and model
eligibility.

The other controls compare observation costs, show how personal and work homes
select different state, and provide a downloadable first-watch checklist.
Copying an example puts the request on the clipboard or exposes selectable
text. The demonstrations run locally in the browser.

## Authoring and publication

Edit the [overview template](presentation/overview.html) for the first-visit
page. Edit the [self-contained walkthrough](presentation/index.html) for the
examples and interactive controls. The walkthrough opens directly from disk
and supplies the site’s shared palettes, theme switch and icon. New readers
see the dark theme. The header lets them switch themes on any page.

The [Pages builder](../scripts/build-pages) assembles both routes, rewrites
public guide links and adds page metadata. The overview uses the install request
from the management guide. The walkthrough uses the same install and upgrade
requests. Older overview URLs
with walkthrough fragments show a link to the corresponding example or
control. The [Pages deployment guide](pages-deployment.md) covers the build and
publication checks.

Before publication, check the overview diagrams at narrow and wide widths,
follow the old fragment links, and try each walkthrough scene, routing change,
copy fallback, download and JavaScript-free transcript. Use the
[feature table](getting-started.md#released-and-source-features) and current
release receipt when updating availability or execution claims.

For a separately requested immutable report edition, publish the
self-contained walkthrough to the configured report endpoint.

```sh
codex-plus-report --json publish --source /absolute/codex-plus/docs/presentation/index.html --title "Codex Plus: daily use and workflow guide" --project codex-plus --check-delivery
```

The [historical report edition](http://snap:8787/reports/293fdc3828d80409edd88861719fa5d376df1afa4bbdf5fae6a569d8f12aaa17/)
retains the 2026-10-14 walkthrough on Snap. It requires access to the report
endpoint. The [historical documentation checks](documentation-pass-results.md)
record its publication, HTTP verification and browser checks. New content
receives its own immutable URL when published.
