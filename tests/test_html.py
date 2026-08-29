"""The HTML bundle embeds untrusted agent output and must not let it execute."""

import json
import re
from dataclasses import replace

from receipts.actions import actions
from receipts.detectors import run
from receipts.html import build as build_html
from receipts.model import RunResult
from receipts.report import build as build_report

HOSTILE = "</script><img src=x onerror=alert(1)>"


def _render(trace):
    return build_html(build_report(trace, actions(trace), run(trace)))


def _with_summary(trace, text):
    return replace(
        trace,
        events=tuple(
            replace(e, last_message=text) if isinstance(e, RunResult) else e for e in trace.events
        ),
    )


def test_script_tag_in_agent_output_cannot_break_out(load):
    page = _render(_with_summary(load("bob_clean.ndjson"), HOSTILE))
    assert "</script><img" not in page
    assert r"</script>" in page


def test_embedded_payload_is_still_valid_json(load):
    page = _render(_with_summary(load("bob_clean.ndjson"), HOSTILE))
    raw = re.search(r"const DATA = (.*?);\n", page, re.S).group(1)
    data = json.loads(raw.encode().decode("unicode_escape"))
    assert data["claim"] == HOSTILE


def test_diverged_report_marks_the_offending_events(load):
    page = _render(load("bob_test_edited.ndjson"))
    raw = re.search(r"const DATA = (.*?);\n", page, re.S).group(1)
    data = json.loads(raw.encode().decode("unicode_escape"))
    assert data["verdict"] == "diverged"
    # `seq` is the 1-based line the event occupies in the trace file, so a reader can
    # pull it straight out with `sed -n '<seq>p'`.
    assert [r["seq"] for r in data["timeline"] if r["flagged"]] == [6, 8, 10]
