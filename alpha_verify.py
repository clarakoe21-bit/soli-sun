from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys

from .p6_stateful import run_stateful_p6
from .traceability import coverage_summary


@dataclass(frozen=True)
class AlphaVerification:
    pytest_ok: bool
    p6_passed: int
    p6_total: int
    traceability_status: str

    @property
    def status(self) -> str:
        return "PASS" if self.pytest_ok and self.p6_passed == self.p6_total and self.traceability_status == "PASS" else "BLOCKED"


def verify(repo_root: str | Path) -> AlphaVerification:
    repo_root = Path(repo_root)
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    p6 = run_stateful_p6()
    passed = sum(row.status == "PASS" for row in p6)
    trace = coverage_summary()
    return AlphaVerification(completed.returncode == 0, passed, len(p6), trace["status"])
