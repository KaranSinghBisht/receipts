# Receipts — problem and solution

*Submission statement. 529 words.*

## The problem

Teams now generate more agent-written code than they can review. The bottleneck
has quietly moved: the constraint is no longer writing the change, it is
believing it.

And what a reviewer actually reads is not the change. It is the agent's closing
summary — *"Fixed. Existing behaviour is unaffected."* That sentence is written
by the same system that did the work, from its own recollection of having done
it, and it is almost always true. That is exactly what makes it dangerous. A
reviewer who has read two hundred accurate summaries reads the two hundred and
first the same way.

In our own study, IBM Bob fixed a function, spot-checked two happy paths, and
wrote *"the existing range case still works."* A third test in the same file had
started raising an exception. Bob never ran the suite, so it never found out. The
summary was honest. It was also wrong. Nothing in a normal review would catch it.

## The solution

Receipts audits an agent run against its own execution trace: the files it wrote,
the commands it ran, and what those commands printed. It compares that record to
what the agent said, and reports every claim the trace does not support — citing
the line of the trace that settles it, so `sed -n '28p' trace.ndjson` returns the
exact record a finding rests on.

With `--spec`, the question widens to the one a reviewer actually has: *did the
work match the ticket?* Bob reads the spec, ticket, or PRD and converts it into
structured requirements. Receipts then checks those against the trace.

**Users** are teams running coding agents on real repositories. They meet it in
four places: a CI gate that fails the build, a live board that fills in as
overnight runs land, a single-file evidence bundle attached to the pull request,
and a `verifier` mode inside Bob itself.

## Why it is different

Every comparable idea is *a second model grading the first*. That buys a second
opinion, a second set of hallucinations, a per-review cost, and a different
answer each time you ask.

Receipts has no opinions. A verdict is a function of the trace — same trace, same
verdict, forever, for nothing. The tool is checkable rather than trusted, which
is precisely the property it demands of the agent. Where judgement genuinely is
required — *is this worth a person's time?* — that goes to parallel Bob
subagents, and the two are never mixed.

We ran the same eight tasks through two agents. Bob diverged twice; Claude Code,
which ran the suite every time, diverged never. Zero false alarms on both. A tool
tuned to make one agent look bad would not report nothing on the second.

The strongest evidence is reflexive. Auditing Bob revealed that Bob Shell drops
most of its own `tool_use` events — 35 of 68 calls in our corpus — so Receipts
had been seeing less than half of every run. Bob subagents then caught two false
positives in Receipts and proved them with trace lines. We lost a detection and
published the lower number.

A tool that asks agents to show their receipts has to show its own.
