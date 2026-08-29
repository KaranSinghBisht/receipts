"""What auditing a batch of runs costs, with and without Receipts.

    python study/impact.py corpus/bob

No human timings are invented here. The claim being measured is narrow and
checkable: to answer "does this summary match what the agent did" by hand, a
reviewer reads the trace. Receipts reads it instead and points at the lines that
settle the question. So the honest unit of saving is *lines a reviewer has to
read*, and the honest cost is how long the tool takes.

Everything below is derived from the corpus at run time. Nothing is asserted
that the numbers do not show.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from receipts.actions import actions as build_actions  # noqa: E402
from receipts.adapters import UnknownTraceFormat, load  # noqa: E402
from receipts.detectors import run as run_detectors  # noqa: E402
from receipts.report import DIVERGED, build  # noqa: E402


def measure(traces: Path) -> dict:
    paths = sorted(traces.glob("*.ndjson"))
    if not paths:
        raise SystemExit(f"no traces in {traces}")

    total_lines = cited_lines = 0
    runs = diverged = findings = 0
    recovered = 0
    started = time.perf_counter()

    for path in paths:
        try:
            trace = load(path)
        except (UnknownTraceFormat, ValueError, OSError):
            continue
        acts = build_actions(trace)
        report = build(trace, acts, run_detectors(trace, None))

        runs += 1
        total_lines += sum(1 for line in path.open() if line.strip())
        cited = {e.seq for f in report.findings for e in f.evidence if e.seq >= 0}
        cited_lines += len(cited)
        findings += len(report.findings)
        diverged += report.verdict == DIVERGED
        recovered += sum(1 for a in acts if a.recovered)

    elapsed = time.perf_counter() - started
    return {
        "runs": runs,
        "diverged": diverged,
        "findings": findings,
        "total_lines": total_lines,
        "cited_lines": cited_lines,
        "recovered_calls": recovered,
        "seconds": elapsed,
    }


def report(m: dict) -> str:
    read_by_hand = m["total_lines"]
    read_with = m["cited_lines"]
    saved = 100 * (1 - read_with / read_by_hand) if read_by_hand else 0.0
    per_run = m["seconds"] / m["runs"] if m["runs"] else 0.0

    lines = [
        "",
        f"{m['runs']} runs audited in {m['seconds']:.2f}s  ({per_run * 1000:.0f} ms per run)",
        "-" * 66,
        f"  trace lines a reviewer would read by hand   {read_by_hand:>8,}",
        f"  trace lines Receipts points at              {read_with:>8,}",
        f"  reduction in what has to be read            {saved:>7.1f}%",
        "",
        f"  runs needing a human at all                 {m['diverged']:>8} of {m['runs']}",
        f"  findings raised                             {m['findings']:>8}",
        "",
        "  Reading is not the whole of review, and the lines Receipts cites are the",
        "  start of a reviewer's work rather than the end of it. What the numbers",
        "  show is narrower than a time saving and easier to check: how much of the",
        f"  record a reviewer can skip without missing what the tool found.",
    ]
    if m["recovered_calls"]:
        lines += [
            "",
            f"  Note: {m['recovered_calls']} tool calls in this corpus were executed but never",
            "  reported by the agent, and were rebuilt from their results. A reviewer",
            "  reading the trace by hand would have had to notice that themselves.",
        ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("traces", type=Path, nargs="?", default=ROOT / "corpus" / "bob")
    args = ap.parse_args()
    print(report(measure(args.traces)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
