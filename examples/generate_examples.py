"""Generate the synthetic example workbooks used by the quickstart and tests.

Run from the repo root:  python examples/generate_examples.py

The data is entirely synthetic. It is seeded with deliberate gaps so the checker has real findings
to surface (every MVP finding type is triggered at least once):
- Op 40 exists only in the PFMEA            -> UNMATCHED_PROCESS_STEP
- Op 30 has no control method               -> MISSING_CONTROL
- Op 20 special char not marked in CP        -> SPECIAL_CHARACTERISTIC_NOT_CONTROLLED
- Op 20 high severity, no reaction plan       -> MISSING_REACTION_PLAN
- Op 20 visual-only control                  -> WEAK_DETECTION_METHOD + HIGH_SEVERITY_WEAK_CONTROL
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

HERE = Path(__file__).resolve().parent

PFMEA_HEADERS = [
    "Operation ID",
    "Process Step",
    "Failure Mode",
    "Severity",
    "Special Characteristic",
    "Current Detection Control",
    "Detection",
]
PFMEA_ROWS = [
    ["10", "Incoming Inspection", "Wrong material grade", 8, "No", "Certificate review", 4],
    ["20", "Laser Welding", "Insufficient weld penetration", 9, "Yes", "Operator visual check", 6],
    ["30", "Screw Assembly", "Missing fastener", 7, "No", "Torque monitoring", 3],
    ["40", "Final Inspection", "Surface scratch", 4, "No", "Visual check", 7],
]

CONTROL_PLAN_HEADERS = [
    "Operation ID",
    "Process Step",
    "Characteristic",
    "Special Characteristic",
    "Control Method",
    "Reaction Plan",
]
CONTROL_PLAN_ROWS = [
    ["10", "Incoming Inspection", "Material grade", "No", "Certificate verification", "Quarantine & notify supplier"],
    ["20", "Laser Welding", "Weld penetration", "No", "Visual inspection", ""],
    ["30", "Screw Assembly", "Fastener presence", "No", "", "Rework station"],
]


def _write(path: Path, headers: list[str], rows: list[list]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    workbook.save(path)


def main() -> None:
    _write(HERE / "pfmea.xlsx", PFMEA_HEADERS, PFMEA_ROWS)
    _write(HERE / "control-plan.xlsx", CONTROL_PLAN_HEADERS, CONTROL_PLAN_ROWS)
    print(f"Wrote {HERE / 'pfmea.xlsx'} and {HERE / 'control-plan.xlsx'}")


if __name__ == "__main__":
    main()
