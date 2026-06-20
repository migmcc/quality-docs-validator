# MVP Scope (v0.1.0)

## Goal
Prove that important PFMEA ↔ Control Plan inconsistencies can be detected **automatically** from
simple Excel files using **explicit rules**, a simple **score** and a **clear Markdown report** —
one module, one happy path, end to end.

## In scope
- Single module: **PFMEA ↔ Control Plan consistency checker**.
- Read a PFMEA `.xlsx` and a Control Plan `.xlsx` (recommended template + column aliases).
- Match rows by `operation_id` / `process_step` (or equivalent key).
- Explicit, documented rules producing **≥5 finding types** (of 11 planned).
- **Severity-weighted score** 0–100 with verdict bands
  (PASS / PASS-WITH-WARNINGS / NEEDS-REVIEW / FAIL).
- **Markdown report** (`reports/report.md`) + **rich terminal summary**.
- CLI: `qdv pfmea-control-plan --pfmea ... --control-plan ... --output ...`.
- Bundled **synthetic** examples with ≥1 seeded gap.
- Automated tests, README quickstart (<5 min), MIT license, `CONTRIBUTING.md`, ≥3 good-first-issues.

## Out of scope (see ROADMAP for phasing)
- CSV / `.md` / `.json` / `.yaml` input.
- Fully configurable column mapping.
- JSON / HTML report output, GitHub Action, status badges.
- All other modules (Process Flow↔PFMEA, CP↔Work Instructions, PPAP, 8D, SPC, MSA).
- Web UI, ERP/MES/QMS integration, PDF/OCR, mandatory GenAI.
- Any regulatory/normative conformance claim; replacing human judgement.

## Acceptance criteria (13)
1. Installs locally (`pip install -e .`).
2. Reads ≥1 example PFMEA `.xlsx`.
3. Reads ≥1 example Control Plan `.xlsx`.
4. Matches rows by `operation_id` / `process_step` / equivalent.
5. Identifies ≥5 finding types.
6. Generates a `.md` report.
7. Prints a terminal summary.
8. Has automated tests.
9. Has a README with quickstart.
10. Ships bundled examples.
11. MIT licensed.
12. Has a simple `CONTRIBUTING.md`.
13. Has ≥3 `good first issue` issues.

## Non-goals
- Being exhaustive/authoritative — surfaces **potential** findings only.
- Supporting every customer-specific template on day one.
