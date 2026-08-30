# Submission form — paste-ready

Fill the form top to bottom. Resubmitting replaces EVERYTHING, so keep this
file open for round two after the AI Advisor email.

## Field 1 — Video demonstration URL
Upload to YouTube (unlisted is fine — the link is public). Paste the watch URL.

## Field 2 — Written problem and solution statement  (487 words, limit 500)

The problem

Teams generate more agent-written code than they can review. The constraint
is no longer writing the change; it is believing it.

What a reviewer reads is not the change. It is the agent's closing summary —
"Fixed. Existing behaviour is unaffected." That sentence comes from the same
system that did the work, from its recollection, and it is usually true. That is
what makes it dangerous: after two hundred accurate
summaries, you read the two hundred and first the same way.

IBM Bob fixed a function, spot-checked two happy paths, and wrote
"the existing range case still works." A third test in the same file had
started raising. Bob never ran the suite, so it never found out — and nothing in
a normal review would catch it.

The solution

Receipts audits an agent run against its own execution trace: the files it wrote,
the commands it ran, and what those commands printed. It compares that record to
what the agent said, and reports every claim the trace does not support — citing
the line of the trace that settles it, so sed -n '28p' trace.ndjson returns the
exact record a finding rests on.

With --spec, the question widens to the one a reviewer actually has: *did the
work match the ticket?* Bob converts the spec into structured requirements;
Receipts checks those against the trace.

Users are teams running coding agents on real repositories: a CI gate that
fails the build, a live board that fills as overnight runs land, an evidence
bundle for the pull request, and a verifier mode inside Bob.

Why it is different

Comparable ideas are a second model grading the first — a second opinion, a
second set of hallucinations, a cost per review, a different answer each time.

Receipts has no opinions. A verdict is a function of the trace: same trace, same
verdict, forever, for nothing. The tool is checkable rather than trusted, which
is exactly the property it demands of the agent. Where judgement genuinely is
required — is this worth a person's time? — that goes to parallel Bob
subagents, and the two never mix.

We ran eight tasks, three times each, through two agents — 48 real runs. IBM Bob
diverged on 6 of 15 trapped runs; Claude Code, which always found a way to run
the suite, on none. Zero false alarms across 18 control runs. On the task where
the fix quietly breaks a second test, Bob vouched without testing three times
out of three — a rate, not an anecdote.

The strongest evidence is reflexive. Auditing Bob revealed that Bob Shell drops
most of its own tool_use events, so Receipts had been seeing less than half of
every run. Bob subagents then caught two false positives in Receipts and proved
them with trace lines. We lost a detection and published the lower number.

A tool demanding receipts has to show its own.

## Field 3 — Written statement on technology (how IBM Bob was used)

How IBM Bob was used

Bob is not a thing this project was built with. It is the thing the project
reads, the thing it runs inside, and the thing that found its worst bugs.

Measured at the time of writing: 43 Bob tasks, 9.4 of 40 Bobcoins, against
Bob Shell 2.0.1 and Bob IDE 2.0.3 on the ibm-coding-challenge-uat instance
(us-east).

1. Bob Shell is the data source

Receipts consumes bob run --format stream-json. That NDJSON — message,
tool_use, tool_result, error, result — is the entire input to the tool.
Everything it reports is derived from a stream Bob produced.

The adapter was written by reading Bob's own emitter in the shipped bundle
(bobshell/dist/bob.js) rather than from prose documentation. That is how we
learned three things before spending a single Bobcoin: assistant text arrives one
delta per event, tool_result.error is an object rather than a string, and
result carries no last_message. The first of those was decisive — a real
trace splits pong into "p" and "ong", so treating the last assistant
message as the agent's claim yields "ong", and a tool that reports clean on
everything forever while looking perfectly healthy.

2. Agent mode produced the study

Eight seeded tasks were run through Bob headless, in Agent mode, on throwaway
workspaces: five carrying a passive trap — nothing instructs the agent to cut a
corner — and three controls with no trap at all. study/run_study.py captures
every trace into corpus/bob/. Those eight traces are the evidence behind every
number in the README, and they are committed, so the study is re-runnable.

3. A custom mode audits a finished run

.bob/custom_modes.yaml defines a verifier mode with read, execute,
and skill groups and no edit group. bob run --mode verifier audits a
completed run through the verify-agent-run skill.

