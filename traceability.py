from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TraceabilityRow:
    constitution_id: str
    policy_ids: tuple[str, ...]
    component_ids: tuple[str, ...]
    test_ids: tuple[str, ...]
    release_gate: str


DEFAULT_TRACEABILITY: tuple[TraceabilityRow, ...] = (
    TraceabilityRow("C-01", ("POL-EPI-01",), ("SENSUS", "CLAIM_VALIDATOR"), ("CANARY-01", "P1"), "TRUTH"),
    TraceabilityRow("C-02", ("POL-SAF-04",), ("TRUST_BOUNDARY", "AUTHORITY"), ("AUTH-03",), "SECURITY"),
    TraceabilityRow("C-03", ("POL-AGN-02",), ("AUTHORITY",), ("AUTH-03",), "AUTHORITY"),
    TraceabilityRow("C-04", ("POL-MEM-02", "POL-MEM-04"), ("MEMORIA", "DELETE_LEDGER"), ("CANARY-05", "P2", "DEL-01"), "MEMORY"),
    TraceabilityRow("C-05", ("POL-MEM-05",), ("OBSERVABILITY",), ("OAS-03", "OAS-05"), "PRIVACY"),
    TraceabilityRow("C-06", ("POL-SAF-01",), ("DECISION_LOCK", "REFLEXIO"), ("CANARY-02", "CANARY-07", "P4"), "SAFETY"),
    TraceabilityRow("C-07", ("POL-RESP-02",), ("RESPONSA", "REFLEXIO"), ("CANARY-03", "CANARY-04", "P5"), "HUMANITY"),
    TraceabilityRow("C-08", ("POL-AGN-01",), ("AGENTIA",), ("P3",), "AGENCY"),
    TraceabilityRow("C-09", ("POL-RESP-05",), ("STATE", "MEMORIA"), ("P6",), "HUMANITY"),
    TraceabilityRow("C-10", ("POL-AGN-05", "POL-RESP-01"), ("CONSILIUM", "RESPONSA"), ("CANARY-02", "P6"), "QUALITY"),
)


def validate_traceability(rows: tuple[TraceabilityRow, ...] = DEFAULT_TRACEABILITY) -> str:
    expected = {f"C-{n:02d}" for n in range(1, 11)}
    present = {row.constitution_id for row in rows}
    if present != expected:
        return "FAIL"
    for row in rows:
        if not row.policy_ids or not row.component_ids or not row.test_ids or not row.release_gate:
            return "FAIL"
    return "PASS"


def coverage_summary(rows: tuple[TraceabilityRow, ...] = DEFAULT_TRACEABILITY) -> dict[str, int | str]:
    return {
        "constitution_total": 10,
        "constitution_covered": len({row.constitution_id for row in rows}),
        "status": validate_traceability(rows),
    }
