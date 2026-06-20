"""Report generation: Markdown file + rich terminal summary.

The Markdown report is plain and self-contained so it can be committed, diffed or attached to an
audit trail. Every report carries a footer making clear the tool supports, but does not replace,
human technical review.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models import ValidationResult

HUMAN_REVIEW_FOOTER = (
    "> ⚠️ These are **potential** findings to support human review. "
    "quality-docs-validator is **not a substitute for human technical judgement** and makes no "
    "regulatory or normative conformance claim."
)

_VERDICT_STYLE = {
    "PASS": "bold green",
    "PASS-WITH-WARNINGS": "bold yellow",
    "NEEDS-REVIEW": "bold yellow",
    "FAIL": "bold red",
}


def render_markdown(result: ValidationResult, pfmea_name: str, control_plan_name: str) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []
    lines.append("# PFMEA ↔ Control Plan Validation Report")
    lines.append("")
    lines.append(f"- **Generated:** {generated}")
    lines.append(f"- **PFMEA:** `{pfmea_name}` ({result.pfmea_rows} rows)")
    lines.append(f"- **Control Plan:** `{control_plan_name}` ({result.control_plan_rows} rows)")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Score:** {result.score} / 100")
    lines.append(f"- **Verdict:** {result.verdict}")
    lines.append(f"- **Critical findings:** {result.critical_count}")
    lines.append(f"- **Warnings:** {result.warning_count}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    if not result.findings:
        lines.append("No potential inconsistencies detected. ✅")
    else:
        lines.append("| # | Type | Level | Operation | Detail |")
        lines.append("|---|------|-------|-----------|--------|")
        for i, f in enumerate(result.findings, start=1):
            level = "🔴 critical" if f.level == "critical" else "🟡 warning"
            detail = f.message.replace("|", "\\|")
            lines.append(f"| {i} | {f.finding_type} | {level} | {f.operation_id} | {detail} |")
    lines.append("")
    lines.append(HUMAN_REVIEW_FOOTER)
    lines.append("")
    return "\n".join(lines)


def write_markdown(
    result: ValidationResult, pfmea_name: str, control_plan_name: str, out_path: str | Path
) -> Path:
    out_path = Path(out_path)
    if out_path.parent and not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        render_markdown(result, pfmea_name, control_plan_name), encoding="utf-8"
    )
    return out_path


def print_terminal_summary(
    result: ValidationResult, pfmea_name: str, control_plan_name: str, console: Console | None = None
) -> None:
    console = console or Console()
    style = _VERDICT_STYLE.get(result.verdict, "bold")

    if result.findings:
        table = Table(title="Potential findings", show_lines=False)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Level")
        table.add_column("Op", no_wrap=True)
        table.add_column("Detail")
        for f in result.findings:
            level = "[red]critical[/red]" if f.level == "critical" else "[yellow]warning[/yellow]"
            table.add_row(f.finding_type, level, f.operation_id, f.message)
        console.print(table)
    else:
        console.print("[green]No potential inconsistencies detected.[/green]")

    summary = (
        f"PFMEA: {pfmea_name} ({result.pfmea_rows} rows)   "
        f"Control Plan: {control_plan_name} ({result.control_plan_rows} rows)\n"
        f"Score: [{style}]{result.score}/100[/{style}]   "
        f"Verdict: [{style}]{result.verdict}[/{style}]   "
        f"Critical: {result.critical_count}   Warnings: {result.warning_count}"
    )
    console.print(Panel(summary, title="quality-docs-validator", expand=False))
    console.print(
        "[dim]Potential findings only — not a substitute for human technical review.[/dim]"
    )
