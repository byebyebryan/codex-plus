# Get started with Codex Plus

Choose the part that helps your work: delegate a task, follow a running job or
publish a browser handoff. The components install separately and keep native
Codex as your daily interface.

## Choose what to install

| You want to… | Install | First request |
| --- | --- | --- |
| Delegate investigation or implementation | Worker agent definitions and workflow skills | `$luna-task` Investigate the importer failure and return a reproduction. |
| Follow work, coordinate sessions or check later | Monitoring runtime and its `codex_plus` MCP configuration | “Watch this run and tell me if it stalls or fails.” |
| Share findings in a browser | Reporting runtime, hosting configuration and report skill or `html_report` MCP | “Make a browser report of the results, including the risks.” |

Workers use native agent tools. Monitoring provides 15 MCP tools for observation,
peer communication and later checks. Reporting provides four tools and an
independent static report store. Installing one component does not install the
others.

## If your setup is already managed

Use the configuration manager that owns your agent, skill and MCP files. For
Bryan's Snap and Starship installations, that is chezmoi. Open a fresh ordinary
session in the intended environment and use a request from the table above.
Existing explicit opt-outs remain effective. Loaded processes adopt selected
code on normal reconnect; updating documentation does not update them.

On Snap, `codex` selects personal/OSS work and `codex-work` selects work. Their
conversations, tools, follow-up state and reports use separate contexts. See
[environment selection](environments.md) for the managed paths and portable
`CODEX_HOME` behavior. Choose that environment before starting a task.

## Set up workers

Install the `luna-max` and `sol-xhigh` agent definitions and the four worker
workflow skills using the [worker installation steps](workers.md#installation).
Your client and account must support custom agents, skills and the selected
models. The intended primary is Sol XHigh; workflows keep your current primary
selection.

Start with `$luna-task` for one bounded assignment. Use `$luna-goal-loop` for a
substantial goal with Luna, or the adaptive `$worker-task` / `$worker-goal-loop`
workflows when the primary should choose useful delegation. Your primary owns
decisions and review. Generic “goal loop” wording does not select a worker.

## Set up monitoring and coordination

The [monitoring installation guide](runtime-distribution.md) covers verified
release archives, immutable installation and MCP configuration. The preview
targets Linux/Unix, Python 3.11 or newer and RTK. It was qualified against Codex
0.162.1; that is a compatibility result, not a claim about every newer client.

Integrate the generated MCP table through your configuration owner. Once loaded
in a native conversation, ask for a useful update from a source your session
can already access. Peer coordination needs independent loaded sessions within
the same owning daemon. See [daily use](daily-use.md#watch-another-session) for
discovery and handling receipts.

## Set up reporting

The [report guide](html-report-usage.md) covers the separate report artifact,
MCP or CLI entry point, store and serving configuration. Its Python runtime does
not require a native agent owner. Optional automatic hosting uses tmux; an
external HTTP server can also serve the configured public subtree.

Configure a report URL reachable from your viewing desktop. Publication stores
an immutable snapshot; a delivery check verifies HTTP bytes; opening it in your
browser verifies the presentation. These are separate results. Publishing a
report does not publish a GitHub Pages site or make a private endpoint public.

## Try one useful request

Use work already in front of you. Give a worker a concrete outcome and acceptance
check, describe the change you want a watch to report, or ask for a browser
handoff of actual findings. You can inspect registrations and explicitly stop a
watch. Esc interrupts the foreground turn while independent observation remains
within its bounds.

Continue with [everyday requests](daily-use.md), explore the
[illustrative walkthrough](presentation.md), or read
[how the components fit together](architecture.md). The
[daily-use checklist](soak-checklist.md) helps record useful outcomes and friction
without treating bounded synthetic checks as long-term reliability evidence.
