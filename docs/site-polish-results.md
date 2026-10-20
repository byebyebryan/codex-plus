# Documentation and site polish

Started 2026-10-20. This pass refines documentation and publication around the
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

Pending: commit/push, Pages deployment, deployed-byte/browser verification and
final protected-file comparison. This section will record those receipts when
they are available.

Runtime, agent and skill bytes; selected release pins; native owners; credentials;
report stores and historical snapshots remain outside the changes. The two
pre-existing untracked bytecode files remain in the checkout; inventory validation
uses an isolated candidate and CI's clean checkout.
