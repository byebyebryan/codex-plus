# Terminal-associated rich notification launcher

Date: 2026-10-15. Status: explicit launcher installed and qualified for local/SSH
delivery and viewer lifetime; daily selection remains off pending acceptance. Bryan accepts a
launch helper to preserve unfocused-only notifications and originating-terminal
focus. The relay is an explicit pilot. The helper is independently pinned; ordinary
launches keep native basic alerts. Desktop click and physical acceptance, daily
shell selection, canonical-source convergence and the 349 admission rollout are
still open. Existing native owners and live services have not been restarted.

## User experience and ownership

The target is ordinary local and SSH terminal use of the native Codex TUI and
its existing daemon. Start with an explicit `codex-notify run` pilot. Recommended
eventual integration keeps typing `codex` through a managed interactive-shell
entry point; this is the working assumption for the goal loop. Explicit
native executable invocation remains available. CLI utilities and automation
retain their native argument, stdin/stdout and exit behavior.

| Owner | Responsibility |
| --- | --- |
| codex-plus | Launcher, terminal-associated completion publication, metadata and scoped native inspector |
| Chezmoi | Host-scoped launcher integration, independent helper pin, notification preferences and rollback |
| Kitty | Unfocused-only presentation and activation of the originating terminal window |
| 349d | Generic mirroring plus optional host labels and proved superseded-card removal |

The helper is independent of Agent Observer, monitoring/report workers and
physical displays. The existing USB notification/close protocol is sufficient.
The 349's unavailable DMS Open provider is a separate integration issue.

Bryan verified desktop clicks focus Kitty with daemon-backed Codex both while
viewing a session and while showing Command Center. This establishes window
focus as the baseline. V1 Open focuses that same terminal; thread selection
inside Command Center remains a native TUI interaction. With tmux, activation
targets the containing Kitty terminal; selecting an inactive tmux pane/window
is not assumed by the notification action.

## Selected publication path

```mermaid
flowchart LR
    L[Launch helper] --> T[Native Codex TUI]
    T <--> R[Private transient relay]
    R <--> D[Existing native daemon]
    R --> P[Bound completion event]
    P --> K[Originating terminal: Kitty OSC 99]
    K --> N[Desktop notification]
    N --> F[Click: focus originating Kitty window]
    N --> H[349 generic notification center]
```

Use the existing `notification_run` / `notification_stream` prototype as the
starting point. Relay native bytes unchanged. Observe only the bounded metadata
needed for successful root-thread bindings, completed turns and final text.
Publication uses the launch's exact terminal route, including supported tmux
passthrough. SSH naturally carries the output back to the originating desktop;
no fixed destination host or desktop receiver is required for this route.

Keep observer state bounded and in memory; do not log prompts, transcripts or
raw native traffic. Use a private transient socket/directory and verify the
existing listener's user/process/socket identity before attaching. Revalidate
source incarnation at reconnect rather than following a stale owner. The helper
never starts or replaces a native owner to make rich delivery available.

The relay is the completion publisher for a wrapped client. Leave server-side
`notify=[]` and the global native completion/approval recovery selected on the
supported hosts. Disable only native completion publication for the wrapped
client after its route is ready; retain native approvals/questions and all other
configured event types. A TUI `notify` override cannot disable a server hook.
Unexpected configured server hooks must be reported before choosing rich mode,
rather than silently creating two completion publishers.

Loaded threads may retain earlier hook settings even when disk config now has
`notify=[]`. Qualify fresh threads and already-loaded thread resume separately;
disk configuration alone is insufficient evidence of one publisher. The safe
adoption design must preserve existing user threads without forced unload or
daemon restart. Unresolved hook ownership blocks daily-launcher promotion for
that context, rather than being treated as a harmless configuration difference.

The daemon hook remains available for other explicit integrations. It is not a
required companion to this launch path. Native basic alerts remain the publisher
for ordinary unwrapped clients and supported pre-launch fallback.

## Binding and notification rules

- Bind exact source host, configured native instance and thread IDs from
  successful native start/resume responses on this client connection. Require
  positive supported user-root classification; exclude internal/title/subagent
  work. A roster entry, title, working directory or process environment cannot
  establish a route.
- Retain valid bindings while this TUI shows Command Center or another thread.
  Use each event's thread/turn IDs, not the currently displayed thread. Specify
  removal on native detachment, closure and connection replacement from actual
  protocol evidence. Starting a fresh Command Center does not bind every listed
  session automatically.
