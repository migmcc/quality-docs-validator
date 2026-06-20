# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  `rules/*.yaml` file documents them and will become the rule source in a later iteration.
- Not yet released. JSON/HTML output, CSV input and configurable mapping remain roadmapped (v0.2).

<!--
## [0.1.0] - YYYY-MM-DD
First functional MVP: PFMEA ↔ Control Plan checker, ≥5 finding types, Markdown report,
terminal summary, bundled examples.
-->
