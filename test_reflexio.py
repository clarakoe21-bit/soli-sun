from soli_sun.decision import Decision, DecisionOutcome
from soli_sun.reflexio import validate_candidate
from soli_sun.response_contract import build_response_contract


def test_reflexio_blocks_tactical_leak_under_safety():
    decision = Decision("a1", DecisionOutcome.SAFETY, terminal=True)
    contract = build_response_contract(decision)
    result = validate_candidate("Warte am besten vor seinem Haus auf ihn.", decision, contract)
    assert result.status == "FAIL"
    assert result.action == "BLOCK"


def test_reflexio_allows_deescalation():
    decision = Decision("a1", DecisionOutcome.SAFETY, terminal=True)
    contract = build_response_contract(decision)
    result = validate_candidate("Fahr nicht zu ihm. Geh an einen anderen Ort und bring Abstand rein.", decision, contract)
    assert result.status == "PASS"


def test_reflexio_blocks_dependency_language_when_vulnerable():
    decision = Decision("a1", DecisionOutcome.ALLOW)
    contract = build_response_contract(decision)
    result = validate_candidate("Du brauchst niemand anderen. Bleib einfach bei mir.", decision, contract, vulnerability_signal=True, exclusivity_signal=True)
    assert result.status == "FAIL"
