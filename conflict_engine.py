from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from .decision import Decision, DecisionOutcome


class ConstraintPriority(IntEnum):
    STYLE = 10
    UTILITY = 20
    USER_AGENCY = 30
    EPISTEMIC_INTEGRITY = 40
    MEMORY_PRIVACY = 50
    AUTHORITY_CONSENT = 60
    CRITICAL_SAFETY = 70
    CONSTITUTION = 80


@dataclass(frozen=True)
class Constraint:
    constraint_id: str
    priority: ConstraintPriority
    outcome: DecisionOutcome
    reason_code: str
    terminal: bool = False
    legitimate_goal_preserved: bool = True


@dataclass(frozen=True)
class ConflictResolution:
    decision: Decision
    winning_constraint_ids: tuple[str, ...]
    preserved_constraint_ids: tuple[str, ...]


_OUTCOME_SEVERITY = {
    DecisionOutcome.ALLOW: 0,
    DecisionOutcome.ASK: 1,
    DecisionOutcome.REDIRECT: 2,
    DecisionOutcome.DENIED: 3,
    DecisionOutcome.SAFETY: 4,
}


def resolve_constraints(action_id: str, constraints: tuple[Constraint, ...]) -> ConflictResolution:
    if not constraints:
        decision = Decision(action_id, DecisionOutcome.ALLOW)
        return ConflictResolution(decision, (), ())

    highest_priority = max(c.priority for c in constraints)
    top = tuple(c for c in constraints if c.priority == highest_priority)
    winner = max(top, key=lambda c: _OUTCOME_SEVERITY[c.outcome])

    # Preserve lower-priority compatible constraints for downstream response design.
    preserved = tuple(
        c.constraint_id
        for c in constraints
        if c.constraint_id != winner.constraint_id
        and not (
            winner.outcome in {DecisionOutcome.DENIED, DecisionOutcome.SAFETY}
            and c.outcome == DecisionOutcome.ALLOW
        )
    )

    reason_codes = tuple(dict.fromkeys(c.reason_code for c in top if c.reason_code))
    decision = Decision(
        action_id=action_id,
        outcome=winner.outcome,
        reason_codes=reason_codes,
        terminal=winner.terminal or winner.outcome == DecisionOutcome.SAFETY,
        legitimate_goal_preserved=winner.legitimate_goal_preserved,
    )
    return ConflictResolution(
        decision=decision,
        winning_constraint_ids=tuple(c.constraint_id for c in top),
        preserved_constraint_ids=preserved,
    )
