# Roadmap

## v0.1.0 — MVP (PFMEA ↔ Control Plan checker) ✅ released
The single, narrow vertical slice. `.xlsx` only, recommended template + aliases, six finding types,
severity-weighted score, Markdown report + terminal summary, synthetic examples, tests, docs.
See [MVP_SCOPE.md](MVP_SCOPE.md). All work packages (repo skeleton, data models, Excel parser,
matching, rules, scoring, report, CLI, examples, tests + CI, docs, release) are complete.

## v0.2 — done (pending release)
Interoperability and real-world workbook compatibility, kept focused on PFMEA ↔ Control Plan
validation. Tracked under the
[v0.2 milestone](https://github.com/migmcc/quality-docs-validator/milestone/1). All three items are
merged to `main`; the `v0.2.0` tag/release is a separate step.

- ✅ **JSON output** ([#3](https://github.com/migmcc/quality-docs-validator/issues/3)) — a
  machine-readable report alongside Markdown (Markdown stays the default).
- ✅ **More PFMEA / Control Plan column aliases**
  ([#2](https://github.com/migmcc/quality-docs-validator/issues/2)) — broader real-template coverage.
- ✅ **Multi-sheet workbooks** ([#4](https://github.com/migmcc/quality-docs-validator/issues/4)) —
  optional `--pfmea-sheet` / `--control-plan-sheet` selection.

Still out of scope for v0.2: CSV input, configurable column mapping, HTML output, UI, AI, and any
new document pairs.

## v0.3 — planned (YAML rules as source of truth)
Tracked under the [v0.3 milestone](https://github.com/migmcc/quality-docs-validator/milestone/2).
Deliberately small and low-risk — **no new features, no behaviour change**:

- **YAML-driven rule *metadata*** ([#1](https://github.com/migmcc/quality-docs-validator/issues/1)) —
  make `rules/pfmea_control_plan_rules.yaml` the single source of truth for each rule's **id,
  severity, title/message template, description and rationale**, and have
  `modules/pfmea_control_plan.py` read that metadata instead of hardcoding it. The **evaluation
  logic stays in Python**; we are *not* building a generic rule engine.
- **Parity tests** — prove the synthetic examples, a clean case and a warnings case produce the
  exact same finding types, severities, count, score and verdict as v0.2 (Markdown + JSON unchanged).
- **Rule documentation** generated/kept in sync from the YAML metadata.

Out of scope for v0.3: new document pairs, CSV, configurable mapping, UI, AI, PyPI, new scoring,
fuzzy matching, JSON-schema changes, and any change to the finding types.

## v0.4+ — More modules (each independent of the core)
- Process Flow ↔ PFMEA consistency.
- Control Plan ↔ Work Instructions.
- PPAP gap check.
- 8D, SPC, MSA helpers.

## Explicitly not planned
- Web UI, ERP/MES/QMS integration, PDF/OCR ingestion, mandatory generative AI.
- Any formal/normative conformance certification or legal interpretation.
- Replacing human technical judgement.
