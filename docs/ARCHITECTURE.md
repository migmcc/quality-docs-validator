# Architecture

> Scaffold-stage design. Code under `src/` is mostly empty placeholders; this document describes
> the intended layout so the vertical slice (Run C) drops into a known structure.

## Principles
- **Local-first.** Everything runs offline on the user's machine; no upload of confidential data.
- **Explicit, documented rules.** Checks are data (`rules/*.yaml`), named, severity-classified,
  and testable — never opaque heuristics.
- **Potential findings, not verdicts.** Output is advisory; a human makes the call. Every report
  carries a "not a substitute for human review" footer.
- **Module independence.** The core (parse → match → score → report) never depends on a specific
  module, so adding modules later never forces a rewrite.

## Data flow

```
PFMEA .xlsx ─┐
             ├─► parsers/excel.py ─► models (PFMEARow, ControlPlanRow)
Control .xlsx┘                          │
                                        ▼
                              core/matching.py        (match by operation_id / process_step,
                                        │              orphans -> UNMATCHED_PROCESS_STEP)
                                        ▼
                       modules/pfmea_control_plan.py   (apply rules/*.yaml -> Findings)
                                        │
                                        ▼
                              core/scoring.py          (severity weights -> 0..100 + verdict band)
                                        │
                                        ▼
                              core/report.py           (jinja2 Markdown + rich terminal summary)
```

## Package layout

```
src/quality_docs_validator/
├── __init__.py            # version
├── cli.py                 # typer app; entry points `quality-docs-validator` and `qdv`
├── models.py              # (planned) PFMEARow, ControlPlanRow, Finding  [placeholder]
├── parsers/               # (planned) excel.py: load sheets, apply aliases  [placeholder]
├── core/                  # (planned) matching.py, scoring.py, report.py   [placeholder]
├── modules/               # (planned) pfmea_control_plan.py                [placeholder]
└── rules/
    └── pfmea_control_plan_rules.yaml   # rule definitions (data)           [placeholder]
```

## Key components (to be implemented)

| Component | Responsibility |
|-----------|----------------|
| `parsers/excel.py` | Read `.xlsx`, map columns via recommended-template aliases, build row models; clear errors on messy headers. |
| `core/matching.py` | Join PFMEA and Control Plan rows by `operation_id` / `process_step`; emit `UNMATCHED_PROCESS_STEP` for orphans. |
| `modules/pfmea_control_plan.py` | Apply the YAML rules to matched rows, produce `Finding`s (≥5 finding types for MVP). |
| `core/scoring.py` | Severity-weighted score 0–100 + verdict band (PASS / PASS-WITH-WARNINGS / NEEDS-REVIEW / FAIL). |
| `core/report.py` | Render Markdown report (jinja2) + rich terminal summary, with human-review footer. |
| `cli.py` | `pfmea-control-plan` command wiring the pipeline together. |

## Matching model
Rows are matched by a **normalised `operation_id`** (`core/matching.py`): lower-cased with
non-alphanumeric characters stripped, so `Op 10`, `op-10` and `10` collapse to the same key. PFMEA
and Control Plan rows are grouped per operation; an operation present in only one document is
surfaced as `UNMATCHED_PROCESS_STEP` rather than dropped. Duplicate rows for one operation are
grouped and evaluated together. Matching by description/fuzzy keys is out of MVP scope.

## Scoring model
Score starts at 100 and is reduced per finding: **critical −15**, **warning −4**, clamped to
`[0, 100]`. Verdict bands: `PASS` (no findings), `PASS-WITH-WARNINGS` (no criticals),
`NEEDS-REVIEW` (a critical and score ≥ 50), `FAIL` (a critical and score < 50). Weights are kept
conservative so warnings cannot dominate the verdict (false-positive protection, [DECISIONS.md](DECISIONS.md) D3).
Full detail and the per-type rationale live in [FINDINGS.md](FINDINGS.md).

## Rules: metadata in YAML, evaluation in Python
`rules/pfmea_control_plan_rules.yaml` is the **single source of truth for rule metadata** — each
rule's `id`, `severity`, `title`, `message_template`, `description` and `rationale`. The loader
(`rules.load_rule_specs()` / `parse_rule_specs()`) reads and validates it, failing clearly on a
missing id, missing required field, invalid severity, duplicate id or an empty ruleset.

The checker in `modules/pfmea_control_plan.py` reads that metadata — it builds each `Finding` with
the severity and the formatted `message_template` from the YAML rather than hardcoding them. The
deliberate split is:

- **YAML → rule metadata** (what a rule is, how severe it is, how it reads).
- **Python → rule evaluation** (the per-finding-type detection logic stays in the module).

This is intentionally *not* a generic rule engine: the bespoke evaluation logic remains in code.
A consistency test plus behaviour-parity tests (seeded example, clean case, warnings case) ensure
the YAML and the code never drift and that finding types, severities, count, score, verdict, and
the Markdown/JSON output are unchanged from v0.2.

## Known limitations (MVP)
- **`.xlsx` only**; one worksheet is read per file (selectable by name via `--pfmea-sheet` /
  `--control-plan-sheet`, otherwise the active sheet). The header row is auto-located within the
  first few rows, but merged/multi-line header cells are not specially handled.
- **Recommended template + fixed aliases** only — no configurable column mapping (v0.2).
- **Weak-method detection is heuristic** (phrase matching) and English-oriented; shipped as warnings.
- **Matching is exact on normalised `operation_id`** — no fuzzy/description matching.
- Single module (PFMEA ↔ Control Plan); other documents are out of scope.

## Testing strategy
Unit tests per stage (parsing, matching, rules, scoring, report), edge-case/robustness tests
(missing columns, non-`.xlsx`, empty workbook, non-numeric severity, missing/duplicate operation
ids, extra columns, header not on row 1), a YAML↔code consistency test, and an end-to-end test over
the bundled synthetic examples asserting the seeded gap appears. CI targets Windows + Linux,
Python 3.12 and 3.13.
