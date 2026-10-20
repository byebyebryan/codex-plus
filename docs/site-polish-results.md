# Documentation and site polish

Completed 2026-10-20. This pass refines documentation and publication around the
existing package. It uses the ordinary primary workflow and does not activate a
worker skill, observation, message or native model trial.

## Audit and selected changes

The public site covered workers only after an omission fix, while its main
setup path still led straight to monitoring installation. Long reference guides
had no contents navigation. Luna had no interactive scene, and publication
metadata was inconsistent between the landing page and generated guides.

The selected changes are a component-based setup guide, balanced capability
coverage, a Luna scene, navigable guide sections, consistent share metadata and
stronger publication checks. Keep evidence history available on GitHub and
preserve existing public routes.

## Candidate acceptance

The isolated candidate passes the 115-file source inventory and unchanged
agent/skill metadata contracts. All 18 Pages regression tests and five metadata
tests pass. The generated landing page plus eight guides pass 220 local
link/asset/fragment checks and the public inventory, URL metadata and sitemap
contract. The repository link audit also corrected a historical handoff anchor
that moved to `implementation-history.md`.

An owned headless Chrome profile exercised all 16 scene states, back/reset,
native Enter activation, clipboard fallback and manual copy, both environment
selections, the cost slider, FAQ, checklist and checklist download. It followed
each of the eight guide routes, used skip links and contents navigation, and
checked layouts at 1440, 768, 390 and 320 pixels without global overflow. The
architecture SVG loaded; reduced-motion and no-JavaScript content checks passed;
browser errors were zero. Desktop/mobile screenshots were inspected.

The narrow-width contents check initially clicked the gap between wrapped link
lines. Giving the link its whole row made that same pointer interaction pass.
The stale optional-349 wording is corrected, and worker installation paths were
checked against the official custom-agent and local-skill documentation.

## Publication

The content/navigation implementation is commit `376aa1a`; publication and the
final setup-card layout are `f543008`. Both were pushed to the personal
`byebyebryan/codex-plus` repository. The
[final implementation deployment](https://github.com/byebyebryan/codex-plus/actions/runs/39513590938)
completed successfully with actor `byebyebryan` and zero build/deploy annotations.
The first successful run exposed deprecated Node actions and the moving Ubuntu
image. The refined workflow pins Ubuntu 24.04 and official Node-24-compatible
Pages actions to full commit hashes, with the existing permission separation.

The [public site](https://dev.byebyebryan.com/codex-plus/) serves the landing
page, all eight guide routes, architecture SVG and sitemap with HTTP 200 and
exact bytes matching the accepted candidate. The actual public HTTPS browser
pass repeated the 16 scene states, eight guides, controls, keyboard/contents
navigation, reduced-motion/no-JavaScript checks and four viewport widths with
zero errors. Owned browser profiles and the temporary preview server were closed.

Final protected-file comparison retains all 41 runtime/agent/skill hashes and
both pre-existing bytecode hashes. Read-only selected-manifest checks agree with
the documented host split: Snap runtime preview.3 / report preview.8; Starship
runtime preview.2 / report preview.7. No managed apply, release repin, native-owner
restart, report-store mutation or real watch/message was performed.

## Remaining acceptance

Documentation/publication acceptance is complete. Real-source soak, provider
recovery, long unattended operation and personal UX remain separate. Browser
interaction checks are evidence of the tested paths, not a formal accessibility
certification. Immutable Snap report editions retain their historical contents;
the public Pages site is the current guide.

Runtime, agent and skill bytes; selected release pins; native owners; credentials;
report stores and historical snapshots remain outside the changes. The two
pre-existing untracked bytecode files remain in the checkout; inventory validation
uses an isolated candidate and CI's clean checkout.
