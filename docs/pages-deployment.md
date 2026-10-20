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

## Site contents

- Interactive walkthrough at the root, from `docs/presentation/index.html`.
- [Setup](getting-started.md), which separates worker, monitoring and report installation.
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
github.com` to render the eight public guides. GitHub Actions supplies its temporary
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

The current site renders eight guides and four illustrative conversations.
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
