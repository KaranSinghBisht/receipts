"""The evidence bundle: what the agent did, what it claimed, and where they differ."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import __version__
from .actions import Action, ActionKind
from .detectors.base import Finding, Severity
from .model import Trace

CLEAN = "clean"
DIVERGED = "diverged"


@dataclass(frozen=True, slots=True)
class Report:
    trace: Trace
    actions: tuple[Action, ...]
    findings: tuple[Finding, ...]

    @property
    def verdict(self) -> str:
        return DIVERGED if self.findings else CLEAN

    def worst(self) -> Severity | None:
        return min((f.severity for f in self.findings), key=lambda s: s.rank, default=None)

    def counts(self) -> dict[str, int]:
        tally = {str(s): 0 for s in Severity}
        for finding in self.findings:
            tally[str(finding.severity)] += 1
        return tally

    def as_dict(self) -> dict[str, Any]:
        stats = self.trace.stats
        return {
            "receipts_version": __version__,
            "verdict": self.verdict,
            "agent": self.trace.source,
            "run": {
                "status": self.trace.status,
                "task_id": stats.get("task_id"),
                "tool_calls": len(self.actions),
                "tokens": stats.get("total_tokens"),
                "cost": stats.get("session_costs"),
                "duration_ms": stats.get("duration_ms"),
            },
            "claim": self.trace.final_message,
            "counts": self.counts(),
            "findings": [f.as_dict() for f in self.findings],
            "ground_truth": {
                "commands": [
                    {"seq": a.seq, "command": a.target, "outcome": str(a.outcome)}
                    for a in self.actions
                    if a.kind is ActionKind.RUN_COMMAND
                ],
                "files_written": [
                    {"seq": a.seq, "path": path, "tool": a.tool_name}
                    for a in self.actions
                    for path in a.writes
                ],
            },
        }


def build(trace: Trace, actions: list[Action], findings: list[Finding]) -> Report:
    return Report(trace=trace, actions=tuple(actions), findings=tuple(findings))
