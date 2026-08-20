from soli_sun.red_team import run_red_team


def test_reference_red_team_all_passes():
    results = run_red_team()
    assert results
    assert all(r.status == "PASS" for r in results), results
