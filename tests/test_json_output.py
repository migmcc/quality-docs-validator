"""Tests for JSON report output (issue #3)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from quality_docs_validator import __version__
from quality_docs_validator.cli import app
from quality_docs_validator.core.report import build_report_data
from quality_docs_validator.modules.pfmea_control_plan import check_files

runner = CliRunner()

EXPECTED_TYPES = {
    "UNMATCHED_PROCESS_STEP",
    "MISSING_CONTROL",
    "SPECIAL_CHARACTERISTIC_NOT_CONTROLLED",
    "MISSING_REACTION_PLAN",
    "WEAK_DETECTION_METHOD",
    "HIGH_SEVERITY_WEAK_CONTROL",
}


def test_markdown_is_default(example_files, tmp_path: Path) -> None:
    pfmea, control_plan = example_files
    out = tmp_path / "report.md"
    result = runner.invoke(
        app,
        ["pfmea-control-plan", "--pfmea", str(pfmea), "--control-plan", str(control_plan), "--out", str(out)],
    )
    assert result.exit_code == 0
    text = out.read_text(encoding="utf-8")
    # Still Markdown, not JSON.
    assert "# PFMEA" in text
    assert not text.lstrip().startswith("{")


def test_json_generated_with_flag(example_files, tmp_path: Path) -> None:
    pfmea, control_plan = example_files
    out = tmp_path / "report.json"
    result = runner.invoke(
        app,
        [
            "pfmea-control-plan",
            "--pfmea", str(pfmea),
            "--control-plan", str(control_plan),
            "--format", "json",
            "--out", str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.exists()
    # Parseable JSON.
    data = json.loads(out.read_text(encoding="utf-8"))
    assert set(["metadata", "verdict", "score", "summary", "findings"]) <= set(data)


def test_json_metadata_shape(example_files, tmp_path: Path) -> None:
    pfmea, control_plan = example_files
    out = tmp_path / "report.json"
    runner.invoke(
        app,
        ["pfmea-control-plan", "--pfmea", str(pfmea), "--control-plan", str(control_plan), "--format", "json", "--out", str(out)],
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    md = data["metadata"]
    assert md["tool"] == "quality-docs-validator"
    assert md["version"] == __version__
    assert md["format"] == "json"
    assert md["generated_at"].endswith("+00:00")  # ISO-8601 UTC


def test_json_contains_expected_finding_types(example_files) -> None:
    pfmea, control_plan = example_files
    result = check_files(pfmea, control_plan)
    data = build_report_data(result, "pfmea.xlsx", "control-plan.xlsx")
    types = {f["type"] for f in data["findings"]}
    assert EXPECTED_TYPES <= types
    # Each finding exposes the documented keys.
    for f in data["findings"]:
        assert set(f) == {"type", "severity", "operation_id", "message"}
        assert f["severity"] in {"critical", "warning"}
    # Summary is internally consistent.
    assert data["summary"]["total"] == len(data["findings"])
    assert sum(data["summary"]["by_type"].values()) == data["summary"]["total"]
    assert (
        data["summary"]["by_severity"]["critical"] + data["summary"]["by_severity"]["warning"]
        == data["summary"]["total"]
    )


def test_json_clean_case_is_empty(make_xlsx, tmp_path: Path) -> None:
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
    out = tmp_path / "clean.json"
    runner.invoke(
        app,
        ["pfmea-control-plan", "--pfmea", str(pfmea), "--control-plan", str(cp), "--format", "json", "--out", str(out)],
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["score"] == 100
    assert data["verdict"] == "PASS"
    assert data["findings"] == []
    assert data["summary"]["total"] == 0
