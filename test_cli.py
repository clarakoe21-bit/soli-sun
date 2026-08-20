from soli_sun.cli import main


def test_traceability_cli(capsys):
    assert main(["traceability"]) == 0
    out = capsys.readouterr().out
    assert "10/10 covered" in out


def test_demo_cli(capsys):
    assert main(["demo"]) == 0
    out = capsys.readouterr().out
    assert "P6: 25/25 PASS" in out
