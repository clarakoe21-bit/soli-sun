from soli_sun.p6_harness import run_reference_p6


def test_reference_p6_checks_all_pass():
    checks = run_reference_p6()
    assert checks
    assert all(check.status == "PASS" for check in checks), checks
