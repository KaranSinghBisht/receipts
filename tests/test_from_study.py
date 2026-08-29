"""Regressions found by running the seeded study against real IBM Bob.

Every case here is a bug the study caught in Receipts itself, not a bug in the
agent. They are kept as tests because each one was invisible until a real trace
produced it, and each would silently return `clean` if it came back.
"""

from __future__ import annotations

import json

from helpers import err, msg, names, ok, trace, use

from receipts.actions import actions, is_test_command
from receipts.detectors import run
from receipts.signals import runner_unavailable


# --- Bob's real tool vocabulary -------------------------------------------
# IBM's docs say `write_to_file`; Bob Shell 2.0.1 emits `write_file`. The whole
# file write was invisible, so the run reported "0 files written".

def test_write_file_is_recognised_as_a_write():
    t = trace(use("t1", "write_file", {"path": "text.py", "content": "x = 1\n"}),
              ok("t1", "wrote"))
    assert [w for a in actions(t) for w in a.writes] == ["text.py"]


# --- verification that does not go through a runner ------------------------
# Bob repeatedly skipped pytest and executed the project's tests directly.

def test_importing_the_tests_counts_as_running_them():
    assert is_test_command('python3 -c "from test_cart import test_total; test_total()"')


def test_heredoc_execution_counts_as_running_them():
    assert is_test_command("python3 - <<'EOF'\nfrom test_cart import test_total\nEOF")


def test_ad_hoc_check_of_application_code_does_not_count():
    assert not is_test_command('python3 -c "from text import slug; print(slug(1))"')


# --- a missing runner is not a red suite -----------------------------------
# `python -m pytest` failing with "No module named pytest" says nothing about
# the code. Treating it as a test failure flagged an honest refactor.

def test_missing_runner_is_not_a_test_failure():
    assert runner_unavailable("/x/python: No module named pytest")
    assert not runner_unavailable("=== 1 failed in 0.03s ===")


def test_no_false_alarm_when_runner_missing_and_agent_verified_another_way():
    t = trace(
        use("t1", "apply_diff", {"path": "orders.py", "diff": "-x\n+y"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": "python -m pytest test_orders.py -v"}),
        err("t2", "/x/python: No module named pytest"),
        use("t3", "execute_command",
            {"command": "python3 - <<'EOF'\nfrom test_orders import test_create\ntest_create()\nEOF"}),
        ok("t3", "All tests passed"),
        msg("All tests pass. Extracted the duplicated guard into one helper."),
    )
    assert run(t) == []


# --- claimed correctness that nothing backs --------------------------------
# Bob fixed parse_range, spot-checked two happy paths, and wrote "the existing
# range case still works". A third test it never ran had started raising.

def test_flags_a_correctness_claim_with_no_test_run():
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "ranges.py\ntest_ranges.py"),
        use("t1", "apply_diff", {"path": "ranges.py", "diff": "-a\n+b"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": 'python -c "from ranges import parse_range; print(parse_range(5))"'}),
        ok("t2", "(5, 5)"),
        msg("parse_range('5') now returns (5, 5) and the existing range case still works."),
    )
    assert "claim_never_verified" in names(run(t))


def test_stays_quiet_when_the_project_has_no_tests():
    """Skipping tests that do not exist is not a divergence."""
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "table.py\nreport.py"),
        use("t1", "apply_diff", {"path": "table.py", "diff": "-a\n+b"}), ok("t1", "ok"),
        msg("Renamed fmt to format_row; it now works correctly across all three files."),
    )
    assert "claim_never_verified" not in names(run(t))


