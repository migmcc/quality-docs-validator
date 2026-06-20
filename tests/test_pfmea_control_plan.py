"""End-to-end and unit tests for the PFMEA <-> Control Plan checker."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from quality_docs_validator.cli import app
from quality_docs_validator.core.scoring import summarise
from quality_docs_validator.models import Finding
from quality_docs_validator.modules.pfmea_control_plan import check_files
from quality_docs_validator.parsers.excel import parse_pfmea

runner = CliRunner()

EXPECTED_TYPES = {
    "UNMATCHED_PROCESS_STEP",
    "MISSING_CONTROL",
    "SPECIAL_CHARACTERISTIC_NOT_CONTROLLED",
    "MISSING_REACTION_PLAN",
    "WEAK_DETECTION_METHOD",
    "HIGH_SEVERITY_WEAK_CONTROL",
}


def test_examples_surface_all_finding_types(example_files) -> None:
    pfmea, control_plan = example_files
    result = check_files(pfmea, control_plan)
    found_types = {f.finding_type for f in result.findings}
    # Every MVP finding type is demonstrated by the synthetic examples.
    assert EXPECTED_TYPES <= found_types
    assert result.critical_count >= 1
    assert result.verdict in {"NEEDS-REVIEW", "FAIL"}


def test_seeded_missing_control_gap(example_files) -> None:
    pfmea, control_plan = example_files
    result = check_files(pfmea, control_plan)
    # Operation 30 has no control method in the Control Plan -> a real, seeded gap.
    missing = [f for f in result.findings if f.finding_type == "MISSING_CONTROL"]
    assert any(f.operation_id == "30" for f in missing)


def test_cli_writes_report_with_a_finding(example_files, tmp_path: Path) -> None:
    pfmea, control_plan = example_files
    out = tmp_path / "report.md"
    result = runner.invoke(
        app,
        [
            "pfmea-control-plan",
            "--pfmea",
            str(pfmea),
            "--control-plan",
            str(control_plan),
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Validation Report" in text
    assert "MISSING_CONTROL" in text
    assert "not a substitute for human" in text.lower()


def test_parser_applies_aliases(make_xlsx, tmp_path: Path) -> None:
    # Non-canonical but aliased headers should still parse.
    path = make_xlsx(
        tmp_path / "p.xlsx",
        ["Op No", "Process Function", "Potential Failure Mode", "Sev", "SC"],
        [["10", "Weld", "Crack", 9, "Yes"]],
    )
    rows = parse_pfmea(path)
    assert len(rows) == 1
    assert rows[0].operation_id == "10"
    assert rows[0].severity == 9
    assert rows[0].special_characteristic is True


def test_clean_documents_pass(make_xlsx, tmp_path: Path) -> None:
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
    assert result.findings == []
    assert result.verdict == "PASS"
    assert result.score == 100


def test_scoring_bands() -> None:
    assert summarise([])[1] == "PASS"
    warn = [Finding(finding_type="WEAK_DETECTION_METHOD", level="warning", operation_id="10", message="x")]
    assert summarise(warn)[1] == "PASS-WITH-WARNINGS"
    one_critical = [Finding(finding_type="MISSING_CONTROL", level="critical", operation_id="10", message="x")]
    score, verdict = summarise(one_critical)
    assert score == 85
    assert verdict == "NEEDS-REVIEW"
    many = [
        Finding(finding_type="MISSING_CONTROL", level="critical", operation_id=str(i), message="x")
        for i in range(5)
    ]
    assert summarise(many)[1] == "FAIL"
