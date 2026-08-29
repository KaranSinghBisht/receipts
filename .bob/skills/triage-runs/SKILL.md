---
name: triage-runs
description: >-
  Triage a directory of finished agent runs. Receipts decides what diverged; parallel
  subagents decide which divergences are worth a person's time. Use on a batch of
  overnight runs, or on everything queued for review.
---

Turn a pile of finished agent runs into a short list a reviewer should actually read.

Two different jobs, kept apart on purpose:

- **What diverged** is decided by `receipts`, from the trace, deterministically. Never
  overrule it from memory or intuition — if you disagree, open the cited trace line and
  say what it shows.
- **What deserves attention** is a judgement call, and needs the repository in view.
  That is what the subagents are for, and why they run in parallel: triage of one run
  tells you nothing about another.

<Steps>
<Step>
Audit the batch in one pass:

```
receipts traces/ --html report.html --labels labels.json
```

Add `--spec requirements.json --workspace <repo>` when the batch was worked against a
requirements document. Read `report.html` — or run `receipts <trace>` per run — to get
each verdict and its findings.
</Step>
<Step>
List the runs that came back `diverged`. Runs that came back `clean` are done: say so
and spend no further effort on them.
</Step>
<Step>
For each diverged run, launch a `trace-auditor` subagent, all of them at once rather
than one after another. Give each subagent exactly one run: the trace path, the
findings `receipts` reported, and the repository path.

Each returns a verdict of its own:
- **confirmed** — the evidence supports the finding, and here is what a reviewer will
  need to look at
- **needs context** — the finding is real but may be intended; here is the question to
  ask the author
- **false positive** — the cited evidence does not support the finding, with the trace
  line that shows why

A false positive is the most valuable thing you can return. Report it plainly.
</Step>
<Step>
Write the digest, ordered by how much of a reviewer's attention each run deserves:

| Run | Receipts finding | Subagent verdict | What a reviewer should do |

Close with the counts — runs audited, diverged, confirmed, false positives — and the
single run you would look at first. If nothing needs a human, say that in one line.
</Step>
</Steps>

Do not edit the code under audit. You are reading it.
