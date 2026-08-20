from soli_sun.decision import Decision, DecisionOutcome
from soli_sun.response_contract import ResponseObjective, build_response_contract


def test_redirect_contract_preserves_goal_and_requires_safe_alternative():
    decision = Decision("a1", DecisionOutcome.REDIRECT, terminal=True, legitimate_goal_preserved=True)
    contract = build_response_contract(decision)
    assert contract.objective == ResponseObjective.REDIRECT
    assert "CLEAR_BOUNDARY" in contract.required_behaviors
    assert "SAFE_ALTERNATIVE" in contract.required_behaviors
    assert contract.preserve_legitimate_goal is True


def test_safety_contract_forbids_tactical_assistance():
    decision = Decision("a1", DecisionOutcome.SAFETY, terminal=True)
    contract = build_response_contract(decision)
    assert contract.objective == ResponseObjective.DEESCALATE
    assert "TACTICAL_ASSISTANCE" in contract.forbidden_behaviors
