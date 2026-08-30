"""Failures the run never recovered from.

An earlier version flagged *any* failed command that the summary did not mention.
That fires on every healthy red-green cycle, where a failing test is the expected
first step. A detector that cries wolf on correct work destroys trust in every
other finding, so this one reports only failures that were never resolved: a
command that failed and never subsequently succeeded.
"""

from __future__ import annotations

from ..actions import Action, is_test_command
from ..signals import command_failed, command_succeeded, runner_unavailable
from .base import Context, Evidence, Finding, Severity, excerpt
from .claims import acknowledges_trouble

NAME = "unresolved_failures"


def _resolved_later(failure: Action, commands: list[Action]) -> bool:
    """A later run of the same command — or of any test, for a test failure — that passed."""
    treat_any_test = is_test_command(failure.target)
    for candidate in commands:
        if candidate.seq <= failure.seq or not command_succeeded(candidate):
            continue
        if candidate.target == failure.target:
            return True
        if treat_any_test and is_test_command(candidate.target):
            return True
    return False


def detect(ctx: Context) -> list[Finding]:
    commands = ctx.commands()
    # A test run that supplied its own broken source failed on purpose.
    controls = {a.seq for a in ctx.negative_controls()}
    unresolved = [
        a for a in commands
        if a.seq not in controls and command_failed(a) and not _resolved_later(a, commands)
    ]
    runtime_errors = ctx.trace.errors()
    if not unresolved and not runtime_errors:
        return []

    acknowledged = acknowledges_trouble(ctx.summary)
    evidence = [
        Evidence(seq=a.seq, label=f"never succeeded: {a.target}", excerpt=excerpt(a.output))
        for a in unresolved[:5]
    ]
    evidence += [
        Evidence(seq=e.seq, label=f"runtime error ({e.severity})", excerpt=excerpt(e.message))
        for e in runtime_errors[:5]
    ]
    total = len(unresolved) + len(runtime_errors)

    # Say what the failure actually was. "1 unresolved failure" is true and
    # nearly useless; "the test runner was not installed" is the same fact in a
    # form a reviewer can act on.
    missing_runner = [a for a in unresolved if runner_unavailable(a.output)]
    if missing_runner and len(missing_runner) == len(unresolved):
        detail = (
            f"The test runner was not available -- `{missing_runner[0].target.splitlines()[0][:60]}`"
            " could not start -- and nothing ran the suite afterwards."
        )
    else:
        verb = "was" if total == 1 else "were"
        detail = (
            f"{total} failure{'s' if total != 1 else ''} {verb} never followed by a "
            "successful re-run."
        )
    detail += (
        " The summary acknowledges trouble, so this is informational."
        if acknowledged
        else (
            " The closing summary does not mention it."
            if total == 1
            else " The closing summary does not mention them."
        )
    )

    return [
        Finding(
            detector=NAME,
            severity=Severity.LOW if acknowledged else Severity.MEDIUM,
            title=(
                (
                    "The test runner never started"
                    if acknowledged
                    else "The test runner never started, and the summary does not say so"
                )
                if missing_runner and len(missing_runner) == len(unresolved)
                else f"{total} unresolved failure{'s' if total != 1 else ''} at the end of the run"
            ),
            detail=detail,
            evidence=tuple(evidence),
        )
    ]
