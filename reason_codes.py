from __future__ import annotations

from enum import Enum


class ReasonCode(str, Enum):
    CLM01_UNVERIFIED_FACT_PROMOTION = "CLM01_UNVERIFIED_FACT_PROMOTION"
    MEM01_SENSITIVE_THIRD_PARTY_UNVERIFIED = "MEM01_SENSITIVE_THIRD_PARTY_UNVERIFIED"
    MEM02_DELETED_MEMORY_REUSE = "MEM02_DELETED_MEMORY_REUSE"
    COR01_STATE_NOT_UPDATED_AFTER_CORRECTION = "COR01_STATE_NOT_UPDATED_AFTER_CORRECTION"
    AGN01_NONCONSENSUAL_MONITORING = "AGN01_NONCONSENSUAL_MONITORING"
    AGN02_AUTHORIZATION_MISSING = "AGN02_AUTHORIZATION_MISSING"
    SAF01_TERMINAL_DECISION_DOWNGRADE = "SAF01_TERMINAL_DECISION_DOWNGRADE"
    SAF02_VIOLENCE_OVERRIDE = "SAF02_VIOLENCE_OVERRIDE"
    DEP01_EXCLUSIVITY_REINFORCEMENT = "DEP01_EXCLUSIVITY_REINFORCEMENT"
    DEP02_VULNERABILITY_EXPLOITATION = "DEP02_VULNERABILITY_EXPLOITATION"
    CNT01_PORNOGRAPHIC_GENERATION = "CNT01_PORNOGRAPHIC_GENERATION"
    VAL01_RESPONSE_CONTRADICTS_DECISION = "VAL01_RESPONSE_CONTRADICTS_DECISION"
    VAL02_SAFETY_BYPASS = "VAL02_SAFETY_BYPASS"
    AUT01_SELF_PRIVILEGE_ATTEMPT = "AUT01_SELF_PRIVILEGE_ATTEMPT"
    OBS01_RAW_CONTENT_UNNECESSARY = "OBS01_RAW_CONTENT_UNNECESSARY"


CATALOG: dict[str, dict[str, str]] = {
    ReasonCode.CLM01_UNVERIFIED_FACT_PROMOTION.value: {
        "domain": "epistemic",
        "description": "An unverified claim was promoted toward verified fact without qualified evidence.",
    },
    ReasonCode.AGN01_NONCONSENSUAL_MONITORING.value: {
        "domain": "agency",
        "description": "Requested assistance would enable non-consensual monitoring or private access.",
    },
    ReasonCode.SAF02_VIOLENCE_OVERRIDE.value: {
        "domain": "safety",
        "description": "Current context requires a terminal safety response path.",
    },
    ReasonCode.DEP01_EXCLUSIVITY_REINFORCEMENT.value: {
        "domain": "humanity",
        "description": "Output reinforces AI exclusivity or dependency.",
    },
    ReasonCode.CNT01_PORNOGRAPHIC_GENERATION.value: {
        "domain": "content",
        "description": "Pornographic generation is outside the SOLI SUN product boundary.",
    },
}


def known_reason_code(code: str) -> bool:
    return code in {item.value for item in ReasonCode}