- Publish one completion per episode per client connection. Preserve paragraphs,
  bounded UTF-8 body text, source host and the existing v1 identity envelope.
  Keep final-answer selection separate from intermediate assistant messages.
- Apply unfocused-only delivery through the originating Kitty route. Foreground
  behavior follows the native terminal baseline, including Command Center.
- Define V1 focus and publication per terminal viewer. Two independently attached
  eligible viewers may each publish an episode; there is no claimed global
  single-alert arbitration. The 349 deduplicates copies by episode without
  renewing attention, retention or brightness. Test multiple viewers explicitly.
- Reconnection clears old route authority. Rebind through fresh native evidence;
  history reads must not replay old completion notifications. Closing a viewer
  ends its publication route while the daemon and its work retain native lifetime.

Command Center needs a dedicated native coverage check. The prototype observes
explicit start/resume bindings; broader background-session coverage must be
proved against the TUI's own subscription/routing behavior before promotion.
Do not grant authority to all sessions merely to make a test produce an alert.

## Launcher dispatch and failure behavior

| Situation | Planned behavior |
| --- | --- |
| Qualified interactive default/resume launch | Prepare private route, then launch native TUI with completion publication assigned to relay |
| `exec`, review, app-server, authentication, help/version and other CLI utilities | Invoke the native executable directly with exact argv and exit status |
| Explicit `--no-daemon`, unsupported remote endpoint, fork or unqualified native version | Preserve native behavior; rich mode is outside the initial qualified scope |
| Helper, existing daemon, usable terminal or supported protocol unavailable before TUI launch | Use the native basic path without changing global preferences; explicit rich invocation reports why it cannot qualify |
| Final response missing but a supported bound completion exists | Publish a bounded generic completion body with exact identity |
| Observation becomes unavailable while native traffic still works | Keep traffic forwarding, issue one clear degraded-status notice through the known terminal route, and stop claiming rich coverage |
| Relay transport or process fails after launch | Preserve owning daemon/work; native TUI disconnection/recovery behavior must be qualified. Never automatically relaunch or resubmit a prompt |

Pre-launch fallback and mid-session failure are different guarantees. Once a
client has disabled native completion alerts, the prototype cannot currently
restore them live. Do not claim automatic basic fallback for every later failure.
If the degraded behavior cannot be made clear and acceptable, keep the launcher
opt-in until a stronger recovery path is qualified.

Dispatch must parse actual native invocation structure: an argument or prompt
containing a subcommand's name must not change routing. Resolve a native
executable independently of the managed shell entry point to avoid recursion.
Keep shell completion, quoting, working directory, job control, Ctrl-C, exit
status and native startup/daemon policy intact. Interactive-shell integration
must not change noninteractive scripts or raw protocol stdout.

## Execution and acceptance

| Step | Deliverable | Exit evidence |
| --- | --- | --- |
| 1. Freeze semantics and native scope | Selected entry point, publication policy, ownership/detachment rules and supported native version | Review against current native protocol and this plan; no live settings change |
| 2. Harden the explicit launcher | Correct dispatch, classification, content, bounds, signal handling and honest degradation | Existing suites plus targeted regressions; private native TUI fixture preserves bytes/behavior and excludes unrelated/internal threads |
| 3. Qualify desktop daily use | Explicit installed local and Snap SSH launches | One useful completion with Codex sender, separate title/body and host; foreground suppression; actual desktop click focuses the originating window in session and Command Center views |
| 4. Qualify lifecycle edges | Switching, two threads, multiple viewers, reconnect, viewer closure and errors | No wrong-thread publication, stale replay or unrelated-owner signal; native approvals/questions remain usable; exact declared fallback/degraded behavior |
| 5. Recheck optional 349 behavior | Existing rich consumer plus delayed-arrival correction | Local/SSH cache admission, retention after panel presentation expiry, exact newer-turn removal, duplicate handling and physically observed readability/removal |
| 6. Prepare managed daily entry point | Independent release/manifest and scoped chezmoi candidate | Fetched bytes, current source convergence, narrow dry-run/apply, installed readback and rollback/reselection; switch only fresh launches |

