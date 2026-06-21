"""Ensure the rule metadata (YAML) and the implemented checks (code) never drift."""

from __future__ import annotations

import pytest

from quality_docs_validator.modules.pfmea_control_plan import _RULES, check_files
from quality_docs_validator.rules import (
    RuleSpecError,
    load_rule_specs,
    parse_rule_specs,
)

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
        assert spec["message_template"], rule_id
        assert spec["description"], rule_id


def test_every_rule_id_is_used_by_the_checker() -> None:
    # No documented rule id is left unused, and the checker uses no undocumented id.
    assert set(_RULES) == EXPECTED_RULE_IDS


def test_loader_rejects_invalid_severity() -> None:
    with pytest.raises(RuleSpecError, match="invalid severity"):
        parse_rule_specs(
            {"rules": [{"id": "X", "severity": "blocker", "message_template": "m", "description": "d"}]}
        )


def test_loader_rejects_duplicate_ids() -> None:
    with pytest.raises(RuleSpecError, match="Duplicate rule id"):
        parse_rule_specs(
            {
                "rules": [
                    {"id": "X", "severity": "warning", "message_template": "m", "description": "d"},
                    {"id": "X", "severity": "critical", "message_template": "m", "description": "d"},
                ]
            }
        )


def test_loader_rejects_missing_required_field() -> None:
    with pytest.raises(RuleSpecError, match="missing required field 'severity'"):
        parse_rule_specs({"rules": [{"id": "X", "message_template": "m", "description": "d"}]})


def test_loader_rejects_missing_id() -> None:
    with pytest.raises(RuleSpecError, match="missing or empty 'id'"):
        parse_rule_specs(
            {"rules": [{"severity": "warning", "message_template": "m", "description": "d"}]}
        )


def test_loader_rejects_empty_ruleset() -> None:
    with pytest.raises(RuleSpecError, match="No rules"):
        parse_rule_specs({"rules": []})


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
