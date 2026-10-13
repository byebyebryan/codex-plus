# Natural requests and readable peer communication

Execution requested 2026-10-12 as an ordinary goal loop from planning checkpoint
`c61059a`, with incremental validated commits. The objective is a reviewed local
candidate and a prepared primary-driven demonstration; personal UX acceptance and
installation remain separate. Existing real sessions are read-only sources.

## Qualification decision

The CLI and existing daemon still report 0.162.1. Fresh owned synthetic probes used
the same owner, without global configuration/trust edits or daemon replacement.
Generated schemas, raw history, MCP messages and native captures remain private.

| Gate | Evidence | Decision and limit |
| --- | --- | --- |
| Session-local model tools | A per-thread MCP configuration launched a local stdio probe. The model invoked it successfully; a second invocation succeeded with the ordinary native TUI attached through remote resume. | Use a small stdio MCP interface around the existing candidate. This proves the selected loaded-session path, not managed installation or cold recovery. |
| Caller context | The native MCP request supplied matching thread/session identities and turn identity in its metadata. | Bind operations to that verified native context. Model arguments and peer text cannot supply caller authority. Revalidate the owning listener and loaded independent caller. |
| Native tool-output presentation | Idle `turn/start.toolOutput` persisted a `functionCallOutput` item and completed a recipient turn. | Presentation is supported, but that alone does not qualify its delivery semantics. |
| Busy tool output | With foreground work active and earlier human input queued, `turn/start.toolOutput` returned the foreground turn ID. Full native history contains the later tool output inside that foreground turn. | Reject this route for the coordinator's ordering contract. Retain exact queue admission/start/withdrawal with readable attributed event text. |

This is a compatibility decision, not a claim that native tool output is generally
broken. The coordinator promises follow-ups behind foreground/earlier human input;
joining the active turn does not preserve that boundary. No ordinary-input fallback
can be described as a hidden native notification. Structured journals and explicit
technical inspection remain available independently of human-readable delivery.

## Probe corrections and counted usage

The first harness checked summary history for MCP tool items. Summary history omits
those items, so it incorrectly reported unavailable access despite the recorded MCP
call and the model's result. The actor was closed; its turn stays counted. A fresh
targeted probe used full history and established native TUI availability.

The later queue-start check raced native consumption and returned submission-not-found.
No input was replayed. Fresh passive reads of the archived owned actors identified
the consumed human input and its interrupted cleanup outcome. The race does not
undo the direct busy-output evidence or provide a successful human-input acceptance
case. It is a harness/cleanup limit, rather than a provider failure.

Qualification usage is **3 experimental deliveries / 6 started turns**: five
completed and one human-queue fixture turn interrupted during archive cleanup.
There were zero provider failures. Both actors are archived/notLoaded, owned probe
servers and the qualification viewer are stopped, and no owned pending input
remains. The original listener identity and requesting conversation's positive
loaded membership were freshly verified preserved. Remaining combined allowance:
**9 deliveries / 18 turns**. The old walkthrough fixtures are not reopened.

## Implementation and acceptance

The first source slice renders compact readable queue input, retaining exact native
client identities and raw evidence in the journal. Peer snapshots become selected
facts rather than JSON prompts. Message bodies appear once and carry distinct
information/request labels. Requests require a frozen sender; the engine validates
its same-owner independent provenance before admission and before queue start.
Legacy messages show unavailable origin rather than claiming a sender. Quoting,
control-character handling, deep/partial data and identity/cancellation boundaries
have behavioral regression coverage. This is offline source acceptance; the natural
request/interface integration still needs the subsequent native recipe.

In progress. The selected scope is ordinary watches, peer information and requests
within existing recipient tasks. A general new-task delegation policy remains a
separate scope choice. The next checks must use reusable capabilities and natural
requests without driver-supplied target identities or per-callback recipes.

The source-local model interface now supplies a stdio MCP server and reusable
capability guidance. It binds caller identity from native thread/session/turn
metadata, checks the active calling turn, and uses immutable private journal state.
Contextual discovery returns bounded recent agent/plan content with completeness,
child exclusion and unknown-classification disclosures. Persisted peer/watch/message
references avoid user-supplied exact titles and refuse ambiguity or retargeting.
Tool arguments cannot forge caller identity; a fixture allowlist protects real
sessions from writes. Current-event acknowledgement uses native client/turn
correlation, with distinct recipient receipt and accepted/declined outcomes.

All **161 offline tests** and the explicit **59-file inventory** pass at this source
checkpoint. New regressions cover contextual discovery, alias reuse/ambiguity,
native owner/caller changes, interrupted calling turns, configured operation bounds,
read-only peers, request attribution/decline, malformed or unadmitted acknowledgement,
consumed-turn preservation, cancelled-update action refusal, pending-renewal
cancellation and MCP metadata/protocol bounds. Full native integration remains the
next acceptance step; these unit checks do not establish personal UX acceptance.
