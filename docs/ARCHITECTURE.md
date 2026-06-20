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

## Scoring model
Each finding type carries a severity weight; critical findings cost more than warnings. The score
starts at 100 and is reduced by weighted findings, then mapped to a verdict band. Exact weights are
defined alongside the rules and tuned against the synthetic examples (kept conservative to limit
false positives — see [DECISIONS.md](DECISIONS.md) D3).

## Testing strategy
Unit tests per stage (parsing, matching, rules, scoring, report) plus an end-to-end test over the
bundled synthetic examples asserting the seeded gap appears. CI runs on Windows + Linux.
