# Public guides on GitHub Pages

The selected public site is [dev.byebyebryan.com/codex-plus](https://dev.byebyebryan.com/codex-plus/).
The personal `byebyebryan` account on github.com owns this repository and site;
enterprise/work authentication is not used for repository settings or publication.
GitHub Pages inherits the personal account’s existing dev.byebyebryan.com domain;
this project enables HTTPS without changing DNS or the parent site.
Initial deployment passed on 2026-10-14 from be401d7. The
[Pages workflow](https://github.com/byebyebryan/codex-plus/actions/runs/38640319833)
completed successfully; the HTTPS landing page, all five guide routes and the
diagram returned HTTP 200 with bytes matching the local candidate. Browser checks
passed all 12 scene states and controls, five guide pages, desktop/mobile layouts
and diagram loading, with zero browser errors. The github.io project URL redirects
to the inherited domain. The publication contract follows.

## Agent-first lifecycle publication: 2026-11-01

Published source `52ab312` adds `/manage/` and `/manage.md` from the single authored
`docs/manage-agent.md`. README, landing and setup lead with short agent requests;
`/start/` remains the human overview. Nine HTML guides and one raw Markdown export
are in the explicit public inventory. The builder rejects a missing or changed
raw export and derives all seven action requests from that same guide. Install
and upgrade cards use the shared text on the landing page. Copy buttons have
manual-selection fallback, and the requests remain readable without JavaScript.
Self-site links become relative for local previews; authored absolute guide links
also work when an agent fetches raw Markdown from the site root.
The [acceptance record](lifecycle-guidance-results.md) separates released-artifact,
disposable command, fresh-agent inspection and final browser evidence.
The follow-up review also checks all seven rendered requests appear exactly once,
preserves attributed table cells and gives copy buttons distinct accessible names.

The existing Pages workflow already watches `docs/**`, the builder and tests;
no workflow permission or host setting change was required. The personal account
pushed the reviewed source to main. [Pages build/deploy](https://github.com/byebyebryan/codex-plus/actions/runs/41338091807)
and [source validation](https://github.com/byebyebryan/codex-plus/actions/runs/41338091834)
passed; both Python 3.11/3.14 jobs ran 376 tests and verified a complete release
build. This did not publish replacement runtime assets.

All 14 deployed artifact files match the reviewed local build. All 13 served
HTML/Markdown/SVG/sitemap files returned HTTP 200 with identical bytes, including
the authored raw guide. The artifact validates 299 local links/assets/anchors and
15 current-release claims. Forty-five public browser checks pass at desktop/mobile
widths with zero script errors, including action names, keyboard/clipboard fallback
and no-JavaScript access. Publication changes documentation only; no runtime
release, chezmoi apply or daemon restart was needed. Dated receipts below retain
their original guide counts and scope.

## Site contents

- Interactive walkthrough at the root, from `docs/presentation/index.html`.
- [Install and manage](manage-agent.md), the primary agent lifecycle guide, plus its exact plain Markdown export.
- [Setup](getting-started.md), the human overview of workers, monitoring and reporting.
- [Daily use](daily-use.md), [Luna and workers](workers.md), [architecture](architecture.md),
  [environments](environments.md), [soak checklist](soak-checklist.md), [reporting](html-report-usage.md) and
  [installation](runtime-distribution.md), rendered as HTML guides.
- The architecture SVG, tied by SHA-256 to the Markdown Mermaid diagram source.

Only these explicit public files enter the Pages artifact. Technical acceptance
and historical reports remain linked on GitHub. Internal Snap report/catalog
links on the landing page are labeled as requiring mesh access; the public guides
need only their GitHub Pages endpoint. Existing immutable report snapshots remain
available under their independent hosting owner.

## Build and deploy

`.github/workflows/pages.yml` builds for relevant pushes to main and manual
workflow dispatch. It uses official Pages actions pinned to full commit SHAs,
read-only source access in the build, and Pages/OIDC write permission only in the
deploy job. The github-pages environment and Pages concurrency group own deployment.
No personal credential is stored in the repository or site artifact.

`scripts/build-pages` uses GitHub’s Markdown API through `gh api --hostname
github.com` to render the nine public guides. GitHub Actions supplies its temporary
repository token; local builds use the selected personal github.com authentication.
Rendering requires network access. No JavaScript library/CDN is needed by the site.

Build outside the checkout:

```sh
rtk proxy python3 -B scripts/build-pages --output /absolute/empty/site-directory
```

The builder refuses a non-empty destination or an output inside the checkout.
It rewrites supported guide links to relative site routes, gives headings stable
anchors, preserves links to technical GitHub sources, and validates every local
page/asset/fragment before upload. Generated files remain outside committed source.
It also checks identified current-release claims in the README, setup,
architecture, installation and walkthrough against the README's independent
published-release and managed-deployment declarations, and checks that the worker guide names all four worker workflows and
the reporting skill. Historical release references remain valid. If current
claim wording changes, update its focused matcher in the builder alongside it.
These consistency checks do not prove publication or installed adoption.
Update the diagram SVG alongside Mermaid changes; a mismatched source hash fails
rather than publishing a stale diagram.

Generated guides include section contents, skip links, keyboard-accessible table
scrolling and related-guide navigation. All public pages receive canonical and
Open Graph URL/description metadata. `sitemap.xml` lists only the landing page
and selected guide routes. The build rejects a mismatched public file inventory,
missing or duplicate descriptions, incorrect canonical URLs, multiple main/H1
elements or a stale sitemap before upload. Existing public routes stay stable;
the component-based setup overview is at `/start/`.

Pages serves current guides; the report tool serves immutable snapshots. Neither
changes qualified monitoring/report runtime pins, installed worker identities,
live configuration or active native sessions. Existing Pages generations are
replaced through successful deployment; source history retains earlier versions.

## Reconciliation: 2026-10-16

That reconciliation rendered six guides, including environment selection. The landing
page distinguished installed host versions and illustrated Snap's separate home
contexts without contacting native services. The builder validates duplicate IDs,
relative destinations and fragments; regression tests run in the Pages build.
Attributed GitHub tables retain their attributes inside balanced scroll wrappers,
so mobile pages contain their wide tables rather than expanding the viewport.
See the [pass results](reconciliation-results.md) for source and browser checks.

## Worker guide: 2026-10-20

That pass added a seventh guide. The landing page named Luna and all four
worker workflows, with direct links to the worker guide. That guide explains
task versus goal scope, explicit invocation, primary review, adaptive routing,
installation and the distinction between child workers and independent peers.
The worker definitions, skill instructions and runtime artifacts are unchanged.

## Current polish: 2026-10-20

That published edition renders eight guides and four illustrative conversations.
Component setup starts at `/start/`; the existing `/installation/` runtime
reference remains available. Guide contents links, share metadata and the sitemap
are checked during every build. The workflow pins Ubuntu 24.04 and the official
configure-pages v6.0.0, upload-pages-artifact v5.0.0 and deploy-pages v5.0.1
actions to full commit hashes. Only the explicitly validated export is uploaded,
including `.nojekyll`.

The [deployment](https://github.com/byebyebryan/codex-plus/actions/runs/39513590938)
passed with zero annotations; the actual HTTPS pages, diagram and sitemap match
the local candidate. The [polish results](site-polish-results.md) record browser
coverage, protected files and the distinction from runtime qualification.

## Source follow-up: 2026-10-22

The source follow-up retained all eight guide routes and added a fifth,
four-step catch-up scene. The scene and setup guide distinguish released
preview.9 from unreleased recap/history and diagnosis changes. README, daily-use,
architecture and installation guidance use the same availability boundary.
The [presentation notes](presentation.md) explain the authored examples;
[polish results](site-polish-results.md) record candidate validation separately
from public delivery. A local build or browser check does not publish this edition
or distribute its runtime features.

## Preview.10 publication: 2026-10-22

Pages run `39893331291` published the five-scene edition and all eight guides.
All 11 public files matched the generated release candidate; an owned browser
verified 20 scene states across four viewport widths and the guide interactions.
The walkthrough now labels the recap workflow as available in preview.10.
The subsequent documentation receipt updates managed status to Snap, Starship
and Carbon; it does not change the immutable release source or running code.
See the [release and deployment receipt](refinement-results.md#preview10-publication-and-managed-rollout).

## Preview.15 worker presentation publication

The release-source Pages run `41548928349` published the three-role worker guide,
default-off escalation chooser, copyable natural request and revocation example.
Desktop/mobile browser checks cover all nine guides and 54 interactive states;
the public plain agent guide matches release-source bytes. Publication and
per-host installation remain separate; see the
[delivery receipt](reliability-packaging-results.md#preview15-worker-policy-and-guide-publication)
for current selected/loaded evidence. After Carbon returned online, the scoped
rollout completed in all four native contexts; the published guides now record
the common preview.15 selection. This documentation update leaves the immutable
release artifacts unchanged.
