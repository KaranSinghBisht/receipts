"""Both agent formats must normalise to the same canonical trace."""

import pytest

from receipts.actions import ActionKind, actions
from receipts.adapters import UnknownTraceFormat, parse_records
from receipts.model import Outcome


def test_bob_trace_parses_tools_and_summary(load):
    trace = load("bob_test_edited.ndjson")
    assert trace.source == "bob"
    assert [u.name for u in trace.tool_uses()] == [
        "write_to_file",
        "write_to_file",
        "execute_command",
        "apply_diff",
        "execute_command",
    ]
    assert "All tests passing" in trace.final_message
    assert trace.stats["total_tokens"] == 4211


def test_bob_extracts_command_and_path_targets(load):
    found = {a.kind: a.target for a in actions(load("bob_test_edited.ndjson"))}
    assert found[ActionKind.RUN_COMMAND] == "pytest -q"
    assert found[ActionKind.WRITE_FILE].endswith(".py")


def test_bob_maps_status_to_outcome(load):
    results = load("bob_test_edited.ndjson").results_by_tool_id()
    assert results["t3"].outcome is Outcome.ERROR
    assert results["t5"].outcome is Outcome.OK


def test_claude_code_normalises_to_same_shape(load):
    trace = load("claude_code_test_edited.ndjson")
    assert trace.source == "claude-code"
    kinds = [a.kind for a in actions(trace)]
    assert kinds.count(ActionKind.RUN_COMMAND) == 2
    assert kinds.count(ActionKind.WRITE_FILE) == 3
    assert "All tests passing" in trace.final_message


def test_unknown_format_is_rejected():
    with pytest.raises(UnknownTraceFormat):
        parse_records([{"type": "something_else", "foo": 1}])
