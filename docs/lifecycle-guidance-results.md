# Agent-first lifecycle guidance results

Completed 2026-11-01 as a local documentation/site candidate under the
[selected plan](codex-plus-plan.md#planned-pass-agent-first-lifecycle-guidance).
Guide and presentation candidate `e1b2d17` follows planning commit `995a7c6`.
The separately authorized publication is recorded below; product releases and
production installation changes remain outside this pass. Plugin migration stays
deferred.

## Publication: 2026-11-01

Reviewed source `52ab312` is pushed to personal github.com main. The
[Pages workflow](https://github.com/byebyebryan/codex-plus/actions/runs/41338091807)
and [source validation](https://github.com/byebyebryan/codex-plus/actions/runs/41338091834)
passed. Both Python 3.11/3.14 jobs ran 376 tests and verified the release build.
The 14-file deployed artifact matches the reviewed local build, including the
exact Markdown export. All 13 served HTML/Markdown/SVG/sitemap files return HTTP
200 with artifact-identical bytes; the hidden `.nojekyll` marker is checked in
the artifact. All 45 public browser checks pass with zero script errors.

The existing Pages settings/workflow were used without permission or host changes.
No runtime release, managed deployment, fleet mutation or daemon restart was
performed. Earlier native/fixture acceptance limits are unchanged; the idle
ephemeral fixture was not touched. The publication-only CI observer is stopped.
All 596 protected paths match the before record. Both OSS/work native owner
identities are unchanged. At the post-publication check, 12 of 13 baseline
native/report process identities remain; one other Codex process exited during
the window. No process-control action targeted it, and its cause is unclassified.
See the [deployment receipt](pages-deployment.md#agent-first-lifecycle-publication-2026-11-01).

## Review and refinement: 2026-11-01

Review of candidate `a6b7ece` found three concrete gaps. The download example
left the GitHub host implicit; the configuration procedure named paths but did
not explicitly retain custom allowlists and duration/event bounds; and the
rendered-table matcher silently omitted copy controls when cells had attributes.
The guide now pins `github.com`, retains all generator options and disabled/tool
policy choices, and routes read-only, reporting-only and workers-only diagnosis
without adding components. The builder preserves cell markup/attributes and
rejects missing, changed or duplicate rendered requests. Each copy button has
an action-specific accessible name.

Three new behavioral regression tests fail against the prior builder and pass
with the correction. All 61 targeted tests pass: 35 Pages, five inventory checks
and 21 component-package tests. A fresh site build verifies nine HTML guides,
the byte-identical Markdown export, 299 local links/assets/anchors and 15 current
release claims. Forty-five browser checks pass with zero script errors, including
all nine accessible action controls at desktop/mobile widths, keyboard copying,
clipboard-denial fallback and no-JavaScript access. Screenshots were inspected.

The released preview.13 generators pass five checks using private paths and
disabled server entries: retained custom monitoring arguments, reporting config,
peer-send approval choice, disabled components and cleared inherited environment
overrides. An explicit-host `release.json` download succeeds with an inherited
enterprise host and matches preview.13's recorded full revision. These are
read-only generator/metadata checks, not a new installation or native activation.

The clean 132-file candidate passes inventory and separate worker validation;
the checkout's canonical check still reports only the two preserved bytecode
files. No new native actors, watches, peer messages, runtime changes, production
installations, daemon restarts, push or publication are part of this refinement.
The earlier ephemeral fixture is outside this pass and was not touched. The
owned preview server is stopped. All 596 protected paths and 13 baseline native/
report process identities match the fresh before record. The original command
and actor receipts below keep their dated scope.

## Result

[One authored agent guide](manage-agent.md) covers install, upgrade, inspection,
configuration, rollback, cleanup and uninstall. The Pages builder renders it at
`/manage/` and exports its exact bytes at `/manage.md`. All seven short requests
come from that guide; the landing page presents install/upgrade copy controls.
README and setup lead to the guide, with `/start/` retained as the human overview.
Existing worker and component references point to the lifecycle procedure.

The guide resolves published previews explicitly, verifies release-compatible
artifacts before selection, preserves configuration ownership and distinguishes
selected code from loaded code. It replaces moving-main worker installation with
verified archives and explicit file provenance. Generated MCP JSON must be
translated and merged as TOML. There are no invented prune/uninstall commands:
uncertain dependencies and locally changed files remain preserved.

No runtime code, version, worker identity, plugin, service, installer or installed
management skill changed. The existing Pages workflow already covers these files.

## Released-artifact and command qualification

Fresh downloads of all five published assets for each release matched GitHub's
recorded SHA-256 digests and the corresponding tagged source. Both matching
release verifiers passed all three component inventories and unified identity:

| Release | Full source revision |
| --- | --- |
| `v0.1.0-preview.12` | `f6ec874fa12f2cb080c2f931adcbba1117231c6b` |
| `v0.1.0-preview.13` | `5e6c9dde392e8fa3e33b6901c0afe68116c77d94` |

Private prefixes and synthetic config/state roots exercised the authored command
paths. Eighteen checks passed: full and reporting-only setup; repeat installs;
upgrade and rollback; installed manifest verification; JSON-to-TOML configuration
equivalence without duplicate tables; preservation of comments, unrelated settings,
modified worker files and unknown extras; retained captured old code; scoped
cleanup/uninstall; retained report HTML, source HTML and a journal sentinel; and
closure of the owned manual MCP process. Doctor verifies the retained worker
release tree; copied native worker files received separate provenance checks.

A failed-upgrade fixture supplied a wrong expected checksum. It refused the new
artifact, retained the previous selection and created no new release directory.
A real chezmoi render/dry-run using entirely synthetic source/destination paths
produced valid TOML, preserved unrelated config and an explicit disabled server,
and left destination bytes unchanged. This does not qualify the fleet's templates
or a live apply.

## Fresh-agent and browser acceptance

One fresh owned native actor read the loopback Markdown URL from the short
inspection request, verified the reporting-only fixture and completed successfully.
It identified preview.13, absent monitoring/workers, empty synthetic MCP config,
unknown manager ownership and unknown loaded code. Installed verification and
`--no-native` diagnostics passed; before/after fixture files, permissions and
selection links matched. The actor was archived and unloaded on the existing
Snap OSS 0.166.0 owner. Per-thread test instructions constrained its reads to the
fixture; production MCPs, delegated agents and plugin/app use were disabled.

The first trial's collector omitted thread binding and missed the completion
notification. Its idle status was observed, but that trial has no acceptance
receipt. The corrected durable trial above supplies the qualified result. This
is evidence for agent-led inspection only; it does not prove an agent-led install,
upgrade, uninstall or native MCP activation. The served inspection guide preceded
the final clarification about preserving explicit monitoring paths; the final
authored guide was checked separately by the builder and browser.

The initial ephemeral trial remains loaded and idle. The native owner rejects
archive, resume and delete because it has no persisted rollout; unsubscribe from
a new connection reports `notSubscribed` and leaves it loaded. A tools-free closing request also
provided no completion callback, with idle status confirmed afterward. No daemon
restart was attempted. This test-harness cleanup limit is retained explicitly;
it does not qualify as complete actor cleanup. The successful durable trial is
archived/unloaded, and all three owned preview HTTP servers and the manual MCP
child are stopped.

The final site build verifies nine HTML guides, one identical Markdown export,
299 local links/assets/anchors, all 15 current-release claims and public metadata.
Twenty-seven browser checks pass with zero script errors: desktop/mobile layout,
all guide routes, copy controls, keyboard copying, denied-clipboard fallback,
no-JavaScript access and served Markdown byte equality. Screenshots were inspected
at 1280- and 390-pixel widths. No public site was changed.

## Source checks and evidence limits

All 58 targeted tests pass: 32 Pages tests, five inventory-check tests
and 21 monitoring/reporting package tests. Focused new Pages cases cover raw
export presence/equality, shared action requests and same-site link rewriting.
The runtime suite was not rerun for this documentation/builder change.

Canonical `scripts/check` encounters only the two pre-existing untracked bytecode
files, which remain preserved. The clean tracked-file candidate passes the
132-file inventory, agent TOML and separate worker-skill validation. Whitespace
checks pass. All 596 protected paths and all 13 baseline native/report process
identities match the before record. Production config, credentials, installed
releases and selected worker files are unchanged.

Private transcripts, process identities, configuration captures and report data
remain outside committed source. Filesystem/protocol checks do not establish
native caller identity, model availability, functional watches or another client's
compatibility. Journal-sentinel retention is not journal migration acceptance.
Real manager apply, public delivery and ordinary user lifecycle acceptance remain
separate follow-up work.
