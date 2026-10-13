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

## Installed workflow acceptance

Installed scheduled MCP inspection, a handled successor after model-selected slower
cadence, and natural stop passed. Authenticated endpoint polling passed quiet
revision suppression, a useful stall/input callback, actual foreground command
isolation, earlier human queue ordering, unsent TUI draft preservation and natural
stop. A timed native wakeup performed an actual configured inspection and recorded
handling. A prompt-only tool under native never-approval was refused before the
fixture was called. These are controlled local sources, not real endpoint/auth pilots.

The endpoint/continuation and ordering scenes used immutable candidates outside
this checkout. The final guidance refinement adds explicit background wakeup and
consistent snapshot-field instructions; the command, engine and delivery code are
unchanged from the candidate that passed foreground/queue/draft acceptance.
Fresh final-artifact endpoint use passed authenticated observation, quiet filtering,
handled useful updates and natural stop. In-flight cancellation stopped the owned
source before its endpoint call, with no active observation intent afterward.

## Findings corrected or retained

- One-shot command sources silently ignored generic interval. Periodic commands
  now use command_interval, preserving their filtering baseline without inference
  per read. Generic interval on command sources is rejected. Continuing scripts
  retain control over polling/backoff; unsuccessful short reads stop visibly.
- New runtime status lookup could not recognize an old release's wrapper. It now
  verifies exact owned process identity and that immutable release's manifest.
  Registration/renewal of new source capabilities holds while older code owns
  the state. Fresh selection/rollback preserved the old coordinator and its
  pending reminder, which was handled; journals were not migrated.
- A generated reader selected a diagnostic field it omitted on success. The runtime
  correctly reported malformed selected snapshots; a too-short harness gate closed
  before assessing recovery. Later fresh endpoint acceptance passed. Guidance now
  specifies consistently present projection fields.
- A natural later-inspection request initially used foreground sleep and one normal
  tool call. Guidance now explicitly registers a one-shot wakeup and returns. A fresh
  installed actor used the timer and actually inspected at its callback.
- A reminder-to-inspect correctly reminded the user rather than inspecting itself.
  Its handled callback counts as reminder/rollback evidence, not timed MCP inspection.
- A historical tmux session was absent before any model turn. A fresh owned tmux
  session provided later TUI acceptance. Failed/partial trial turns remain counted;
  no closed actor or event was replayed.

All 206 offline tests and the 69-file source inventory pass. Coverage includes
permission mismatch/denial, cache narrowing, revocation and late output,
periodic command baseline/cadence, disabled MCP sources, inspection backlog,
cancellation/recovery, frozen arguments, native-event binding and old-runtime
registration/renewal holds. Worker files are unchanged against their managed baseline.

## Package and managed distribution

The final candidate is 0.1.0-preview.2 at source
`2274f4b54817fae88c3762c39c1284b8b1eb2695`, with 19 runtime files plus its manifest.
Independent builds are byte-identical. Runtime SHA-256:
`d4b23b83339f2a59bd12eadc0408695d899b993020d0fa496dc394de9e49ecdf`.
The fetched 69-file source archive matches committed contents and executable bits,
with SHA-256 `9ea1a17ad1e5e8c35f799c33d3232f324dc246fc3bc352fedaa5acc6edb994fb`.
Archive permission normalization differs from runtime modes; contents and executable
intent are checked separately. The actual previous published preview was downloaded,
checksum-verified, installed and reselected. Older code does not understand newer
source registrations; selection is neither journal migration nor daemon restart.

The surviving local chezmoi integration was reconciled in an isolated worktree from
current published history. Source/runtime URLs, revisions, checksums, immutable
selection and validators move together. Concurrent canonical SSH, Claude and Codex
edits are preserved. The release is [published](https://github.com/byebyebryan/codex-plus/releases/tag/v0.1.0-preview.2).
Downloaded runtime/checksum bytes match the tested artifact, and its manifest,
exact inventory and executable modes validate. Component renders and the scoped
11-target-group dry-run and full dotfiles check passed. The managed change is
committed and pushed to dotfiles main as `1bac126`. Actual local Codex configuration
rendering changes only the codex_plus namespace; other settings are unchanged. No live apply, global configuration
mutation, daemon restart or operational workload action occurred.

Named permission profiles have offline coverage and retain exact native anchors;
native qualification covered legacy full/read-only policies. Unsupported profile
narrowing fails explicitly. Existing MCP authentication is used by native calls;
controlled tests do not qualify real OAuth, expired credentials, provider outages,
long operation or personal UX. MCP polling uses a model turn per check. HTTP reads
can be quiet native commands. These source mechanisms cover the studied Claude
workflow shapes; real-source equivalence remains a separately selected pilot.

## Closed native allowance and cleanup

The combined recipe closed at 31 started native turns (29 completed, two owned
cleanup interruptions), nine automatic events, 54 authenticated fixture HTTP
requests and ten controlled MCP fixture calls, including qualification probes.
There were zero provider-failed turns. All counts include failed/partial scenes;
none were replayed in a closed actor. These totals are below the 48-turn,
24-event, 300-HTTP-call and 100-MCP-call ceilings.

All 21 owned actors are archived and absent from loaded inventory. Owned input
queues were checked during settlement; archived queue reads are unavailable and
no actor was unarchived to obtain extra evidence. Owned observer processes, MCP
bridges, coordinators/viewers, the exact HTTP fixture process group and dedicated
tmux session are closed. Original kernel listener identity and positive loaded
requester membership remain unchanged. Private raw history, fixture credentials,
state and captures remain outside committed source.

The seven recorded concurrent canonical files retain their original hashes and
modes. The canonical dotfiles checkout remains on 271b35d with those unfinished
edits, while published main includes 1bac126. The clean isolated rollout checkout
contains that managed change; no branch movement, auto-stash, apply or enablement
was performed in the active canonical checkout. The next selected live rollout
must reconcile that checkout and review current source/live drift before scoped
apply. This is separate from the completed publication/distribution finish.
