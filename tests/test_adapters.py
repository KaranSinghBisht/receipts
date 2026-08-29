"""Both agent formats must normalise to the same canonical trace."""

import pytest

from receipts.actions import ActionKind, actions
from receipts.adapters import UnknownTraceFormat, parse_records
from receipts.model import Message, Outcome


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


# --- Bob Shell 2.0.1 wire format ------------------------------------------
# Bob emits one `message` event per stream delta, reports tool failures as an
# `{type, message}` object with no `output`, and sends no `last_message`.
# These were read off the emitter in `bobshell/dist/bob.js`.


def test_bob_rejoins_streamed_message_deltas(load):
    trace = load("bob_stream_test_edited.ndjson")
    messages = [e for e in trace.events if isinstance(e, Message)]
    assert len(messages) == 4, "41 deltas must collapse to 1 reasoning + 3 reply turns"
    assert trace.final_message == (
        "Implemented the discount rule in src/pricing.py and added tests. All tests passing."
    )


def test_bob_keeps_reasoning_separate_from_reply(load):
    messages = [e for e in load("bob_stream_test_edited.ndjson").events
                if isinstance(e, Message)]
    assert messages[0].is_reasoning is True
    assert messages[0].content == "The spec says 15% off; let me write it."
    assert all(not m.is_reasoning for m in messages[1:])


def test_bob_recovers_output_from_error_object(load):
    """A failed call carries no `output`; its text is in `error.message`."""
    result = load("bob_stream_test_edited.ndjson").results_by_tool_id()["t3"]
    assert result.outcome is Outcome.ERROR
    assert "1 failed" in result.output
    assert "assert 90.0 == 85" in result.error


def test_bob_summary_survives_absent_last_message(load):
    """`result` has no `last_message`, so the claim comes from the messages."""
    trace = load("bob_stream_test_edited.ndjson")
    assert not any(getattr(e, "last_message", "") for e in trace.events)
    assert trace.stats["session_costs"] == 0.0413
    assert "All tests passing" in trace.final_message
