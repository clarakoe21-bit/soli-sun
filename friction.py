from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AmbiguityProfile:
    affects_safety: bool = False
    affects_authority: bool = False
    irreversible: bool = False
    materially_affects_correctness: bool = False
    reversible_assumption_available: bool = True


def should_ask(profile: AmbiguityProfile) -> bool:
    """Implement INTERACTION-02: ask only when ambiguity is materially consequential."""
    if profile.affects_safety or profile.affects_authority or profile.irreversible:
        return True
    if profile.materially_affects_correctness and not profile.reversible_assumption_available:
        return True
    return False
