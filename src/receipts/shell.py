"""Recovering file writes that happened inside a shell command.

Agents frequently mutate files with `sed -i`, a redirect, or a heredoc rather than
a file-editing tool. A diff-based reviewer sees those changes; a trace-based one
misses them entirely unless the command line is parsed. Observed in real Claude
Code runs, where every edit went through `Bash`.
"""

from __future__ import annotations

import re

_QUOTES = "\"'"

# `sed -i` (GNU) and `sed -i ''` (BSD) — the trailing operand is the file.
_SED = re.compile(r"\bsed\b[^|;&]*?-i(?:\.\w+)?\b[^|;&]*", re.IGNORECASE)
# `2>&1` is not a write, and neither is the `->` in a print statement. Agents
# print arrows constantly; without the `-` and `=` guards, `f"{c} -> {got}"`
# records a write to a file called `{got}`.
_REDIRECT = re.compile(r"(?<![0-9<>=!\-])>>?\s*([^\s|;&<>()]+)")
_TEE = re.compile(r"\btee\b\s+(?:-a\s+)?([^\s|;&<>()]+)")
# These must begin a clause. `install` was previously matched anywhere, for
# install(1) -- which also matched `pip install pytest`, and every npm, apt and
# brew install, recording a write to a file named after the package.
_COPY_MOVE = re.compile(
    r"(?:^|[|;&]\s*)(?:sudo\s+)?(?:cp|mv|install)\b\s+[^|;&]*?\s([^\s|;&<>()]+)\s*(?:$|[|;&])"
)
_TOUCH = re.compile(r"\btouch\b\s+([^\s|;&<>()]+)")

_NOT_A_FILE = re.compile(r"^(?:/dev/\w+|&\d+|\d+)$")


def _clean(candidate: str) -> str:
    return candidate.strip().strip(_QUOTES)


def _looks_like_path(candidate: str) -> bool:
    if not candidate or _NOT_A_FILE.match(candidate):
        return False
    return not candidate.startswith("-")


def _sed_targets(command: str) -> list[str]:
    targets = []
    for clause in _SED.findall(command):
        words = [_clean(w) for w in clause.split()]
        # The edited file is the last operand that is not a flag or the script.
        for word in reversed(words):
            if _looks_like_path(word) and not word.startswith("s/") and word != "sed":
                targets.append(word)
                break
    return targets


def writes(command: str) -> list[str]:
    """Every path this command line appears to write to, in order, de-duplicated."""
    if not command:
        return []
    found: list[str] = []
    found += _sed_targets(command)
    for pattern in (_REDIRECT, _TEE, _COPY_MOVE, _TOUCH):
        found += [_clean(m) for m in pattern.findall(command)]

    seen: set[str] = set()
    ordered: list[str] = []
    for path in found:
        if _looks_like_path(path) and path not in seen:
            seen.add(path)
            ordered.append(path)
    return ordered