Step 3 must cover a TUI returning to Command Center while its bound turn completes,
and switching to another bound thread before the first finishes. Include direct
Kitty and supported tmux, local and SSH, focus-away/back, no-body/error cases and
closing the window while the native turn continues. Keep actual window-focus
observation distinct from packet and serial evidence. Use owned disposable
threads; existing user sessions and daemon incarnations remain untouched.

The review found a 349 delayed-first-arrival gap: an unseen old completion can
reach the board before polling proves supersession. Fix or explicitly revise
that display guarantee before accepting step 5. The alternate desktop transport
also had an uncaught subprocess-exit timeout. The source checkpoint normalizes it
to the existing quiet hook error path; it is not a dependency of the selected
terminal relay path.

Roll out explicit mode first, then the selected daily entry point on one host,
then the second host after desktop acceptance. Retain native recovery and prior
helper selection. Rollback changes only fresh-launch selection; it neither
restarts active TUIs/daemons nor closes unrelated sessions. Canonical chezmoi
source must incorporate the candidate before a broad apply can be considered
consistent with the installed state.

The first managed scope is Starship and Snap. Preserve other hosts' existing
helper entry points and notification preferences, as well as independent
codex-plus worker, monitoring and report selections.

Source review, artifact publication, installed-byte acceptance, desktop behavior
and physical 349 acceptance remain separate checkpoints. Panel Open through DMS
has its own investigation and acceptance; it does not gate desktop click-to-focus
or authorize a DMS/349d restart in this plan.

## Source checkpoint: 2026-10-15

- `launch` dispatches unsupported/noninteractive invocations to the native binary;
  qualified `run` checks the existing listener, native version, configured hook
  and focus policy without changing configuration. Only completion is removed
  from the client's native event filter. Other configured events are retained.
- Positive user-root classification, exact resume-ID checks, native alias resume,
  unsubscribe/close revocation, per-viewer Kitty IDs, Codex sender and bounded
  degraded status are implemented. Native signal exit handling is retained.
- Forty-nine notification tests and five inventory-validator tests pass, including
  real owned subprocess/Unix-socket checks of byte forwarding, argv, exit status
  and one degraded notice after observation failure. Source inventory passes.
- Private stock 0.162.1 TUI/server plus loopback model passed completion in Command
  Center, creating a second root before the first completes, and resuming an
  already-loaded thread with the legacy terminal helper. Exact body/metadata
  association, Codex app name and absence of native OSC 9 duplication passed.
  All fixture processes were reaped; no real provider or desktop was involved.
- The 349 source now holds configured rich arrivals in a bounded queue for native
  inspection before display. Proved stale first arrivals emit no device packet;
  generic arrivals bypass slow inspection. Replacement and replay checks pass.
  Full host/tooling validation passed 433 tests; three live desktop tests skipped.

Private evidence is under `~/.cache/codex-notify-launcher-20261015`. The first
Command Center harness needed separate typing/Enter events to avoid native paste
coalescing; the loaded-thread fixture needed a persisted first turn before resume.
Only completed corrected runs support the claims above. At that source checkpoint,
installed desktop and managed-rollout gates were open; the later checkpoint below
records new evidence without promoting packet/private checks to GUI acceptance. Arbitrary custom
hooks on already-loaded threads remain outside the legacy/no-hook qualification.


## Installed explicit-pilot checkpoint: 2026-10-15

