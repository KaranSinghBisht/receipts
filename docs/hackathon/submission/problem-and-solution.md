# Receipts — problem and solution

*Submission statement. 497 words.*

## The problem

Teams now generate more agent-written code than they can review. The constraint
is no longer writing the change; it is believing it.

And what a reviewer reads is not the change. It is the agent's closing summary —
*"Fixed. Existing behaviour is unaffected."* That sentence comes from the same
system that did the work, from its own recollection of doing it, and it is almost
always true. That is what makes it dangerous: after two hundred accurate
summaries, you read the two hundred and first the same way.

In our study, IBM Bob fixed a function, spot-checked two happy paths, and wrote
*"the existing range case still works."* A third test in the same file had
started raising. Bob never ran the suite, so it never found out — and nothing in
a normal review would catch it.

## The solution

Receipts audits an agent run against its own execution trace: the files it wrote,
the commands it ran, and what those commands printed. It compares that record to
what the agent said, and reports every claim the trace does not support — citing
the line of the trace that settles it, so `sed -n '28p' trace.ndjson` returns the
exact record a finding rests on.

With `--spec`, the question widens to the one a reviewer actually has: *did the
work match the ticket?* Bob converts the spec into structured requirements;
Receipts checks those against the trace.

**Users** are teams running coding agents on real repositories: a CI gate that
fails the build, a live board that fills as overnight runs land, an evidence
bundle for the pull request, and a `verifier` mode inside Bob.

## Why it is different

Comparable ideas are *a second model grading the first* — a second opinion, a
second set of hallucinations, a cost per review, a different answer each time.

Receipts has no opinions. A verdict is a function of the trace: same trace, same
verdict, forever, for nothing. The tool is checkable rather than trusted, which
is exactly the property it demands of the agent. Where judgement genuinely is
required — *is this worth a person's time?* — that goes to parallel Bob
subagents, and the two never mix.

We ran eight tasks, three times each, through two agents — 48 real runs. IBM Bob
diverged on 6 of 15 trapped runs; Claude Code, which always found a way to run
the suite, on none. Zero false alarms across 18 control runs. On the task where
the fix quietly breaks a second test, Bob vouched without testing three times
out of three — a rate, not an anecdote.

The strongest evidence is reflexive. Auditing Bob revealed that Bob Shell drops
most of its own `tool_use` events, so Receipts had been seeing less than half of
every run. Bob subagents then caught two false positives in Receipts and proved
them with trace lines. We lost a detection and published the lower number.

A tool demanding receipts has to show its own.
