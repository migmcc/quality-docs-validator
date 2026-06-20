"""Match PFMEA and Control Plan rows by operation.

MVP matching key is the normalised `operation_id`. Rows that share a key are grouped together so
the checker can reason about all failure modes and all controls for one operation at once.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..models import ControlPlanRow, PFMEARow


def normalise_key(operation_id: str) -> str:
    """Normalise an operation id for matching (e.g. 'Op 10' and 'op-10' collapse to 'op10')."""
    return re.sub(r"[^a-z0-9]", "", operation_id.lower())


@dataclass
class MatchResult:
    """Grouped PFMEA/Control Plan rows keyed by normalised operation id."""

    pfmea_by_op: dict[str, list[PFMEARow]] = field(default_factory=dict)
    control_by_op: dict[str, list[ControlPlanRow]] = field(default_factory=dict)

    @property
    def matched_ops(self) -> list[str]:
        return sorted(set(self.pfmea_by_op) & set(self.control_by_op))

    @property
    def pfmea_only_ops(self) -> list[str]:
        return sorted(set(self.pfmea_by_op) - set(self.control_by_op))

    @property
    def control_only_ops(self) -> list[str]:
        return sorted(set(self.control_by_op) - set(self.pfmea_by_op))

    def display_op(self, key: str) -> str:
        """Return a human-friendly operation id for a normalised key."""
        rows: list = self.pfmea_by_op.get(key) or self.control_by_op.get(key) or []
        return rows[0].operation_id if rows else key


def match_rows(pfmea: list[PFMEARow], control_plan: list[ControlPlanRow]) -> MatchResult:
    result = MatchResult()
    for row in pfmea:
        result.pfmea_by_op.setdefault(normalise_key(row.operation_id), []).append(row)
    for row in control_plan:
        result.control_by_op.setdefault(normalise_key(row.operation_id), []).append(row)
    return result
