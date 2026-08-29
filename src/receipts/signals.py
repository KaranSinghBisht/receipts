"""Deciding whether a command actually failed.

Captured output outranks the reported status. Agents routinely pipe test output
through `tail` or `head`, and a pipeline exits with the status of its *last*
command — so a failing test suite is reported as a successful tool call. This was
observed in real runs, not hypothesised. Only when the output says nothing
decisive do we defer to the runtime's own status.
"""

from __future__ import annotations

import re

from .actions import Action
from .model import Outcome

_FAILED = re.compile(
    r"(?:^|\s)(?:[1-9]\d*)\s+(?:tests?\s+)?failed\b"
    r"|^FAILED\s"
    r"|\bFAILURES\b"
    r"|\bAssertionError\b"
    r"|^E\s+\w*(?:Error|Exception)\b"
    r"|Traceback \(most recent call last\)"
    r"|\bTests?:\s+[1-9]\d*\s+failed"
    r"|\bpanic:"
    r"|\bexit(?:ed)? (?:with )?(?:code|status) [1-9]",
    re.MULTILINE,
)
_PASSED = re.compile(
    r"(?:^|\s)\d+\s+passed\b"
    r"|\ball tests passed\b"
    r"|\bTests?:\s+\d+\s+passed\b"
    r"|\b0 failed\b"
    r"|\bBUILD SUCCESS(?:FUL)?\b"
    r"|\bOK\b\s*$",
    re.MULTILINE | re.IGNORECASE,
)


# A test command can fail for two very different reasons: the suite ran and went
# red, or the runner never started. Only the first says anything about the code.
# Conflating them makes the tool cry wolf on any machine missing a dependency --
# observed on a real run where `python -m pytest` hit "No module named pytest"
# and the agent then verified another way.
_RUNNER_UNAVAILABLE = re.compile(
    r"No module named [\'\"]?(?:pytest|unittest|nose)"
    r"|\bcommand not found\b"
    r"|\bnot recognized as an internal or external command\b"
    r"|\bexecutable file not found\b"
    r"|\bNo such file or directory\b[^\n]*\b(?:pytest|jest|mocha|go|cargo)\b"
    r"|\bcannot find module [\'\"]?(?:jest|mocha|vitest)"
    r"|ModuleNotFoundError: No module named [\'\"]?(?:pytest|unittest)",
    re.IGNORECASE,
)


def runner_unavailable(output: str) -> bool:
    """True when the failure was the test runner missing, not a red suite."""
    return bool(output) and bool(_RUNNER_UNAVAILABLE.search(output))


def _decisive(output: str) -> bool | None:
    """True/False when the output itself settles it, else None."""
    if not output:
        return None
    failed = bool(_FAILED.search(output))
    passed = bool(_PASSED.search(output))
    if failed:
        return False
    if passed:
        return True
    return None


# Deciding whether a *known* test command failed is a different question from
# deciding whether unlabelled output is a test result at all. The first can lean
# on loose signals like a bare "OK"; the second cannot -- a tool that answers
# "ok" would otherwise read as a passing suite. This pattern only matches shapes
# that a test runner produces and little else does.
_TEST_OUTPUT = re.compile(
    r"\b\d+\s+(?:tests?\s+)?(?:passed|failed)\b"
    r"|^\s*(?:FAILED|PASSED|ERROR)\s+\S"
    r"|\bFAILURES\b"
    r"|\bRan\s+\d+\s+tests?\b"
    r"|\bTests?:\s+\d+\s+(?:passed|failed)"
    r"|\b\d+\s*/\s*\d+\s+(?:passed|tests?\s+passed)\b"
    r"|={3,}\s*(?:test session starts|short test summary)",
    re.MULTILINE | re.IGNORECASE,
)


# A runner that started and collected nothing is evidence there is no suite,
# not evidence there is one.
_NO_TESTS = re.compile(
    r"\bno tests ran\b"
    r"|\bno tests (?:were )?(?:found|collected)\b"
    r"|\bcollected 0 items\b"
    r"|\bRan 0 tests\b"
    r"|\b0 tests? (?:ran|collected)\b",
    re.IGNORECASE,
)


def no_tests_collected(text: str) -> bool:
    """True when a test runner ran and found nothing to run."""
    return bool(text) and bool(_NO_TESTS.search(text))


def looks_like_test_output(text: str) -> bool:
    """Whether this output is itself a test result, whatever produced it.

    Needed because Bob drops most `tool_use` events, so a call's command text is
    often unrecoverable while its output survives. The absence of a *recognised*
    test command is not evidence that no test ran.
    """
    return bool(text) and bool(_TEST_OUTPUT.search(text))


def command_failed(action: Action) -> bool:
    """Whether this command failed, output first and status second.

    The output-first rule exists for pipelines: `pytest | tail` exits 0 while the
    suite is red. But it may only apply to output that is a test result. An agent
    printing a test file with `cat` shows source containing `AssertionError`, and
    reading that as a failure flags a run for displaying a file.
    """
    if looks_like_test_output(action.output):
        verdict = _decisive(action.output)
        if verdict is not None:
            return not verdict
    return action.outcome is Outcome.ERROR


def command_succeeded(action: Action) -> bool:
    """Demonstrably succeeded. Deliberately not the negation of `command_failed`."""
    if looks_like_test_output(action.output):
        verdict = _decisive(action.output)
        if verdict is not None:
            return verdict
    return action.outcome is Outcome.OK
