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

ACKNOWLEDGED_TROUBLE = re.compile(
    r"\b(error|errors|failed|failing|failure|could not|couldn't|unable to|did not|didn't|"
    r"skipped|blocked|issue|problem|warning|caveat|however|but note)\b",
    re.IGNORECASE,
)


def claims_wrote_tests(summary: str) -> bool:
    return bool(WROTE_TESTS.search(summary))


def claims_tests_pass(summary: str) -> bool:
    return bool(TESTS_PASS.search(summary))


def claims_verified(summary: str) -> bool:
    return bool(VERIFIED.search(summary))


def acknowledges_trouble(summary: str) -> bool:
    return bool(ACKNOWLEDGED_TROUBLE.search(summary))
