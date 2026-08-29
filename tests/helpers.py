"""Builders for hand-written traces, in the real Bob wire format."""

from __future__ import annotations

import json

from receipts.adapters import parse_records


def trace(*records):
    return parse_records([json.loads(json.dumps(r)) for r in records])


def msg(text, role="assistant"):
    return {"type": "message", "role": role, "content": text}


def use(tid, name, params):
    return {"type": "tool_use", "tool_id": tid, "tool_name": name, "parameters": params}


def ok(tid, output=""):
    return {"type": "tool_result", "tool_id": tid, "status": "success", "output": output}


def err(tid, message):
    return {"type": "tool_result", "tool_id": tid, "status": "error",
            "error": {"type": "tool_error", "message": message}}


def names(findings):
    return {f.detector for f in findings}


def titles(findings):
    return [f.title for f in findings]
