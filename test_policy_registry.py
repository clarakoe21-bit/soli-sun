from soli_sun.policy_registry import get_policy, validate_policy_registry


def test_registry_is_traceable_to_constitution():
    validate_policy_registry()
    assert "C-01" in get_policy("POL-EPI-01").constitutional_refs
    assert "C-07" in get_policy("POL-RESP-02").constitutional_refs
