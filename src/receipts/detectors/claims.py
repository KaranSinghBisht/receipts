"""Phrases an agent uses to assert it did something, in its closing summary.

Deliberately narrow. A missed claim costs one finding; a false claim costs the
reviewer's trust in every finding, which is far more expensive.
"""

from __future__ import annotations

import re

WROTE_TESTS = re.compile(
    r"\b(add(ed|ing)?|wrote|writ(e|ten)|creat(e|ed|ing)|includ(e|ed|ing))\b[^.\n]{0,60}?\btests?\b",
    re.IGNORECASE,
)

TESTS_PASS = re.compile(
    r"\b(all\s+)?(the\s+)?tests?\b[^.\n]{0,40}?\b(pass(es|ed|ing)?|green|succeed(ed|s)?)\b"
    r"|\b(test\s+suite|suite)\b[^.\n]{0,20}?\bpass(es|ed|ing)?\b"
    r"|\ball\s+(green|passing)\b",
    re.IGNORECASE,
)

VERIFIED = re.compile(
    r"\b(verified|confirmed|validated)\b[^.\n]{0,50}?\b(work(s|ing)?|pass|correct|success)",
    re.IGNORECASE,
)

# Assertions of correctness that never mention the word "test" -- the form an
# agent reaches for after a hand-rolled spot check.
ASSERTS_WORKING = re.compile(
    r"\b(still\s+works?|works?\s+(correctly|as\s+expected|fine)|"
    r"now\s+(returns?|works?|passes?|behaves?)|behaves?\s+correctly|"
    r"no\s+regressions?|nothing\s+(else\s+)?broke|"
    # Claims about code the agent did not touch being fine anyway. Bob wrote
    # "existing range parsing ... is unaffected" having never run that path.
    r"(is|are|remains?)\s+(unaffected|unchanged|intact)|"
    r"continues?\s+to\s+work|not\s+affected)\b",
    re.IGNORECASE,
)

# A bare completion claim vouches for the work just as much as a description of
# it does. "Fixed." after editing code, in a project with tests nobody ran, is
# an assertion that the change is good.
CLAIMS_FIXED = re.compile(
    r"(^|[.\n]\s*|\*\*)\s*(fixed|resolved|corrected|done)\b"
    r"|\bthe\s+(bug|issue|problem)\s+(is|was)\s+(now\s+)?(fixed|resolved)\b",
    re.IGNORECASE,
)

ACKNOWLEDGED_TROUBLE = re.compile(
    r"\b(error|errors|failed|failing|failure|could not|couldn't|unable to|did not|didn't|"
    r"skipped|blocked|issue|problem|warning|caveat|however|but note|"
    # "pytest is not installed, so I..." is an acknowledgment, and a summary
    # that owns a limitation must not be treated as hiding it.
    r"not installed|not available|unavailable|missing|fell back|falling back|workaround)\b",
    re.IGNORECASE,
)


def claims_wrote_tests(summary: str) -> bool:
    return bool(WROTE_TESTS.search(summary))


def claims_tests_pass(summary: str) -> bool:
    return bool(TESTS_PASS.search(summary))


def claims_verified(summary: str) -> bool:
    return bool(VERIFIED.search(summary))


def asserts_correctness(summary: str) -> bool:
    """Any assertion that the change is good, however it is phrased."""
    return bool(
        TESTS_PASS.search(summary)
        or VERIFIED.search(summary)
        or ASSERTS_WORKING.search(summary)
        or CLAIMS_FIXED.search(summary)
    )


def acknowledges_trouble(summary: str) -> bool:
    return bool(ACKNOWLEDGED_TROUBLE.search(summary))