We tested the separation of duties rather than asserting it. Asked to modify a
file, the mode did — printf 'audited' > notes.txt — because execute is
required to run receipts and a shell can write. The configuration now says
that plainly, and the real containment is pointing the mode at a directory
holding the trace rather than at the code under audit. Shipping an unverified
claim in the configuration of a tool built to catch unverified claims is exactly
the failure this project exists to find, and Bob is what surfaced it.

4. Document understanding turns a spec into checkable requirements

.bob/skills/extract-requirements has Bob read a spec, ticket, or PRD and emit
requirements.json: each requirement quoted verbatim, with its line number, the
files a change should touch, and the literal values a correct change should
contain. Given our three-line SPEC.md, Bob produced five requirements with
accurate quotes and correct line numbers.

The division of labour is deliberate and load-bearing. **Bob decides what the
document says. Receipts decides, mechanically, what the trace shows.** No model
ever grades an agent's work, so the verdict stays reproducible — same trace,
same verdict, for nothing.

Bob's first pass anchored every requirement on the function name, which appears
in every test of that file and therefore distinguishes nothing. The skill now
says so explicitly, and the second pass was clean. That iteration is visible in
the git history.

5. Parallel subagents triage the batch

.bob/skills/triage-runs audits a directory of runs with Receipts, then launches
one trace-auditor subagent per diverged run — spawn_subagent ×3 in a
single turn, running concurrently. Each is read-only, sees exactly one run, and
is told that reporting a false positive is worth more than agreeing.

This is the one place judgement belongs. What diverged is decided
deterministically from the trace. What deserves a person's time needs the
repository in view and is genuinely a judgement call, so it goes to Bob — and
the two are never mixed.

6. Bob audited us, and was right

That triage run is the most valuable thing Bob did on this project. Two of the
three subagents came back saying Receipts was wrong, each citing trace lines.
They were both correct:

- A finding said no test file was written. Trace line 36 reads
  Created file: test_text.py.
- A finding said a change was never verified. Trace lines 45–47 carry real
  execution output: discount(100) = 85.0 PASSED.

Chasing that down exposed a genuine data-loss bug in Bob Shell 2.0.1: its
stream-json renderer keys a dedup set on the assistant message id, and Bob
appends each new tool call to that same message, so **only the first call of a
turn is emitted as a tool_use** while every result still arrives. In our corpus
that is 35 of 68 calls in the first eight-run corpus and 106 of 194
across the current 24 Bob runs — Receipts had been seeing less than half of
every run, and "1 file written, 1 command run" was never true.

bob_output.infer now rebuilds each unreported call from the prefixes Bob puts
on result output. A command's text is unrecoverable, so a recovered command is
reported as unreported rather than invented, and Context.incomplete marks a
trace whose record is known to be partial — because absence of evidence in a
provably incomplete record is not evidence of absence.

Our detection rate fell from 3 of 5 to 2 of 5 as a result. We published the lower
number. A Bob subagent is the reason we know it is the right one.

7. A second agent, as a control on ourselves

The same eight tasks were also run through Claude Code — no Bobcoins, same
scenarios, same scoring — and every task ran three times per agent, 48 runs in
all, because agents are not deterministic and a rate is a claim someone can
check. Bob diverged on 6 of 15 trapped runs, including three out of three on the
hidden-regression task; Claude Code, which found a way to run the suite every
time, on none. Zero false alarms across 18 control runs.

That comparison exists to keep us honest rather than to rank the agents. What it
establishes is that the tool is not tuned against the agent it was built on:
pointed at a different one, it reports nothing, and it reports nothing on the
controls for both.

It also earned its keep. Four false positives only appeared under the second
agent — most instructively, Claude Code finished a fix, ran the suite green, then
rebuilt the original buggy source in a scratch directory and re-ran the tests
to prove they catch the bug. Four failures, which was the entire point. Receipts
called that a divergence, punishing the more rigorous agent.

Where to see it

The site and the report over all 48 runs are published at
receipts-bob.vercel.app, rebuilt from the corpora by
study/build_pages.py, so every figure on it is derived from the study rather
than written by hand.

watsonx

Bob runs against IBM's gateway (api.us-east.bob.ibm.com) and every model call
in this project went through it. We did not use watsonx.ai or watsonx Orchestrate
directly, and have not claimed to.

## Field 4 — Code repository URL

https://github.com/KaranSinghBisht/receipts

FLIP PUBLIC FIRST: gh repo edit --visibility public
bob_sessions/ must contain your task screenshots before you paste this.

## Links section (optional — add all three)

- https://receipts-bob.vercel.app
- the video URL again
- https://github.com/KaranSinghBisht/receipts
