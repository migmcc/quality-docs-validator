"""Rule definitions (YAML) for the validation modules.

Packaged so rule files ship with the wheel. In the MVP the checks are implemented in
``modules/pfmea_control_plan.py``; this YAML documents each finding type (id, severity,
description) and is the single source of truth for that metadata. A consistency test asserts the
code and the YAML never drift. Making the module *consume* this YAML to drive logic is deferred
to a later iteration (it requires a small rule-interpretation layer).
"""

from __future__ import annotations

from importlib import resources

import yaml

_RULES_FILE = "pfmea_control_plan_rules.yaml"


def load_rule_specs() -> dict[str, dict]:
    """Load the documented rules as ``{rule_id: {"severity": ..., "description": ...}}``."""
    text = resources.files(__package__).joinpath(_RULES_FILE).read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    specs: dict[str, dict] = {}
    for rule in data.get("rules", []):
        rule_id = rule.get("id")
        if rule_id:
            specs[rule_id] = {
                "severity": rule.get("severity"),
                "description": (rule.get("description") or "").strip(),
            }
    return specs

