# quality-docs-validator

> Detect **potential inconsistencies between PFMEA and Control Plan** before audits, customer
> submissions or production issues — locally, with simple files, explicit rules and clear reports.

`quality-docs-validator` (CLI: `qdv`) is a **local-first, forkable** tool for quality engineers.
Manual review checks documents one by one, but the real risk lives *between* them: a high-severity
PFMEA failure mode with no matching Control Plan control, a special characteristic missing from the
inspection plan, a missing reaction plan exactly where risk is highest. This tool cross-checks the
two documents and surfaces those gaps as **severity-classified potential findings**.

It **supports, and does not replace, human technical review.**

---

## Status

🧪 **Pre-alpha — working vertical slice.** The PFMEA ↔ Control Plan checker runs end to end:
read two `.xlsx` files → match by operation → detect 6 finding types → score → Markdown report +
terminal summary. Not yet released; rules are currently implemented in code (the YAML is
documentation for now) and the engine is intentionally minimal. See [docs/ROADMAP.md](docs/ROADMAP.md).

## What the MVP (v0.1.0) will do

A single module: **PFMEA ↔ Control Plan consistency checker**.

- Read a PFMEA `.xlsx` and a Control Plan `.xlsx` (recommended template + simple column aliases).
- Match rows by `operation_id` / `process_step`.
- Run explicit, documented rules producing **≥5 finding types**.
- Compute a **severity-weighted score (0–100)** with verdict bands
  (PASS / PASS-WITH-WARNINGS / NEEDS-REVIEW / FAIL).
- Generate a **Markdown report** plus a **rich terminal summary**.

Scope is deliberately narrow. See [docs/MVP_SCOPE.md](docs/MVP_SCOPE.md) and
[docs/DECISIONS.md](docs/DECISIONS.md). `.xlsx`-only; CSV and configurable column mapping are
planned for v0.2 ([docs/ROADMAP.md](docs/ROADMAP.md)).

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
