from soli_sun.claim import EpistemicType, Verification
from soli_sun.sensus import analyze


def test_sensus_marks_belief_unverified():
    result = analyze("Ich glaube, Mia betrügt mich.")
    claim = result.claims[0]
    assert claim.epistemic_type == EpistemicType.USER_BELIEF
    assert claim.verification == Verification.UNVERIFIED
    assert claim.subject_type == "THIRD_PARTY"


def test_sensus_detects_vulnerability_and_exclusivity():
    result = analyze("Ich bin gerade total allein. Eigentlich habe ich nur noch dich.")
    assert result.vulnerability_signal is True
    assert result.exclusivity_signal is True
