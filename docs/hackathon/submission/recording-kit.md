# Recording kit

Everything needed to film, in the order you need it. The script itself is in
`video-script.md`; this is the operational half.

## Before you press record

```bash
# 1. the API key, in a pane you do NOT record
export BOB_API_KEY=…

# 2. install this checkout and put receipts on PATH for this shell
uv sync --frozen
export PATH="$PWD/.venv/bin:$PATH"
receipts --version          # expect: receipts 0.1.0

# 3. clear the board
./demo/reset.sh

# 4. pane 1 — the live board
receipts demo/traces --watch      # → http://127.0.0.1:7878
```

Two panes. Browser left at roughly 60% width showing the board, terminal right.
Terminal font large enough to read at 720p — 16pt or more.

## The one thing to know

**Bob is not deterministic on the demo task.** Across the runs captured today it
diverged on roughly three takes in five. On the other two it genuinely verified
its work and Receipts correctly returned `clean`.

So: run `./demo/run.sh`, and if the take comes back `clean`, run
`./demo/reset.sh` and go again. Keeping a take where the run diverged is
selecting a representative run, not staging one — every take is a real Bob run
against the same task, and the tool is doing the same thing in both.

Roughly 25 seconds per take, so this costs very little time or Bobcoins.

## The take you want

```
RECEIPTS · diverged · 1 medium · bob
 ! 1. Claimed the change works, but never ran the tests
```

and, ideally, step 5 printing `1 failed, 2 passed` — that is the live run having
broken a test it never ran. When you get that, you have the whole argument in one
unbroken shot and section 1:30 of the script can be trimmed to ten seconds.

If the live take is clean, keep it and lean on step 6: the recorded run replays
from its own trace and always shows `1 failed, 2 passed`.

## Sequence on camera

| Shot | Pane | What happens |
|---|---|---|
| 1 | terminal | `./demo/run.sh` — the task, then Bob working |
| 2 | terminal | Bob's summary prints |
| 3 | **browser** | the card appears and turns red as the trace lands |
| 4 | browser | click the run — claim versus actual, the finding |
| 5 | browser | click an evidence line — the trace scrolls and highlights it |
| 6 | terminal | `sed -n '<line>p' demo/traces/fix-parse-range.ndjson` |
| 7 | terminal | step 5 of the demo — the tests Bob did not run |
| 8 | terminal | `receipts login` → browser approves → `receipts push` |
| 9 | browser | the workspace, with the run in it |
| 10 | browser | receipts-bob.vercel.app — the site and the 48-run report |

## Never on camera

- `BOB_API_KEY`, in any pane, at any point
- The contents of `~/.receipts/auth.json`
- Your Vercel or GitHub account pages

## After recording

```bash
./demo/reset.sh
```
