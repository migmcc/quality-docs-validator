"""Smoke tests: package imports, version, and CLI wiring."""

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