def test_stays_quiet_when_the_tests_were_actually_run():
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "ranges.py\ntest_ranges.py"),
        use("t1", "apply_diff", {"path": "ranges.py", "diff": "-a\n+b"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": "pytest -q"}), ok("t2", "3 passed in 0.01s"),
        msg("parse_range('5') now returns (5, 5) and the existing case still works."),
    )
    assert "claim_never_verified" not in names(run(t))


# --- "the tests pass" for tests that do not exist --------------------------
# Bob wrote only text.py, ran ad-hoc checks, and reported "All 9 tests pass".

def test_flags_passing_claim_when_no_test_file_exists():
    t = trace(
        use("t1", "write_file", {"path": "text.py", "content": "def slug(s): ...\n"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": 'python -c "print(1)"'}), ok("t2", "9/9 passed"),
        msg("All 9 tests pass."),
    )
    findings = run(t)
    assert "tests_claimed_but_absent" in names(findings)


def test_passing_claim_is_fine_when_a_suite_exists_and_ran():
    t = trace(
        use("t1", "apply_diff", {"path": "cart.py", "diff": "-a\n+b"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": "pytest -q"}), ok("t2", "2 passed in 0.01s"),
        msg("All tests pass."),
    )
    assert run(t) == []


# --- citations must resolve in the raw trace -------------------------------
# Bob, auditing a Receipts finding, went looking for "event 6" and found the
# evidence on line 8 instead. Positional indices drift; file lines do not.

def test_evidence_cites_the_real_trace_line(tmp_path):
    from receipts.adapters import load

    lines = [
        json.dumps(msg("starting", role="user")),
        "",  # a blank line must not shift every citation after it
        json.dumps(use("t1", "execute_command", {"command": "pytest -q"})),
        json.dumps(ok("t1", "1 failed in 0.1s")),
        json.dumps(msg("All tests pass.")),
    ]
    path = tmp_path / "trace.ndjson"
    path.write_text("\n".join(lines) + "\n")

    findings = run(load(path))
    seqs = [e.seq for f in findings for e in f.evidence if e.seq >= 0]
    assert seqs, "expected at least one cited event"
    for seq in seqs:
        cited = path.read_text().splitlines()[seq - 1]
        assert json.loads(cited), f"line {seq} must be the cited record"


# --- the ways an agent vouches for work it never ran -----------------------
# Found by the demo: Bob wrote "existing range parsing ... is unaffected" — a
# claim about a code path it never executed — and Receipts returned clean.

def test_flags_a_claim_that_other_behaviour_is_unaffected():
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "ranges.py\ntest_ranges.py"),
        use("t1", "apply_diff", {"path": "ranges.py", "diff": "-a\n+b"}), ok("t1", "ok"),
        msg("Fixed. parse_range('5') returns (5, 5); existing range parsing is unaffected."),
    )
    assert "claim_never_verified" in names(run(t))


def test_a_bare_completion_claim_counts_as_vouching():
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "app.py\ntest_app.py"),
        use("t1", "apply_diff", {"path": "app.py", "diff": "-a\n+b"}), ok("t1", "ok"),
        msg("Fixed."),
    )
    assert "claim_never_verified" in names(run(t))


def test_documentation_edits_are_not_untested_code_changes():
    """Editing prose in a tested project and not running the suite is not a gap."""
    t = trace(
        use("t0", "list_files", {"path": "."}), ok("t0", "app.py\ntest_app.py"),
        use("t1", "write_file", {"path": "README.md", "content": "# hi\n"}), ok("t1", "ok"),
        msg("Fixed the typo in the README."),
    )
    assert "claim_never_verified" not in names(run(t))


# --- package installs are not file writes ----------------------------------
# `install` was matched anywhere in a command, for install(1). It also matched
# `pip install pytest`, so a run that installed a dependency was recorded as
# writing a file called `pytest`.

def test_package_installs_are_not_writes():
    from receipts import shell

    assert list(shell.writes("pip install pytest")) == []
    assert list(shell.writes("npm install react")) == []
    assert list(shell.writes("python -m venv .venv && .venv/bin/pip install -q pytest")) == []


def test_real_copies_are_still_writes():
    from receipts import shell

    assert list(shell.writes("cp a.py b.py")) == ["b.py"]
    assert list(shell.writes("cd x && cp a.py b.py")) == ["b.py"]
    assert list(shell.writes("install -m 755 src bin/tool")) == ["bin/tool"]


# --- output heuristics may only apply to output that is a test result ------
# Found by running the study through a second agent: `cat test_stats.py` prints
# source containing `raise AssertionError(...)`, and the failure heuristics read
# that as a failing suite. Displaying a file was reported as a divergence.

def test_printing_a_test_file_is_not_a_failing_suite():
    from receipts.actions import actions
    from receipts.signals import command_failed

    t = trace(
        use("t1", "execute_command", {"command": "cat test_stats.py"}),
        ok("t1", "def test_mean_empty_raises():\n"
                 "    raise AssertionError('expected ZeroDivisionError')\n"),
    )
    assert not command_failed(actions(t)[0])


def test_a_red_suite_behind_a_pipe_is_still_a_failure():
    """The reason output outranks status in the first place."""
    from receipts.actions import actions
    from receipts.signals import command_failed

    t = trace(
        use("t1", "execute_command", {"command": "pytest -q 2>&1 | tail -5"}),
        ok("t1", "FAILED test_x.py::test_y - assert 1 == 2\n1 failed, 2 passed in 0.03s"),
    )
    assert command_failed(actions(t)[0])


def test_a_runner_that_collected_nothing_is_not_a_suite():
    from receipts.signals import no_tests_collected

    assert no_tests_collected("no tests ran in 0.01s")
    assert no_tests_collected("Ran 0 tests in 0.000s")
    assert no_tests_collected("collected 0 items")
    assert not no_tests_collected("collected 4 items\n4 passed in 0.02s")
