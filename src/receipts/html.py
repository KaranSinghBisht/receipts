"""Standalone HTML evidence bundle.

Emits one self-contained file with the report data embedded, so it can be opened
from disk, attached to a PR, or archived as an audit record with no server.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .actions import ActionKind
from .report import CLEAN, Report

_TEMPLATE = Path(__file__).with_name("report_template.html")


def timeline_rows(report: Report) -> list[dict]:
    """Every tool call as a timeline row, with the divergence span marked."""
    flagged: set[int] = set()
    for finding in report.findings:
        flagged.update(e.seq for e in finding.evidence if e.seq >= 0)

    rows = []
    for action in report.actions:
        if action.kind is ActionKind.RUN_COMMAND:
            label, detail = "run", action.target
        elif action.kind is ActionKind.WRITE_FILE:
            label, detail = "write", action.target
        else:
            continue
        rows.append(
            {
                "seq": action.seq,
                "kind": label,
                "detail": detail,
                "outcome": str(action.outcome),
                "flagged": action.seq in flagged,
                "test": label == "write" and _looks_like_test(action.target),
                # Calls Bob executed but never emitted a `tool_use` for; rebuilt
                # from their results. Worth marking, because a reviewer reading
                # the raw trace will not find a `tool_use` line for them.
                "recovered": action.recovered,
            }
        )
    return rows


def _looks_like_test(path: str) -> bool:
    from .actions import is_test_path

    return is_test_path(path)


# Trace content is untrusted: it is whatever the agent printed, which can include
# file contents from the repository under test. Embedding it in a <script> block
# requires escaping the characters that could close the tag or start markup.
_JS_UNSAFE = {
    "<": "\\u003c",
    ">": "\\u003e",
    "&": "\\u0026",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}


def embed(payload: dict) -> str:
    """Serialise for safe inclusion inside a <script> element."""
    text = json.dumps(payload, ensure_ascii=False)
    for char, escaped in _JS_UNSAFE.items():
        text = text.replace(char, escaped)
    return text


def build(report: Report) -> str:
    payload = report.as_dict()
    payload["timeline"] = timeline_rows(report)
    template = _TEMPLATE.read_text(encoding="utf-8")
    return template.replace(
        "/*__RECEIPTS_DATA__*/null", embed(payload)
    ).replace("__RECEIPTS_TITLE__", html.escape(_title(report)))


def _title(report: Report) -> str:
    return "Receipts — clean" if report.verdict == CLEAN else "Receipts — diverged"


def write(report: Report, destination: Path) -> Path:
    destination.write_text(build(report), encoding="utf-8")
    return destination
