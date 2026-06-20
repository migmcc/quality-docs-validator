"""Excel (.xlsx) parser for PFMEA and Control Plan documents.

MVP behaviour (see docs/DECISIONS.md D1/D2): `.xlsx` only, recommended template plus a small set
of column aliases. The first worksheet is read; the first row is treated as the header. Headers are
normalised (lowercased, non-alphanumeric stripped) before being matched against the alias maps.
"""

from __future__ import annotations

import re
from pathlib import Path

from openpyxl import load_workbook

from ..models import ControlPlanRow, PFMEARow


class ParseError(Exception):
    """Raised when a file cannot be parsed into the expected document shape."""


# Canonical field -> accepted normalised header aliases.
PFMEA_ALIASES: dict[str, set[str]] = {
    "operation_id": {"operationid", "opid", "opno", "operationno", "operation", "processnumber"},
    "process_step": {"processstep", "processfunction", "operationdescription", "step", "processname"},
    "failure_mode": {"failuremode", "potentialfailuremode", "failure"},
    "effect": {"effect", "potentialeffect", "effectsoffailure"},
    "severity": {"severity", "sev", "s"},
    "cause": {"cause", "potentialcause", "causeoffailure"},
    "prevention_control": {"preventioncontrol", "currentpreventioncontrol", "prevention"},
    "detection_control": {"detectioncontrol", "currentdetectioncontrol", "currentcontrolsdetection"},
    "detection": {"detection", "det", "d"},
    "special_characteristic": {"specialcharacteristic", "specialchar", "classification", "sc"},
}

CONTROL_PLAN_ALIASES: dict[str, set[str]] = {
    "operation_id": {"operationid", "opid", "opno", "operationno", "operation", "processnumber"},
    "process_step": {"processstep", "processname", "processdescription", "operationdescription", "step"},
    "characteristic": {"characteristic", "productcharacteristic", "processcharacteristic"},
    "special_characteristic": {"specialcharacteristic", "specialchar", "classification", "sc"},
    "control_method": {"controlmethod", "control", "method", "evaluationmeasurementtechnique"},
    "detection_method": {"detectionmethod", "inspectionmethod", "evaluationmethod"},
    "reaction_plan": {"reactionplan", "reaction", "responseplan", "correctiveaction"},
}

_TRUE_TOKENS = {"yes", "y", "true", "1", "x", "cc", "sc", "critical", "significant", "*", "✓", "✔"}


def _normalise(header: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(header).strip().lower()) if header is not None else ""


def _build_header_map(headers: list[object], aliases: dict[str, set[str]]) -> dict[str, int]:
    """Map canonical field name -> column index, using the alias table."""
    field_to_index: dict[str, int] = {}
    for index, header in enumerate(headers):
        norm = _normalise(header)
        if not norm:
            continue
        for field, accepted in aliases.items():
            if norm in accepted and field not in field_to_index:
                field_to_index[field] = index
    return field_to_index


def _cell(row: tuple, index: int | None) -> object:
    if index is None or index >= len(row):
        return None
    return row[index]


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_int(value: object) -> int | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def _to_bool(value: object) -> bool:
    if value is None:
        return False
    return _normalise(value) in {_normalise(t) for t in _TRUE_TOKENS}


def _load_rows(path: Path) -> tuple[list[object], list[tuple]]:
    if path.suffix.lower() != ".xlsx":
        raise ParseError(f"Only .xlsx files are supported in the MVP (got '{path.suffix}').")
    if not path.exists():
        raise ParseError(f"File not found: {path}")
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    if not rows:
        raise ParseError(f"Worksheet in '{path.name}' is empty.")
    headers = list(rows[0])
    return headers, rows[1:]


def _require(field_map: dict[str, int], required: str, doc: str, path: Path) -> None:
    if required not in field_map:
        raise ParseError(
            f"Could not find a '{required}' column in {doc} '{path.name}'. "
            f"Check the recommended template / column aliases (docs/DECISIONS.md D2)."
        )


def parse_pfmea(path: str | Path) -> list[PFMEARow]:
    path = Path(path)
    headers, data = _load_rows(path)
    field_map = _build_header_map(headers, PFMEA_ALIASES)
    _require(field_map, "operation_id", "PFMEA", path)

    out: list[PFMEARow] = []
    for offset, raw in enumerate(data, start=2):
        operation_id = _text(_cell(raw, field_map.get("operation_id")))
        if operation_id is None:
            continue  # skip blank/spacer rows
        out.append(
            PFMEARow(
                operation_id=operation_id,
                process_step=_text(_cell(raw, field_map.get("process_step"))),
                failure_mode=_text(_cell(raw, field_map.get("failure_mode"))),
                effect=_text(_cell(raw, field_map.get("effect"))),
                severity=_to_int(_cell(raw, field_map.get("severity"))),
                cause=_text(_cell(raw, field_map.get("cause"))),
                prevention_control=_text(_cell(raw, field_map.get("prevention_control"))),
                detection_control=_text(_cell(raw, field_map.get("detection_control"))),
                detection=_to_int(_cell(raw, field_map.get("detection"))),
                special_characteristic=_to_bool(_cell(raw, field_map.get("special_characteristic"))),
                row_number=offset,
            )
        )
    if not out:
        raise ParseError(f"No PFMEA data rows found in '{path.name}'.")
    return out


def parse_control_plan(path: str | Path) -> list[ControlPlanRow]:
    path = Path(path)
    headers, data = _load_rows(path)
    field_map = _build_header_map(headers, CONTROL_PLAN_ALIASES)
    _require(field_map, "operation_id", "Control Plan", path)

    out: list[ControlPlanRow] = []
    for offset, raw in enumerate(data, start=2):
        operation_id = _text(_cell(raw, field_map.get("operation_id")))
        if operation_id is None:
            continue
        out.append(
            ControlPlanRow(
                operation_id=operation_id,
                process_step=_text(_cell(raw, field_map.get("process_step"))),
                characteristic=_text(_cell(raw, field_map.get("characteristic"))),
                special_characteristic=_to_bool(_cell(raw, field_map.get("special_characteristic"))),
                control_method=_text(_cell(raw, field_map.get("control_method"))),
                detection_method=_text(_cell(raw, field_map.get("detection_method"))),
                reaction_plan=_text(_cell(raw, field_map.get("reaction_plan"))),
                row_number=offset,
            )
        )
    if not out:
        raise ParseError(f"No Control Plan data rows found in '{path.name}'.")
    return out
