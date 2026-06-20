# Roadmap

## v0.1.0 — MVP (PFMEA ↔ Control Plan checker) ✅ released
The single, narrow vertical slice. `.xlsx` only, recommended template + aliases, six finding types,
severity-weighted score, Markdown report + terminal summary, synthetic examples, tests, docs.
See [MVP_SCOPE.md](MVP_SCOPE.md). All work packages (repo skeleton, data models, Excel parser,
matching, rules, scoring, report, CLI, examples, tests + CI, docs, release) are complete.

## v0.2 — planned
Improve interoperability and real-world workbook compatibility while keeping the tool focused on
PFMEA ↔ Control Plan validation. Tracked under the
[v0.2 milestone](https://github.com/migmcc/quality-docs-validator/milestone/1). Recommended order:

1. **JSON output** ([#3](https://github.com/migmcc/quality-docs-validator/issues/3)) — first PR; a
   machine-readable report alongside Markdown (Markdown stays the default).
2. **More PFMEA / Control Plan column aliases**
   ([#2](https://github.com/migmcc/quality-docs-validator/issues/2)) — broaden real-template coverage.
3. **Multi-sheet workbooks** ([#4](https://github.com/migmcc/quality-docs-validator/issues/4)) —
   optional sheet selection.
4. **YAML-driven rules** ([#1](https://github.com/migmcc/quality-docs-validator/issues/1)) —
   *stretch / optional*; a rule-engine refactor, deferred to v0.3 if scope grows.

Still out of scope for v0.2: CSV input, configurable column mapping, HTML output, UI, AI, and any
new document pairs. No dates promised.

## v0.3+ — More modules (each independent of the core)
- Process Flow ↔ PFMEA consistency.
- Control Plan ↔ Work Instructions.
- PPAP gap check.
- 8D, SPC, MSA helpers.

## Explicitly not planned
- Web UI, ERP/MES/QMS integration, PDF/OCR ingestion, mandatory generative AI.
- Any formal/normative conformance certification or legal interpretation.
- Replacing human technical judgement.
