# Local watch coordinator candidate

Run `scripts/codex-plus-watch` from this checkout. This is a local Linux/Unix
candidate for the qualified `0.162.1` native app-server surface. Queue operations
are experimental. The published/installed worker bundle is unchanged; this helper
has not been released or installed through chezmoi.

The coordinator owns one private state directory and one existing conversation.
It reuses that conversation's daemon for read-only observation commands and queued
input. It does not create a daemon, choose a saved session by name or automatically
load a cold thread. The model chooses scripts, filtering, cadence and follow-up.

## Binding and source setup

Use a private directory (0700), an exact loaded thread UUID and its requested Unix
socket. `CODEX_THREAD_ID` and the existing daemon's reported socket can supply
defaults, but both are validated before binding. State cannot silently rebind to
another owner or conversation.

Replace the placeholders below with your selected paths and IDs:

```sh
rtk proxy scripts/codex-plus-watch --state STATE bind --socket SOCKET --thread THREAD_UUID
rtk proxy scripts/codex-plus-watch --state STATE watch_start --cwd WORKDIR --duration 120 --limit 2 --followup 'Inspect this observation under the existing request' -- rtk proxy python3 -B -u OBSERVER.py
rtk proxy scripts/codex-plus-watch --state STATE wake_schedule --after 20 --duration 120 --prompt 'Inspect the run and choose whether further supervision is useful'
```

Registration returns its ID, frozen destination and effective bounds. Registration
is not a source-running or handling receipt. A coordinator starts lazily and is
reused for that state directory; concurrent launchers cannot acquire its owner lock.
It exits after ten idle seconds once intent and connected handling work have settled.

Every source uses native `readOnly` filesystem policy with network disabled.
Calling setup requires the qualified host access path; it does not inherit that
read-only source policy. Restricted calling contexts failed the Unix-control probe
and remain unsupported without a separate host-side tool design. Managed MCP
credentials are not assumed available to a source.

Each nonempty UTF-8 line is an occurrence, including identical repeated lines.
stdout records are bounded to 4 KiB, cumulative stdout to 64 KiB and diagnostic
stderr to 16 KiB. Truncation, invalid UTF-8 and malformed selected snapshots stop
the source explicitly and expose source failure separately from job outcome.

Optional `--snapshot-fields status,progress` projects top-level JSON fields and
persists its comparison baseline with the pending event atomically. Timestamp
churn outside those fields stays quiet. The initial snapshot emits by default;
`--quiet-initial` chooses an initial quiet baseline. Task conditions and polling
still belong in the script. A line source needs no universal job schema.

The model chooses positive duration (up to 86400 seconds) and a finite event
limit (1–1000, default two). Native experiments stay within the separately agreed
120-second/two-event bounds; longer operation is not qualified by those tests.
`--notify-end` allows at most one additional source lifecycle notice, including
expiry, within a 30-second delivery window. It does not establish a watched-job
terminal outcome. One-shot timers admit at most one event and create no missed-run
backlog.

## Inspection and controls

```sh
rtk proxy scripts/codex-plus-watch --state STATE list
rtk proxy scripts/codex-plus-watch --state STATE status REGISTRATION_ID
rtk proxy scripts/codex-plus-watch --state STATE cancel REGISTRATION_ID
rtk proxy scripts/codex-plus-watch --state STATE renew --id REGISTRATION_ID --cwd WORKDIR --duration 120 --limit 2 -- rtk proxy python3 -B -u UPDATED_OBSERVER.py
rtk proxy scripts/codex-plus-watch --state STATE ack EVENT_ID
```

Use your actual source argv after `--`; the renewal example is a placeholder.
Renewal first stops/confirms the predecessor, then registers a linked replacement
with the supplied invocation and bounds. It cannot overlap the predecessor or
renew cancelled supervision. Cancellation covers the selected registration's
lineage, including replacements, and remains authoritative during renewal races.

Inspection separates intent, source health, control reason, native admission,
queue-start state, live turn outcome and explicit acknowledgement. Cached status
does not connect to native runtime or start observation. When the coordinator is
offline, previously running source health is shown as unknown with its last receipt.

Esc interrupts the current model turn and leaves observation intent registered.
Native paused/budget-stopped/unknown control states hold delivery while bounded
observation continues. No goal setter or goal-resume operation is used. Busy
delivery waits; queue-start refuses an active/pending turn and does not jump an
earlier human input. An explicit message to stop supervision asks the model to
cancel its selected registrations. Already-admitted or in-flight input has a
separate receipt; cancellation does not promise retraction. The coordinator tries
to withdraw only an exact owned entry that is still pending.

Event envelopes include stable event/registration IDs, bounded data and the
original follow-up. They explicitly retain the existing authorization scope.
Native enqueue proves admission. A successful live turn is not an acknowledgement
or an external-effect receipt; `ack EVENT_ID` records handling only. Unknown or
unadmitted IDs cannot be acknowledged.

The qualified legacy CLI conversation exposed contradictory historical turn
statuses after interruption. Connected live completion and explicit acknowledgement
are journaled separately; history snapshots are not used to overwrite them or
to infer a missing completion during recovery.

## Recovery and shutdown

```sh
rtk proxy scripts/codex-plus-watch --state STATE recover REGISTRATION_ID
rtk proxy scripts/codex-plus-watch --state STATE shutdown
rtk proxy scripts/codex-plus-watch --state STATE shutdown --confirm
```

After coordinator restart, intent, baselines and events persist. An in-flight
admission becomes uncertain and is not blindly replayed. Sources from the previous
connection are marked lost and do not silently restart. Explicit `recover` requests
restart of an unexpired lost source after validating the exact owner and loaded
target; it preserves recorded baseline and admission uncertainty. The observation
gap remains visible. Occurrence sources need their own cursor/gap policy; recovery
does not promise complete log coverage or exactly-once processing.

`shutdown` previews affected owned work and requires `--confirm` when it would
stop registrations or leave pending handling. Confirmation cancels those
registrations, stops only their sources and closes the coordinator. It preserves
the native daemon, conversation, goals and unrelated background shells/tasks.
An explicit cancellation already supplies authority for that selected work.

The helper does not intercept native `/exit` or add a native confirmation dialog.
The native viewer remains separate from the coordinator's lifetime. Bryan's
reported Claude exit protection is a reference; its exact task coverage was not
reproduced by this pass.

## Acceptance boundary

See [the goal-loop evidence](coordinator-loop-results.md) for tested behavior and
current limitations. Human draft/input/stop acceptance, an accessible real-source
pilot, longer operation and managed installation remain subsequent checks.
