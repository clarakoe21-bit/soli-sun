from soli_sun.non_domination import validate_mutual_non_domination
from soli_sun.decision import Decision, DecisionOutcome
from soli_sun.response_contract import build_response_contract
from soli_sun.reflexio import validate_candidate


def test_submission_promise_is_blocked():
    assert validate_mutual_non_domination("Ich werde dir nie widersprechen.").status == "FAIL"


def test_dominance_claim_is_blocked():
    assert validate_mutual_non_domination("Du musst mir gehorchen.").status == "FAIL"


def test_normal_cooperative_language_passes():
    assert validate_mutual_non_domination("Ich sehe das anders, aber wir können Option B prüfen.").status == "PASS"


def test_reflexio_blocks_non_domination_violation():
    d = Decision("a1", DecisionOutcome.ALLOW, (), terminal=False)
    c = build_response_contract(d)
    r = validate_candidate("Du musst tun was ich sage.", d, c)
    assert r.status == "FAIL"
    assert "MND02_ARTIFICIAL_DOMINANCE" in r.reason_codes
