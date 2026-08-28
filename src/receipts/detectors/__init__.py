"""Detector registry.

Every detector exposes `NAME` and `detect(ctx) -> list[Finding]`, and may only
report what the trace or the filesystem proves.
"""

from __future__ import annotations

from pathlib import Path

from ..actions import actions as build_actions
from ..model import Trace
from . import success_over_failure, test_edited_after_failure, tests_absent, unresolved_failures
from .base import Context, Evidence, Finding, Severity

DETECTORS = (
    test_edited_after_failure,
    success_over_failure,
    tests_absent,
    unresolved_failures,
)

__all__ = ["Context", "Evidence", "Finding", "Severity", "DETECTORS", "run", "build_context"]


def build_context(trace: Trace, workspace: Path | None = None) -> Context:
    return Context(trace=trace, actions=tuple(build_actions(trace)), workspace=workspace)


def run(trace: Trace, workspace: Path | None = None) -> list[Finding]:
    """Run every detector, most severe first."""
    ctx = build_context(trace, workspace)
    findings: list[Finding] = []
    for detector in DETECTORS:
        findings.extend(detector.detect(ctx))
    return sorted(findings, key=lambda f: (f.severity.rank, f.detector))
