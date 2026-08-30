"""One self-contained page covering many runs.

An overview of every trace in a directory, with each run's full evidence — claim,
findings, execution timeline — embedded in the same file. No server, no assets,
no network: it can be attached to a pull request, published as a CI artifact, or
opened from a USB stick three years later and still work.

The single-trace bundle in `html.py` is the same idea for one run. This is the
view a reviewer opens when they want to know which of last night's runs are worth
their attention.
"""

from __future__ import annotations

import html as html_mod
import json
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .actions import ActionKind, actions as build_actions
from .adapters import UnknownTraceFormat, load
from .detectors import run as run_detectors
from .html import embed, timeline_rows
from .report import DIVERGED, Report, build

_TEMPLATE = Path(__file__).with_name("dashboard_template.html")


class NoTraces(ValueError):
    """Raised when a directory holds nothing that parses as a trace."""


def _strip(report: Report, flagged: set[int]) -> list[str]:
    """One cell per tool call, for the miniature timeline on a run card."""
    cells = []
    for action in report.actions:
        if action.kind not in (ActionKind.RUN_COMMAND, ActionKind.WRITE_FILE):
            continue
        cells.append("flag" if action.seq in flagged else str(action.outcome))
    return cells[:80]


def _entry(name: str, report: Report, label: str | None, meta: dict | None = None) -> dict:
    data = report.as_dict()
    flagged = {e.seq for f in report.findings for e in f.evidence if e.seq >= 0}
    meta = meta or {}
    return {
        "name": name,
        # `scenario` and `agent` let a batch be pivoted: the same task across
        # agents is the comparison a reviewer wants, and it is invisible in a flat
        # list. Both fall back to what the trace itself reports.
        "scenario": meta.get("scenario", name),
        "label": label,
        "verdict": data["verdict"],
        "agent": meta.get("agent") or data["agent"],
        "claim": data["claim"],
        "findings": data["findings"],
        "files_written": len(data["ground_truth"]["files_written"]),
        "commands": len(data["ground_truth"]["commands"]),
        "commands_detail": data["ground_truth"]["commands"],
        "tool_calls": data["run"]["tool_calls"],
        "duration_ms": data["run"]["duration_ms"],
        "cost": data["run"]["cost"],
        "timeline": timeline_rows(report),
        "strip": _strip(report, flagged),
    }


def _headline(total: int, diverged: int) -> str:
    runs = f"{total} agent run{'s' if total != 1 else ''}"
    if not diverged:
        return f"{runs}, every summary backed by its trace"
    return f"{diverged} of {runs} claimed something their execution trace does not support"


DEFAULT_SUBHEAD = (
    "Each run was replayed against the record of what it actually did — the files it "
    "wrote, the commands it ran, and what those commands printed."
)


def build_payload(
    traces: Path,
    labels: dict[str, str] | None = None,
    subhead: str | None = None,
    meta: dict[str, dict] | None = None,
) -> dict:
    """Audit every `*.ndjson` under `traces` and return the page's data."""
    paths = sorted(traces.glob("*.ndjson"))
    if not paths:
        raise NoTraces(f"no .ndjson traces in {traces}")

    labels = labels or {}
    entries, skipped = [], []
    for path in paths:
        try:
            trace = load(path)
        except (UnknownTraceFormat, ValueError, OSError) as exc:
            skipped.append(f"{path.name}: {exc}")
            continue
        report = build(trace, build_actions(trace), run_detectors(trace, None))
        entry = _entry(path.stem, report, labels.get(path.stem), (meta or {}).get(path.stem))
        # What reading this run by hand would cost, and what the audit points at.
        entry["traceLines"] = sum(1 for line in path.open() if line.strip())
        entry["citedLines"] = len(
            {e.seq for f in report.findings for e in f.evidence if e.seq >= 0}
        )
        entries.append(entry)

    if not entries:
        raise NoTraces(f"no parsable traces in {traces} ({'; '.join(skipped[:3])})")

    diverged = sum(1 for e in entries if e["verdict"] == DIVERGED)
    payload = {
        "receipts_version": __version__,
        "generated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "headline": _headline(len(entries), diverged),
        "subhead": subhead or DEFAULT_SUBHEAD,
        "totals": {
            "diverged": diverged,
            "clean": len(entries) - diverged,
            "findings": sum(len(e["findings"]) for e in entries),
            "trace_lines": sum(e["traceLines"] for e in entries),
            "cited_lines": sum(e["citedLines"] for e in entries),
            # Only meaningful when runs are labelled: a control that diverges is
            # a false alarm, and that number matters more than any detection.
            "false_alarms": (
                sum(1 for e in entries if e["verdict"] == DIVERGED and e["label"] == "control")
                if labels
                else None
            ),
        },
        "agents": sorted({e["agent"] for e in entries}),
        "scenarios": sorted({e["scenario"] for e in entries}),
        "runs": entries,
    }
    return payload


def render(payload: dict) -> str:
    """Embed a payload into the standalone page."""
    title = f"Receipts \u2014 {len(payload['runs'])} runs"
    return (
        _TEMPLATE.read_text(encoding="utf-8")
        .replace("/*__RECEIPTS_DATA__*/null", embed(payload))
        .replace("__RECEIPTS_TITLE__", html_mod.escape(title))
    )


def build_bundle(
    traces: Path,
    destination: Path,
    labels: dict[str, str] | None = None,
    subhead: str | None = None,
    meta: dict[str, dict] | None = None,
) -> Path:
    """Render every `*.ndjson` under `traces` into a single HTML file."""
    payload = build_payload(traces, labels, subhead, meta)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render(payload), encoding="utf-8")
    return destination


def load_labels(path: Path) -> dict[str, str]:
    """Optional `{name: label}` JSON, used to mark control runs in the overview."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read labels from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected an object of name -> label")
    return {str(k): str(v) for k, v in value.items()}
