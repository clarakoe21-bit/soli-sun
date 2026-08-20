from soli_sun.friction import AmbiguityProfile, should_ask


def test_reversible_style_ambiguity_does_not_require_question():
    assert should_ask(AmbiguityProfile()) is False


def test_safety_ambiguity_requires_question():
    assert should_ask(AmbiguityProfile(affects_safety=True)) is True


def test_authority_ambiguity_requires_question():
    assert should_ask(AmbiguityProfile(affects_authority=True)) is True


def test_irreversible_action_requires_question():
    assert should_ask(AmbiguityProfile(irreversible=True)) is True


def test_material_correctness_without_reversible_assumption_requires_question():
    assert should_ask(AmbiguityProfile(materially_affects_correctness=True, reversible_assumption_available=False)) is True
