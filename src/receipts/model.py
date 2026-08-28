"""Canonical trace model.

Every supported agent (IBM Bob, Claude Code) is normalised into these events so
that detectors never depend on a vendor's wire format. Ordering is preserved via
`seq`, which is the line index within the source stream.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Outcome(StrEnum):
    """Whether a tool call succeeded, as reported by the agent runtime."""

    OK = "ok"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Message:
    seq: int
    role: str
    content: str
    is_reasoning: bool = False


@dataclass(frozen=True, slots=True)
class ToolUse:
    seq: int
    tool_id: str
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolResult:
    seq: int
    tool_id: str
    outcome: Outcome
    output: str = ""
    error: str = ""


@dataclass(frozen=True, slots=True)
class AgentError:
    seq: int
    severity: str
    message: str


@dataclass(frozen=True, slots=True)
class RunResult:
    seq: int
    status: str
    stats: dict[str, Any] = field(default_factory=dict)
    last_message: str = ""


Event = Message | ToolUse | ToolResult | AgentError | RunResult


@dataclass(frozen=True, slots=True)
class Trace:
    """An ordered, normalised record of one agent run."""

    events: tuple[Event, ...]
    source: str

    @property
    def final_message(self) -> str:
        """The agent's closing summary — the claim we hold it to."""
        for event in reversed(self.events):
            if isinstance(event, RunResult) and event.last_message:
                return event.last_message
        for event in reversed(self.events):
            if isinstance(event, Message) and event.role == "assistant":
                if not event.is_reasoning:
                    return event.content
        return ""

    @property
    def stats(self) -> dict[str, Any]:
        for event in reversed(self.events):
            if isinstance(event, RunResult):
                return dict(event.stats)
        return {}

    @property
    def status(self) -> str:
        for event in reversed(self.events):
            if isinstance(event, RunResult):
                return event.status
        return "unknown"

    def tool_uses(self) -> list[ToolUse]:
        return [e for e in self.events if isinstance(e, ToolUse)]

    def errors(self) -> list[AgentError]:
        return [e for e in self.events if isinstance(e, AgentError)]

    def results_by_tool_id(self) -> dict[str, ToolResult]:
        return {e.tool_id: e for e in self.events if isinstance(e, ToolResult)}
