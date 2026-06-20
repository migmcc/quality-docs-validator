"""Edge-case and robustness tests for the parser and pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook
from typer.testing import CliRunner

from quality_docs_validator.cli import app
from quality_docs_validator.modules.pfmea_control_plan import check_files
from quality_docs_validator.parsers.excel import (
    ParseError,
    parse_control_plan,
    parse_pfmea,
)

runner = CliRunner()


def test_missing_operation_id_column_raises_clear_error(make_xlsx, tmp_path: Path) -> None:
    path = make_xlsx(tmp_path / "p.xlsx", ["Failure Mode", "Severity"], [["Crack", 9]])
    with pytest.raises(ParseError) as exc:
        parse_pfmea(path)
    assert "operation_id" in str(exc.value)
    assert "recommended template" in str(exc.value).lower() or "alias" in str(exc.value).lower()


def test_non_xlsx_file_raises_clear_error(tmp_path: Path) -> None:
    csv = tmp_path / "data.csv"
    csv.write_text("Operation ID,Failure Mode\n10,Crack\n", encoding="utf-8")
    with pytest.raises(ParseError) as exc:
        parse_pfmea(csv)
    assert ".xlsx" in str(exc.value)


def test_missing_file_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ParseError) as exc:
        parse_pfmea(tmp_path / "does-not-exist.xlsx")
    assert "not found" in str(exc.value).lower()


def test_empty_worksheet_raises_clear_error(tmp_path: Path) -> None:
    path = tmp_path / "empty.xlsx"
    Workbook().save(path)  # active sheet with no content
    with pytest.raises(ParseError) as exc:
        parse_pfmea(path)
    assert "empty" in str(exc.value).lower()


def test_header_only_no_data_rows_raises(make_xlsx, tmp_path: Path) -> None:
    path = make_xlsx(tmp_path / "p.xlsx", ["Operation ID", "Failure Mode"], [])
    with pytest.raises(ParseError) as exc:
        parse_pfmea(path)
    assert "no pfmea data rows" in str(exc.value).lower()


def test_non_numeric_severity_does_not_crash(make_xlsx, tmp_path: Path) -> None:
    path = make_xlsx(
        tmp_path / "p.xlsx",
        ["Operation ID", "Failure Mode", "Severity"],
        [["10", "Crack", "high"]],
    )
    rows = parse_pfmea(path)
    assert rows[0].severity is None  # gracefully degraded, not an exception


def test_rows_without_operation_id_are_skipped(make_xlsx, tmp_path: Path) -> None:
    path = make_xlsx(
        tmp_path / "p.xlsx",
        ["Operation ID", "Failure Mode"],
        [["10", "Crack"], [None, "Orphan failure"], ["20", "Leak"]],
    )
    rows = parse_pfmea(path)
    assert [r.operation_id for r in rows] == ["10", "20"]


def test_duplicate_operation_id_is_grouped(make_xlsx, tmp_path: Path) -> None:
    pfmea = make_xlsx(
        tmp_path / "pf.xlsx",
        ["Operation ID", "Failure Mode", "Severity", "Special Characteristic"],
        [["10", "Crack", 5, "No"], ["10", "Porosity", 9, "Yes"]],
    )
    cp = make_xlsx(
        tmp_path / "cp.xlsx",
        ["Operation ID", "Control Method", "Special Characteristic"],
        [["10", "CMM scan", "No"]],
    )
    result = check_files(pfmea, cp)
    # The special characteristic from the second op-10 row is still detected.
    types = {f.finding_type for f in result.findings}
    assert "SPECIAL_CHARACTERISTIC_NOT_CONTROLLED" in types
    assert "UNMATCHED_PROCESS_STEP" not in types  # op 10 matched despite duplicate rows


def test_extra_columns_are_ignored(make_xlsx, tmp_path: Path) -> None:
    path = make_xlsx(
        tmp_path / "p.xlsx",
        ["Operation ID", "Notes", "Failure Mode", "Owner", "Severity"],
        [["10", "n/a", "Crack", "QA", 7]],
    )
    rows = parse_pfmea(path)
    assert rows[0].operation_id == "10"
    assert rows[0].failure_mode == "Crack"
    assert rows[0].severity == 7


def test_header_not_on_first_row(make_xlsx, tmp_path: Path) -> None:
    # A leading title row before the real header should be tolerated.
    path = make_xlsx(
        tmp_path / "cp.xlsx",
        ["Control Plan - Project X", None, None],
        [
            ["Operation ID", "Control Method", "Reaction Plan"],
            ["10", "CMM scan", "Rework"],
        ],
    )
    rows = parse_control_plan(path)
    assert len(rows) == 1
    assert rows[0].operation_id == "10"
    assert rows[0].control_method == "CMM scan"


def test_cli_reports_parse_error_clearly(make_xlsx, tmp_path: Path) -> None:
    bad = tmp_path / "data.csv"
    bad.write_text("Operation ID,Failure Mode\n10,Crack\n", encoding="utf-8")
    good = make_xlsx(tmp_path / "cp.xlsx", ["Operation ID", "Control Method"], [["10", "CMM"]])
    result = runner.invoke(
        app,
        ["pfmea-control-plan", "--pfmea", str(bad), "--control-plan", str(good), "--out", str(tmp_path / "r.md")],
    )
    assert result.exit_code == 2
    assert "Error" in result.stdout
    assert ".xlsx" in result.stdout


def test_weak_keyword_precision(make_xlsx, tmp_path: Path) -> None:
    # "Manual gauge" / "Operator runs CMM" must NOT be flagged weak; "Visual" must be.
    pfmea = make_xlsx(
        tmp_path / "pf.xlsx",
        ["Operation ID", "Failure Mode", "Severity"],
        [["10", "Crack", 5], ["20", "Leak", 5]],
    )
    cp = make_xlsx(
        tmp_path / "cp.xlsx",
        ["Operation ID", "Control Method", "Reaction Plan"],
        [["10", "Manual gauge measurement", "Rework"], ["20", "Visual inspection", "Rework"]],
    )
    result = check_files(pfmea, cp)
    weak_ops = {f.operation_id for f in result.findings if f.finding_type == "WEAK_DETECTION_METHOD"}
    assert weak_ops == {"20"}
