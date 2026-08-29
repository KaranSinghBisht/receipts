"""What an edit actually put into a file.

A diff carries both halves of a change. Asking whether a requirement's values
appear "in the change" gives the wrong answer if the deleted lines count: an
agent removing `return None` would look like an agent writing it.

So for every edit format we understand, keep only the added side.
"""

from __future__ import annotations

import re

# Bob's apply_diff: a SEARCH block, a divider, then the REPLACE block.
_SEARCH_REPLACE = re.compile(
    r"<{5,}\s*SEARCH\s*\n(?::start_line:\d+\s*\n)?(?:-{3,}\s*\n)?"
    r".*?\n?={5,}\s*\n(.*?)\n?>{5,}\s*REPLACE",
    re.DOTALL,
)

# A unified diff, in case a shell command produced one.
_UNIFIED_HUNK = re.compile(r"^@@ .*? @@", re.MULTILINE)


def added(text: str) -> str:
    """The lines an edit introduces, with removals and markers stripped out."""
    if not text:
        return ""

    blocks = _SEARCH_REPLACE.findall(text)
    if blocks:
        return "\n".join(blocks)

    if _UNIFIED_HUNK.search(text):
        kept = [
            line[1:]
            for line in text.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        return "\n".join(kept)

    # A whole file body, or a replacement string: all of it is added.
    return text
