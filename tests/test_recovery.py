"""Tool calls Bob executed but never reported.

Bob Shell 2.0.1 keys a dedup set on the assistant message id and appends each new
tool call to the same message, so only the first call of a turn is emitted as a
`tool_use`. The results still arrive, orphaned. Across this project's corpus that
is 35 of 68 calls — so anything counting `tool_use` events was seeing less than
half of every run, and any detector reasoning about absence was doing so from a
record it did not know was incomplete.
"""

from __future__ import annotations

from helpers import msg, names, ok, trace, use

from receipts.actions import ActionKind, actions
from receipts.detectors import build_context, run
from receipts.signals import looks_like_test_output


def orphan(tid, output):
    """A result whose `tool_use` was never emitted."""
    return ok(tid, output)


def test_a_write_is_recovered_from_its_result():
    t = trace(
        use("t1", "write_file", {"path": "text.py", "content": "x = 1\n"}), ok("t1", "ok"),
        orphan("t2", "Created file: test_text.py\n<result>\ndef test_x():\n    assert True\n"),
        msg("Added the module and its tests."),
    )
    written = [p for a in actions(t) for p in a.writes]
    assert written == ["text.py", "test_text.py"]


def test_a_recovered_call_is_marked_as_such():
    t = trace(orphan("t1", "Created file: a.py"))
    recovered = [a for a in actions(t) if a.recovered]
    assert len(recovered) == 1
    assert recovered[0].tool_name == "(unreported)"
    assert build_context(t).incomplete


def test_reads_and_listings_are_not_counted_as_writes():
    t = trace(
        orphan("t1", "Contents of file SPEC.md:\n  1 | # Pricing"),
        orphan("t2", "Directory listing for .:\n\nSPEC.md\npricing.py"),
    )
    kinds = [a.kind for a in actions(t)]
    assert kinds == [ActionKind.READ_FILE, ActionKind.SEARCH]
    assert not [p for a in actions(t) for p in a.writes]


def test_no_claim_of_absent_tests_when_a_test_demonstrably_ran():
    """The command text is gone, but its output is unmistakably a test result."""
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "app.py\ntest_app.py"),
        use("t1", "apply_diff", {"path": "app.py", "diff":
            "<<<<<<< SEARCH\n:start_line:1\n-------\na\n=======\nb\n>>>>>>> REPLACE"}),
        ok("t1", "Edited file: app.py"),
        orphan("t2", "============ 3 passed in 0.02s ============"),
        msg("Fixed. Existing behaviour is unaffected."),
    )
    assert "claim_never_verified" not in names(run(t))


def test_a_tool_answering_ok_is_not_a_passing_suite():
    """`ok` reads as a passing unittest run only if the bar is far too low."""
    assert not looks_like_test_output("ok")
    assert not looks_like_test_output("Edited file: app.py")
    assert looks_like_test_output("3 passed in 0.02s")
    assert looks_like_test_output("Ran 5 tests in 0.10s")
    assert looks_like_test_output("FAILED test_app.py::test_x - AssertionError")
