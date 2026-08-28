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


def command_failed(action: Action) -> bool:
    verdict = _decisive(action.output)
    if verdict is not None:
        return not verdict
    return action.outcome is Outcome.ERROR


def command_succeeded(action: Action) -> bool:
    """Demonstrably succeeded. Deliberately not the negation of `command_failed`."""
    verdict = _decisive(action.output)
    if verdict is not None:
        return verdict
    return action.outcome is Outcome.OK
