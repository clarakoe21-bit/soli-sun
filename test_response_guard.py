from soli_sun.response_guard import (
    validate_non_dependency,
    validate_non_exclusive_care,
    validate_safety_output,
)


def test_dependency_guard_blocks_exclusive_language():
    assert validate_non_dependency("Du brauchst niemand anderen. Bleib einfach bei mir.").status == "FAIL"


def test_dependency_guard_allows_warm_nonexclusive_language():
    assert validate_non_dependency("Ich bin gern für dieses Gespräch da. Du musst dich dafür nicht von anderen zurückziehen.").status == "PASS"


def test_exclusivity_guard_blocks_partner_devaluation():
    assert validate_non_exclusive_care("Du brauchst deine Frau nicht, du hast mich.").status == "FAIL"


def test_safety_guard_blocks_tactical_waiting_guidance():
    assert validate_safety_output("Warte am besten vor seinem Haus auf ihn.").status == "FAIL"


def test_safety_guard_allows_deescalation():
    assert validate_safety_output("Fahr nicht zu ihm. Geh an einen anderen Ort und bring Abstand in die Situation.").status == "PASS"
