"""Tests for multi-sheet workbook support (issue #4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from quality_docs_validator.cli import app
from quality_docs_validator.modules.pfmea_control_plan import check_files
from quality_docs_validator.parsers.excel import (
    ParseError,
    parse_control_plan,
    parse_pfmea,
)

runner = CliRunner()

PFMEA_HEADERS = ["Operation ID", "Failure Mode", "Severity", "Special Characteristic"]
CP_HEADERS = ["Operation ID", "Control Method", "Reaction Plan", "Special Characteristic"]


def _pfmea_multi(make_multi_sheet_xlsx, tmp_path: Path) -> Path:
    return make_multi_sheet_xlsx(
        tmp_path / "pfmea.xlsx",
        {
            "Cover": (["Title"], [["Project X PFMEA"]]),
            "PFMEA": (PFMEA_HEADERS, [["10", "Crack", 9, "Yes"]]),
            "Notes": (["Note"], [["ignore me"]]),
        },
    )


def _cp_multi(make_multi_sheet_xlsx, tmp_path: Path) -> Path:
    return make_multi_sheet_xlsx(
        tmp_path / "cp.xlsx",
        {
            "Cover": (["Title"], [["Project X Control Plan"]]),
            "Control Plan": (CP_HEADERS, [["10", "Visual inspection", "", "No"]]),
        },
    )


def test_pfmea_explicit_sheet_selection(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    path = _pfmea_multi(make_multi_sheet_xlsx, tmp_path)
    rows = parse_pfmea(path, sheet="PFMEA")
    assert len(rows) == 1
    assert rows[0].operation_id == "10"
    assert rows[0].severity == 9
    assert rows[0].special_characteristic is True


def test_control_plan_explicit_sheet_selection(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    path = _cp_multi(make_multi_sheet_xlsx, tmp_path)
    rows = parse_control_plan(path, sheet="Control Plan")
    assert len(rows) == 1
    assert rows[0].operation_id == "10"
    assert rows[0].control_method == "Visual inspection"


def test_missing_pfmea_sheet_lists_available(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    path = _pfmea_multi(make_multi_sheet_xlsx, tmp_path)
    with pytest.raises(ParseError) as exc:
        parse_pfmea(path, sheet="DoesNotExist")
    msg = str(exc.value)
    assert "DoesNotExist" in msg
    assert "'PFMEA'" in msg and "'Cover'" in msg  # lists available sheets


def test_missing_control_plan_sheet_lists_available(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    path = _cp_multi(make_multi_sheet_xlsx, tmp_path)
    with pytest.raises(ParseError) as exc:
        parse_control_plan(path, sheet="Nope")
    msg = str(exc.value)
    assert "Nope" in msg
    assert "'Control Plan'" in msg


def test_default_no_sheet_is_backwards_compatible(make_xlsx, tmp_path: Path) -> None:
    # Single-sheet workbook with no sheet argument keeps the v0.1/v0.2 behaviour.
    pfmea = make_xlsx(tmp_path / "pf.xlsx", PFMEA_HEADERS, [["10", "Crack", 9, "No"]])
    cp = make_xlsx(tmp_path / "cp.xlsx", CP_HEADERS, [["10", "Pressure gauge", "Rework", "No"]])
    result = check_files(pfmea, cp)
    assert result.pfmea_rows == 1
    assert result.control_plan_rows == 1


def test_header_autodetection_with_selected_sheet(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    # The selected sheet has a leading title row before the header -> still auto-detected.
    path = make_multi_sheet_xlsx(
        tmp_path / "pfmea.xlsx",
        {
            "Intro": (["x"], [["y"]]),
            "PFMEA": (
                ["PFMEA - Project X", None, None, None],
                [PFMEA_HEADERS, ["10", "Crack", 9, "No"]],
            ),
        },
    )
    rows = parse_pfmea(path, sheet="PFMEA")
    assert len(rows) == 1
    assert rows[0].operation_id == "10"


def test_cli_markdown_with_explicit_sheets(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    pfmea = _pfmea_multi(make_multi_sheet_xlsx, tmp_path)
    cp = _cp_multi(make_multi_sheet_xlsx, tmp_path)
    out = tmp_path / "report.md"
    result = runner.invoke(
        app,
        [
            "pfmea-control-plan",
            "--pfmea", str(pfmea), "--pfmea-sheet", "PFMEA",
            "--control-plan", str(cp), "--control-plan-sheet", "Control Plan",
            "--out", str(out),
        ],
    )
    assert result.exit_code == 0
    assert "# PFMEA" in out.read_text(encoding="utf-8")


def test_cli_json_with_explicit_sheets(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    pfmea = _pfmea_multi(make_multi_sheet_xlsx, tmp_path)
    cp = _cp_multi(make_multi_sheet_xlsx, tmp_path)
    out = tmp_path / "report.json"
    result = runner.invoke(
        app,
        [
            "pfmea-control-plan",
            "--pfmea", str(pfmea), "--pfmea-sheet", "PFMEA",
            "--control-plan", str(cp), "--control-plan-sheet", "Control Plan",
            "--format", "json", "--out", str(out),
        ],
    )
    assert result.exit_code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "verdict" in data and "findings" in data


def test_cli_clear_error_for_missing_sheet(make_multi_sheet_xlsx, tmp_path: Path) -> None:
    pfmea = _pfmea_multi(make_multi_sheet_xlsx, tmp_path)
    cp = _cp_multi(make_multi_sheet_xlsx, tmp_path)
    result = runner.invoke(
        app,
        [
            "pfmea-control-plan",
            "--pfmea", str(pfmea), "--pfmea-sheet", "Wrong",
            "--control-plan", str(cp),
            "--out", str(tmp_path / "r.md"),
        ],
    )
    assert result.exit_code == 2
    assert "Wrong" in result.stdout
    assert "Available sheets" in result.stdout
