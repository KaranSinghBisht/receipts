"""Claude Code adapter.

Parses `claude -p --output-format stream-json`, which nests Anthropic Messages
API content blocks inside envelope records. Used to develop and test detectors
without spending Bobcoins; Bob remains the primary target.
"""

from __future__ import annotations

from typing import Any

from ..model import Event, Message, Outcome, RunResult, ToolResult, ToolUse, Trace

SOURCE = "claude-code"


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [b.get("text", "") for b in value if isinstance(b, dict)]
        return "\n".join(p for p in parts if p)
    if value is None:
        return ""
    return str(value)


def matches(records: list[dict[str, Any]]) -> bool:
    for record in records:
        if record.get("type") in {"assistant", "user"} and "message" in record:
            return True
    return False


def _blocks(record: dict[str, Any]) -> list[dict[str, Any]]:
    message = record.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    return [b for b in content if isinstance(b, dict)] if isinstance(content, list) else []


def _from_assistant(record: dict[str, Any], seq: int) -> list[Event]:
    events: list[Event] = []
    for block in _blocks(record):
        if block.get("type") == "text" and block.get("text"):
            events.append(Message(seq=seq, role="assistant", content=_text(block.get("text"))))
        elif block.get("type") == "tool_use":
            params = block.get("input")
            events.append(
                ToolUse(
                    seq=seq,
                    tool_id=_text(block.get("id")),
                    name=_text(block.get("name")),
                    params=params if isinstance(params, dict) else {},
                )
            )
    return events


def _from_user(record: dict[str, Any], seq: int) -> list[Event]:
    events: list[Event] = []
    for block in _blocks(record):
        if block.get("type") != "tool_result":
            continue
        is_error = bool(block.get("is_error"))
        body = _text(block.get("content"))
        events.append(
            ToolResult(
                seq=seq,
                tool_id=_text(block.get("tool_use_id")),
                outcome=Outcome.ERROR if is_error else Outcome.OK,
                output="" if is_error else body,
                error=body if is_error else "",
            )
        )
    return events


def _from_result(record: dict[str, Any], seq: int) -> list[Event]:
    usage = record.get("usage") if isinstance(record.get("usage"), dict) else {}
    stats = {
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "duration_ms": record.get("duration_ms"),
        "session_costs": record.get("total_cost_usd"),
        "task_id": record.get("session_id"),
    }
    return [
        RunResult(
            seq=seq,
            status="error" if record.get("is_error") else "success",
            stats={k: v for k, v in stats.items() if v is not None},
            last_message=_text(record.get("result")),
        )
    ]


def parse(records: list[dict[str, Any]]) -> Trace:
    events: list[Event] = []
    for seq, record in enumerate(records):
        kind = record.get("type")
        if kind == "assistant":
            events.extend(_from_assistant(record, seq))
        elif kind == "user":
            events.extend(_from_user(record, seq))
        elif kind == "result":
            events.extend(_from_result(record, seq))
    return Trace(events=tuple(events), source=SOURCE)
