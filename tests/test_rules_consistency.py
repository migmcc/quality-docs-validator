"""Ensure the documented rules (YAML) and the implemented checks (code) never drift."""

from __future__ import annotations

from quality_docs_validator.modules.pfmea_control_plan import check_files
from quality_docs_validator.rules import load_rule_specs

EXPECTED_RULE_IDS = {
    "UNMATCHED_PROCESS_STEP",
    "MISSING_CONTROL",
    "SPECIAL_CHARACTERISTIC_NOT_CONTROLLED",
    "MISSING_REACTION_PLAN",
    "WEAK_DETECTION_METHOD",
    "HIGH_SEVERITY_WEAK_CONTROL",
}


def test_yaml_documents_exactly_the_known_rules() -> None:
    specs = load_rule_specs()
    assert set(specs) == EXPECTED_RULE_IDS
    for rule_id, spec in specs.items():
        assert spec["severity"] in {"critical", "warning"}, rule_id
        assert spec["description"], rule_id


def test_warning_rules_stay_warnings() -> None:
    # D3: these two false-positive-prone checks must remain warnings, not hard-fails.
    specs = load_rule_specs()
    assert specs["WEAK_DETECTION_METHOD"]["severity"] == "warning"
    assert specs["HIGH_SEVERITY_WEAK_CONTROL"]["severity"] == "warning"


def test_emitted_levels_match_documented_severity(example_files) -> None:
    pfmea, control_plan = example_files
    result = check_files(pfmea, control_plan)
    specs = load_rule_specs()
    for finding in result.findings:
        assert finding.level == specs[finding.finding_type]["severity"], finding.finding_type
