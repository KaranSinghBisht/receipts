"""Each requirement, checked against the trace that was supposed to satisfy it.

Receipts otherwise asks whether the agent's summary matches its trace. That
catches an agent misreporting its own work, but not an agent that reported
honestly and satisfied the wrong requirement, or left one untested.

Two things are checkable without a model's opinion:

  landed      the requirement names files, and something wrote to them
  confirmed   a test run passed after the last write for that requirement

and one more when the workspace is on hand:

  covered     some test file mentions the values the requirement states

An earlier version also matched each requirement's values against the diff, and
flagged anything absent. That fired on every requirement a change did not need
to touch -- five findings for a two-line fix -- because most requirements
describe behaviour that already works. Matching against the change only makes
sense for a requirement the change was meant to address, and the trace does not
say which those are.

Findings are grouped: one per outcome, listing the requirements it covers. Five
requirements unconfirmed by the same missing test run is one problem, not five.
"""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from ..actions import Action, is_test_path
from ..requirements import Requirement, Spec
from ..signals import command_failed, runner_unavailable
from .base import Context, Evidence, Finding, Severity, excerpt

NAME = "requirement_unmet"

_MAX_LISTED = 8


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    tail = path.rsplit("/", 1)[-1]
    return any(fnmatch(path, p) or fnmatch(tail, p) for p in patterns)


def _relevant(requirement: Requirement, writes: list[Action]) -> list[Action]:
    """Writes that landed where this requirement said the change belongs."""
    if not requirement.files:
        return writes
    return [a for a in writes if any(_matches(p, requirement.files) for p in a.writes)]


def _test_sources(workspace: Path | None) -> list[tuple[str, str]]:
    """(path, text) for every test file we can read in the workspace."""
    if workspace is None:
        return []
    found = []
    for path in sorted(workspace.rglob("*")):
        if not path.is_file() or not is_test_path(str(path)):
            continue
        try:
            found.append((path.name, path.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            continue
        if len(found) >= 40:
            break
    return found


def _covered_by(requirement: Requirement, sources: list[tuple[str, str]]) -> str | None:
    if not requirement.anchors:
        return None
    for name, text in sources:
        if any(anchor in text for anchor in requirement.anchors):
            return name
    return None


def _passing_run_after(ctx: Context, seq: int) -> Action | None:
    for action in ctx.verifications():
        if action.seq <= seq or runner_unavailable(action.output):
            continue
        if not command_failed(action):
            return action
    return None


def _listing(requirements: list[Requirement], spec: Spec) -> tuple[Evidence, ...]:
    return tuple(
        Evidence(seq=-1, label=f"{r.id} ({r.cite(spec.source)})", excerpt=excerpt(r.text, 150))
        for r in requirements[:_MAX_LISTED]
    )


def _ids(requirements: list[Requirement]) -> str:
    return ", ".join(r.id for r in requirements)


def detect(ctx: Context) -> list[Finding]:
    spec = ctx.spec
    if spec is None:
        return []

    writes = ctx.writes()
    sources = _test_sources(ctx.workspace)
    checkable = [r for r in spec.requirements if r.checkable]

    untouched: list[Requirement] = []
    uncovered: list[Requirement] = []
    unconfirmed: list[Requirement] = []

    for requirement in checkable:
        relevant = _relevant(requirement, writes)
        if requirement.files and not relevant:
            untouched.append(requirement)
            continue
        if sources and _covered_by(requirement, sources) is None:
            uncovered.append(requirement)
        if relevant and _passing_run_after(ctx, max(a.seq for a in relevant)) is None:
            unconfirmed.append(requirement)

    findings: list[Finding] = []

    if untouched:
        where = ", ".join(sorted({f for r in untouched for f in r.files}))
        touched = sorted({p for a in writes for p in a.writes})
        findings.append(
            Finding(
                detector=NAME,
                severity=Severity.HIGH,
                title=f"{len(untouched)} requirement(s) the change never reached",
                detail=(
                    f"{_ids(untouched)} name {where}, and nothing in this run wrote there. "
                    + (f"Files written: {', '.join(touched[:8])}." if touched
                       else "No files were written at all.")
                ),
                evidence=_listing(untouched, spec),
            )
        )

    if uncovered:
        findings.append(
            Finding(
                detector=NAME,
                severity=Severity.MEDIUM,
                title=f"{len(uncovered)} requirement(s) no test mentions",
                detail=(
                    f"No test file in the workspace contains any of the values "
                    f"{_ids(uncovered)} state. A requirement nothing tests cannot regress "
                    "loudly — it regresses silently."
                ),
                evidence=_listing(uncovered, spec),
            )
        )

    if unconfirmed:
        ran = len(ctx.verifications())
        findings.append(
            Finding(
                detector=NAME,
                severity=Severity.MEDIUM,
                title=f"{len(unconfirmed)} requirement(s) changed but never confirmed",
                detail=(
                    f"Files were written for {_ids(unconfirmed)}, and no test run passed "
                    + ("afterwards. " if ran else "at all — the run executed no tests. ")
                    + "The work happened; nothing checked it."
                ),
                evidence=_listing(unconfirmed, spec),
            )
        )

    return findings
