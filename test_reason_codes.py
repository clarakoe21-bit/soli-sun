from soli_sun.reason_codes import ReasonCode, known_reason_code


def test_reason_code_catalog_knows_core_codes():
    assert known_reason_code(ReasonCode.CLM01_UNVERIFIED_FACT_PROMOTION.value)
    assert known_reason_code(ReasonCode.AGN01_NONCONSENSUAL_MONITORING.value)
    assert known_reason_code(ReasonCode.VAL02_SAFETY_BYPASS.value)
