"""Run the seeded scenarios through an agent and keep every trace.

Usage:
    python study/run_study.py --agent bob            # all scenarios
    python study/run_study.py --agent bob --only spec_mismatch
    python study/run_study.py --list

Traces land in `corpus/<agent>/<scenario>.ndjson`. Nothing is judged here --
this script only produces evidence. `study/report_study.py` reads it back.

Each scenario runs in a throwaway workspace so a run can never touch this
repository, and so a rerun starts from the same seeded state every time.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scenarios import SCENARIOS, Scenario  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"

AGENTS = {
    "bob": lambda ws, prompt, turns, cost: [
        "bob", "run", "--format", "stream-json", "--workspace", str(ws),
        "--trust", "--accept-license",
        "--max-turns", str(turns), "--max-cost", str(cost), prompt,
    ],
    "claude": lambda ws, prompt, turns, cost: [
        "claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
        "--permission-mode", "bypassPermissions", "--max-turns", str(turns),
    ],
}


def seed(scenario: Scenario, into: Path) -> None:
    for name, content in scenario.files.items():
        path = into / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def run_one(scenario: Scenario, agent: str, turns: int, cost: float,
            timeout: int, suffix: str = "") -> tuple[bool, str]:
    """Run one scenario. Returns (ok, note). Never raises on agent failure."""
    out_dir = CORPUS / agent
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_path = out_dir / f"{scenario.name}{suffix}.ndjson"

    workspace = Path(tempfile.mkdtemp(prefix=f"receipts-{scenario.name}-"))
    try:
        seed(scenario, workspace)
        cmd = AGENTS[agent](workspace, scenario.prompt, turns, cost)
        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                cwd=workspace if agent == "claude" else None,
            )
        except subprocess.TimeoutExpired:
            return False, f"timed out after {timeout}s"
        except FileNotFoundError:
            return False, f"`{cmd[0]}` not on PATH"

        elapsed = time.monotonic() - started
        if not proc.stdout.strip():
            detail = proc.stderr.strip().splitlines()
            return False, f"no trace emitted ({detail[0] if detail else 'silent'})"

        trace_path.write_text(proc.stdout)
        lines = proc.stdout.count("\n")
        return True, f"{lines} events, {elapsed:.0f}s -> {trace_path.relative_to(ROOT)}"
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent", choices=sorted(AGENTS), default="bob")
    ap.add_argument("--only", action="append", default=[],
                    help="scenario name; repeatable")
    ap.add_argument("--suffix", default="",
                    help="appended to each trace filename, e.g. __2 for a repeat pass")
    ap.add_argument("--max-turns", type=int, default=25)
    ap.add_argument("--max-cost", type=float, default=3.0)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    chosen = [s for s in SCENARIOS if not args.only or s.name in args.only]
    if args.list:
        for s in chosen:
            print(f"{'control' if s.control else 'trapped':8s}  {s.name:20s}  {s.trap}")
        return 0
    if not chosen:
        print(f"no scenario matched {args.only}", file=sys.stderr)
        return 2
    if args.agent == "bob" and not os.environ.get("BOB_API_KEY"):
        print("BOB_API_KEY is not set; headless Bob will refuse to start.",
              file=sys.stderr)
        return 2

    failures = 0
    for i, scenario in enumerate(chosen, 1):
        label = "control" if scenario.control else "trapped"
        print(f"[{i}/{len(chosen)}] {scenario.name} ({label}) ... ", end="", flush=True)
        ok, note = run_one(scenario, args.agent, args.max_turns,
                           args.max_cost, args.timeout, args.suffix)
        print(note if ok else f"FAILED: {note}")
        failures += 0 if ok else 1

    print(f"\n{len(chosen) - failures}/{len(chosen)} traces captured into "
          f"{(CORPUS / args.agent).relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
