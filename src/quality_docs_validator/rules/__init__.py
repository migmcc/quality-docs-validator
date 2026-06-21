"""Rule definitions (YAML) for the validation modules.

Packaged so rule files ship with the wheel. The YAML is the **single source of truth for rule
metadata** — id, severity, title, message_template, description and rationale. The checker in
``modules/pfmea_control_plan.py`` reads this metadata instead of hardcoding it, while the
per-finding-type detection logic stays in Python (this is intentionally not a generic rule engine).
"""

from __future__ import annotations

from importlib import resources

import yaml

_RULES_FILE = "pfmea_control_plan_rules.yaml"

VALID_SEVERITIES = {"critical", "warning"}
REQUIRED_FIELDS = ("severity", "message_template", "description")


class RuleSpecError(ValueError):
    """Raised when the rule metadata file is malformed."""


def parse_rule_specs(data: dict) -> dict[str, dict]:
    """Validate parsed YAML and return ``{rule_id: {severity, title, message_template, ...}}``.

    Raises RuleSpecError on a missing id, missing required field, invalid severity, or duplicate id.
    """
    specs: dict[str, dict] = {}
    for rule in (data or {}).get("rules", []):
        rule_id = (rule.get("id") or "").strip()
        if not rule_id:
            raise RuleSpecError("Rule with a missing or empty 'id'.")
        if rule_id in specs:
            raise RuleSpecError(f"Duplicate rule id: '{rule_id}'.")
        for field in REQUIRED_FIELDS:
            value = rule.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise RuleSpecError(f"Rule '{rule_id}' is missing required field '{field}'.")
        severity = rule["severity"]
        if severity not in VALID_SEVERITIES:
            raise RuleSpecError(
                f"Rule '{rule_id}' has invalid severity '{severity}' "
                f"(expected one of {sorted(VALID_SEVERITIES)})."
            )
        specs[rule_id] = {
            "severity": severity,
            "title": (rule.get("title") or "").strip(),
            "message_template": " ".join(str(rule["message_template"]).split()),
            "description": " ".join(str(rule["description"]).split()),
            "rationale": " ".join(str(rule.get("rationale") or "").split()),
        }
    if not specs:
        raise RuleSpecError("No rules found in the rule metadata file.")
    return specs


def load_rule_specs() -> dict[str, dict]:
    """Load and validate the rule metadata from the packaged YAML file."""
    text = resources.files(__package__).joinpath(_RULES_FILE).read_text(encoding="utf-8")
    return parse_rule_specs(yaml.safe_load(text))
