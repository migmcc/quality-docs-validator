# Contributing

Thanks for your interest in `quality-docs-validator`! This project is in an early scaffold stage.

## Principles

- **Stay in scope.** v0.1.0 is *only* the PFMEA ↔ Control Plan checker, `.xlsx` input. New formats
  (CSV), configurable mapping, additional modules and report formats are roadmapped for v0.2+
  (see [docs/ROADMAP.md](docs/ROADMAP.md)). Please discuss scope-expanding ideas in an issue first.
- **Potential findings, not verdicts.** The tool surfaces *potential* inconsistencies for a human
  to judge. It makes no regulatory/normative conformance claim.
- **Explicit, documented rules.** Every check is named, documented and testable.

## Development setup

```bash
python -m venv .venv
. .venv/Scripts/activate      # Windows;  source .venv/bin/activate on Linux/macOS
pip install -e ".[dev]"
pytest
ruff check .
```

Target runtime is **Python 3.12+**.

## Pull requests

- Keep PRs focused and small.
- Add or update tests for any behaviour change.
- Update `CHANGELOG.md` under `[Unreleased]`.

Good first issues will be labelled `good first issue` once the vertical slice lands.
