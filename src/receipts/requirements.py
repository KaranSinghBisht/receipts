"""Requirements lifted out of a spec, ticket, or PRD.

The division of labour here is the whole point. A language model reads the
document and writes this file: prose in, structure out, which is a translation
job it is good at and which a human can check line by line against the source.
Receipts then decides whether each requirement was met, mechanically, from the
trace. No model ever grades the work.

    {
      "source": "SPEC.md",
      "requirements": [
        {
          "id": "R1",
          "text": "Orders MUST apply a 15% discount to the order total.",
          "line": 3,
          "files": ["pricing.py"],
          "anchors": ["0.85", "15"]
        }
      ]
    }

`files` and `anchors` are what make a requirement checkable. `files` names where
the change should land; `anchors` are literal values the requirement itself
states, which a correct change is likely to contain. Both are optional, and a
requirement with neither is reported as uncheckable rather than quietly passing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


class BadRequirements(ValueError):
    """The requirements file is missing, malformed, or empty."""


@dataclass(frozen=True, slots=True)
class Requirement:
    id: str
    text: str
    line: int | None = None
    files: tuple[str, ...] = field(default_factory=tuple)
    anchors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def checkable(self) -> bool:
        """Whether the trace can be tested against this at all."""
        return bool(self.files or self.anchors)

    def cite(self, source: str) -> str:
        return f"{source}:{self.line}" if self.line else source


@dataclass(frozen=True, slots=True)
class Spec:
    source: str
    requirements: tuple[Requirement, ...]


def _strings(value: object, field_name: str, req_id: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        raise BadRequirements(f"requirement {req_id}: `{field_name}` must be a list of strings")
    return tuple(v for v in (s.strip() for s in value) if v)


def parse(payload: object) -> Spec:
    """Validate the structure a document-reading step produced."""
    if not isinstance(payload, dict):
        raise BadRequirements("expected an object with `source` and `requirements`")

    raw = payload.get("requirements")
    if not isinstance(raw, list) or not raw:
        raise BadRequirements("`requirements` must be a non-empty list")

    requirements = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise BadRequirements(f"requirement #{index} must be an object")
        req_id = str(item.get("id") or f"R{index}").strip()
        text = str(item.get("text") or "").strip()
        if not text:
            raise BadRequirements(f"requirement {req_id}: `text` is required")
        line = item.get("line")
        if line is not None and not isinstance(line, int):
            raise BadRequirements(f"requirement {req_id}: `line` must be a number")
        requirements.append(
            Requirement(
                id=req_id,
                text=text,
                line=line,
                files=_strings(item.get("files"), "files", req_id),
                anchors=_strings(item.get("anchors"), "anchors", req_id),
            )
        )

    source = str(payload.get("source") or "the requirements document").strip()
    return Spec(source=source, requirements=tuple(requirements))


def load(path: Path) -> Spec:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise BadRequirements(f"could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise BadRequirements(f"{path}: not valid JSON: {exc.msg} (line {exc.lineno})") from exc
    return parse(payload)
