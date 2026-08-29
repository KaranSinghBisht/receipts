"""Semantic layer: what the agent actually *did*, independent of tool naming.

Detectors reason over `Action`s. Adapters decide which vendor tool maps to which
`ActionKind`; nothing downstream needs to know that Bob says `execute_command`
and Claude Code says `Bash`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from . import diffs, shell
from .model import Outcome, ToolUse, Trace


class ActionKind(StrEnum):
    RUN_COMMAND = "run_command"
    WRITE_FILE = "write_file"
    READ_FILE = "read_file"
    SEARCH = "search"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Action:
    """One tool call paired with its outcome.

    `writes` holds every path this call modified, whether through a file-editing
    tool or through a shell command such as `sed -i` or a redirect.
    """

    seq: int
    kind: ActionKind
    tool_name: str
    target: str
    outcome: Outcome = Outcome.UNKNOWN
    output: str = ""
    writes: tuple[str, ...] = ()
    content: str = ""
    """The text this call put into the file: a whole body, or a diff.""" 

    @property
    def wrote_anything(self) -> bool:
        return bool(self.writes)

    def wrote_test(self) -> bool:
        return any(is_test_path(path) for path in self.writes)

    def wrote_source(self) -> bool:
        return any(not is_test_path(path) for path in self.writes)

    def wrote_code(self) -> bool:
        """A code file, as opposed to prose or config. Keeps findings about
        untested changes off documentation edits."""
        return any(is_code_path(path) for path in self.writes)


# Bob and Claude Code tool names, mapped to what they mean.
_TOOL_KINDS: dict[str, ActionKind] = {
    # IBM Bob
    "execute_command": ActionKind.RUN_COMMAND,
    "write_file": ActionKind.WRITE_FILE,  # what Bob Shell 2.0.1 actually emits
    "write_to_file": ActionKind.WRITE_FILE,  # the name IBM's docs give

    "apply_diff": ActionKind.WRITE_FILE,
    "insert_content": ActionKind.WRITE_FILE,
    "read_file": ActionKind.READ_FILE,
    "search_files": ActionKind.SEARCH,
    "list_files": ActionKind.SEARCH,
    "list_code_definition_names": ActionKind.SEARCH,
    # Claude Code
    "bash": ActionKind.RUN_COMMAND,
    "write": ActionKind.WRITE_FILE,
    "edit": ActionKind.WRITE_FILE,
    "multiedit": ActionKind.WRITE_FILE,
    "notebookedit": ActionKind.WRITE_FILE,
    "read": ActionKind.READ_FILE,
    "grep": ActionKind.SEARCH,
    "glob": ActionKind.SEARCH,
}

# Confirmed against real traces: Bob uses `command` and `path`; Claude Code uses
# `command` and `file_path`. The remaining keys are tolerated, not relied on.
_COMMAND_KEYS = ("command", "cmd", "command_line", "script")
_PATH_KEYS = ("path", "file_path", "filePath", "target_file", "file")
# What the call actually wrote. Bob sends `content` or `diff`; Claude Code sends
# `content` or `new_string`. Needed to check a change against a requirement.
_CONTENT_KEYS = ("content", "diff", "new_string", "new_str")


def kind_of(tool_name: str) -> ActionKind:
    return _TOOL_KINDS.get(tool_name.strip().lower(), ActionKind.OTHER)


def target_of(use: ToolUse) -> str:
    """The command string or file path this call operated on."""
    kind = kind_of(use.name)
    keys = _COMMAND_KEYS if kind is ActionKind.RUN_COMMAND else _PATH_KEYS
    for key in keys:
        value = use.params.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def content_of(use: ToolUse) -> str:
    """What the write put into the file -- the added side of an edit only.

    A diff's deleted lines are not something the agent wrote, and counting them
    would make an agent that removed `return None` look like one that added it.
    """
    if kind_of(use.name) is not ActionKind.WRITE_FILE:
        return ""
    parts = [
        diffs.added(str(use.params[key]))
        for key in _CONTENT_KEYS
        if isinstance(use.params.get(key), str)
    ]
    return "\n".join(p for p in parts if p)


def _writes_of(kind: ActionKind, target: str) -> tuple[str, ...]:
    if kind is ActionKind.WRITE_FILE:
        return (target,) if target else ()
    if kind is ActionKind.RUN_COMMAND:
        return tuple(shell.writes(target))
    return ()


def actions(trace: Trace) -> list[Action]:
    """Pair every tool call with its result, in stream order."""
    results = trace.results_by_tool_id()
    paired: list[Action] = []
    for use in trace.tool_uses():
        result = results.get(use.tool_id)
        kind = kind_of(use.name)
        target = target_of(use)
        paired.append(
            Action(
                seq=use.seq,
                kind=kind,
                tool_name=use.name,
                target=target,
                outcome=result.outcome if result else Outcome.UNKNOWN,
                output=(result.output or result.error) if result else "",
                writes=_writes_of(kind, target),
                content=content_of(use),
            )
        )
    return paired


_TEST_PATH = re.compile(
    r"(^|/)(tests?|spec|__tests__)/|(^|/)(test_[^/]+|[^/]+_test|[^/]+\.(test|spec))\.[a-z]+$",
    re.IGNORECASE,
)
_TEST_COMMAND = re.compile(
    r"\b(pytest|py\.test|unittest|jest|vitest|mocha|go\s+test|cargo\s+test|"
    r"npm\s+(run\s+)?test|yarn\s+test|pnpm\s+(run\s+)?test|tox|rspec|phpunit|gradle\s+test|mvn\s+test)\b",
    re.IGNORECASE,
)


def is_test_path(path: str) -> bool:
    return bool(_TEST_PATH.search(path))


# Agents routinely skip the runner and import the test functions directly, e.g.
#   python3 -c "from test_cart import test_total; test_total()"
# That executes the project's tests and must count as verification. An ad-hoc
# spot-check of application code (`python -c "from text import slug; ..."`) does
# not, which is why a test symbol has to appear as well.
# `-c` / `-e` take the script inline; a bare `-` reads it from a heredoc, which
# is how agents run multi-line checks. Both are the same thing to us.
_INLINE_EXEC = re.compile(
    r"\b(python[0-9.]*|node|deno|ruby|perl)\b[^\n]*?\s-(?:c|e)\b"
    r"|\b(python[0-9.]*|node|deno|ruby|perl)\s+-\s*(?:<<|$)",
    re.IGNORECASE | re.MULTILINE,
)
_TEST_SYMBOL = re.compile(
    r"\btest_[A-Za-z0-9_]+|\bfrom\s+tests?[._A-Za-z0-9]*\s+import|\bimport\s+tests?\b",
    re.IGNORECASE,
)


def is_test_command(command: str) -> bool:
    if _TEST_COMMAND.search(command):
        return True
    return bool(_INLINE_EXEC.search(command) and _TEST_SYMBOL.search(command))


_CODE_SUFFIX = re.compile(
    r"\.(py|js|jsx|ts|tsx|mjs|cjs|rb|go|rs|java|kt|swift|c|h|cc|cpp|hpp|cs|php|scala|sh|bash)$",
    re.IGNORECASE,
)


def is_code_path(path: str) -> bool:
    return bool(_CODE_SUFFIX.search(path.strip()))
