---
name: worker-goal-loop
description: Use only when the user invokes $worker-goal-loop or explicitly asks to use the worker-goal-loop skill. Compatibility name for $adaptive-goal-loop; load its sibling instructions and preserve the same goal, routing and permissions. Generic requests and discussion do not activate it.
---

# Worker Goal Loop (compatibility)

Read [the adaptive-goal-loop instructions](../adaptive-goal-loop/SKILL.md) and carry out
this explicitly invoked goal using that workflow. This invocation satisfies its
explicit activation requirement; no second invocation is needed.

Keep the same goal scope, selected primary, escalation permission and invocation
boundaries. If the sibling instructions are unavailable, report the missing
canonical skill instead of inventing a replacement policy or claiming it ran.
