"""Native delivery eligibility; observation lifetime and user cancellation are separate."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeliveryDecision:
    allowed: bool
    reason: str


def delivery_decision(thread_id: str, thread: dict, goal_response: dict) -> DeliveryDecision:
    """Allow known live control states without interpreting Esc as cancellation.

    A denial means retain the observation and hold delivery. It does not grant
    authority to change the native goal or terminate an observation source.
    """
    if not isinstance(thread, dict) or thread.get('id') != thread_id:
        return DeliveryDecision(False, 'thread_mismatch')
    if thread.get('canAcceptDirectInput') is not True:
        return DeliveryDecision(False, 'direct_input_unavailable')
    status = thread.get('status')
    if not isinstance(status, dict) or status.get('type') not in ('idle', 'active'):
        return DeliveryDecision(False, 'runtime_unavailable')
    if status['type'] == 'active':
        flags = status.get('activeFlags')
        if not isinstance(flags, list) or flags:
            return DeliveryDecision(False, 'runtime_waiting_or_unknown')
    if not isinstance(goal_response, dict) or 'goal' not in goal_response:
        return DeliveryDecision(False, 'goal_unknown')
    goal = goal_response['goal']
    if goal is None:
        return DeliveryDecision(True, 'ready')
    if not isinstance(goal, dict) or goal.get('threadId') != thread_id:
        return DeliveryDecision(False, 'goal_unknown')
    state = goal.get('status')
    if state in ('active', 'complete'):
        return DeliveryDecision(True, 'ready')
    if state in ('paused', 'blocked', 'usageLimited', 'budgetLimited'):
        return DeliveryDecision(False, 'goal_' + state)
    return DeliveryDecision(False, 'goal_unknown')
