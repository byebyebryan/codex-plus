# Install and manage Codex Plus with your agent

Give your coding agent this guide and the action you want. It uses ordinary
file, shell and network tools; Codex Plus does not need to be installed first.
The [setup overview](https://dev.byebyebryan.com/codex-plus/start/) explains components for human readers.
The [plain Markdown guide](https://dev.byebyebryan.com/codex-plus/manage.md)
contains these same instructions without the website navigation.

## Choose an action

Copy a request, or describe the same intent in your own words:

| Action | Request to your agent |
| --- | --- |
| Install | Read https://dev.byebyebryan.com/codex-plus/manage.md and install Codex Plus on this machine. |
| Upgrade | Read https://dev.byebyebryan.com/codex-plus/manage.md and upgrade my existing Codex Plus installation. |
| Inspect | Read https://dev.byebyebryan.com/codex-plus/manage.md and check my Codex Plus installation without changing it. |
| Configure | Read https://dev.byebyebryan.com/codex-plus/manage.md and help configure my Codex Plus components. |
| Roll back | Read https://dev.byebyebryan.com/codex-plus/manage.md and roll back Codex Plus to my previous verified release. |
| Clean up | Read https://dev.byebyebryan.com/codex-plus/manage.md and clean up unused installation files, keeping my reports and history. |
| Uninstall | Read https://dev.byebyebryan.com/codex-plus/manage.md and uninstall Codex Plus, keeping my reports and history. |

The rest of this guide addresses the agent carrying out that request. Execute
only the requested action. Reading this page does not authorize unrelated work.
An upgrade request includes changing ordinary installation pins through their
owner; ask only for missing scope, a meaningful choice or an action beyond the
request. Complete independent preparation before reporting a manual prerequisite.

Start with environment discovery below. For **Inspect**, perform read-only
verification and diagnostics, then stop; no release download or repair is needed.
For **Configure**, change only the requested settings. **Roll back**, **Clean up**
and **Uninstall** use their action sections and retained provenance; they do not
begin by installing a newer release. Only **Install** and **Upgrade** follow the
new-release installation sequence. Fetch missing provenance only when needed for
the requested action and available under existing access.

## Inspect the existing environment

Identify the target machine and effective `CODEX_HOME`, including launcher/env
overrides. Inspect current component prefixes, `current` links, manifests,
native agent/skill locations, MCP entries, report configuration and explicit
`CODEX_PLUS_*` overrides. Use the [environment contract](https://dev.byebyebryan.com/codex-plus/environments/).
A native profile name alone does not establish a separate home. Do not copy
another home's credentials or move its state.

Determine who owns each file: chezmoi, another configuration manager or this
unmanaged installation. Resolve symlinks and inspect manager source before edits.
Keep unknown ownership explicit. On an existing installation preserve selected
components, custom paths, disabled tools, explicit opt-outs and approval policy.
For a generic fresh install, propose workers, monitoring and reporting together;
honor an explicit partial selection. Reporting's skill is optional; legacy Terra
workers are an explicit separate choice.

The current runtime preview requires Linux and Python 3.11+; monitoring's native
command paths also require RTK. Workers alone use native agent/skill support.
Git and network access support fetching release/verifier sources.
Optional automatic report hosting uses tmux; an external static server can serve
reports instead. Check prerequisites without upgrading native Codex or changing
system services automatically. Workers require the named native models and custom
agent/skill support; do not substitute models silently. See the recorded native
compatibility limits in the [runtime reference](https://dev.byebyebryan.com/codex-plus/installation/).

When a runtime is installed, choose `DIAGNOSTICS` as its verified release
directory: `MONITOR/current` or, for a reporting-only setup, `REPORT/current`.
Run its read-only diagnostics in the intended native home with discovered prefixes:

```sh
rtk proxy env CODEX_HOME=CODEX_HOME_PATH python3 -B DIAGNOSTICS/scripts/codex-plus-context
rtk proxy env CODEX_HOME=CODEX_HOME_PATH python3 -B DIAGNOSTICS/scripts/codex-plus-doctor --human --runtime-prefix MONITOR --report-prefix REPORT --worker-prefix WORKERS --no-native
```

Uppercase names and example paths in commands are parameters for the agent to
resolve, not literal user commands. Use absolute paths. Prefix shell commands
with RTK in environments that require it. The context command describes its own
environment; pass the same explicit overrides used by the installed MCPs. A
workers-only setup has no runtime doctor; verify its retained manifest and copied
agent/skill files instead. Do not add a missing component just to diagnose it.
`--no-native` checks files
and configuration without contacting native sessions. Omit it only for an
authorized read against an existing owner. Never start a daemon to make diagnosis
pass. Keep a private before/after record of affected files and process identities;
do not put credentials or private runtime captures in source control.

## Resolve and verify one published release

Use the public repository **byebyebryan/codex-plus**. Honor a requested version or
hold policy. Otherwise enumerate published, non-draft product releases and select
the newest version appropriate to the installation, including previews for this
preview project. Compare version numbers, not lexical tag order or the website's
version text. Exclude old `reports-*` and `codex-notify-*` component releases from
the unified upgrade path. Check enough release pages to establish the choice;
do not assume an API's `latest` alias includes previews.

For example, with an existing personal github.com `gh` connection:

```sh
rtk proxy gh api --hostname github.com --paginate 'repos/byebyebryan/codex-plus/releases?per_page=100' --jq '.[] | select(.draft == false) | {tag_name, prerelease, published_at, assets: [.assets[].name]}'
rtk proxy gh api --hostname github.com repos/byebyebryan/codex-plus/releases/tags/TAG
rtk proxy gh release download TAG --repo github.com/byebyebryan/codex-plus --dir STAGE/assets
rtk proxy git clone --branch TAG --single-branch --depth 1 https://github.com/byebyebryan/codex-plus.git STAGE/source
rtk proxy git -C STAGE/source rev-parse HEAD
rtk proxy python3 -B STAGE/source/scripts/codex-plus-release verify STAGE/assets
```

Use a new private staging directory outside the installation and source checkout.
Keep `github.com` explicit when `gh` also has an enterprise host configured.
The public GitHub REST/download URLs can be used without `gh` or an account; do
not change authentication or copy tokens to staging. Download the three archives,
`release.json` and `SHA256SUMS` from that exact tag. Record their expected asset
digests from the selected release when supplied. Match the tag, checked-out full
commit, manifest version/revision, archive hashes/modes and selected components.
The release-compatible verifier above checks all three inventories and their
shared identity. Checksums prove consistency with the recorded release, not an
independent signature of its publisher. On a failed check, preserve the current
installation and explain the mismatch.

Keep this selected tag/revision fixed through the operation. The current website
explains the lifecycle; commands and compatibility must also match the selected
release. Older verifiers accept only their declared versions. Do not run a moving
`main` verifier against an arbitrary historical release. If an older component
release has no unified manifest, follow its retained version-specific reference
and record that narrower verification. An offline inspection can finish; an
offline upgrade must report unavailable release evidence rather than use main.

## Install or upgrade through the configuration owner

For **chezmoi or another manager**, work in its canonical source. Preserve local
changes, inspect existing pins and update the requested component URLs, full
revision, checksums and relevant validators together from the verified release.
Render and parse the relevant config, preview the diff, then apply only the
requested targets. Inspect rendered agent files, skill paths and both MCP entries.
Do not overwrite managed output with the unmanaged commands below or run an
unrelated full-manager apply. Respect explicit host/environment selectors.

For Bryan's managed setup, `.chezmoiexternals/codex-plus.toml` owns the archives;
the worker prefix retains the compatible `codex-worker-kit` name. Monitoring and
reporting have separate selections. These personal paths are examples, not
portable defaults. The [managed rollout reference](https://dev.byebyebryan.com/codex-plus/installation/#upgrade-rollback-and-activation)
and the manager's own instructions govern its render/apply procedure.

For an **unmanaged installation**, choose dedicated absolute prefixes for
monitoring and reporting and a retained worker release directory. Install and
verify all selected runtimes before changing either selection:

```sh
rtk proxy python3 -B STAGE/source/scripts/codex-plus-package install STAGE/assets/RUNTIME_ARCHIVE --prefix MONITOR --sha256 RUNTIME_SHA256
rtk proxy python3 -B STAGE/source/scripts/codex-plus-package verify-install MONITOR/releases/REVISION
rtk proxy python3 -B STAGE/source/scripts/codex-plus-report-package install STAGE/assets/REPORT_ARCHIVE --prefix REPORT --sha256 REPORT_SHA256
rtk proxy python3 -B STAGE/source/scripts/codex-plus-report-package verify-install REPORT/releases/REVISION
rtk proxy python3 -B STAGE/source/scripts/codex-plus-package activate --prefix MONITOR --revision REVISION
rtk proxy python3 -B STAGE/source/scripts/codex-plus-report-package activate --prefix REPORT --revision REVISION
```

Run only the selected component commands. Keep previous releases and their
verifiers for rollback and for processes that captured those paths. Repeating
an install of identical verified bytes should reuse that release; never replace
an immutable directory with different content.

For **workers**, verify the unified release first, then extract its verified
worker archive into a private retained directory. Its `workers.json` records
exact member hashes/modes and source revision. Preview.15 and later provide
`agents/luna-max.toml`, `agents/sol-xhigh.toml` and `agents/astra-xhigh.toml`.
Preview.17 provides both files (`SKILL.md`, `agents/openai.yaml`) from each of
`luna-task`, `luna-goal-loop`, `adaptive-task` and `adaptive-goal-loop`. Remove the
retired `worker-task` and `worker-goal-loop` directories through their configuration
owner, with backups and a scoped deletion preview; preserve unclassified local
edits before removal. Verify both old paths are absent. Preserve fixed model/effort pins and any
local restrictions. The Astra role's presence enables no automatic escalation.
For older selected releases, use only the roles and skills they actually contain.
Retain local disable preferences and restrictions on the canonical workflows.
If upgrading directly from an older worker-name installation, carry its existing
restrictions to the adaptive replacement; do not silently re-enable it.
Keep cleanup declarations consistent with the chosen release when rolling back.
Keep the verified archive/manifest as provenance. Do not install legacy Terra
files by default and do not change the primary model.

The source candidate adds explicit `sol-task`, `astra-task` and current
`terra-task` skills; preview.17 does not contain them. Install only workflows present in the chosen verified
release manifest. Do not graft moving-main skills into a pinned managed release.
When a release adds them, install both files per skill through the same owner,
preserve invocation restrictions, and verify discovery and model execution as
separate acceptance steps. The [named-task guide](workers.md#choose-sol-or-astra-explicitly-source-candidate)
explains their assignment-scoped permission and primary ownership.
Current Terra also requires `terra-6-1-xhigh` (`gpt-6.1-terra` / `xhigh`), separate
from legacy `terra-xhigh` (`gpt-5.6-terra`). Both task variants use `terra-task`:
identify any installed variant from retained provenance, select one deliberately
and preview a scoped migration through its owner. Preserve local edits and disable
preferences. Never merge/install both variants or delete a current task as legacy
cleanup; a role pin mismatch is a hold, not permission to substitute or retune.

For a conventional unmanaged home, native agent files go under `~/.codex/agents`
and user skills under `~/.agents/skills`. Confirm client-supported locations for
an alternate home; do not assume user skills are isolated merely by `CODEX_HOME`.
See the official [custom agent](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents)
and [local skill](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)
references. For empty targets, use explicit file copies such as:

```sh
rtk proxy install -D -m 644 VERIFIED_WORKERS/agents/luna-max.toml AGENT_ROOT/luna-max.toml
rtk proxy install -D -m 644 VERIFIED_WORKERS/skills/luna-task/SKILL.md SKILL_ROOT/luna-task/SKILL.md
rtk proxy install -D -m 644 VERIFIED_WORKERS/skills/luna-task/agents/openai.yaml SKILL_ROOT/luna-task/agents/openai.yaml
```

Repeat for the other named files. On upgrade, compare each destination with the
previous verified manifest before replacing it; retain a backup of changed local
content and reconcile the requested update. Unknown extra files stay intact.
Avoid recursive copying into an existing skill directory, which can merge old
files or nest directories. An existing skill disable preference stays effective.
Installing these files does not activate a worker workflow.

## Configure tools and reporting

Generate configuration from the selected release with the discovered home and
existing explicit overrides:

```sh
rtk proxy python3 -B MONITOR/current/scripts/codex-plus-package mcp-config --prefix MONITOR --codex-home CODEX_HOME_PATH
rtk proxy python3 -B REPORT/current/scripts/codex-plus-report-package mcp-config --prefix REPORT --codex-home CODEX_HOME_PATH --config REPORT_CONFIG
```

Run only the selected component generator. On an existing setup, carry forward
monitoring's `--state-root`, `--socket`, `--allowlist`, `--max-duration` and
`--max-events`, plus reporting's `--config`, when set. Keep disabled servers
disabled (`--disabled`), preserve peer-send policy and merge other custom settings
through their owner. Regenerating with defaults must not silently reset an
existing bound, approval choice or path.

Home-bound generators deliberately clear inherited component environment
overrides; merely leaving those variables in the agent's shell does not preserve
an old explicit path. Compare effective arguments, paths, limits and tool policy
with the before record before apply.

These commands **print JSON objects**, not TOML and not live config changes.
Translate the selected `mcp_servers.codex_plus` and `mcp_servers.html_report`
objects into corresponding TOML tables through the configuration owner. Retain
strings, arrays, booleans, nested `env` and tool policy tables; parse the merged
TOML and compare its values with the intended objects. Preserve unrelated tables,
comments and existing explicit permissions. Do not append JSON to `config.toml`
or create duplicate server tables. The official [MCP configuration reference](https://learn.chatgpt.com/docs/extend/mcp)
describes native stdio configuration.

Keep generated required/approval settings subject to existing user policy.
Monitoring's `--allow-peer-send` is an explicit approval opt-in; preserve an
existing choice or explain it when peer communication is requested. It does not
authorize messages by itself. Under a policy that cannot approve a required
operation, report that limitation instead of weakening the policy.

For reporting, preserve an existing endpoint/store. For a fresh local setup,
create only an owned configuration with suitable absolute paths, for example:

```toml
schema = 1
data_root = "/absolute/private/report-store"
server_autostart = false
```

This supports stored reports without a public URL. Configuring a URL reachable
from the viewing desktop is a separate meaningful choice; do not guess a public
bind address, change a firewall or start hosting as an installation check. The
[report reference](https://dev.byebyebryan.com/codex-plus/reports/#configuration-and-hosting) covers owned
tmux hosting and external servers. If requested, install the two
`skills/html-report` files from the verified reporting release using the same
provenance checks as worker skills. It is separate from the four worker skills.

## Verify and finish

Re-run manifest verification, parse affected configuration and compare only the
requested files/selections with the before record. Use the installed doctor with
the correct prefixes/overrides. Its worker-prefix check verifies the retained
release tree; separately compare the copied native agent/skill files with that
manifest and report local modifications. Enabled config and selected files are separate
from tools loaded into an existing conversation. Normal reconnect/fresh native
loading can adopt the selection; do not restart a daemon, globally refresh MCPs
or disrupt active sessions just to report success.

If a fresh session or reported MCP version is checked, state exactly that result.
A manual stdio initialization proves protocol behavior, not native caller
identity, model availability or a successful watch. Report unavailable native
owners or unknown loaded versions plainly. Functional watch/message/report tests
need their own owned scope; installation is not permission to contact peers or
publish real reports.

Return a short receipt with the action and environment, configuration owner,
tag/revision and components selected, verified files/config, loaded version or
unknown, rollback retained, data preserved and any deferred work/reconnect.

## Inspect or change configuration

For inspection, stop after read-only discovery, verification and diagnostics.
Separate missing/disabled components, mismatched selected versions, unavailable
owners, unavailable hosting and unknown loaded code. Do not auto-repair them.
For configuration changes, edit only requested settings through their owner and
verify the rendered result. Use existing context/doctor/report-server status
commands. Do not launch a watch, send a message, enable a disabled skill, rotate
credentials, start hosting or recover a native owner merely to inspect health.

## Roll back

Locate and verify the requested previous revision with its compatible retained
verifier/archive. Through the configuration owner, reselect its immutable code
and previous worker/config version where requested. For unmanaged runtimes the
same package `activate --prefix PREFIX --revision PREVIOUS_REVISION` operations
perform selection. Use the previous release's retained package script when the
current verifier does not support that version. Verify the selected link/files
again. Keep data and journals intact; rollback does not replay pending intent,
migrate state, recover an owner or reload captured processes.

## Clean up installation files

There is no package `prune` command. Inventory precise candidates first:
completed private download staging, verified unused release directories and
owned stale copies. Check the selected links, all environments sharing the
prefix, running MCP/coordinator/report helpers and queued/active Plus work.
A process can still need helper code it has not opened yet: an empty open-file
list or old directory timestamp does not prove a release is unused.

Remove an exact candidate only when its ownership, unchanged content and lack
of active dependencies are established within the cleanup request. Preserve
selected releases and a verified rollback by default. When dependency evidence
is unavailable, retain that release and explain what remains to be checked.
Use the manager's source exclusions/selection rules for managed paths so apply
will not recreate removed files. Never recursively delete a shared Codex home,
skill root, report store or journal root as installation cleanup.

## Uninstall selected components

There is no package `uninstall` command. Identify requested components and all
environments using their files. Through the configuration owner, disable/remove
only their MCP entries, selected wrappers and managed file declarations.
Review affected Plus watches, reminders, MCPs and report helpers before shutdown.
Do not terminate native Codex or unrelated work. If removing a component would
interrupt active work beyond the request, prepare the file changes first and
explain the exact remaining shutdown decision. Defer code deletion while a
captured process or unsettled registration still depends on it.

Remove copied agent/skill files only when their hashes match retained installation
provenance; preserve locally changed or unclassified files and other skills.
Remove only empty owned directories afterward. After dependencies are settled,
remove verified component payloads/links by exact path, accounting for other
environments. Preserve reports, catalogs, journals, original HTML, user config,
credentials and the native client by default. Deleting data requires a separate
explicit request naming its scope. Verify the requested wiring is absent/disabled,
retained data still exists and remaining components/config parse correctly.

## Scope and further references

This guide coordinates the existing release tools. It adds no plugin installer,
service, automatic updater or installed management skill. Website publication,
product releases and deployment remain separate operations. These instructions
do not publish a release, alter another host or upgrade native Codex.

Read the [worker reference](https://dev.byebyebryan.com/codex-plus/workers/), [monitoring release reference](https://dev.byebyebryan.com/codex-plus/installation/),
[report reference](https://dev.byebyebryan.com/codex-plus/reports/), [environment contract](https://dev.byebyebryan.com/codex-plus/environments/)
and [daily-use examples](https://dev.byebyebryan.com/codex-plus/daily-use/) for the selected component.
