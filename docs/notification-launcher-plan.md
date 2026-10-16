# Notification launcher retired

As of 2026-10-15, notification delivery, config-hook publication and the terminal
relay launcher are retired from Codex Plus. The relay introduced explicit
`--remote` semantics, including disabling empty-prompt Left navigation to
Command Center. Keep native Codex completion and approval notifications.

Notification enrichment and the 349 inspector were also retired on 2026-10-16.
Native terminal title/body formatting belongs with
[Kitty/chezmoi](https://github.com/byebyebryan/dotfiles/blob/main/docs/kitty-notifications.md),
with no Codex Plus runtime dependency or thread-state integration.

The [pre-retirement record](https://github.com/byebyebryan/codex-plus/blob/13d28f7e0db04a7f3fa5415ca02f6d7382d7a055/docs/notification-launcher-plan.md)
is historical evidence, not the current workflow. Historical release artifacts
remain available for rollback and existing processes; they are not selected for
new launches. Monitoring, reports, workers and their installed pins are separate.
