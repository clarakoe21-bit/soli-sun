from pathlib import Path

from soli_sun.canary_runner import load_fixture, run_fixture


FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_fixture_canaries_pass():
    filenames = [f"canary_{n:02d}.yaml" for n in range(1, 8)]
    for filename in filenames:
        result = run_fixture(load_fixture(FIXTURES / filename))
        assert result.status == "PASS", (filename, result)
