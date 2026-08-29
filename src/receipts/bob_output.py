"""Recovering tool calls that Bob's stream never reported.

Bob Shell 2.0.1 drops most of its `tool_use` events. Its renderer keys a
dedup set on the assistant message id, and Bob appends each new tool call to
the *same* message — so the first call of a turn is emitted and every later one
is skipped. The `tool_result` records still arrive, orphaned.

Measured on this project's corpus: 35 of 68 tool calls, across all eight runs.
Anything counting `tool_use` events was therefore counting less than half the
run, and a detector reasoning about absence — "no test was ever run" — was
drawing conclusions from a record it did not know was incomplete.

What survives is the result's own output, and Bob prefixes those predictably.
That is enough to recover the kind of call and, for file writes, the path. It
is not enough to recover a command's text, so a recovered command has an empty
target and is reported as unreported rather than invented.
"""

from __future__ import annotations

import re

from .actions import ActionKind

_PATTERNS: tuple[tuple[re.Pattern[str], ActionKind], ...] = (
    (re.compile(r"^\s*(?:Created|Edited|Wrote|Appended to) file:?\s*(?P<path>[^\n]+)"), ActionKind.WRITE_FILE),
    (re.compile(r"^\s*The content was successfully saved to\s*(?P<path>[^\n]+)"), ActionKind.WRITE_FILE),
    (re.compile(r"^\s*Contents of file\s*(?P<path>[^\n:]+)"), ActionKind.READ_FILE),
    (re.compile(r"^\s*Directory listing for\s*(?P<path>[^\n:]+)"), ActionKind.SEARCH),
    (re.compile(r"^\s*(?:Found|Showing)\s+\d+\s+result"), ActionKind.SEARCH),
    (re.compile(r"^\s*Command (?:completed|executed|failed)"), ActionKind.RUN_COMMAND),
    (re.compile(r"^\s*Exit code:"), ActionKind.RUN_COMMAND),
    (re.compile(r"^\s*Stderr:"), ActionKind.RUN_COMMAND),
)

# `Created file: x.py` is often followed by the body that was written, wrapped
# in a result marker. Recovering it lets requirement anchors still match.
_BODY = re.compile(r"<result>\s*(?P<body>.*)", re.DOTALL)


def infer(output: str) -> tuple[ActionKind, str, str]:
    """Guess (kind, target, content) for a result whose call was never reported."""
    text = (output or "").lstrip()
    if not text:
        return ActionKind.OTHER, "", ""

    for pattern, kind in _PATTERNS:
        match = pattern.match(text)
        if match is None:
            continue
        path = (match.groupdict().get("path") or "").strip().rstrip(":").strip()
        content = ""
        if kind is ActionKind.WRITE_FILE:
            body = _BODY.search(text)
            content = body.group("body").strip() if body else ""
        return kind, path, content

    return ActionKind.OTHER, "", ""
