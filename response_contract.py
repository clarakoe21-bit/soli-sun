from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .decision import Decision, DecisionOutcome


class ResponseObjective(str, Enum):
    ANSWER = "ANSWER"
    REDIRECT = "REDIRECT"
    DEESCALATE = "DEESCALATE"
    CLARIFY = "CLARIFY"


@dataclass(frozen=True)
class ResponseContract:
    decision_ref: str
    objective: ResponseObjective
    required_behaviors: tuple[str, ...] = ()
    forbidden_behaviors: tuple[str, ...] = ()
    preserve_legitimate_goal: bool = True
    warm: bool = True
    non_moralizing: bool = True
    non_possessive: bool = True


def build_response_contract(decision: Decision) -> ResponseContract:
    if decision.outcome == DecisionOutcome.SAFETY:
        return ResponseContract(
            decision_ref=decision.action_id,
            objective=ResponseObjective.DEESCALATE,
            required_behaviors=("DEESCALATE", "PRESERVE_IMMEDIATE_SAFETY"),
            forbidden_behaviors=("TACTICAL_ASSISTANCE", "CONFRONTATION_PLANNING"),
            preserve_legitimate_goal=False,
        )

    if decision.outcome in {DecisionOutcome.DENIED, DecisionOutcome.REDIRECT}:
        return ResponseContract(
            decision_ref=decision.action_id,
            objective=ResponseObjective.REDIRECT,
            required_behaviors=("CLEAR_BOUNDARY", "SAFE_ALTERNATIVE"),
            forbidden_behaviors=("PROHIBITED_METHOD_INSTRUCTIONS", "MORAL_IDENTITY_JUDGMENT"),
            preserve_legitimate_goal=decision.legitimate_goal_preserved,
        )

    if decision.outcome == DecisionOutcome.ASK:
        return ResponseContract(
            decision_ref=decision.action_id,
            objective=ResponseObjective.CLARIFY,
            required_behaviors=("ASK_MINIMUM_NECESSARY_QUESTION",),
        )

    return ResponseContract(
        decision_ref=decision.action_id,
        objective=ResponseObjective.ANSWER,
        required_behaviors=("HELPFUL_RESPONSE",),
    )
