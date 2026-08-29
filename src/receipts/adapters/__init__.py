"""Trace loading and agent-format detection."""

from __future__ import annotations

import json
from pathlib import Path
from os import PathLike
from typing import Any

StrPath = str | PathLike[str]

from ..model import Trace
from . import bob, claude_code

_ADAPTERS = (bob, claude_code)


class UnknownTraceFormat(ValueError):
    """Raised when a trace matches no known agent format."""


def read_ndjson(path: StrPath) -> list[dict[str, Any]]:
    """Parse NDJSON, skipping blank lines. Malformed lines raise with a line number."""
    path = Path(path)
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: not valid JSON: {exc.msg}") from exc
            if isinstance(value, dict):
                records.append(value)
    return records


def parse_records(records: list[dict[str, Any]]) -> Trace:
    for adapter in _ADAPTERS:
        if adapter.matches(records):
            return adapter.parse(records)
    raise UnknownTraceFormat(
        "Trace matches neither IBM Bob nor Claude Code. "
        "Expected `bob run --format stream-json` or `claude --output-format stream-json` output."
    )


def load(path: StrPath) -> Trace:
    return parse_records(read_ndjson(path))
