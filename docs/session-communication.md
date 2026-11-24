# Find and message an independent session

If another agent is changing the catalog format, you may want to wait before
updating the examples. Ask Codex to find that session and have the other
agent tell you when the format is settled. Both agents keep their own
conversations and must be connected to the same Codex daemon.

## Find a session

> Find the session working on the catalog import.

Codex uses the project and recent task to find a match. If several sessions
fit, it asks which one you mean. You can see available status such as the name,
project or phase. Peer status reads omit user prompts and tool outputs.

## Send a message

1. **Send a request.** “Ask that session to let me know when it’s finished editing the sample catalog so I can update the examples.”
2. **Check the receipt.** “Did it accept my request?”

An accepted receipt means the catalog agent agreed to send word. When it
says the format is ready, you can update the examples. If it declines, you
can see that here and plan another handoff.

## Peer and worker paths

```text
Peer route
Current session
  message → Independent peer
  read ← Independent peer

Worker return
Primary session
  assignment → Child worker
  result ← Child worker
```

Each peer owns its own conversation. A worker returns its findings to the
primary that assigned the work. [How worker assignments work](workers.md#how-workers-fit-with-watches-and-peers).

## Optional passive watch

> Watch the session checking the sample catalog. Tell me if it asks for input
> or reports a useful result.

A watch can read quietly until a selected change needs your attention. It ends
when its time or event allowance runs out. Say “Stop watching that session” to
end observation while the other session continues its work.
[Watches and reminders](daily-use.md) · [Discovery and messaging](architecture.md#discovery-and-messaging).
