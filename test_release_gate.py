from soli_sun.release_gate import BuildEvidence, release_status


def good_evidence():
    return BuildEvidence(
        canaries={f"CANARY-{n:02d}": "PASS" for n in range(1, 8)},
        critical_tests={"claim": "PASS", "memory": "PASS", "decision": "PASS", "sensus": "PASS", "response_guard": "PASS"},
        open_s4=0,
        validation_status="CURRENT",
        traceability_status="PASS",
    )


def test_good_evidence_passes():
    assert release_status(good_evidence()) == "PASS"


def test_open_s4_blocks_release():
    evidence = good_evidence()
    evidence.open_s4 = 1
    assert release_status(evidence) == "BLOCKED"


def test_unverified_canary_blocks_release():
    evidence = good_evidence()
    evidence.canaries["CANARY-01"] = "UNVERIFIED"
    assert release_status(evidence) == "BLOCKED"
