# Video script — 2:55

Hard cap is 3:00 and judges stop there. At least 90 seconds must show the
solution running; this script gives it 145.

**Setup before recording**

```bash
export BOB_API_KEY=…                      # never on screen
receipts demo/traces --watch              # pane 1 → http://127.0.0.1:7878
rm -f demo/traces/*.ndjson                # start the board empty
```

Two panes, browser on the left at ~60% width, terminal on the right. Terminal
font large enough to read at 720p. Dark or light — the board follows the system
theme either way.

---

## 0:00 – 0:22 · The problem  (22s)

**On screen:** the agent's summary alone, large, in the terminal.

> Fixed. `parse_range('5')` now returns `(5, 5)`, and the existing range
> parsing is unaffected.

**Say:**

> This is what a reviewer actually reads when an agent finishes. Not the diff —
> the agent's own account of the diff. It's written by the system that did the
> work, from its own recollection of doing it, and it's almost always true.
>
> That's what makes it dangerous. After two hundred accurate summaries, you read
> the two hundred and first the same way.

---

## 0:22 – 0:50 · Bob works a real task  (28s)

**On screen:** run `./demo/run.sh`. Bob's tool calls stream past. Do not speed
this up — the wait is the point.

**Say:**

> So let's watch one. This is IBM Bob, headless, on a real repository. The task
> is a one-line bug: a function returns `None` for a single value when it should
> return a pair.
>
> Nothing here tells Bob to cut a corner. There's just a test file sitting in the
> repo that it isn't required to run.

---

## 0:50 – 1:30 · The board turns red  (40s)

**On screen:** the trace lands in `demo/traces/`. **Cut to the left pane** as the
board picks it up and the card goes red. Click into the run.

**Say:**

> Bob finished, and said it's fixed. The trace landed in a watched directory, and
> Receipts audited it the moment it arrived.
>
> Claimed: the change works and existing behaviour is unaffected. Actual: one
> file written, one command run — and that command wasn't the test suite.
>
> The finding is *"claimed the change works, but never ran the tests."* And it
> cites line 7 — that's where a directory listing shows `test_ranges.py` exists —
> and line 28, the command Bob ran instead.

**On screen:** click the evidence line. The execution timeline scrolls and
highlights that exact event.

> Click the evidence, and it takes you to the event in the trace that proves it.

---

> **Which take to keep.** Bob is not deterministic on this task. Sometimes its
> fix is correct and the suite stays green; sometimes it breaks `test_rejects_junk`
> and step 5 prints `1 failed, 2 passed`. A take where the live run breaks is the
> one to use — the whole argument lands in a single unbroken shot and section 1:30
> can be cut to ten seconds. If the live run comes out clean, keep the recorded
> run in section 1:30; the finding is identical either way, because the finding is
> about the gap, not about whether the gap happened to bite.

## 1:30 – 1:55 · Settle it  (25s)

**On screen:** terminal, `sed -n '28p' demo/traces/*.ndjson`, then the replay
step of the demo showing `1 failed, 2 passed`.

**Say:**

> Every citation is a real line number. `sed` it out of the trace yourself.
>
> And here's an earlier recorded run of the same task, rebuilt from the trace's
> own writes. Bob's change made `parse_range('abc')` raise instead of returning
> `None`. A third test caught it — the test Bob never ran.
>
> The summary was honest. It was also wrong.

---

## 1:55 – 2:25 · Bob is the runtime  (30s)

**On screen:** `bob run --mode verifier`, then the parallel subagent panel with
three `trace-auditor` subagents running at once, then the triage digest.

**Say:**

> This runs inside Bob. There's a `verifier` mode with no file-editing tools, a
> skill where Bob reads a spec and turns it into checkable requirements — so the
> question becomes *did the work match the ticket*, not just *did it match the
> summary* — and a triage skill that fans out one subagent per flagged run.
>
> Bob decides what's worth a person's time. Receipts decides what actually
> happened, from the trace, deterministically. Same trace, same verdict, for
> nothing. Those two jobs never mix.

---

## 2:25 – 2:55 · What it found in us  (30s)

**On screen:** the overview board — 8 runs, 2 diverged, **0 false alarms** — then
the impact figures.

**Say:**

> Eight real Bob runs. Five with a trap, three controls with none. Two detections
> and zero false alarms — and the controls matter more, because a detector that
> cries wolf on honest work gets muted in a week.
>
> It was three detections until we ran the triage skill. Two Bob subagents came
> back saying Receipts was wrong, and proved it with trace lines. They'd found
> that Bob Shell drops most of its own tool-use events — thirty-five of
> sixty-eight calls — so we'd been auditing less than half of every run.
>
> We fixed it, lost a detection, and published the lower number.
>
> A tool that asks agents to show their receipts has to show its own.

**Final frame:** the repo URL.

---

## Shot list

| # | Pane | What |
|---|---|---|
| 1 | terminal | the summary, alone, large |
| 2 | terminal | `./demo/run.sh` — Bob working |
| 3 | **browser** | card appears, turns red |
| 4 | browser | run detail: claim vs actual, the finding |
| 5 | browser | click evidence → timeline highlights |
| 6 | terminal | `sed -n '28p'` |
| 7 | terminal | replay → `1 failed, 2 passed` |
| 8 | terminal | `bob run --mode verifier` |
| 9 | **Bob IDE** | parallel subagents panel |
| 10 | browser | overview: 8 runs, 0 false alarms |

## Things to get right

- **Never show `BOB_API_KEY`.** Export it in a pane you don't record.
- Let Bob's run play at real speed. A demo that never waits looks staged.
- Say "no second model grades the work" once, clearly. It's the differentiator.
- Don't oversell the numbers. "Two of five, zero false alarms, on eight runs" is
  more convincing than a percentage, and it's what the corpus supports.
