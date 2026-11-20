# Private routing diagnostics

Preview.22 adds an opt-in ledger and a bounded, read-only native-record reader.
The ledger observes policy A, with Sol XHigh and selective Luna Max. The adaptive
goal skill holds its default Astra route for an enrolled A episode. A separately
authorized non-Luna worker can be recorded as `--route other`, which flags a
policy deviation and keeps its usage visible. The ledger enables no model
comparison, additional routing permission, or background process. An A-only
observation cannot establish savings over another policy.

Preview.23 also normalizes nullable integer Unix seconds in native timeline
fields to UTC. It preserves the outer record timestamp's finer precision for
episode boundaries, leaves null values unknown and rejects invalid timing data
without copying arbitrary strings into output.

## Current run usage

Preview.27 adds `codex-plus-diagnostics usage` for a read-only
snapshot of the invoking primary's active native root. Pass `--worker PATH`
once per participating worker using the exact task path returned by native
collaboration. The reader counts observed responses within that root and its
named, directly linked workers. The command requires no study and prints only
aggregate usage, model/effort metadata, and coverage cues.

The primary's running turn has a partial count, and an unavailable or
unattributed count stays unknown. A goal resumed under a new native root may
span more work than this snapshot. Cached input is included in input tokens.
The counts are native usage observations, with billing outside their scope.

## Model-version tracking

New studies record exact model/effort on each episode and native turn. Supported
Sol version updates do not stop enrollment or require another study. Collection
exposes `model_observations` and `accounting.usage_by_context`, so analysis can
separate versions without conflating their capability, quality or cost. A known
version change within a goal is an observation, not a missing-coverage error.
Unknown model context and actual family/effort deviations remain explicit gaps.
The study still observes Sol XHigh with selective Luna Max; this enables no
other routing policy or automatic model change.

For an existing legacy or frozen study, explicitly request its policy update:

```sh
rtk proxy codex-plus-diagnostics allow-model-upgrades
```

Use the same native home and optional `--state-root` as that study. The operation
creates a private byte-for-byte backup under the ledger lock, records the prior
version policy, and preserves the study identity, existing episodes/outcomes,
deadlines and goal limit. Repeating it changes nothing. It never reopens a closed
study, extends an expired window, starts a new study or backfills ongoing work.
Only new goals enroll prospectively. Existing episodes keep their recorded
versions; older episode starting versions come from their own native contexts.

Old studies remain unchanged until this explicit operation. Older helpers may
refuse the updated policy; retain the new helper and backup when rolling back a
runtime, and never restore an old ledger over subsequently recorded goals.

## Start and enroll

Ask your agent: “Open a private seven-day/eight-goal A study, then use
`$adaptive-goal-loop` for naturally selected goals. Use Sol and Luna only for
enrolled goals, and keep the observations private.”

The operator runs `codex-plus-diagnostics start` once in the intended native
environment. `CODEX_HOME` selects that environment; its diagnostics directory
defaults to the matching Codex Plus state root. Snap's default and Work homes
remain separate. An explicit `--state-root` selects an isolated private ledger,
not another native environment. No daemon or MCP reload is needed for the helper. Enrollment verifies its
invoking loaded independent Sol XHigh primary through existing read-only native
controls; collection needs no live owner.
Already loaded skill instructions may require an ordinary fresh invocation;
do not interrupt existing sessions to replace them.

Before planning a selected goal's first routing decision, the adaptive goal
skill runs:

```sh
rtk proxy codex-plus-diagnostics enroll --if-open --routing-not-started
```

No open study means a read-only no-op. An enrolled goal returns a private episode
identity. A continuing open episode in the same parent reuses that identity;
related goals retain the parent as their lineage cluster. Enrollment admits at
most eight goals and ends after seven calendar days, whichever comes first.
The helper never extends or replaces an existing study, even after closure.
Prospective enrollment is an operator assertion: native data cannot prove that
no routing preceded it. The entire starting primary turn is included so that
its pre-enrollment preparation is not silently dropped.

## Record assignments and reviewed outcomes

Keep compact contract, acceptance-check, route-rationale and first-review
references in the existing private conversation or artifact. Do not copy raw
prompts, tool output or transcripts into this repository. Use the episode ID
from enrollment and actual native IDs when recording work:

