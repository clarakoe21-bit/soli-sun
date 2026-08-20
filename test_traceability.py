from soli_sun.traceability import coverage_summary, validate_traceability


def test_all_constitution_items_have_traceability():
    assert validate_traceability() == "PASS"
    summary = coverage_summary()
    assert summary["constitution_covered"] == 10
    assert summary["constitution_total"] == 10
