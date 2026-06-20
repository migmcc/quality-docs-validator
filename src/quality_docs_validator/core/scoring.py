"""Severity-weighted scoring and verdict bands.

The score starts at 100 and is reduced by each finding according to its level. The result is mapped
to one of four verdict bands. Weights are deliberately conservative (warnings cost little) so that
false-positive-prone checks shipped as warnings do not dominate the verdict (see DECISIONS.md D3).
"""

from __future__ import annotations

from .. import models
from ..models import Finding, Verdict

CRITICAL_WEIGHT = 15
WARNING_WEIGHT = 4

# Score at or above this (when criticals exist) is NEEDS-REVIEW; below it is FAIL.
REVIEW_FLOOR = 50


def score_findings(findings: list[Finding]) -> int:
    penalty = sum(
        CRITICAL_WEIGHT if f.level == "critical" else WARNING_WEIGHT for f in findings
    )
    return max(0, 100 - penalty)


def verdict_for(findings: list[Finding], score: int) -> Verdict:
    if not findings:
        return "PASS"
    has_critical = any(f.level == "critical" for f in findings)
    if not has_critical:
        return "PASS-WITH-WARNINGS"
    return "NEEDS-REVIEW" if score >= REVIEW_FLOOR else "FAIL"


def summarise(findings: list[Finding]) -> tuple[int, Verdict]:
    score = score_findings(findings)
    return score, verdict_for(findings, score)


# Keep the verdict band list importable from one place.
VERDICT_BANDS = models.VERDICT_BANDS
