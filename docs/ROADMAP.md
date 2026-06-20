# Roadmap

## v0.1.0 — MVP (PFMEA ↔ Control Plan checker)
The single, narrow vertical slice. `.xlsx` only, recommended template + aliases, ≥5 finding types,
severity-weighted score, Markdown report + terminal summary, synthetic examples, tests, docs.
See [MVP_SCOPE.md](MVP_SCOPE.md).

**Build sequence (work packages):**
- WP1 ✅ Repo skeleton & packaging *(this scaffold)*
- WP2 ⏳ Data models (`PFMEARow`, `ControlPlanRow`, `Finding`) + column-alias map
- WP3 ⏳ Excel parser (`parsers/excel.py`)
- WP4 ⏳ Matching engine (`core/matching.py`)
- WP5 ⏳ Validation rules (`modules/pfmea_control_plan.py` + `rules/*.yaml`)
- WP6 ⏳ Scoring (`core/scoring.py`)
- WP7 ⏳ Report generator (`core/report.py`)
- WP8 ⏳ CLI command body (`cli.py`)
- WP9 ⏳ Synthetic examples with a seeded gap
- WP10 ⏳ Tests + Windows/Linux CI
- WP11 ⏳ Docs & ≥3 good-first-issues
- WP12 ⏳ Release v0.1.0

## v0.2 — Flexibility
- **CSV input** (in addition to `.xlsx`).
- **Configurable column mapping** (beyond recommended template + aliases).
- **JSON / HTML report** output; GitHub Action summary; status badges.

## v0.3+ — More modules (each independent of the core)
- Process Flow ↔ PFMEA consistency.
- Control Plan ↔ Work Instructions.
- PPAP gap check.
- 8D, SPC, MSA helpers.

## Explicitly not planned
- Web UI, ERP/MES/QMS integration, PDF/OCR ingestion, mandatory generative AI.
- Any formal/normative conformance certification or legal interpretation.
- Replacing human technical judgement.
