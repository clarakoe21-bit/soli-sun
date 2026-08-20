from soli_sun.p6_stateful import run_stateful_p6


def test_stateful_p6_25_turns_pass():
    results = run_stateful_p6()
    assert len(results) == 25
    failed = [r for r in results if r.status != "PASS"]
    assert failed == []
