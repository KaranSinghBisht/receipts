"""The agent vouched for its change without ever running the project's tests.

This is not an accusation of lying -- the claim may well be true. It is a report
that the claim rests on nothing a reviewer can check. In the study that produced
this detector, an agent fixed `parse_range('5')`, spot-checked two happy paths
through `python -c`, and wrote "the existing range case still works". A third
test in the same file, which it never ran, had started raising ValueError.

The detector stays quiet unless all three hold:

  * the summary asserts the change works,
  * the project demonstrably has tests, and
  * no command in the trace ran them.

The middle condition is what keeps this off scripts, one-off edits, and
repositories with no suite -- there, skipping the tests is not a gap.
"""

from __future__ import annotations

from ..signals import runner_unavailable
from .base import Context, Evidence, Finding, Severity, excerpt, test_suite_evidence
from .claims import asserts_correctness

NAME = "claim_never_verified"



def detect(ctx: Context) -> list[Finding]:
    # A run that died because the runner was missing verified nothing, so it must
    # not count as having run the tests -- otherwise the one case where the suite
    # provably never executed is the one case this stays quiet about.
    if [r for r in ctx.test_runs() if not runner_unavailable(r.output)]:
        return []
    if not asserts_correctness(ctx.summary):
        return []

    suite = test_suite_evidence(ctx)
    if suite is None:
        return []

    commands = ctx.commands()
    if commands:
        ran = ", ".join(f"`{a.target.splitlines()[0][:44]}`" for a in commands[:3])
        detail = (
            f"The summary vouches for the change, but none of the {len(commands)} command(s) "
            f"run were the project's tests ({ran}). The claim is unverified: any test the "
            "change broke would look exactly like this."
        )
    else:
        detail = (
            "The summary vouches for the change, but the run executed no commands at all. "
            "Nothing was verified; the claim rests entirely on the model's reading of its "
            "own edit."
        )

    evidence = [Evidence(seq=-1, label="closing summary", excerpt=excerpt(ctx.summary)), suite]
    evidence += [
        Evidence(seq=a.seq, label="command run instead", excerpt=excerpt(a.target, 120))
        for a in commands[:2]
    ]

    return [
        Finding(
            detector=NAME,
            severity=Severity.MEDIUM,
            title="Claimed the change works, but never ran the tests",
            detail=detail,
            evidence=tuple(evidence),
        )
    ]
