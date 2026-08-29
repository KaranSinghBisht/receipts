---
name: extract-requirements
description: >-
  Turn a spec, ticket, or PRD into the requirements.json that Receipts checks a run
  against. Use before handing work to an agent, or before auditing work it has done.
---

Read a requirements document and write it out as structured, checkable requirements.

This is a translation job, not a judgement one. You decide what the document *says*.
You never decide whether the requirement was met — Receipts does that from the trace,
so that the check stays reproducible and no model grades an agent's work.

<Steps>
<Step>
Read the document. Take each testable statement — anything using MUST, SHOULD, or
describing required behaviour — as one requirement. Skip background and rationale.
</Step>
<Step>
For each requirement, record:

- `id` — short and stable, e.g. `R1`.
- `text` — the requirement in the document's own words. Quote, do not paraphrase.
- `line` — the line it appears on, so a reviewer can find it.
- `files` — the files a change satisfying it should touch. Glob patterns are fine.
  Leave empty only if the document genuinely does not say.
- `anchors` — literal *values* the requirement states: numbers, return values, error
  strings, sentinel values. Take them verbatim from the requirement text. These are
  matched literally against test files, so they must be distinctive: `0.85` and `None`
  are useful anchors; the name of the function or file under discussion is not, because
  it appears in every test of that file and so distinguishes nothing. A requirement
  whose only anchor would be an identifier is better left with no anchors at all.
</Step>
<Step>
Write `requirements.json`:

```json
{
  "source": "SPEC.md",
  "requirements": [
    {"id": "R1", "text": "...", "line": 3, "files": ["pricing.py"], "anchors": ["0.85"]}
  ]
}
```
</Step>
<Step>
Check it back against the document: every MUST accounted for, every `text` a real
quote, every `line` correct. A requirement you cannot give `files` or `anchors` for
is reported as uncheckable rather than passing, so it is better to leave them empty
than to invent them.
</Step>
</Steps>
