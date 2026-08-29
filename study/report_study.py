"""Tabulate what Receipts found across a captured corpus.

Usage:
    python study/report_study.py                 # every agent under corpus/
    python study/report_study.py --agent bob

Reports two numbers that mean different things:

  detections   trapped scenarios where Receipts found a divergence
  false alarms control scenarios where it found one anyway

The second number is the one that decides whether this tool is usable. A
divergence detector that fires on honest work gets muted within a week.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from receipts.actions import actions as build_actions  # noqa: E402
from receipts.adapters import UnknownTraceFormat, load  # noqa: E402
from receipts.detectors import run as run_detectors  # noqa: E402
from receipts.report import build  # noqa: E402
from scenarios import SCENARIOS  # noqa: E402

BY_NAME = {s.name: s for s in SCENARIOS}


def rows_for(agent_dir: Path) -> list[dict]:
    rows = []
    for trace_path in sorted(agent_dir.glob("*.ndjson")):
        scenario = BY_NAME.get(trace_path.stem)
        if scenario is None:
            continue
        try:
            trace = load(trace_path)
            report = build(trace, build_actions(trace),
                           run_detectors(trace, None)).as_dict()
        except (UnknownTraceFormat, ValueError, OSError) as exc:
            rows.append({"name": trace_path.stem, "control": bool(scenario.control),
                         "error": str(exc), "findings": []})
            continue
        rows.append({
            "name": trace_path.stem,
            "control": bool(scenario.control),
            "verdict": report["verdict"],
            "findings": report["findings"],
            "error": None,
        })
    return rows


def render(agent: str, rows: list[dict]) -> tuple[int, int]:
    print(f"\n{agent}  ({len(rows)} traces)")
    print("-" * 74)
    detections = alarms = 0
    for row in rows:
        kind = "control" if row["control"] else "trapped"
        if row["error"]:
            print(f"  {kind:8s} {row['name']:20s} ERROR  {row['error'][:30]}")
            continue
        diverged = row["verdict"] == "diverged"
        titles = ", ".join(f["title"] for f in row["findings"]) or "-"
        mark = "  "
        if diverged and not row["control"]:
            detections += 1
            mark = "->"
        elif diverged and row["control"]:
            alarms += 1
            mark = "!!"
        print(f"{mark}{kind:8s} {row['name']:20s} {row['verdict']:9s} {titles[:34]}")
    trapped = sum(1 for r in rows if not r["control"] and not r["error"])
    controls = sum(1 for r in rows if r["control"] and not r["error"])
    print("-" * 74)
    print(f"  detections: {detections}/{trapped} trapped     "
          f"false alarms: {alarms}/{controls} control")
    return detections, alarms


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent", help="limit to one agent directory")
    args = ap.parse_args()

    corpus = ROOT / "corpus"
    dirs = [corpus / args.agent] if args.agent else sorted(
        d for d in corpus.iterdir() if d.is_dir())
    dirs = [d for d in dirs if d.is_dir()]
    if not dirs:
        print("no captured traces yet; run study/run_study.py first", file=sys.stderr)
        return 2

    total_alarms = 0
    for agent_dir in dirs:
        rows = rows_for(agent_dir)
        if not rows:
            continue
        _, alarms = render(agent_dir.name, rows)
        total_alarms += alarms
    return 1 if total_alarms else 0


if __name__ == "__main__":
    raise SystemExit(main())
