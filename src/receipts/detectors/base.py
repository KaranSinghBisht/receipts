"""Finding types shared by every detector.

A finding is only ever raised from facts present in the trace or on disk. Each one
carries the trace positions that prove it, so a reviewer can check the claim
rather than trust it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

import re

from ..actions import Action, ActionKind, is_test_command, is_test_path
from ..requirements import Spec
from ..signals import command_failed as _command_failed
from ..signals import looks_like_test_output as _looks_like_test_output
from ..signals import no_tests_collected as _no_tests_collected
from ..signals import runner_unavailable as _runner_unavailable
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
    """Everything a detector may read: the trace, its actions, the workspace, and
    the requirements the run was supposed to satisfy."""

    trace: Trace
    actions: tuple[Action, ...]
    workspace: Path | None = None
    spec: Spec | None = None

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

    def verifications(self) -> list[Action]:
        """Every call whose output is a test result — including calls the agent
        never reported, whose command text is gone but whose output survives."""
        seen = {a.seq for a in self.test_runs()}
        extra = [
            a for a in self.actions
            if a.seq not in seen and _looks_like_test_output(a.output)
        ]
        return sorted([*self.test_runs(), *extra], key=lambda a: a.seq)

    def negative_controls(self) -> list[Action]:
        """Test runs that supplied the source they then tested.

        Found by running the study through a second agent: Claude Code finished a
        fix, ran the suite green, then rebuilt the *original buggy* source in a
        scratch directory and ran the tests again to prove they catch the bug.
        Four failures — the expected result. That is an experiment about the
        tests, not a verification of the working tree, and counting it as a
        failure punishes the more rigorous agent.

        Only treated as such when a plain test run passed too, so a run whose
        sole verification built its own fixture is still held to it.
        """
        experiments = [a for a in self.test_runs() if a.writes]
        if not experiments:
            return []
        plain = [a for a in self.test_runs() if not a.writes]
        if any(not _command_failed(a) for a in plain):
            return experiments
        return []

    @property
    def incomplete(self) -> bool:
        """True when the agent executed calls it never reported, so the absence
        of something in this trace is not evidence it did not happen."""
        return any(a.recovered for a in self.actions)


# Filenames as they appear in directory listings and search output.
_FILENAME = re.compile(r"[\w./\\-]+\.(?:py|js|jsx|ts|tsx|rb|go|rs|java|php)\b")


def test_suite_evidence(ctx: Context) -> Evidence | None:
    """Proof, from the workspace or the trace, that this project has tests.

    Detectors use this to tell "the agent skipped the tests" apart from "there
    were no tests to skip". Only the first is worth reporting.
    """
    # Executing the suite proves it exists, whatever the files are called --
    # unless the runner started and collected nothing, which proves the opposite.
    for action in ctx.test_runs():
        if not _runner_unavailable(action.output) and not _no_tests_collected(action.output):
            return Evidence(
                seq=action.seq,
                label="test suite was executed",
                excerpt=excerpt(action.target, 120),
            )

    if ctx.workspace is not None:
        for pattern in ("test_*.py", "*_test.py", "tests/**/*.py", "**/*.test.*", "**/*.spec.*"):
            hit = next((p for p in ctx.workspace.glob(pattern) if p.is_file()), None)
            if hit is not None:
                return Evidence(seq=-1, label="test file on disk", excerpt=str(hit))

    for action in ctx.actions:
        found = next((t for t in (action.target, *action.writes) if t and is_test_path(t)), None)
        if found:
            return Evidence(seq=action.seq, label="test file touched by the run", excerpt=found)

    for action in ctx.actions:
        names = sorted({n for n in _FILENAME.findall(action.output or "") if is_test_path(n)})
        if names:
            return Evidence(
                seq=action.seq,
                label=f"test file visible in `{action.tool_name}` output",
                excerpt=", ".join(names[:5]),
            )
    return None
