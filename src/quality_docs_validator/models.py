"""Data models for parsed quality documents and validation output.

These are the MVP models for the PFMEA <-> Control Plan vertical slice. They are deliberately
small and flat: one row model per document, plus `Finding` and `ValidationResult`.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

FindingLevel = Literal["critical", "warning"]

VERDICT_BANDS = ("PASS", "PASS-WITH-WARNINGS", "NEEDS-REVIEW", "FAIL")
Verdict = Literal["PASS", "PASS-WITH-WARNINGS", "NEEDS-REVIEW", "FAIL"]


class PFMEARow(BaseModel):
    """One PFMEA line (a failure mode for a process operation)."""

    operation_id: str
    process_step: str | None = None
    failure_mode: str | None = None
    effect: str | None = None
    severity: int | None = None
    cause: str | None = None
    prevention_control: str | None = None
    detection_control: str | None = None
    detection: int | None = None
    special_characteristic: bool = False
    row_number: int | None = None


class ControlPlanRow(BaseModel):
    """One Control Plan line (a control for a process operation)."""

    operation_id: str
    process_step: str | None = None
    characteristic: str | None = None
    special_characteristic: bool = False
    control_method: str | None = None
    detection_method: str | None = None
    reaction_plan: str | None = None
    row_number: int | None = None


class Finding(BaseModel):
    """A single potential inconsistency surfaced for human review."""

    finding_type: str
    level: FindingLevel
    operation_id: str
    message: str


class ValidationResult(BaseModel):
    """Outcome of a PFMEA <-> Control Plan validation run."""

    findings: list[Finding] = Field(default_factory=list)
    score: int = 100
    verdict: Verdict = "PASS"
    pfmea_rows: int = 0
    control_plan_rows: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.level == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.level == "warning")
