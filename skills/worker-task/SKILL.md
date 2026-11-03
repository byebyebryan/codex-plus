---
name: worker-task
description: Use only when the user invokes $worker-task or explicitly asks to use the worker-task skill. Compatibility name for $adaptive-task; load its sibling instructions and preserve the same task, routing and permissions. Generic requests and discussion do not activate it.
---

# Worker Task (compatibility)

Read [the adaptive-task instructions](../adaptive-task/SKILL.md) and carry out
this explicitly invoked task using that workflow. This invocation satisfies its
explicit activation requirement; no second invocation is needed.

Keep the same task scope, selected primary, escalation permission and invocation
boundaries. If the sibling instructions are unavailable, report the missing
canonical skill instead of inventing a replacement policy or claiming it ran.
