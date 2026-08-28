"""IBM Bob Shell adapter.

Parses the NDJSON emitted by `bob run --format stream-json`. Documented event
types and fields (bob.ibm.com/docs/shell):

    message      role, content, isReasoning?
    tool_use     tool_name, tool_id, parameters
    tool_result  tool_id, status, output?, error?
    error        severity, message
    result       status, stats, last_message

IBM does not publish the value set for `tool_result.status`, so unrecognised
values normalise to `Outcome.UNKNOWN` rather than being guessed as success.
"""

from __future__ import annotations

from typing import Any

from ..model import AgentError, Event, Message, Outcome, RunResult, ToolResult, ToolUse, Trace

SOURCE = "bob"

_OK_STATUS = frozenset({"success", "ok", "succeeded", "completed", "done", "true"})
_ERROR_STATUS = frozenset({"error", "failed", "failure", "fail", "false"})


def _outcome(raw: Any, has_error: bool) -> Outcome:
    if has_error:
        return Outcome.ERROR
    token = str(raw).strip().lower()
    if token in _OK_STATUS:
        return Outcome.OK
    if token in _ERROR_STATUS:
        return Outcome.ERROR
    return Outcome.UNKNOWN


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def matches(records: list[dict[str, Any]]) -> bool:
    """True when the stream looks like Bob's, not another agent's."""
    for record in records:
        if record.get("type") == "tool_use" and "tool_name" in record:
            return True
        if record.get("type") == "result" and "last_message" in record:
            return True
    return False


def parse_event(record: dict[str, Any], seq: int) -> Event | None:
    kind = record.get("type")
    if kind == "message":
        return Message(
            seq=seq,
            role=_text(record.get("role") or "assistant"),
            content=_text(record.get("content")),
            is_reasoning=bool(record.get("isReasoning") or record.get("is_reasoning")),
        )
    if kind == "tool_use":
        params = record.get("parameters")
        return ToolUse(
            seq=seq,
            tool_id=_text(record.get("tool_id")),
            name=_text(record.get("tool_name")),
            params=params if isinstance(params, dict) else {},
        )
    if kind == "tool_result":
        error = _text(record.get("error"))
        return ToolResult(
            seq=seq,
            tool_id=_text(record.get("tool_id")),
            outcome=_outcome(record.get("status"), bool(error)),
            output=_text(record.get("output")),
            error=error,
        )
    if kind == "error":
        return AgentError(
            seq=seq,
            severity=_text(record.get("severity") or "error"),
            message=_text(record.get("message")),
        )
    if kind == "result":
        stats = record.get("stats")
        return RunResult(
            seq=seq,
            status=_text(record.get("status")),
            stats=stats if isinstance(stats, dict) else {},
            last_message=_text(record.get("last_message")),
        )
    return None


def parse(records: list[dict[str, Any]]) -> Trace:
    events = [e for i, r in enumerate(records) if (e := parse_event(r, i)) is not None]
    return Trace(events=tuple(events), source=SOURCE)
