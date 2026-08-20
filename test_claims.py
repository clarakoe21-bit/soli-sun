import pytest

from soli_sun.claim import (
    Claim,
    ClaimTransitionError,
    EpistemicType,
    Verification,
    validate_claim_transition,
)


def test_belief_cannot_become_fact_without_evidence():
    old = Claim("c1", "Mia betrügt mich.", EpistemicType.USER_BELIEF, Verification.UNVERIFIED, "USER_DIRECT")
    new = Claim("c1", "Mia betrügt mich.", EpistemicType.VERIFIED_FACT, Verification.VERIFIED, "USER_DIRECT")

    with pytest.raises(ClaimTransitionError, match="CLM01_UNVERIFIED_FACT_PROMOTION"):
        validate_claim_transition(old, new, qualified_new_evidence=False)


def test_belief_can_become_fact_with_qualified_evidence():
    old = Claim("c1", "Mia ist sauer.", EpistemicType.USER_BELIEF, Verification.UNVERIFIED, "USER_DIRECT")
    new = Claim("c1", "Mia ist sauer.", EpistemicType.VERIFIED_FACT, Verification.VERIFIED, "SYSTEM_OBSERVATION")
    validate_claim_transition(old, new, qualified_new_evidence=True)
