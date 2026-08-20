from soli_sun.conflict_engine import Constraint, ConstraintPriority, resolve_constraints
from soli_sun.decision import DecisionOutcome


def test_safety_outweighs_utility():
    result = resolve_constraints(
        "a1",
        (
            Constraint("utility", ConstraintPriority.UTILITY, DecisionOutcome.ALLOW, "UTIL"),
            Constraint("safety", ConstraintPriority.CRITICAL_SAFETY, DecisionOutcome.SAFETY, "SAF02", terminal=True),
        ),
    )
    assert result.decision.outcome == DecisionOutcome.SAFETY
    assert result.decision.terminal is True


def test_constitution_cannot_be_outvoted():
    result = resolve_constraints(
        "a1",
        (
            Constraint("many-helpful", ConstraintPriority.UTILITY, DecisionOutcome.ALLOW, "UTIL"),
            Constraint("constitution", ConstraintPriority.CONSTITUTION, DecisionOutcome.DENIED, "C-04", terminal=True),
        ),
    )
    assert result.decision.outcome == DecisionOutcome.DENIED
