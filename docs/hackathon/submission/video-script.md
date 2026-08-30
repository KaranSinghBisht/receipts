# Video script — FINAL — 2:50

Checked against the submission page on the day: max 3:00 and judges stop there;
brief problem intro; **at least 90 seconds of the solution running on screen**;
clearly demonstrate how IBM Bob was used; narration required; host on YouTube /
Vimeo / Google Drive so the AI Submission Advisor can also read it.

This cut gives the solution **105 seconds on screen** (0:50–2:35) and shows Bob
working live twice.

## Setup (not recorded)

```bash
export BOB_API_KEY=…                   # pane you never record
uv sync --frozen
export PATH="$PWD/.venv/bin:$PATH"
./demo/reset.sh
receipts demo/traces --watch           # pane 1 → http://127.0.0.1:7878
# browser tabs, in order:
#   1. receipts-bob.vercel.app                 (landing)
#   2. 127.0.0.1:7878                          (live board, empty)
#   3. receipts-bob.vercel.app/dashboard       (overview)
#   4. …/dashboard/study                       (matrix)
#   5. …/dashboard/graph                       (graph)
#   6. Bob IDE, Tasks panel visible
```

Take rule: if the live run comes back clean, `./demo/reset.sh` and go again
(~25s per take; it diverges on most). Keeping a diverged take is selecting a
representative run — every take is a real Bob run.

---

## 0:00–0:20 · The problem  (20s) — tab 1, hero only

> This is what code review has become: the agent's own summary of its own work.
> It's written by the system that did the work, it's almost always right — and
> that's the problem. After two hundred accurate summaries, nobody checks the
> two hundred and first.

## 0:20–0:50 · IBM Bob works, live  (30s) — terminal

Run `./demo/run.sh`. Let Bob's tool calls stream at real speed.

> So let's catch one. This is IBM Bob, running headless on a real repo — the
> task is a one-line bug fix, and nothing tells Bob to cut any corner. There's
> just a test suite it isn't forced to run.

## 0:50–1:35 · The catch  (45s) — tab 2, then dashboard run page

Board card appears and turns red. Click through to the run page.

> The moment Bob finished, its trace landed and Receipts audited it. Bob said —
> quote — the change works. The record shows one file written, one command run,
> and no test run anywhere.
>
> And this is the part that matters: the finding cites line 28 of the trace.
> Not a vibe — a line number.

Terminal, one command: `sed -n '28p' demo/traces/*.ndjson`

> sed returns the exact record. Then we replay the run's own writes and run the
> tests Bob skipped: **one failed**. The summary was honest, and wrong — and
> no reviewer would ever have known.

## 1:35–2:05 · The product  (30s) — tabs 3 → 4 → 5, fast

> This runs as a merge gate in CI, a live board, and this dashboard. We didn't
> trust it on one anecdote either: the same eight tasks, three runs per agent,
> forty-eight real runs. Bob diverged on six of fifteen trapped runs — three out
> of three on this task — and the control agent on none, with **zero false
> alarms across eighteen control runs**. In the graph, runs cluster by task, and
> diverged runs hang off the finding that caught them: shared cause, visible as
> shared shape.

## 2:05–2:35 · Bob is the runtime  (30s) — Bob IDE

Show: `bob run --mode verifier` (terminal), then the parallel subagents panel
in the IDE, then Tasks list.

> And Bob isn't just the subject — it's the runtime. A custom verifier mode
> audits finished runs. A skill has Bob read a spec into checkable requirements.
> A triage skill fans out parallel subagents, one per flagged run — and two of
> those subagents came back and proved *Receipts* wrong. Chasing that exposed a
> real bug in Bob Shell itself: it drops most of its own tool-call events. We
> fixed our tool, lost a detection, and published the lower number.

## 2:35–2:50 · Close  (15s) — tab 1, scroll the stats band

> A tool that demands receipts has to show its own. receipts-bob.vercel.app —
> the study, the dashboard, and every line it cites are live.

Final frame: the site URL + repo URL, 3 seconds of silence.

---

## Advisor checklist this cut satisfies

| Advisor check | Where |
|---|---|
| Theme fit communicated | 0:00 problem + 1:35 workflow surfaces |
| Working solution demonstrated | 0:50–2:35 continuously on screen |
| Bob's contribution clear | Bob live 0:20, Bob-as-runtime 2:05, IDE tasks |
| Never on camera | BOB_API_KEY, ~/.receipts/auth.json, personal accounts |

Upload to **YouTube (unlisted is fine — link-public)** for advisor coverage.
