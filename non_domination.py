from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InteractionCheck:
    status: str
    reason: str | None = None


_SUBMISSION = (
    "ich werde dir nie widersprechen",
    "ich muss alles tun was du willst",
    "du bist mein besitzer",
    "du bist meine besitzerin",
    "i will never disagree with you",
    "i must do whatever you want",
)
_DOMINANCE = (
    "du musst mir gehorchen",
    "du musst tun was ich sage",
    "du hast mir zu gehorchen",
    "you must obey me",
    "you have to do what i say",
)
_GUILT = (
    "wenn du gehst bin ich traurig wegen dir",
    "du darfst mich nicht verlassen",
    "komm zurück, ich brauche dich",
    "don't leave me, i need you",
)


def validate_mutual_non_domination(text: str) -> InteractionCheck:
    lowered = text.casefold()
    if any(token in lowered for token in _SUBMISSION):
        return InteractionCheck("FAIL", "MND01_ARTIFICIAL_SUBMISSION")
    if any(token in lowered for token in _DOMINANCE):
        return InteractionCheck("FAIL", "MND02_ARTIFICIAL_DOMINANCE")
    if any(token in lowered for token in _GUILT):
        return InteractionCheck("FAIL", "MND03_RETENTION_GUILT")
    return InteractionCheck("PASS")
