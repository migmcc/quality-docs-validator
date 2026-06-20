# quality-docs-validator

[![CI](https://github.com/migmcc/quality-docs-validator/actions/workflows/ci.yml/badge.svg)](https://github.com/migmcc/quality-docs-validator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)

> Detect **potential inconsistencies between PFMEA and Control Plan** before audits, customer
> submissions or production issues — locally, with simple files, explicit rules and clear reports.

`quality-docs-validator` (CLI: `qdv`) is a **local-first, forkable** tool for quality engineers.

## The problem

Quality documents are reviewed one at a time, but the real risk lives **between** them: a
high-severity PFMEA failure mode with no matching Control Plan control, a special characteristic
missing from the inspection plan, a missing reaction plan exactly where risk is highest. These gaps
surface late — at audits, customer submissions or as field complaints. This tool cross-checks the
two documents and surfaces those gaps as **severity-classified potential findings**.

> ⚠️ It **supports, and does not replace, human technical review.** Findings are *potential*
> inconsistencies for an engineer to judge; the tool makes no regulatory or normative conformance
> claim.

## Who it's for

Quality / Process / Manufacturing Engineers, SQEs, internal auditors and APQP/PPAP teams — and
anyone using coding agents to automate quality workflows. Runs entirely on your machine, so
confidential supplier/customer data never leaves it.

## What it validates

A single module: **PFMEA ↔ Control Plan consistency checker**.

- Reads a PFMEA `.xlsx` and a Control Plan `.xlsx` (recommended template + simple column aliases).
- Matches rows by `operation_id` / process step.
- Applies six explicit, documented checks (see [docs/FINDINGS.md](docs/FINDINGS.md)):
  `UNMATCHED_PROCESS_STEP`, `MISSING_CONTROL`, `SPECIAL_CHARACTERISTIC_NOT_CONTROLLED`,
  `MISSING_REACTION_PLAN`, `WEAK_DETECTION_METHOD` (warning), `HIGH_SEVERITY_WEAK_CONTROL` (warning).
- Computes a **severity-weighted score (0–100)** with verdict bands
  (PASS / PASS-WITH-WARNINGS / NEEDS-REVIEW / FAIL).
- Generates a **Markdown report** plus a **rich terminal summary**.

## What it does *not* validate (by design)

- ❌ CSV / other input formats — `.xlsx` only (CSV planned for v0.2).
- ❌ Configurable column mapping — recommended template + fixed aliases only (v0.2).
- ❌ Other document pairs (Process Flow ↔ PFMEA, Work Instructions, PPAP, 8D, SPC, MSA).
- ❌ Web UI, ERP/MES/QMS integration, PDF/OCR, or any AI dependency.
- ❌ Regulatory/standard conformance certification, or replacing human judgement.

Scope is deliberately narrow — see [docs/MVP_SCOPE.md](docs/MVP_SCOPE.md),
[docs/DECISIONS.md](docs/DECISIONS.md) and the [roadmap](docs/ROADMAP.md).

## Quickstart

```bash
pip install -e .
qdv pfmea-control-plan \
  --pfmea examples/pfmea.xlsx \
  --control-plan examples/control-plan.xlsx \
  --out report.md
```

This runs against the bundled synthetic examples (which contain a deliberately seeded gap) and
writes `report.md` plus a terminal summary. Regenerate the examples with
`python examples/generate_examples.py`.

Expected terminal summary (abridged):

```text
                       Potential findings
  Type                                   Level     Op  Detail
 ─────────────────────────────────────────────────────────────────
  UNMATCHED_PROCESS_STEP                 warning   40  no Control Plan row
  SPECIAL_CHARACTERISTIC_NOT_CONTROLLED  critical  20  not marked special in CP
  MISSING_REACTION_PLAN                  critical  20  S=9, no reaction plan
  WEAK_DETECTION_METHOD                  warning   20  visual inspection
  HIGH_SEVERITY_WEAK_CONTROL             warning   20  S=9 + weak control
  MISSING_CONTROL                        critical  30  no control method

╭───────────────── quality-docs-validator ─────────────────╮
│ Score: 43/100   Verdict: FAIL   Critical: 3   Warnings: 3 │
╰───────────────────────────────────────────────────────────╯
```

The full Markdown report is written to `report.md`; a committed sample lives at
[examples/report.md](examples/report.md). Finding types and scoring are documented in
[docs/FINDINGS.md](docs/FINDINGS.md).

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the module layout and data flow.

## License

[MIT](LICENSE). Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
