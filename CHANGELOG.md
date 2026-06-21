# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-21

### Added
- Multi-sheet workbook support: `--pfmea-sheet` / `--control-plan-sheet` select a worksheet by name
  (the active sheet is still used when omitted, so existing behaviour is unchanged). A missing sheet
  raises a clear error listing the available sheet names. Header auto-detection still applies to the
  selected sheet. ([#4](https://github.com/migmcc/quality-docs-validator/issues/4))
- More common column-header aliases for both PFMEA and Control Plan (e.g. `Operation No`/`Op #`/
  `Process No`, `Severity Rating`, `Detection Method`, `Special Characteristics`/`Key
  Characteristic`/`Critical Characteristic`, `Control Technique`/`Measurement Technique`,
  `Out of Control Action`). Existing aliases and behaviour are unchanged.
  ([#2](https://github.com/migmcc/quality-docs-validator/issues/2))
- JSON report output via `--format json` (Markdown remains the default). The JSON includes
  `metadata` (tool, version, UTC timestamp, format), `inputs`, `verdict`, `score`, a `summary`
  (counts by severity and by finding type) and the full `findings` list. Validation, scoring and
  matching behaviour are unchanged. ([#3](https://github.com/migmcc/quality-docs-validator/issues/3))

## [0.1.0] - 2026-06-20

First public release — the PFMEA ↔ Control Plan consistency checker MVP.

### Added
- Initial repository scaffold: packaging (`pyproject.toml`, Python 3.12+), `src/` layout,
  test/docs/examples structure, MIT license, CI stub.
- Project documentation: `docs/DECISIONS.md`, `docs/MVP_SCOPE.md`, `docs/ARCHITECTURE.md`,
  `docs/ROADMAP.md`.
- **PFMEA ↔ Control Plan vertical slice** (functional): `.xlsx` parser with column aliases,
  operation matching, six finding types (`UNMATCHED_PROCESS_STEP`, `MISSING_CONTROL`,
  `SPECIAL_CHARACTERISTIC_NOT_CONTROLLED`, `MISSING_REACTION_PLAN`, `WEAK_DETECTION_METHOD`,
  `HIGH_SEVERITY_WEAK_CONTROL`), severity-weighted scoring with verdict bands, Markdown report and
  rich terminal summary.
- `pfmea-control-plan` CLI command wired to the pipeline (`--pfmea`, `--control-plan`, `--out`).
- Synthetic example workbooks with a seeded gap (`examples/generate_examples.py`) and end-to-end
  tests.
- Hardening (Run D): parser now auto-locates the header row (tolerates a leading title row),
  ignores extra columns, and raises clear errors for non-`.xlsx`, missing files, empty
  workbooks/worksheets and missing `operation_id` columns.
- `docs/FINDINGS.md` documenting all six finding types, the weak-method heuristic, scoring weights
  and verdict bands; expanded `docs/ARCHITECTURE.md` (matching, scoring, limitations).
- YAML↔code consistency: `rules.load_rule_specs()` plus a test asserting documented severities
  match the emitted findings.
- 12 edge-case/robustness tests and CI coverage reporting (`pytest-cov`).

### Changed
- `WEAK_DETECTION_METHOD` heuristic narrowed to specific phrases (no bare `operator`/`manual`) to
  cut false positives; `WEAK_DETECTION_METHOD` and `HIGH_SEVERITY_WEAK_CONTROL` remain warnings.

### Notes
- Validation rules are currently implemented in `modules/pfmea_control_plan.py`; the
  `rules/*.yaml` file documents them (id + severity, kept in sync by a test) and will become the
  rule source in a later iteration.
- JSON/HTML output, CSV input and configurable column mapping remain roadmapped (v0.2).

[Unreleased]: https://github.com/migmcc/quality-docs-validator/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/migmcc/quality-docs-validator/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/migmcc/quality-docs-validator/releases/tag/v0.1.0
