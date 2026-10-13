# Operational source access and refinement pass

Execution selected from planning commit 8900175 on 2026-10-13. Finish:
reviewed/verified updated preview and pushed focused chezmoi integration;
live installation and enablement remain deferred. Existing worker agents/skills,
real active conversations and the original owning daemon are preserved.

## Qualification and implementation checkpoint

Native Codex 0.162.1 and the requesting conversation's positive loaded membership
were checked. Fresh owned fixtures use the new combined 24-delivery/48-turn
allowance. All earlier batches remain closed. Raw captures, fixture credentials,
session identities and private journals stay outside committed source.

| Finding/check | Result and selected route |
| --- | --- |
| Read-only filesystem with network disabled/enabled | Native authenticated HTTP read failed when disabled and succeeded when enabled. Networking is independent of filesystem policy. |
| Effective caller execution permissions | Resuming a positively loaded owned thread without overrides returned and preserved its native policy. Global command defaults are not assumed to be the caller's policy. No peer/cold target is resumed to discover source access. |
| Direct MCP calls | Disabled tools were refused, but prompt-only read and mutation tools executed directly despite the actor's never-approval policy. One controlled fixture mutation exposed this bypass; no real source/tool was changed. This path is not selected for background observation. |
| Native model MCP call | Full-access and read-only owned actors used their configured permitted inspection tool through normal native model execution. |
| Candidate command access | A read-only authenticated source completed with networking enabled. A session-inherited source retained authorized private cache writes; read-only narrowing denied that write. A network-restricted caller's network-required registration was refused with no durable intent. |

The implementation records command permissions from the exact loaded caller,
validates the private execution request, and supplies that policy/profile to native
execution. Session inheritance is the default; filesystem read-only and network
off are narrowing choices, while network required checks an existing grant.
Permission changes stop the owned source; changed grants require explicit new
registration/renewal. Legacy jobs without a new grant retain their old offline
execution policy rather than widening during an upgrade.

Named profiles keep their native working-directory anchor and exact profile
identity. Unsupported legacy narrowing or execution policy representations are
unavailable with an explicit result. Native profile coverage is separate from
the controlled legacy full/read-only qualification above.

Configured MCP watches select scheduled native model inspections. The coordinator
only inspects tool availability; it never invokes the direct MCP RPC. Each check
uses a model turn under normal configured tool permissions. Cached watch_inspect
supplies exact registered arguments; routine event frames contain no argument JSON.
No subsequent check is queued while handling remains pending, and explicit stop
preserves an already consumed turn while ending future inspection. Interrupted
inspection permits a new later check, with a new event identity.

Ending notices are enabled by default in the model interface. Peer/MCP observation
limits produce a notice separately from task outcome, so continuation can be an
explicit model choice under the existing request.

All 201 offline tests and the deliberately updated source inventory pass at this
checkpoint. Regression coverage includes caller/grant mismatch, network denial,
cache permissions, settings revocation/late output, disabled MCP sources,
inspection backlog/cancellation/recovery, frozen arguments and native-event
inspection binding. The source-access qualification has used six completed model
turns and zero automatic deliveries; its actors are closed and original ownership
is preserved. The fixture HTTP service remains owned for the next stage.

## Remaining acceptance and distribution gates

Installed scheduled MCP inspection, an actually handled successor after the
model selected a slower cadence, and natural stop have now passed. The endpoint
prototype exposed a misleading interval option: the model supplied interval
with a one-shot fetch, but command sources ignored it. Command intervals now
have an explicit periodic execution mode; continuing scripts remain an option.
Each completed read uses a fresh native process identity and the same verified
permissions, retaining projection/baseline state without a model turn per poll.

Cross-version qualification also exposed status lookup tied to the importing
release's wrapper path. The new CLI now recognizes an identity-verified owned
coordinator from a verified compatible immutable release. New source capability
registration is held while an older coordinator owns that state. Actual fresh
rollback acceptance remains pending.

The closed endpoint setup included an unavailable historical tmux session before
any model turn, followed by a fresh one-shot-source recipe that failed the
continuing-observer gate. These are harness/interaction findings, not successful
endpoint acceptance; their turns/deliveries remain counted. All 205 tests pass.

The candidate is now version 0.1.0-preview.2 with 19 runtime files plus its
manifest. Its installer explicitly recognizes the previous preview's declared
18-file inventory for selection rollback. All 202 tests pass; actual downloaded
cross-version installation and active-runtime qualification remain subsequent
gates. Selection does not migrate journals or make newer source modes understood
by older runtime code.

Installed model-selected endpoint monitoring, scheduled MCP inspections,
executed continuation, timed MCP reassessment, busy/earlier-input requalification,
TUI capture and complete fixture cleanup remain to be completed. Offline tests
and interface availability are not those acceptance results.

A new immutable preview must be built and qualified outside the source checkout,
then published and fetched/verified. Recreate and reconcile the surviving local
chezmoi integration commit with current published history and concurrent edits,
update pins/checksums/validators together, validate supported-host renders and
scoped dry-run, and push only the owned managed change.

The current published runtime remains v0.1.0-preview.1. No live apply, global
configuration mutation, daemon restart or operational workload action occurred.
