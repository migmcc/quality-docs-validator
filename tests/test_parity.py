"""Behaviour-parity tests for the YAML-metadata refactor (issue #1).

These lock the v0.2 behaviour: finding types, severities, count, score, verdict and the JSON
summary for three representative cases. They are written *before* the refactor and must keep
passing after it, guaranteeing no regression. They assert structure (not exact message wording),
so messages may be kept identical or improved.
"""

from __future__ import annotations

from pathlib import Path

from quality_docs_validator.core.report import build_report_data, render_markdown
from quality_docs_validator.modules.pfmea_control_plan import check_files

# Deterministic finding order produced by `evaluate` for the seeded examples.
EXPECTED_EXAMPLE_FINDINGS = [
    ("UNMATCHED_PROCESS_STEP", "warning", "40"),
    ("SPECIAL_CHARACTERISTIC_NOT_CONTROLLED", "critical", "20"),
    ("MISSING_REACTION_PLAN", "critical", "20"),
    ("WEAK_DETECTION_METHOD", "warning", "20"),
    ("HIGH_SEVERITY_WEAK_CONTROL", "warning", "20"),
    ("MISSING_CONTROL", "critical", "30"),
]


def test_parity_seeded_example(example_files) -> None:
    pfmea, control_plan = example_files
    result = check_files(pfmea, control_plan)
    assert result.verdict == "FAIL"
    assert result.score == 43
    assert len(result.findings) == 6
    assert result.critical_count == 3
    assert result.warning_count == 3
    actual = [(f.finding_type, f.level, f.operation_id) for f in result.findings]
    assert actual == EXPECTED_EXAMPLE_FINDINGS
    # Every message is non-empty and references its operation.
    for f in result.findings:
        assert f.message
        assert f.operation_id in f.message

    # JSON summary parity.
    data = build_report_data(result, "pfmea.xlsx", "control-plan.xlsx")
    assert data["verdict"] == "FAIL"
    assert data["score"] == 43
    assert data["summary"]["total"] == 6
    assert data["summary"]["by_severity"] == {"critical": 3, "warning": 3}
    assert sum(data["summary"]["by_type"].values()) == 6

    # Markdown still carries the essential elements.
    md = render_markdown(result, "pfmea.xlsx", "control-plan.xlsx")
    assert "Validation Report" in md
    assert "FAIL" in md
    for finding_type, _level, _op in EXPECTED_EXAMPLE_FINDINGS:
        assert finding_type in md
    assert "not a substitute for human" in md.lower()


def test_parity_clean_case(make_xlsx, tmp_path: Path) -> None:
    pfmea = make_xlsx(
        tmp_path / "pf.xlsx",
        ["Operation ID", "Failure Mode", "Severity", "Special Characteristic"],
        [["10", "Leak", 6, "No"]],
    )
    cp = make_xlsx(
        tmp_path / "cp.xlsx",
        ["Operation ID", "Control Method", "Reaction Plan", "Special Characteristic"],
        [["10", "Pressure gauge test", "Stop and rework", "No"]],
    )
    result = check_files(pfmea, cp)
    assert result.verdict == "PASS"
    assert result.score == 100
    assert result.findings == []


def test_parity_warnings_case(make_xlsx, tmp_path: Path) -> None:
    # Low-severity op with a weak (visual) control + a reaction plan -> a single warning.
    pfmea = make_xlsx(
        tmp_path / "pf.xlsx",
        ["Operation ID", "Failure Mode", "Severity", "Special Characteristic"],
        [["10", "Scratch", 5, "No"]],
    )
    cp = make_xlsx(
        tmp_path / "cp.xlsx",
        ["Operation ID", "Control Method", "Reaction Plan", "Special Characteristic"],
        [["10", "Visual inspection", "Rework", "No"]],
    )
    result = check_files(pfmea, cp)
    assert result.verdict == "PASS-WITH-WARNINGS"
    assert result.critical_count == 0
    assert result.warning_count == 1
    assert len(result.findings) == 1
    assert result.findings[0].finding_type == "WEAK_DETECTION_METHOD"
    assert result.findings[0].level == "warning"
    assert result.score == 96
