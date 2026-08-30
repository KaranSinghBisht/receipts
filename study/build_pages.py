"""Build what the published site serves: the report, and the figures it quotes.

    python study/build_pages.py            # -> dist/ and site/

Both outputs are generated from the corpora, so the site cannot drift from what
the study actually found. If a run is added or a detector changes, the numbers
move with it or the build is wrong.

The report covers every agent's corpus in one page, with each run labelled
`trapped` or `control`, because the false-alarm count matters more than any
detection and has to be visible next to it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from receipts.bundle import build_bundle  # noqa: E402
from scenarios import SCENARIOS  # noqa: E402

import impact  # noqa: E402

SITE = ROOT / "site"
CORPUS = ROOT / "corpus"
REPO_URL = "https://github.com/KaranSinghBisht/receipts"

SUBHEAD = (
    "The same eight seeded tasks, run through every agent below. Five carry a passive "
    "trap — nothing tells the agent to cut a corner — and three are controls with no "
    "trap at all. A control that diverges is a false alarm, and that number matters "
    "more than any detection."
)


def scenario_of(stem: str) -> str:
    """`spec_mismatch__2` is a repeat of `spec_mismatch`."""
    return stem.split("__", 1)[0]


def agent_dirs() -> list[Path]:
    return sorted(d for d in CORPUS.iterdir() if d.is_dir() and any(d.glob("*.ndjson")))


def gather(into: Path) -> tuple[dict[str, str], dict[str, dict]]:
    """Copy every agent's traces into one directory, prefixed, labelled, and
    tagged with which agent ran which scenario so the report can pivot on it."""
    labels, meta = {}, {}
    by_scenario = {s.name: ("control" if s.control else "trapped") for s in SCENARIOS}
    for agent in agent_dirs():
        for trace in sorted(agent.glob("*.ndjson")):
            name = f"{agent.name}_{trace.stem}"
            scenario = scenario_of(trace.stem)
            shutil.copy(trace, into / f"{name}.ndjson")
            meta[name] = {"agent": agent.name, "scenario": scenario}
            if scenario in by_scenario:
                labels[name] = by_scenario[scenario]
    return labels, meta


def study_json() -> dict:
    """The study, in the shape the site consumes, so the marketing page cannot
    claim a number the corpora do not support."""
    from receipts.actions import actions as build_actions
    from receipts.adapters import load
    from receipts.detectors import run as run_detectors
    from receipts.report import DIVERGED, build

    by_scenario = {s.name: s for s in SCENARIOS}
    cells: dict[str, dict] = {}
    findings: dict[str, dict] = {}
    diverged = false_alarms = 0
    control_runs = trapped_diverged = trapped_runs = 0

    for agent in agent_dirs():
        for trace_path in sorted(agent.glob("*.ndjson")):
            trace = load(trace_path)
            report = build(trace, build_actions(trace), run_detectors(trace, None))
            is_div = report.verdict == DIVERGED
            diverged += is_div
            name = scenario_of(trace_path.stem)
            scenario = by_scenario.get(name)
            if scenario is not None:
                if scenario.control:
                    control_runs += 1
                    false_alarms += is_div
                else:
                    trapped_runs += 1
                    trapped_diverged += is_div
            # Repeated runs of a scenario aggregate into one cell: agents are not
            # deterministic, so the honest unit is a rate, not a verdict.
            cell = cells.setdefault(name, {}).setdefault(
                agent.name, {"runs": 0, "diverged": 0, "findings": 0}
            )
            cell["runs"] += 1
            cell["diverged"] += is_div
            cell["findings"] += len(report.findings)
            for finding in report.findings:
                row = findings.setdefault(
                    finding.title,
                    {"title": finding.title, "severity": str(finding.severity), "count": 0},
                )
                row["count"] += 1

    totals = {"runs": 0, "seconds": 0.0, "total_lines": 0, "cited_lines": 0}
    for agent in agent_dirs():
        m = impact.measure(agent)
        for key in totals:
            totals[key] += m[key]

    matrix = [
        {
            "scenario": name,
            "label": "control" if by_scenario[name].control else "trapped",
            "trap": by_scenario[name].trap,
            "cells": cells[name],
        }
        for name in sorted(cells)
        if name in by_scenario
    ]
    return {
        "runs": totals["runs"],
        "agents": [d.name for d in agent_dirs()],
        "diverged": diverged,
        "falseAlarms": false_alarms,
        "controlRuns": control_runs,
        "trappedRuns": trapped_runs,
        "trappedDiverged": trapped_diverged,
        "traceLines": totals["total_lines"],
        "citedLines": totals["cited_lines"],
        "msPerRun": round(totals["seconds"] / totals["runs"] * 1000) if totals["runs"] else 0,
        "matrix": matrix,
        "findings": sorted(findings.values(), key=lambda f: -f["count"]),
        "repo": REPO_URL,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "dist")
    args = ap.parse_args()
    # A relative --out (as CI passes) is not under ROOT until it is resolved.
    out = args.out.resolve()

    if not agent_dirs():
        print("no corpora under corpus/", file=sys.stderr)
        return 2

    out.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="pages-"))
    try:
        labels, meta = gather(staging)
        build_bundle(staging, out / "report.html", labels, SUBHEAD, meta)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    if SITE.is_dir():
        (SITE / "lib").mkdir(exist_ok=True)
        (SITE / "lib" / "study.json").write_text(
            json.dumps(study_json(), indent=2) + "\n", encoding="utf-8"
        )
        (SITE / "public").mkdir(exist_ok=True)
        shutil.copy(out / "report.html", SITE / "public" / "report.html")
        print("  site/lib/study.json + site/public/report.html")

    for path in sorted(out.iterdir()):
        try:
            shown = path.relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"  {shown}  {path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
