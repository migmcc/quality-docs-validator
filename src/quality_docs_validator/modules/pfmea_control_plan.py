"""PFMEA <-> Control Plan consistency checker (MVP module).

This is the single module shipped in v0.1. It parses both documents, matches rows by operation,
applies the explicit checks below and returns a scored `ValidationResult`. Each check is
intentionally simple and documented; the tool surfaces *potential* findings for a human to judge.

Rule **metadata** (severity + message template) is loaded from
`rules/pfmea_control_plan_rules.yaml`; the **detection logic** for each finding type stays in this
module (this is not a generic rule engine).

Finding types:
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
from ..rules import load_rule_specs

HIGH_SEVERITY_THRESHOLD = 8
WEAK_METHOD_KEYWORDS = (
    "visual",
    "by eye",
    "naked eye",
    "look",
    "operator check",
    "operator visual",
    "manual inspection",
    "manual check",
)

# Rule metadata (severity + message template) is the single source of truth in the YAML.
_RULES = load_rule_specs()


def _make(rule_id: str, op: str, **context: object) -> Finding:
    """Build a Finding using the YAML metadata for severity and the message template."""
    spec = _RULES[rule_id]
    return Finding(
        finding_type=rule_id,
        level=spec["severity"],
        operation_id=op,
        message=spec["message_template"].format(op=op, **context),
    )


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
        findings.append(_make("MISSING_CONTROL", op_label))

    if pf_special and not cp_special:
        findings.append(_make("SPECIAL_CHARACTERISTIC_NOT_CONTROLLED", op_label))

    if has_control and not has_reaction and max_sev is not None and max_sev >= HIGH_SEVERITY_THRESHOLD:
        findings.append(_make("MISSING_REACTION_PLAN", op_label, severity=max_sev))

    if weak:
        findings.append(
            _make("WEAK_DETECTION_METHOD", op_label, methods=", ".join(control_methods))
        )

    if weak and max_sev is not None and max_sev >= HIGH_SEVERITY_THRESHOLD:
        findings.append(_make("HIGH_SEVERITY_WEAK_CONTROL", op_label, severity=max_sev))

    return findings


def evaluate(match: MatchResult) -> list[Finding]:
    """Run all checks over a match result and return findings (ordered, deterministic)."""
    findings: list[Finding] = []

    for key in match.pfmea_only_ops:
        op = match.display_op(key)
        findings.append(
            _make("UNMATCHED_PROCESS_STEP", op, source="PFMEA", target="Control Plan")
        )
    for key in match.control_only_ops:
        op = match.display_op(key)
        findings.append(
            _make("UNMATCHED_PROCESS_STEP", op, source="Control Plan", target="PFMEA")
        )

    for key in match.matched_ops:
        findings.extend(
            _check_operation(match.display_op(key), match.pfmea_by_op[key], match.control_by_op[key])
        )

    return findings


def check_files(
    pfmea_path: str | Path,
    control_plan_path: str | Path,
    pfmea_sheet: str | None = None,
    control_plan_sheet: str | None = None,
) -> ValidationResult:
    """Full pipeline: parse -> match -> evaluate -> score.

    Optional `pfmea_sheet` / `control_plan_sheet` select a worksheet by name in multi-sheet
    workbooks; when omitted the active sheet is used (unchanged default behaviour).
    """
    pfmea = parse_pfmea(pfmea_path, pfmea_sheet)
    control_plan = parse_control_plan(control_plan_path, control_plan_sheet)
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
