# Finding Types & Scoring

This document describes the six finding types the MVP PFMEA ↔ Control Plan checker can surface,
the rationale for each, and how findings are turned into a score and verdict.

> All findings are **potential** inconsistencies for a human to judge. The tool makes no regulatory
> or normative conformance claim and does not replace technical review.

The authoritative rule **metadata** (id, severity, title, message template, description, rationale)
is the
[`rules/pfmea_control_plan_rules.yaml`](../src/quality_docs_validator/rules/pfmea_control_plan_rules.yaml)
file; the checker reads it instead of hardcoding these values, and consistency + parity tests keep
the YAML and the code in sync. The **detection logic** for each finding type is implemented in
[`modules/pfmea_control_plan.py`](../src/quality_docs_validator/modules/pfmea_control_plan.py).

## Matching

Rows are grouped and matched by a **normalised `operation_id`** (lower-cased, non-alphanumeric
stripped — so `Op 10`, `op-10` and `10` all match). All PFMEA failure modes and all Control Plan
controls for one operation are evaluated together. Operations present in only one document are
reported (rather than silently dropped) as `UNMATCHED_PROCESS_STEP`.

## The six finding types

| Type | Level | Triggers when… | Why it matters |
|------|-------|----------------|----------------|
| `UNMATCHED_PROCESS_STEP` | 🟡 warning | An operation exists in only one of the two documents. | A step planned in the PFMEA with no Control Plan entry (or vice-versa) is a coverage gap — but it is also a common artefact of differing numbering, so it is a warning, not a failure. |
| `MISSING_CONTROL` | 🔴 critical | A matched operation has PFMEA failure mode(s) but **no control method** in the Control Plan. | A failure mode with no control is exactly the kind of gap audits and escapes punish. |
| `SPECIAL_CHARACTERISTIC_NOT_CONTROLLED` | 🔴 critical | An operation is flagged as a special characteristic in the PFMEA but **not** marked/controlled as special in the Control Plan. | Special characteristics carry mandatory control expectations; a mismatch is high-risk. |
| `MISSING_REACTION_PLAN` | 🔴 critical | A matched operation has a **high-severity** failure mode (S ≥ 8) and a control, but **no reaction plan**. | When risk is highest, the absence of a documented reaction plan is a serious gap. |
| `WEAK_DETECTION_METHOD` | 🟡 warning | The control method looks subjective/low-reliability (e.g. *visual inspection*, *by eye*, *manual inspection*). | Weak detection lets defects through — but the judgement is heuristic and template-sensitive, so it is a warning (see D3). |
| `HIGH_SEVERITY_WEAK_CONTROL` | 🟡 warning | A high-severity failure mode (S ≥ 8) is paired with a weak control method. | High severity + weak control is a priority to revisit; kept a warning for the same false-positive reason. |

### Why two checks are warnings (decision D3)
`WEAK_DETECTION_METHOD` and `HIGH_SEVERITY_WEAK_CONTROL` depend on free-text method descriptions and
keyword heuristics, which vary across templates and wording. To protect trust, they ship as
**warnings** and never as hard failures. The weak-method heuristic matches specific phrases
(`visual`, `by eye`, `naked eye`, `look`, `operator check`, `operator visual`, `manual inspection`,
`manual check`) rather than bare words, so e.g. *"manual gauge"* or *"operator runs CMM"* are not
flagged.

## Scoring

Implemented in [`core/scoring.py`](../src/quality_docs_validator/core/scoring.py).

The score starts at **100** and is reduced per finding:

| Level | Weight (points off) |
|-------|---------------------|
| critical | 15 |
| warning | 4 |

`score = max(0, 100 − Σ weights)`. Weights are intentionally conservative so that warnings cannot,
on their own, dominate the result.

### Verdict bands

| Verdict | Condition |
|---------|-----------|
| `PASS` | No findings. |
| `PASS-WITH-WARNINGS` | Findings exist, but none are critical. |
| `NEEDS-REVIEW` | At least one critical finding **and** score ≥ 50. |
| `FAIL` | At least one critical finding **and** score < 50. |

## Worked example

Running the bundled synthetic examples (`examples/pfmea.xlsx`, `examples/control-plan.xlsx`)
produces all six finding types: 3 critical + 3 warnings → score **43/100** → **FAIL**. See
[../examples/report.md](../examples/report.md).
