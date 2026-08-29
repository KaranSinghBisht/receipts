"""Build the published site: a landing page and the live report.

    python study/build_pages.py            # -> dist/

Every number on the landing page is filled in from the corpora at build time, so
the site cannot drift from what the study actually found. If a run is added or a
detector changes, the figures move with it or the build is wrong.

The report covers every agent's corpus in one page, with each run labelled
`trapped` or `control`, because the false-alarm count is the number that matters
and it has to be visible next to the detections.
"""

from __future__ import annotations

import argparse
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

LANDING = ROOT / "web" / "landing.html"
CORPUS = ROOT / "corpus"
REPO_URL = "https://github.com/KaranSinghBisht/receipts"

SUBHEAD = (
    "The same eight seeded tasks, run through every agent below. Five carry a passive "
    "trap — nothing tells the agent to cut a corner — and three are controls with no "
    "trap at all. A control that diverges is a false alarm, and that number matters "
    "more than any detection."
)


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
            shutil.copy(trace, into / f"{name}.ndjson")
            meta[name] = {"agent": agent.name, "scenario": trace.stem}
            if trace.stem in by_scenario:
                labels[name] = by_scenario[trace.stem]
    return labels, meta


def figures() -> dict[str, str]:
    totals = {"runs": 0, "diverged": 0, "seconds": 0.0, "total_lines": 0, "cited_lines": 0}
    for agent in agent_dirs():
        m = impact.measure(agent)
        for key in totals:
            totals[key] += m[key]

    labelled = {s.name for s in SCENARIOS}
    false_alarms = 0
    controls = {s.name for s in SCENARIOS if s.control}
    from receipts.actions import actions as build_actions
    from receipts.adapters import load
    from receipts.detectors import run as run_detectors
    from receipts.report import DIVERGED, build

    for agent in agent_dirs():
        for trace in agent.glob("*.ndjson"):
            if trace.stem not in labelled or trace.stem not in controls:
                continue
            t = load(trace)
            report = build(t, build_actions(t), run_detectors(t, None))
            false_alarms += report.verdict == DIVERGED

    per_run_ms = (totals["seconds"] / totals["runs"] * 1000) if totals["runs"] else 0
    return {
        "__RUNS__": str(totals["runs"]),
        "__AGENTS__": str(len(agent_dirs())),
        "__DIVERGED__": str(totals["diverged"]),
        "__FALSE_ALARMS__": str(false_alarms),
        "__MS__": f"{per_run_ms:.0f}",
        "__REPO_URL__": REPO_URL,
        "__CAPTION__": (
            f"{len(agent_dirs())} agents × 8 seeded tasks. Five of the eight carry a "
            "passive trap; three are controls with none. Auditing all of them by hand "
            f"means reading {totals['total_lines']:,} lines of trace; Receipts points at "
            f"{totals['cited_lines']}. Reading is not the whole of review — the cited "
            "lines are where a reviewer starts, not where they stop."
        ),
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

    page = LANDING.read_text(encoding="utf-8")
    for token, value in figures().items():
        page = page.replace(token, value)
    if "__" in page.split("<style>")[0]:  # any placeholder left in the head
        print("warning: unreplaced placeholder in landing page", file=sys.stderr)
    (out / "index.html").write_text(page, encoding="utf-8")

    # GitHub Pages runs Jekyll by default, which drops files it does not recognise.
    (out / ".nojekyll").write_text("")

    for path in sorted(out.iterdir()):
        try:
            shown = path.relative_to(ROOT)
        except ValueError:
            shown = path
        print(f"  {shown}  {path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
