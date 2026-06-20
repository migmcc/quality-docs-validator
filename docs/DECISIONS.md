# Decisions

Locked decisions carried into the repository from incubation (confirmed 2026-06-18). These are
binding for the v0.1.0 MVP.

## D1 — MVP input format
**`.xlsx` only.** CSV input is deferred to v0.2. Reduces ambiguity and parsing surface for the MVP.

## D2 — Template handling
**Recommended template + simple column aliases** for common columns. No fully configurable column
mapping in the MVP (deferred to v0.2).

## D3 — Warning-level checks
`WEAK_DETECTION_METHOD` and `HIGH_SEVERITY_WEAK_CONTROL` ship as **warnings**, not critical
findings, to reduce false positives until validated against real examples.

## D4 — Project location
Standalone, durable repository at `D:\Trabalho\quality-docs-validator` — sibling of
`D:\Trabalho\SkillLab`. Intended to be published public and MIT-licensed.

## Carried-forward (pre-decided in the source brief)
- First and only MVP module: **PFMEA ↔ Control Plan**.
- Severity-weighted score 0–100 with verdict bands PASS / PASS-WITH-WARNINGS / NEEDS-REVIEW / FAIL.
- Markdown report + rich terminal summary; JSON output deferred to v0.2.
- CLI exposes both `quality-docs-validator` and the `qdv` alias.

## Scaffold-stage technical decisions (Run B, 2026-06-20)
- **Build backend:** `hatchling` with a `src/` layout (clean import isolation, modern packaging).
- **Runtime:** Python **3.12+**.
- **CLI framework:** `typer` (concise, type-driven; ships the `qdv` alias via a second entry point).
- **Planned engine deps:** `openpyxl`, `pydantic`, `jinja2`, `rich`, `pyyaml` — declared but not yet
  used (no engine code in the scaffold).
- **Rules as data:** validation rules live in versioned YAML under `rules/`, not hardcoded, so
  checks stay explicit, documented and reviewable.
