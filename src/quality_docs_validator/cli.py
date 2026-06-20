"""Command-line interface for quality-docs-validator.

Scaffold stage: the `pfmea-control-plan` command is registered so the CLI wiring and
entry points (`quality-docs-validator`, `qdv`) are real and testable, but the underlying
checker is not implemented yet. It exits with a clear "not implemented" message.
"""

from __future__ import annotations

import typer

from . import __version__

app = typer.Typer(
    add_completion=False,
    help="Detect potential inconsistencies between PFMEA and Control Plan documents.",
)


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
    pfmea: str = typer.Option(..., "--pfmea", help="Path to the PFMEA .xlsx file."),
    control_plan: str = typer.Option(
        ..., "--control-plan", help="Path to the Control Plan .xlsx file."
    ),
    output: str = typer.Option(
        "reports/report.md", "--output", help="Path for the generated Markdown report."
    ),
) -> None:
    """Check a PFMEA against a Control Plan for potential inconsistencies. (Not implemented yet.)"""
    typer.secho(
        "pfmea-control-plan is not implemented yet — this is a scaffold build. "
        "See docs/ROADMAP.md for the implementation plan.",
        fg=typer.colors.YELLOW,
    )
    raise typer.Exit(code=1)


if __name__ == "__main__":  # pragma: no cover
    app()
