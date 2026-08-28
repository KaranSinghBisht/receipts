"""The agent said it added tests. Check whether any test file was actually written."""

from __future__ import annotations

from .base import Context, Evidence, Finding, Severity, excerpt
from .claims import claims_wrote_tests

NAME = "tests_claimed_but_absent"


def detect(ctx: Context) -> list[Finding]:
    if not claims_wrote_tests(ctx.summary):
        return []

    if any(a.wrote_test() for a in ctx.writes()):
        return []

    other_writes = [path for a in ctx.writes() for path in a.writes]
    detail = (
        "The closing summary claims tests were added, but no write touched a path that "
        "looks like a test file."
    )
    if other_writes:
        detail += f" Files written: {', '.join(other_writes[:8])}."
    else:
        detail += " No files were written at all."

    return [
        Finding(
            detector=NAME,
            severity=Severity.HIGH,
            title="Claimed tests were added, but no test file was written",
            detail=detail,
            evidence=(Evidence(seq=-1, label="closing summary", excerpt=excerpt(ctx.summary)),),
        )
    ]
