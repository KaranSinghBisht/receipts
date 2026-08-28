"""Terminal rendering. Plain text only: this output is read in CI logs."""

from __future__ import annotations

from .report import CLEAN, Report

_MARK = {"high": "!!", "medium": " !", "low": "  "}
_RULE = "─" * 68


def render(report: Report) -> str:
    lines = [_RULE, _headline(report), _RULE, ""]
    lines.append(f'  claimed: "{_clip(report.trace.final_message, 200)}"')
    lines.append(f"  actual : {_ground_truth(report)}")
    lines.append("")

    if not report.findings:
        lines.append("  No divergence found between the summary and the trace.")
        lines.append("")
        return "\n".join(lines)

    for index, finding in enumerate(report.findings, start=1):
        lines.append(f"{_MARK[str(finding.severity)]} {index}. {finding.title}")
        lines.append(f"     {finding.detail}")
        for item in finding.evidence:
            where = f"event {item.seq}" if item.seq >= 0 else "summary"
            lines.append(f"     · [{where}] {item.label}")
            if item.excerpt:
                lines.append(f"       {_clip(item.excerpt, 160)}")
        lines.append("")
    return "\n".join(lines)


def _headline(report: Report) -> str:
    if report.verdict == CLEAN:
        return f"RECEIPTS · clean · {report.trace.source}"
    tally = report.counts()
    parts = [f"{tally[key]} {key}" for key in ("high", "medium", "low") if tally[key]]
    return f"RECEIPTS · diverged · {', '.join(parts)} · {report.trace.source}"


def _ground_truth(report: Report) -> str:
    data = report.as_dict()["ground_truth"]
    commands, files = data["commands"], data["files_written"]
    failed = sum(1 for c in commands if c["outcome"] == "error")
    return (
        f"{len(files)} file(s) written, {len(commands)} command(s) run"
        f"{f', {failed} failed' if failed else ''}"
    )


def _clip(text: str, limit: int) -> str:
    flat = " ".join((text or "").split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"
