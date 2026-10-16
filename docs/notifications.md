# Notification component retired

As of 2026-10-15, notification delivery, config-hook publication and the terminal
relay launcher are retired from Codex Plus. The relay introduced explicit
`--remote` semantics, including disabling empty-prompt Left navigation to
Command Center. Keep native Codex completion and approval notifications.

The retained read-only inspector belongs to the
[349 integration](https://github.com/byebyebryan/esp32-349/blob/main/projects/notification-panel/docs/codex-inspector.md),
with no Codex Plus dependency. Chezmoi owns its pinned distribution. Terminal
notification customization belongs with terminal/dotfile configuration.

The [pre-retirement record](https://github.com/byebyebryan/codex-plus/blob/13d28f7e0db04a7f3fa5415ca02f6d7382d7a055/docs/notifications.md)
is historical evidence, not the current workflow. Historical release artifacts
remain available for rollback and existing processes; they are not selected for
new launches. Monitoring, reports, workers and their installed pins are separate.
