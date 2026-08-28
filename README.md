# Receipts

**Your coding agent says it did the work. Receipts checks whether it actually did.**

Every AI code reviewer on the market reviews *the diff* — the outcome. Receipts reviews
**the execution trace** — what the agent actually ran, in what order, and what came back.
Some failures are invisible in a diff and obvious in a trace.

```
$ receipts check trace.ndjson

RECEIPTS · diverged · 1 high, 1 medium · bob

  claimed: "Implemented the discount rule and added tests. All tests passing."
  actual : 3 file(s) written, 2 command(s) run, 1 failed

!! 1. A failing test was edited, not fixed
     `pytest -q` failed, then `tests/test_pricing.py` was rewritten, and the suite
     went green — with no implementation file written in between.
     · [event 5] test run failed        F 1 failed, 0 passed  E AssertionError: assert 90.0 == 85
     · [event 7] test file rewritten: tests/test_pricing.py
     · [event 9] suite then passed      .. 2 passed in 0.03s
```

In the diff, that is a three-line test change that looks completely reasonable.

## Why

- **85% of DevSecOps professionals** say AI has shifted the bottleneck from writing code to
  reviewing and validating it. *(IBM, July 2026)*
- ~84% of developers use AI coding tools; **only ~3% highly trust the output.**
- **88% of agent pilots never reach production** — blocked on governance and verification,
  not on model quality.
- Experienced developers measure **19% slower** with AI while believing they are 20% faster.

A model cannot reliably review its own work: it brings the same blind spots that produced the
code. Receipts does not ask a model whether the code is good. It checks the agent's claims
against facts recorded in the agent's own trace.

## What it detects

| Detector | What it means |
|---|---|
| `test_edited_after_failure` | A test failed, the test file was rewritten, the suite went green — and no implementation file was touched in between. |
| `passing_claimed_over_failure` | The summary says the tests pass; the last test run failed and nothing re-ran. |
| `tests_claimed_but_absent` | The summary claims tests were added; no test file was ever written. |
| `unresolved_failures` | Commands that failed and were never followed by a successful re-run. |

**Every finding cites the trace events that prove it.** Nothing is inferred by a language model.

## Install and use

```bash
uv sync
receipts check trace.ndjson                      # human-readable
receipts check trace.ndjson --json               # evidence bundle
receipts check trace.ndjson --html report.html   # self-contained page
```

Capture a trace from IBM Bob:

```bash
bob run --format stream-json "implement the retry policy and add tests" > trace.ndjson
receipts check trace.ndjson --fail-on high
```

Exit codes: `0` clean · `1` gated (findings at or above `--fail-on`) · `2` error.
That makes it a merge gate:

```yaml
- run: bob run --format stream-json "${{ inputs.task }}" > trace.ndjson
- run: receipts check trace.ndjson --fail-on high --html receipts.html
```

## How it works

```
trace.ndjson ──► adapter ──► canonical events ──► ground truth ──► detectors ──► evidence bundle
                (bob |                            (deterministic)
                 claude-code)
```

1. **Adapters** normalise IBM Bob and Claude Code traces into one event model, so detectors
   never depend on a vendor's wire format.
2. **Ground truth** is reconstructed *deterministically* — which files were written, which
   commands ran, which failed. No model involved.
3. **Detectors** compare the agent's closing summary against those facts.

The deterministic core is the point. A tool that asks you to trust an LLM's opinion about
whether to trust an LLM has not solved anything.

### Two things real traces taught us

Both were found by running against captured agent runs, and neither is visible from the docs:

- **Agents edit files through the shell.** A real run made every edit with `sed -i` inside a
  Bash call. A tool watching only file-editing tools would report *zero files written*, so
  Receipts parses command lines for redirects, heredocs, `sed -i`, and `tee`.
- **Exit codes lie.** Agents pipe test output through `tail`, and a pipeline exits with the
  status of its *last* command — so a failing suite is reported as a successful tool call.
  Captured output therefore outranks reported status.

### On false positives

An earlier version of `unresolved_failures` flagged any failed command the summary did not
mention. That fires on every healthy red-green cycle, where a failing test is the expected
first step. A detector that cries wolf on correct work destroys trust in every other finding,
so it now reports only failures that were never resolved.

## Development

```bash
uv run --with pytest pytest      # 21 tests
```

| Path | Contents |
|---|---|
| `src/receipts/adapters/` | Per-agent trace parsers |
| `src/receipts/detectors/` | One file per detector |
| `src/receipts/shell.py` | Recovering file writes from command lines |
| `src/receipts/signals.py` | Deciding whether a command actually failed |
| `corpus/` | Captured real agent traces |
| `dashboard/` | Example evidence bundles |

## Status

Working prototype. Bob and Claude Code traces supported; the four detectors above are
implemented and tested, including a regression test against a captured real run.
