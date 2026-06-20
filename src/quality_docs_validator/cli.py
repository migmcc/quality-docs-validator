"""Command-line interface for quality-docs-validator.

Entry points (`quality-docs-validator`, `qdv`) are defined in pyproject.toml. The MVP exposes a
single command, `pfmea-control-plan`, which runs the checker, writes a Markdown report and prints a
terminal summary.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .core.report import print_terminal_summary, write_json, write_markdown
from .modules.pfmea_control_plan import check_files
from .parsers.excel import ParseError


class ReportFormat(str, Enum):
    """Output format for the generated report file."""

    md = "md"
    json = "json"

app = typer.Typer(
    add_completion=False,
    help="Detect potential inconsistencies between PFMEA and Control Plan documents.",
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"quality-docs-validator {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """quality-docs-validator — supports, and does not replace, human technical review."""


@app.command("pfmea-control-plan")
def pfmea_control_plan(
    pfmea: Path = typer.Option(..., "--pfmea", help="Path to the PFMEA .xlsx file."),
    control_plan: Path = typer.Option(
        ..., "--control-plan", help="Path to the Control Plan .xlsx file."
    ),
    out: Path = typer.Option(
        Path("report.md"),
        "--out",
        "--output",
        help="Path for the generated report.",
    ),
    report_format: ReportFormat = typer.Option(
        ReportFormat.md,
        "--format",
        help="Report file format: 'md' (default) or 'json'. Markdown behaviour is unchanged.",
    ),
) -> None:
    """Check a PFMEA against a Control Plan for potential inconsistencies."""
    try:
        result = check_files(pfmea, control_plan)
    except ParseError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    if report_format is ReportFormat.json:
        write_json(result, pfmea.name, control_plan.name, out)
    else:
        write_markdown(result, pfmea.name, control_plan.name, out)
    print_terminal_summary(result, pfmea.name, control_plan.name)
    console.print(f"[dim]Report ({report_format.value}) written to[/dim] {out}")


if __name__ == "__main__":  # pragma: no cover
    app()
