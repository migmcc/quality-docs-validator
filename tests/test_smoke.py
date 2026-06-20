"""Smoke tests for the scaffold.

These assert that the package imports, exposes a version, and that the CLI is wired up.
They are intentionally minimal placeholders; behavioural tests for matching, rules, scoring
and reporting arrive with the vertical slice (see docs/ROADMAP.md).
"""

from __future__ import annotations

from typer.testing import CliRunner

import quality_docs_validator
from quality_docs_validator.cli import app

runner = CliRunner()


def test_package_exposes_version() -> None:
    assert isinstance(quality_docs_validator.__version__, str)
    assert quality_docs_validator.__version__


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "quality-docs-validator" in result.stdout


def test_pfmea_control_plan_is_stubbed() -> None:
    # The command exists and currently exits non-zero with a clear not-implemented message.
    result = runner.invoke(
        app,
        ["pfmea-control-plan", "--pfmea", "a.xlsx", "--control-plan", "b.xlsx"],
    )
    assert result.exit_code == 1
    assert "not implemented" in result.stdout.lower()