When native collaboration returns a task path, the shorter form is
`link EPISODE --route luna --worker /root/example_worker --first-result accepted`.
It resolves only an exact direct-child path and one unlinked turn starting
inside this episode. Missing or ambiguous matches are refused; no title/role
guessing or target resume occurs. For multiple candidate turns, use explicit
identities and record each relevant turn separately:

```sh
rtk proxy codex-plus-diagnostics link EPISODE --route luna \
  --thread CHILD --turn CHILD_TURN --first-result accepted \
  --contract-ref 'private-artifact:contract-and-check'
```

These are placeholders, not discoverable thread aliases. A reused worker needs
each relevant native turn linked explicitly; unrelated past worker turns are
excluded. Record significant retained work with `--route primary` and the
parent's actual thread/turn. Native ownership is checked against the selected
environment's index; a foreign child is rejected. Failed attempts remain in the
ledger: use `--status controls_missing` or `spawn_rejected` without a worker
identity; an actual started error uses `execution_failed` with native identities.
Do not infer unavailable controls from an empty Code Mode registry.

`--first-result` records accepted, correction, rejected or unknown after the
first delivered result is reviewed. A correction turn is a new linked turn,
not an overwrite of the first outcome. Keep first-handoff evidence before
repair. References may point to correction/reuse links or material defects.

After actual acceptance review, record one final outcome:

```sh
rtk proxy codex-plus-diagnostics outcome EPISODE minor_correction \
  --children-reviewed --user-intervention none \
  --evidence-ref 'private-artifact:final-check'
```

Outcomes distinguish first-review acceptance, minor correction, substantial
repair, primary takeover, unresolved and cancelled. Substantial repair means
redoing a central part of the deliverable; ordinary integration is not takeover.
`--children-reviewed` attests that every relevant direct-child turn, including
corrections, is linked. Leave it unset when identity or coverage is uncertain.
Cancellation and unresolved outcomes remain visible. Native completion alone
never fills an acceptance field. Outcome records are immutable; retain later
regressions as private evidence for the study's fixed follow-up review.

## Collect and close

After the closing native turn settles, run:

```sh
rtk proxy codex-plus-diagnostics collect EPISODE
rtk proxy codex-plus-diagnostics status
rtk proxy codex-plus-diagnostics close
```

`collect` prints private JSON to the caller and writes no native or study state.
If saving it, use a private destination outside source with mode `0600`. The
ledger directory is `0700` and its files are `0600`; symlinked or public ledger
paths are rejected. Collection reads only the selected environment's native
SQLite index in query-only mode and bounded JSONL records. It copies no raw
message text, tool content or credentials. No sessions are resumed or prompted.

Primary usage covers the explicit starting-through-closing native turn window,
including planning, review and repair. Workers cover only linked turns. Shared
primary responses count once at goal level; assignment-level allocation remains
unknown. A selected turn's model/effort comes from its matching native context,
not a role label or latest thread setting. Exact per-response identities are
deduplicated, conflicts are excluded, cumulative snapshots are not added, and
missing/invalid fields remain unknown. Reasoning output and cached input are
subsets, not extra tokens to add to totals. The output reports six raw usage
categories without converting them to money or claiming a bill.

Read coverage and source gaps before sums. Unsupported schemas, missing context,
partial writes, read limits, absent records and unreviewed child coverage remain
explicit. A running turn may not yet have response usage or a terminal event;
collect again after it settles. The helper deliberately makes no automatic
complete-workflow, savings or causal-comparison claim. Check the first few
episodes manually against existing native evidence, including naturally occurring
delegation, before interpreting aggregate usage.

At the declared cutoff, close enrollment and review all enrolled goals, including
unresolved ones. Closing never stops user work. The study fixes observation/follow-up at seven days from opening, even if
eight admissions close enrollment sooner. Outcomes recorded after that cutoff
are labeled late; later regressions and unobserved outcomes stay explicit. Report insufficient coverage rather than extending the window
until results look favorable. No Terra trial or A/B launch follows automatically.
See the [staged comparison plan](codex-plus-plan.md#proposed-pass-targeted-routing-soak-and-policy-comparison).
