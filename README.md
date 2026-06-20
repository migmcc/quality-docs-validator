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

🚧 **Pre-alpha — scaffold only.** The repository structure, packaging and documentation are in
place. The validation engine (Excel parsing, matching, rules, scoring, reports) is the next phase
(see [docs/ROADMAP.md](docs/ROADMAP.md)). No working checks are shipped yet.

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

## Planned quickstart (not yet functional)

```bash
pip install -e .
qdv pfmea-control-plan \
  --pfmea examples/pfmea.xlsx \
  --control-plan examples/control-plan.xlsx \
  --output reports/report.md
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the module layout and data flow.

## License

[MIT](LICENSE). Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
