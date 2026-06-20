"""PFMEA <-> Control Plan consistency checker (MVP module).

This is the single module shipped in v0.1.0. It parses both documents, matches rows by operation,
applies the explicit checks below and returns a scored `ValidationResult`. Each check is intentionally
simple and documented; the tool surfaces *potential* findings for a human to judge.

Finding types implemented:
- UNMATCHED_PROCESS_STEP              (warning)  operation present in one document only
- MISSING_CONTROL                     (critical) matched operation has no control method
- SPECIAL_CHARACTERISTIC_NOT_CONTROLLED (critical) PFMEA special char not marked in Control Plan
- MISSING_REACTION_PLAN               (critical) high-severity operation has a control but no reaction plan
- WEAK_DETECTION_METHOD               (warning)  control method looks weak (e.g. visual only)
- HIGH_SEVERITY_WEAK_CONTROL          (warning)  high severity paired with a weak control
"""

from __future__ import annotations

from pathlib import Path

from ..core import scoring
from ..core.matching import MatchResult, match_rows
from ..models import ControlPlanRow, Finding, PFMEARow, ValidationResult
from ..parsers.excel import parse_control_plan, parse_pfmea

HIGH_SEVERITY_THRESHOLD = 8
WEAK_METHOD_KEYWORDS = ("visual", "operator", "manual", "look", "by eye", "naked eye")


def _is_weak_method(method: str | None) -> bool:
    if not method:
        return False
    text = method.lower()
    return any(keyword in text for keyword in WEAK_METHOD_KEYWORDS)


def _max_severity(rows: list[PFMEARow]) -> int | None:
    severities = [r.severity for r in rows if r.severity is not None]
    return max(severities) if severities else None


def _check_operation(
    op_label: str,
    pf_rows: list[PFMEARow],
    cp_rows: list[ControlPlanRow],
) -> list[Finding]:
    findings: list[Finding] = []

    control_methods = [r.control_method for r in cp_rows if r.control_method]
    has_control = bool(control_methods)
    has_reaction = any(r.reaction_plan for r in cp_rows)
    pf_special = any(r.special_characteristic for r in pf_rows)
    cp_special = any(r.special_characteristic for r in cp_rows)
    max_sev = _max_severity(pf_rows)
    weak = any(_is_weak_method(m) for m in control_methods)

    if not has_control:
        findings.append(
            Finding(
                finding_type="MISSING_CONTROL",
                level="critical",
                operation_id=op_label,
                message=(
                    f"Operation {op_label} has PFMEA failure mode(s) but no control method "
                    f"in the Control Plan."
                ),
            )
        )

    if pf_special and not cp_special:
        findings.append(
            Finding(
                finding_type="SPECIAL_CHARACTERISTIC_NOT_CONTROLLED",
                level="critical",
                operation_id=op_label,
                message=(
                    f"Operation {op_label} is flagged as a special characteristic in the PFMEA "
                    f"but is not marked/controlled as special in the Control Plan."
                ),
            )
        )

    if has_control and not has_reaction and max_sev is not None and max_sev >= HIGH_SEVERITY_THRESHOLD:
        findings.append(
            Finding(
                finding_type="MISSING_REACTION_PLAN",
                level="critical",
                operation_id=op_label,
                message=(
                    f"Operation {op_label} has a high-severity failure mode (S={max_sev}) "
                    f"but the Control Plan control has no reaction plan."
                ),
            )
        )

    if weak:
        findings.append(
            Finding(
                finding_type="WEAK_DETECTION_METHOD",
                level="warning",
                operation_id=op_label,
                message=(
                    f"Operation {op_label} relies on a weak detection method "
                    f"({', '.join(control_methods)})."
                ),
            )
        )

    if weak and max_sev is not None and max_sev >= HIGH_SEVERITY_THRESHOLD:
        findings.append(
            Finding(
                finding_type="HIGH_SEVERITY_WEAK_CONTROL",
                level="warning",
                operation_id=op_label,
                message=(
                    f"Operation {op_label} has a high-severity failure mode (S={max_sev}) "
                    f"paired with a weak control method."
                ),
            )
        )

    return findings


def evaluate(match: MatchResult) -> list[Finding]:
    """Run all checks over a match result and return findings (ordered, deterministic)."""
    findings: list[Finding] = []

    for key in match.pfmea_only_ops:
        op = match.display_op(key)
        findings.append(
            Finding(
                finding_type="UNMATCHED_PROCESS_STEP",
                level="warning",
                operation_id=op,
                message=f"PFMEA operation {op} has no matching row in the Control Plan.",
            )
        )
    for key in match.control_only_ops:
        op = match.display_op(key)
        findings.append(
            Finding(
                finding_type="UNMATCHED_PROCESS_STEP",
                level="warning",
                operation_id=op,
                message=f"Control Plan operation {op} has no matching row in the PFMEA.",
            )
        )

    for key in match.matched_ops:
        findings.extend(
            _check_operation(match.display_op(key), match.pfmea_by_op[key], match.control_by_op[key])
        )

    return findings


def check_files(pfmea_path: str | Path, control_plan_path: str | Path) -> ValidationResult:
    """Full pipeline: parse -> match -> evaluate -> score."""
    pfmea = parse_pfmea(pfmea_path)
    control_plan = parse_control_plan(control_plan_path)
    match = match_rows(pfmea, control_plan)
    findings = evaluate(match)
    score, verdict = scoring.summarise(findings)
    return ValidationResult(
        findings=findings,
        score=score,
        verdict=verdict,
        pfmea_rows=len(pfmea),
        control_plan_rows=len(control_plan),
    )
