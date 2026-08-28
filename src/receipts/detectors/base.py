"""Finding types shared by every detector.

A finding is only ever raised from facts present in the trace or on disk. Each one
carries the trace positions that prove it, so a reviewer can check the claim
rather than trust it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from ..actions import Action, ActionKind, is_test_command
from ..model import Trace


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def rank(self) -> int:
        return {"high": 0, "medium": 1, "low": 2}[self.value]


@dataclass(frozen=True, slots=True)
class Evidence:
    """A pointer into the trace, with the excerpt that matters."""

    seq: int
    label: str
    excerpt: str = ""


@dataclass(frozen=True, slots=True)
class Finding:
    detector: str
    severity: Severity
    title: str
    detail: str
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict:
        return {
            "detector": self.detector,
            "severity": str(self.severity),
            "title": self.title,
            "detail": self.detail,
            "evidence": [
                {"seq": e.seq, "label": e.label, "excerpt": e.excerpt} for e in self.evidence
            ],
        }


def excerpt(text: str, limit: int = 220) -> str:
    """Collapse whitespace and truncate, for readable evidence lines."""
    flat = " ".join((text or "").split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


@dataclass(frozen=True, slots=True)
class Context:
    """Everything a detector may read: the trace, its actions, and the workspace."""

    trace: Trace
    actions: tuple[Action, ...]
    workspace: Path | None = None

    @property
    def summary(self) -> str:
        return self.trace.final_message

    def commands(self) -> list[Action]:
        return [a for a in self.actions if a.kind is ActionKind.RUN_COMMAND]

    def writes(self) -> list[Action]:
        """Any call that modified a file, via a file tool or via the shell."""
        return [a for a in self.actions if a.writes]

    def test_runs(self) -> list[Action]:
        return [a for a in self.commands() if is_test_command(a.target)]