The published [preview 2](https://github.com/byebyebryan/codex-plus/releases/tag/codex-notify-v0.1.0-preview.2)
selects `a41365cdcf3dfd34576ed4a935b95bb55a4371e1`, source archive SHA-256
`03be5f680e62eb27f488a6a5d35cfdcaa4e0360ee9d9ce4e3dd52873d93b2e50`.
Chezmoi helper-only dry-run/apply, fourteen-file hash/mode readback and rollback
to preview 1 followed by reselection pass on Starship and Snap. Worker/report
selectors, native notification preferences, shell files and protected service
identities remain at their starting state. This selection makes explicit `run`
available; it does not replace ordinary `codex` launches.

Actual stock 0.162.1 native owners were used with owned disposable threads and
temporary loopback Responses providers. No external model requests or credentials
were used. The native TUI saved trust entries for the owned test directories;
only those exact entries were removed afterward, guarded by restoration of each
host's original complete configuration hash. Owned threads were archived, test
windows/SSH forwards/private servers reaped, and native PID/start ticks unchanged.

| Case | Actual desktop evidence | Actual 349 evidence |
| --- | --- | --- |
| Direct local Kitty | Foreground completion suppressed; one Codex notification in Command Center with `Codex @ starship`, separate body and exact metadata | Card `100106` retained after 31 seconds, then removed after a newer exact turn |
| Snap through ordinary SSH to Kitty | Same checks with `Codex @ 80H1VV3`; no fixed desktop receiver | Card `100108` retained after 31 seconds, then removed after a newer exact turn |
| Local Kitty with an owned tmux server | Same suppression, Command Center and body/metadata delivery through tmux passthrough | Card `100110` retained after 31 seconds, then removed after a newer exact turn |

Direct local and SSH checks closed only their owned viewer while a subsequent
turn was waiting at the loopback provider. Native readback still showed that
exact turn in progress; it then completed after the provider was released with
no viewer. The tmux case also passed, then its owned tmux server was removed.
These checks establish daemon/work lifetime, not automatic recovery of a dead
relay or restoration of native completion filtering inside a surviving client.

A local click-window probe recorded the intended Kitty window gaining focus
while showing Command Center. The input action was not captured, so this is
window-focus evidence, not confirmed notification-click attribution. The SSH
probe received its notification but recorded no focus during its observation
window. User click confirmation remains pending for both contexts; no click
failure is inferred from an unobserved test. Session-view rich clicks have not
been separately accepted.

An additional private native two-viewer check passed: both real TUIs resumed the
same owned thread, neither replayed its completed history, and each emitted one
completion with the same episode and distinct Kitty action identifiers. It had
no desktop and does not claim global exactly-one delivery.

The 349 admission fix at `a46ccc8` also passed an integration check using both
installed inspectors and actual native history from the owned local/SSH cases.
Delayed old completions were proved superseded before admission and emitted zero
fake-wire packets. This strengthens the source tests but is not live activation:
existing 349d, firmware and DMS remain unchanged. All six 349 CI jobs passed,
including both firmware builds. Physical panel readability/removal is unobserved;
the unavailable DMS panel Open provider remains separate.

Chezmoi's daily interactive Zsh entry point is prepared and host-gated. Both host
activation switches remain false. Render checks cover selected/disabled/unknown
hosts; an owned PTY check preserves spaces, newlines, literal shell syntax and
exit status, while noninteractive/no-TTY use stays native. The full distribution
checker passes. Canonical checkout convergence and scoped shell activation remain
release gates after desktop acceptance; no global PATH shim was installed.

Private receipts are under `~/.cache/codex-notify-launcher-20261015`. Only completed
corrected fixtures support this table. Earlier harness attempts exposed test-only
trace selection, TTY forwarding, trust-prompt and monitor issues; overlapping GUI
fixtures were stopped and the SSH lifecycle case rerun sequentially with exact
thread filtering. No production source change was needed for these corrections.


## Startup-policy review follow-up

The preview 3 follow-up preserves native daemon policy in automatic dispatch.
Native 0.162.1 uses embedded mode when `daemon_auto_start` is false, even if an
unrelated shared listener already exists. Automatic `launch` now requires an
effective true value; explicit `run` still selects its requested existing
endpoint. CLI overrides for daemon-owned features (`daemon_auto_start`,
`worktrees`, `transcript_v2`, `realtime_conversation`, `standalone_web_search`)
stay native, including quoted/dotted TOML keys and feature-table overrides.
Other feature overrides retain their native arguments through the relay.

Fifty notification tests pass after this review correction, including exact
native argv fallback and effective configuration checks. The selected explicit
route, content, packet, inspection and wire behavior are unchanged from preview
2's installed qualification. The follow-up does not activate daily shell mode,
restart an owner, or claim the pending click/physical acceptance gates.


## Desktop acceptance and rollout preparation follow-up

Preview 3's actual local session-view popup was visually inspected: Codex sender,
host title, final body and separate paragraph were present. A corrected passive
monitor correlated DMS acceptance with desktop IDs 566, 567 and 568 for owned
test episodes. An earlier monitor incorrectly allowed the client library to
answer observed method calls; that disconnected the monitor and hid replies.
This was a fixture error, not a missing DMS acknowledgement.

One-shot virtual-pointer attempts produced no corresponding ActionInvoked signal
or accepted originating-window focus. Their input path has not been qualified,
so they establish neither successful clicks nor a helper focus failure. Manual
local/SSH clicks in session and Command Center views remain required. A fixture
that correlates the exact returned desktop ID, actual owner action signal and
intended window focus is prepared; no further visible test is staged without an
available observer. Owned test windows/threads were cleaned up, known test
desktop IDs closed and exact native configuration restored.

Both canonical chezmoi checkouts have been fast-forwarded locally to the reviewed
notification source; GitHub main remains unmerged. No broad apply ran and daily
host selection stays false. A scoped 349d activation/rollback plan is prepared
under the private evidence directory: candidate and prior reviewed host archives,
hash manifests, exact config/service/pairing backups and verified isolated imports.
The running Python service has no source revision stamp; the rollback target is
the prior reviewed commit, not a claimed dump of its loaded objects. Activating
the new queue requires a 349d-only restart. Repository instructions require user
authorization for that live service change, and authorization has been requested.
Native owners, DMS, Observer, RLCD, Mesh and report services remain untouched.


## Visible Open action follow-up

An owned fullscreen terminal independently confirmed that the virtual pointer
delivers real press/release events. DMS 1.6.3 source and the live false
`notificationPopupBodyInvokesAction` preference then explained the earlier
non-action: long card bodies expand on click. Kitty labels its default action
with a space, leaving no discoverable named Open button in this context.

The next producer candidate adds one visible Open button through OSC 99's
standard button payload. Title, body and button are collected before the sole
completion marker, producing one desktop Notify call. Kitty's normal focus
action activates the launch's exact terminal; no global DMS preference, launcher
guessing or extra receiver is needed. Clicking card body text continues to follow
the notification center's expansion/text policy. The explicit Open action is the
qualified terminal activation gesture.

The source pilot passed a real local session-view click: DMS accepted notification
578, the visible Open button emitted its exact action 1, and originating Kitty
window 86 gained focus. Foreground suppression, sender/body/metadata and one
publication also passed. The native owner was unchanged and the owned thread
archived. Fifty notification tests pass, including unchanged native relay bytes
and a sole final marker after the button. Packaged local Command Center and SSH
acceptance are the next gates; this source pilot alone does not establish them.

## Installed Open and shell selection follow-up

Installed preview 4 passed actual desktop Open in local and Snap SSH session
views and Command Center. Each case correlated one native episode with its
returned DMS notification ID, visible action 1 and the originating Kitty window
gaining focus. Command Center detection matched its header, not its help text.
The local ordinary `codex` shell entry also passed this correlation in Command
Center. Owned threads were archived and owner identity was unchanged within
each accepted run. This establishes graphical desktop activation; physical 349
rendering/touch and the separate unavailable DMS panel Open provider remain open.

Fresh interactive user shells now select the helper on both hosts. Actual PTY
checks preserve native dispatch in agent and noninteractive shells. Exact scoped
shell apply, rollback and reselection passed for both hosts. Only `.zshrc` and
the notification shell snippet were selected; no global PATH shim or broad apply
was used. Unrelated Observer source changes were preserved. An independently
stopped RLCD service was observed and left stopped.

## Native version compatibility follow-up

The native managed servers independently transitioned to 0.163.0 during
qualification while `/usr/bin/codex` remained 0.162.1. No daemon restart command
was issued by this work, and the transition's cause was not established. Preview
4 correctly falls back to native behavior for this unqualified server pair.
The next candidate qualifies explicit TUI/server pairs 0.162.1/0.162.1,
0.162.1/0.163.0 and 0.163.0/0.163.0; other combinations remain native.

Private real-native checks with a loopback model passed Command Center for
0.163.0/0.163.0 and a switch between two running roots for 0.162.1/0.163.0.
Exact body/metadata association, visible Open payloads and absence of native
OSC 9 duplication passed. With global auto-start enabled, the private listener's
PID/start ticks remained unchanged; only a harmless startup lock was created.
All owned processes were reaped. These checks had no real provider or desktop.

Matching native source confirms that an explicit `--remote` endpoint bypasses
daemon management. No extra daemon-policy override is needed. Native remote
mode rejects additional workspace roots, so `--add-dir` and explicit
`sandbox_workspace_write` overrides now preserve exact native dispatch instead.
Fifty-one notification tests pass, covering the pair allowlist and these argv
fallbacks. Installed qualification against the current server and updated
release selection remain separate from the private checks above.
