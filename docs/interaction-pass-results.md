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

## Implemented local candidate

The first source slice renders compact readable queue input, retaining exact native
client identities and raw evidence in the journal. Peer snapshots become selected
facts rather than JSON prompts. Message bodies appear once and carry distinct
information/request labels. Requests require a frozen sender; the engine validates
its same-owner independent provenance before admission and before queue start.
Legacy messages show unavailable origin rather than claiming a sender. Quoting,
control-character handling, deep/partial data and identity/cancellation boundaries
have behavioral regression coverage. This is offline source acceptance; the natural
request/interface integration was subsequently checked on fresh native actors.

The selected scope is ordinary watches, peer information and requests
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

All **162 offline tests** and the explicit **59-file inventory** pass at the final
checkpoint. New regressions cover contextual discovery, alias reuse/ambiguity,
native owner/caller changes, interrupted calling turns, configured operation bounds,
read-only peers, request attribution/decline, malformed or unadmitted acknowledgement,
consumed-turn preservation, cancelled-update action refusal, pending-renewal
cancellation and MCP metadata/protocol bounds. These unit checks do not establish
personal UX acceptance.

The first natural-request batch created two fresh read-only caller fixtures. Three
turns completed, but native Codex rejected `peer_list` because an unannotated MCP
tool required approval under `never` policy. No bridge state, watch or delivery was
created. Both actors were archived; the failure remains counted. The source now
provides accurate read-only annotations and the documented fixture configuration
explicitly approves the six watch/message/handling controls. This policy attachment
was qualified on fresh read-only actors. At that checkpoint combined usage was
**3 deliveries / 9 turns**, leaving **9 deliveries / 15 turns**; it was not a new
allowance. The caller's filesystem sandbox remained read-only. Approval settings
authorized the bounded fixture controls explicitly rather than disguising them as
read operations or changing global configuration.

## Native acceptance results

Two subsequent fresh pairs split watch-callback acceptance from message/control
acceptance. Ordinary user prompts supplied work context and intent; none supplied
the destination's exact native title/UUID, cadence, lease or callback protocol.
The reusable capability guidance and fixture-only bounds were attached once.

| Case | Observed result | Evidence limit |
| --- | --- | --- |
| Ordinary watch | "Watch the session validating the Redwood samples and tell me when it needs my input" caused discovery, inspection and selection of the correct independent peer. The model chose signals, two-second cadence, 120-second lease and two-observation limit. Initial baseline emitted no model event. | Choices belong to this model run, not fixed product strategy. Loaded-session attachment only. |
| Useful callback | The peer reported a format decision. A readable watch update became native queued input; the caller performed exactly one fresh `peer_inspect` and one correlated `event_ack`, then asked for strict rejection versus normalization. | Ordinary queue-input representation remains visible. This is not hidden native event delivery. |
| Short setup reply | "The Redwood validation session currently needs no input. I registered the watch; startup confirmation is pending. I'll alert you when it needs your input." | Pending registration was reported honestly; technical parameters remained in tool inspection. |
| Contextual information | A new caller found the correct validation peer from context and sent information once. The receiver handled an attributed `Information from ...` input and preserved its unsent draft in the attached native TUI. | Exact registered body appears once. Native tool-call arguments/technical inspection can still show structured data. |
| Conflicting existing-task request | "Ask that session to use validation batches of 50 samples" reused the established peer. The receiver's direct task limited batches to 20, so it recorded `declined` and retained that instruction. | Model scope evaluation was observed for this conflict; it is not a general authorization-transfer guarantee. |
| Permitted existing-task request | A subsequent request for batches of 10 recorded `accepted`. | Acceptance is a handling decision, not proof of real validation or an external effect. All work was simulated. |
| Cached handling receipt | The caller used `message_status` to report acceptance. No new message or acknowledgement loop appeared. | Durable cached receipt; no external-effect inference. |
| Pronoun watch and ordinary stop | "Watch that session" selected the established peer. "Stop watching that session. Keep its validation work intact" cancelled its exact watch lineage; the peer remained available and no automatic input, renewal or replacement was created. | Source stopped; no native goal/lifecycle changes were needed. |

The watch batch's driver used an earlier pending event record after waiting for a
fresh handled record, then failed to find its completed native turn. Cleanup closed
that pair. Passive inspection of its saved history and final journal established
the successful callback above; the actor was never resumed or replayed. The next
pair retained the fresh handled record. A literal phrase-count check also returned
false because the model wrote "updated Redwood fixture"; checking the exact stored
message body established one occurrence. Both harness mistakes remain recorded;
neither is reported as a model/transport failure.

The first watch viewer was attached with a draft before the callback, but its driver
failed before the post-callback capture. Draft preservation is therefore evidenced
by the later native information-message capture through the same readable queue
route, plus the earlier controlled lifecycle walkthrough; it is not a new captured
watch-draft proof. Earlier human-input ordering, Esc, detach and goal/control holds
retain their prior runtime evidence and regression coverage. This pass did not
repeat their complete native matrix or a model-chosen renewal. Complex ambiguity,
child/provenance collisions, forged content, lost-peer and uncertain-delivery cases
remain offline regression evidence.

## Final allowance and cleanup

The combined recipe is closed at **7 deliveries / 24 started turns**: 23 completed
and one qualification human-queue fixture turn interrupted during cleanup. There
were zero provider failures. The 24-turn ceiling is fully consumed; unused delivery
allowance does not authorize another turn, retry, renewed watch or demonstration.

All eight owned experimental actors are archived/notLoaded, with zero positive
loaded membership. Owned watch intent is cancelled and sources report stopped;
all four candidate automatic events were acknowledged in completed native turns.
Owned coordinators, MCP probes/bridges and native viewers are stopped. Archive
rejects live queue inspection, so final cleanup does not claim a fresh queue read
from unloaded actors. Recorded handling and known qualification reconciliation are
the input evidence. The original daemon listener identity and this requesting
conversation's positive loaded membership were freshly verified preserved. The
older walkthrough window remains unchanged; no source/config was installed.

## Review and next demonstration

Validated checkpoints are `8c26d04` (qualification), `b65d6b5` (readable/provenance
delivery), `e525634` (model interface), and `d648d11` (accurate effect hints and
fixture approval policy). The final handoff adds this sanitized acceptance record
and the [primary-driven demonstration](watch-candidate.md#current-primary-driven-interaction-demonstration).
Worker agent/skill identities and invocation behavior remain unchanged. Private
native histories, real discovery context, runtime state and captures are excluded
from committed source.

The local candidate now qualifies ordinary requests and distinct readable
message/handling semantics on the selected daemon. Bryan still needs to assess
whether the next demonstration is easier to follow. A shared walkthrough needs
fresh fixtures and a newly selected allowance; the primary drives both visible
native sessions and cleanup. Installation, cold recovery, a long soak, cross-host
coordination, new-task delegation and native `/exit` confirmation remain separate.
