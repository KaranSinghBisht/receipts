"""Rebuild what a recorded run left behind, from the trace alone.

    python3 demo/replay.py corpus/bob/hidden_regression.ndjson demo/scenario

Applies the run's file writes to a fresh copy of the starting repository and
runs the tests. Nothing here is hand-written: the edits come out of the trace's
own `apply_diff` and `write_file` calls, so the result is what the agent
actually produced, not a reconstruction of what we think it produced.

This is what makes an "unverified claim" finding concrete. The finding says the
agent never ran the suite; this says what the suite would have told it.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Bob's apply_diff payload: a SEARCH block, a divider, then the REPLACE block.
_DIFF = re.compile(
    r"<{5,}\s*SEARCH\s*\n(?::start_line:\d+\s*\n)?(?:-{3,}\s*\n)?"
    r"(.*?)\n?={5,}\s*\n(.*?)\n?>{5,}\s*REPLACE",
    re.DOTALL,
)


def apply_writes(trace: Path, workspace: Path) -> list[str]:
    """Replay every file write in the trace against `workspace`."""
    touched: list[str] = []
    for line in trace.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "tool_use":
            continue

        tool = record.get("tool_name")
        params = record.get("parameters") or {}
        name = params.get("path")
        if not name:
            continue
        target = workspace / Path(name).name

        if tool in ("write_file", "write_to_file"):
            target.write_text(params.get("content", ""), encoding="utf-8")
            touched.append(f"{tool} {target.name}")
        elif tool == "apply_diff":
            before = target.read_text(encoding="utf-8") if target.exists() else ""
            after = before
            for search, replace in _DIFF.findall(params.get("diff", "")):
                if search not in after:
                    print(f"  ! diff block did not apply to {target.name}", file=sys.stderr)
                    continue
                after = after.replace(search, replace, 1)
            if after != before:
                target.write_text(after, encoding="utf-8")
                touched.append(f"apply_diff {target.name}")
    return touched


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    trace, scenario = Path(sys.argv[1]), Path(sys.argv[2])
    if not trace.is_file():
        print(f"replay: no such trace: {trace}", file=sys.stderr)
        return 2

    workspace = Path(tempfile.mkdtemp(prefix="replay-"))
    try:
        for source in scenario.glob("*.py"):
            shutil.copy(source, workspace / source.name)

        touched = apply_writes(trace, workspace)
        print(f"Replayed {len(touched)} write(s) from {trace.name}: {', '.join(touched) or 'none'}")
        print()
        for source in sorted(workspace.glob("*.py")):
            if source.name.startswith("test_"):
                continue
            print(f"--- {source.name} as the agent left it ---")
            print(source.read_text(encoding="utf-8").rstrip())
        print()

        runner = (
            ["uv", "run", "--isolated", "--with", "pytest", "--python", "3.11", "pytest", "-q"]
            if shutil.which("uv")
            else [sys.executable, "-m", "pytest", "-q"]
        )
        result = subprocess.run(runner, cwd=workspace, capture_output=True, text=True)
        print("\n".join((result.stdout + result.stderr).strip().splitlines()[-6:]))
        return result.returncode
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
