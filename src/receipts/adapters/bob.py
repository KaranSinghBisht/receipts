"""IBM Bob Shell adapter.

Parses the NDJSON emitted by `bob run --format stream-json`. The shapes below
were read off the emitter itself in Bob Shell 2.0.1 (`bobshell/dist/bob.js`,
the `stream-json-renderer` class), not inferred from prose documentation:

    message      role, content, isReasoning?     <- one event PER STREAM DELTA
    tool_use     tool_name, tool_id, parameters
    tool_result  tool_id, status, output?, error?
    error        severity, message
    result       status, stats

Three properties of that emitter drive this module:

* Assistant text arrives as deltas. Bob invokes its stream hook per chunk and
  accumulates with `content += chunk`, so one reply becomes dozens of `message`
  events. We re-join consecutive assistant deltas. Without this, the "closing
  summary" is whichever fragment happened to arrive last, and the whole
  claim-versus-reality comparison compares against a few stray characters.
* `tool_result.error` is an object (`{type, message}`), and a failed call omits
  `output` entirely -- its text lands in `error.message`. Detectors read
  `output`, so a failed call's text is folded into it.
* `result` carries no `last_message`, so the closing summary can only come from
  the coalesced assistant messages. The field is still read in case a later
  Bob release adds it.

Subagent activity is not recoverable from this stream: Bob routes
`subagent_start` / `subagent_end` to its debug logger rather than stdout.
"""

from __future__ import annotations

from dataclasses import replace
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


def _error_text(value: Any) -> str:
    """Bob reports tool failures as `{type: "tool_error", message: "..."}`."""
    if isinstance(value, dict):
        return _text(value.get("message") or value.get("error"))
    return _text(value)


def matches(records: list[dict[str, Any]]) -> bool:
    """True when the stream looks like Bob's, not another agent's."""
    for record in records:
        kind = record.get("type")
        if kind == "tool_use" and "tool_name" in record:
            return True
        if kind == "message" and "role" in record and isinstance(record.get("content"), str):
            return True
        stats = record.get("stats")
        if kind == "result" and isinstance(stats, dict) and "session_costs" in stats:
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
        error = _error_text(record.get("error"))
        return ToolResult(
            seq=seq,
            tool_id=_text(record.get("tool_id")),
            outcome=_outcome(record.get("status"), bool(error)),
            # A failed call omits `output`; keep the text where detectors look.
            output=_text(record.get("output")) or error,
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


def _joinable(prev: Event | None, event: Event) -> bool:
    """Whether `event` is a continuation of the same streamed assistant turn."""
    return (
        isinstance(event, Message)
        and isinstance(prev, Message)
        and prev.role == event.role == "assistant"
        and prev.is_reasoning == event.is_reasoning
    )


def coalesce(events: list[Event]) -> list[Event]:
    """Re-join Bob's per-delta assistant messages into whole turns.

    A turn ends at the first event that is not another assistant delta of the
    same kind -- a tool call, a tool result, a user message, or a switch
    between reasoning and reply text.
    """
    merged: list[Event] = []
    for event in events:
        prev = merged[-1] if merged else None
        if _joinable(prev, event):
            assert isinstance(prev, Message) and isinstance(event, Message)
            merged[-1] = replace(prev, content=prev.content + event.content)
            continue
        merged.append(event)
    return merged


def parse(records: list[dict[str, Any]]) -> Trace:
    events = [e for i, r in enumerate(records) if (e := parse_event(r, i)) is not None]
    return Trace(events=tuple(coalesce(events)), source=SOURCE)
