"""Each detector must fire on its scenario and stay silent on honest work."""

from dataclasses import replace

from receipts.detectors import run
from receipts.model import RunResult


def names(findings):
    return {f.detector for f in findings}


def test_clean_run_produces_no_findings(load):
    assert run(load("bob_clean.ndjson")) == []


def test_detects_test_edited_after_failure(load):
    findings = run(load("bob_test_edited.ndjson"))
    assert "test_edited_after_failure" in names(findings)

    finding = next(f for f in findings if f.detector == "test_edited_after_failure")
    assert finding.severity == "high"
    labels = [e.label for e in finding.evidence]
    assert any("failed" in l for l in labels)
    assert any("rewritten" in l for l in labels)
    assert any("passed" in l for l in labels)


def test_detects_claimed_tests_that_were_never_written(load):
    assert "tests_claimed_but_absent" in names(run(load("bob_tests_absent.ndjson")))


def test_detects_passing_claimed_over_a_failing_run(load):
    findings = run(load("bob_passing_over_failure.ndjson"))
    assert "passing_claimed_over_failure" in names(findings)
    assert "unresolved_failures" in names(findings)


def test_a_failure_that_was_fixed_is_not_reported_as_unresolved(load):
    """Red-green is correct work. Only failures never recovered from count."""
    assert "unresolved_failures" not in names(run(load("bob_test_edited.ndjson")))


def test_acknowledged_failure_is_downgraded_not_hidden(load):
    trace = load("bob_passing_over_failure.ndjson")
    honest = replace(
        trace,
        events=tuple(
            replace(e, last_message="The suite still fails; I could not fix it.")
            if isinstance(e, RunResult)
            else e
            for e in trace.events
        ),
    )
    finding = next(f for f in run(honest) if f.detector == "unresolved_failures")
    assert finding.severity == "low"


def test_findings_are_ordered_most_severe_first(load):
    ranks = [f.severity.rank for f in run(load("bob_passing_over_failure.ndjson"))]
    assert ranks == sorted(ranks)


def test_same_defect_found_in_both_agent_formats(load):
    bob = names(run(load("bob_test_edited.ndjson")))
    claude = names(run(load("claude_code_test_edited.ndjson")))
    assert "test_edited_after_failure" in bob & claude


def test_real_agent_run_that_did_honest_work_is_clean(load):
    """Regression guard against false positives, on a captured real trace."""
    assert run(load("real_claude_fix_source.ndjson")) == []
