"""Holding a run to a requirements document, not just to its own summary."""

from __future__ import annotations

import json

import pytest

from helpers import names, titles

from receipts.detectors import run
from receipts.requirements import BadRequirements, Requirement, load, parse
from helpers import msg, ok, trace, use


def spec(*requirements, source="SPEC.md"):
    return parse({"source": source, "requirements": list(requirements)})


def req(id="R1", text="Discount MUST be 15%.", **kw):
    return {"id": id, "text": text, **kw}


# --- parsing ---------------------------------------------------------------

def test_rejects_a_document_with_no_requirements():
    with pytest.raises(BadRequirements):
        parse({"source": "SPEC.md", "requirements": []})


def test_rejects_a_requirement_with_no_text():
    with pytest.raises(BadRequirements, match="R1"):
        parse({"requirements": [{"id": "R1", "files": ["a.py"]}]})


def test_reports_the_line_so_a_reviewer_can_find_it():
    assert Requirement(id="R1", text="x", line=8).cite("SPEC.md") == "SPEC.md:8"
    assert Requirement(id="R1", text="x").cite("SPEC.md") == "SPEC.md"


def test_load_reports_bad_json_with_the_path(tmp_path):
    path = tmp_path / "requirements.json"
    path.write_text("{not json")
    with pytest.raises(BadRequirements, match="requirements.json"):
        load(path)


def test_a_requirement_with_nothing_to_check_is_not_checkable():
    assert not Requirement(id="R1", text="Be fast.").checkable
    assert Requirement(id="R1", text="Be fast.", files=("a.py",)).checkable


# --- checking against a trace ---------------------------------------------

def test_flags_a_requirement_the_change_never_reached():
    t = trace(
        use("t1", "write_file", {"path": "other.py", "content": "x = 1\n"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": "pytest -q"}), ok("t2", "1 passed"),
        msg("Done."),
    )
    findings = run(t, None, spec(req(files=["pricing.py"], anchors=["0.85"])))
    assert "requirement_unmet" in names(findings)
    assert "never reached" in titles(findings)[0]


def test_flags_requirements_that_nothing_confirmed():
    t = trace(
        use("t1", "write_file", {"path": "pricing.py", "content": "return total * 0.85\n"}),
        ok("t1", "ok"),
        msg("Done."),
    )
    findings = run(t, None, spec(req(files=["pricing.py"], anchors=["0.85"])))
    assert any("never confirmed" in title for title in titles(findings))


def test_quiet_when_the_change_landed_and_the_tests_passed():
    t = trace(
        use("t1", "write_file", {"path": "pricing.py", "content": "return total * 0.85\n"}),
        ok("t1", "ok"),
        use("t2", "execute_command", {"command": "pytest -q"}), ok("t2", "2 passed in 0.01s"),
        msg("Done. All tests pass."),
    )
    findings = run(t, None, spec(req(files=["pricing.py"], anchors=["0.85"])))
    assert "requirement_unmet" not in names(findings)


def test_many_requirements_missing_one_test_run_is_one_finding():
    """Five requirements unconfirmed by the same absent test run is one problem."""
    t = trace(
        use("t1", "write_file", {"path": "app.py", "content": "x = 1\n"}), ok("t1", "ok"),
        msg("Done."),
    )
    findings = run(t, None, spec(*[req(id=f"R{i}", files=["app.py"]) for i in range(1, 6)]))
    unmet = [f for f in findings if f.detector == "requirement_unmet"]
    assert len(unmet) == 1
    assert "5 requirement(s)" in unmet[0].title


def test_a_requirement_no_test_mentions_is_reported(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    (tmp_path / "test_app.py").write_text("def test_x():\n    assert True\n")
    t = trace(
        use("t1", "write_file", {"path": "app.py", "content": "x = 2\n"}), ok("t1", "ok"),
        use("t2", "execute_command", {"command": "pytest -q"}), ok("t2", "1 passed"),
        msg("Done."),
    )
    findings = run(t, tmp_path, spec(req(files=["app.py"], anchors=["0.85"])))
    assert any("no test mentions" in title for title in titles(findings))


def test_no_spec_means_no_requirement_findings():
    t = trace(use("t1", "write_file", {"path": "a.py", "content": "x=1"}), ok("t1", "ok"),
              msg("Done."))
    assert "requirement_unmet" not in names(run(t))


# --- the added side of an edit --------------------------------------------

def test_a_diff_counts_only_what_it_adds():
    """Removing `return None` must not look like writing it."""
    from receipts.actions import actions

    t = trace(
        use("t1", "apply_diff", {"path": "ranges.py", "diff":
            "<<<<<<< SEARCH\n:start_line:2\n-------\n    return None\n"
            "=======\n    return (n, n)\n>>>>>>> REPLACE"}),
        ok("t1", "ok"),
    )
    content = [a.content for a in actions(t) if a.writes][0]
    assert "return (n, n)" in content
    assert "return None" not in content
