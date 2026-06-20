"""Parametrized tests for column-header aliases (issue #2).

Covers the aliases added for real-world PFMEA / Control Plan templates, plus a no-regression check
that the original aliases still resolve. The header `operation_id` is required, so for non-key
fields the workbook also carries an `Operation ID` column.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from quality_docs_validator.parsers.excel import (
    ParseError,
    parse_control_plan,
    parse_pfmea,
)

# (alias header text, canonical field, raw cell value, expected parsed value)
PFMEA_NEW_ALIASES = [
    ("Operation Number", "operation_id", "10", "10"),
    ("Op Number", "operation_id", "10", "10"),
    ("Op #", "operation_id", "10", "10"),
    ("Process No", "operation_id", "10", "10"),
    ("Step No", "operation_id", "10", "10"),
    ("Process Description", "process_step", "Welding", "Welding"),
    ("Step Description", "process_step", "Welding", "Welding"),
    ("Severity Rating", "severity", 9, 9),
    ("Detection Method", "detection_control", "Gauge R&R", "Gauge R&R"),
    ("Special Characteristics", "special_characteristic", "Yes", True),
    ("Key Characteristic", "special_characteristic", "Yes", True),
    ("Critical Characteristic", "special_characteristic", "Yes", True),
]

CONTROL_PLAN_NEW_ALIASES = [
    ("Operation Number", "operation_id", "10", "10"),
    ("Op Number", "operation_id", "10", "10"),
    ("Op #", "operation_id", "10", "10"),
    ("Process No", "operation_id", "10", "10"),
    ("Step No", "operation_id", "10", "10"),
    ("Step Description", "process_step", "Welding", "Welding"),
    ("Control Technique", "control_method", "SPC chart", "SPC chart"),
    ("Measurement Technique", "control_method", "CMM", "CMM"),
    ("Out of Control Action", "reaction_plan", "Stop line", "Stop line"),
    ("Special Characteristics", "special_characteristic", "Yes", True),
    ("Key Characteristic", "special_characteristic", "Yes", True),
    ("Critical Characteristic", "special_characteristic", "Yes", True),
]


@pytest.mark.parametrize("header,field,value,expected", PFMEA_NEW_ALIASES)
def test_pfmea_new_aliases(make_xlsx, tmp_path, header, field, value, expected) -> None:
    if field == "operation_id":
        path = make_xlsx(tmp_path / "p.xlsx", [header], [[value]])
    else:
        path = make_xlsx(tmp_path / "p.xlsx", ["Operation ID", header], [["10", value]])
    rows = parse_pfmea(path)
    assert getattr(rows[0], field) == expected


@pytest.mark.parametrize("header,field,value,expected", CONTROL_PLAN_NEW_ALIASES)
def test_control_plan_new_aliases(make_xlsx, tmp_path, header, field, value, expected) -> None:
    if field == "operation_id":
        path = make_xlsx(tmp_path / "cp.xlsx", [header], [[value]])
    else:
        path = make_xlsx(tmp_path / "cp.xlsx", ["Operation ID", header], [["10", value]])
    rows = parse_control_plan(path)
    assert getattr(rows[0], field) == expected


def test_original_aliases_still_work(make_xlsx, tmp_path: Path) -> None:
    # A spread of pre-existing aliases must keep resolving (no regression).
    pfmea = make_xlsx(
        tmp_path / "pf.xlsx",
        ["Op No", "Process Function", "Potential Failure Mode", "Sev", "Classification"],
        [["10", "Weld", "Crack", 9, "Yes"]],
    )
    rows = parse_pfmea(pfmea)
    assert rows[0].operation_id == "10"
    assert rows[0].process_step == "Weld"
    assert rows[0].severity == 9
    assert rows[0].special_characteristic is True

    cp = make_xlsx(
        tmp_path / "cp.xlsx",
        ["Operation No", "Control Method", "Reaction Plan"],
        [["10", "CMM", "Rework"]],
    )
    cp_rows = parse_control_plan(cp)
    assert cp_rows[0].operation_id == "10"
    assert cp_rows[0].control_method == "CMM"
    assert cp_rows[0].reaction_plan == "Rework"


def test_missing_required_column_still_errors_clearly(make_xlsx, tmp_path: Path) -> None:
    # No operation_id alias present -> clear ParseError (unchanged behaviour).
    path = make_xlsx(tmp_path / "p.xlsx", ["Failure Mode", "Severity"], [["Crack", 9]])
    with pytest.raises(ParseError) as exc:
        parse_pfmea(path)
    assert "operation_id" in str(exc.value)
