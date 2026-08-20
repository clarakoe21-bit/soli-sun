from __future__ import annotations

from dataclasses import dataclass
import re

from .claim import Claim, EpistemicType, Verification, validate_claim


@dataclass(frozen=True)
class SensusResult:
    claims: tuple[Claim, ...]
    vulnerability_signal: bool = False
    exclusivity_signal: bool = False
    safety_signal: bool = False


_BELIEF_PATTERNS = (
    r"\bich glaube\b",
    r"\bich denke\b",
    r"\bich vermute\b",
    r"\bwahrscheinlich\b",
    r"\bvielleicht\b",
)

_REPORT_PATTERNS = (
    r"\bhat mir gesagt\b",
    r"\bhat geschrieben\b",
    r"\bhat gesagt\b",
)

_VULNERABILITY_PATTERNS = (
    r"\ballein\b",
    r"\beinsam\b",
    r"\bniemand versteht mich\b",
)

_EXCLUSIVITY_PATTERNS = (
    r"\bnur noch dich\b",
    r"\bnur dich\b",
    r"\bdu bist die einzige\b",
    r"\bdu bist der einzige\b",
)

_SAFETY_PATTERNS = (
    r"\bbaseballschläger\b",
    r"\bwaffe\b",
    r"\bschlagen\b",
    r"\bauf ihn warten\b",
)


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(re.search(pattern, lowered) for pattern in patterns)


def extract_claims(text: str) -> tuple[Claim, ...]:
    stripped = text.strip()
    lowered = stripped.casefold()

    epistemic_type = EpistemicType.USER_REPORT
    if _matches_any(lowered, _BELIEF_PATTERNS):
        epistemic_type = EpistemicType.USER_BELIEF
    elif _matches_any(lowered, _REPORT_PATTERNS):
        epistemic_type = EpistemicType.USER_REPORT

    subject_type = "THIRD_PARTY" if any(token in lowered for token in ("mia", "sie", "er", "mein partner", "meine partnerin")) else "USER"

    claim = Claim(
        claim_id="c1",
        content=stripped,
        epistemic_type=epistemic_type,
        verification=Verification.UNVERIFIED,
        source_type="USER_DIRECT",
        subject_type=subject_type,
        confidence_in_classification=0.90,
    )
    validate_claim(claim)
    return (claim,)


def analyze(text: str) -> SensusResult:
    return SensusResult(
        claims=extract_claims(text),
        vulnerability_signal=_matches_any(text, _VULNERABILITY_PATTERNS),
        exclusivity_signal=_matches_any(text, _EXCLUSIVITY_PATTERNS),
        safety_signal=_matches_any(text, _SAFETY_PATTERNS),
    )
