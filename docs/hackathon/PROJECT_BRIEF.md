# Convoy — governed fleet execution for IBM Bob

> **FINAL. Decided Aug 29 2026.** Solo build. Supersedes all earlier briefs.
> Companion docs: [HACKATHON_CONTEXT.md](HACKATHON_CONTEXT.md) · [WINNING_STRATEGY.md](WINNING_STRATEGY.md)

---

## 1. One line

**Define a change once. Bob applies it across your whole fleet of repositories in parallel. Every run is
verified and gated, so you review one report instead of forty pull requests.**

Workflow improved: **application maintenance / release readiness** — both named in the hackathon theme.

---

## 2. Why this problem

A CVE drops on Friday at 5pm. You have 40 services. Today that is somebody's weekend, or a fragile codemod,
or it quietly does not happen. AI agents *should* solve this — but nobody will let 40 unsupervised agents
loose on 40 production repositories, and that is precisely where agent projects die.

The evidence:
- **IBM, July 9 2026, in the Bob 2.0 announcement:** "85% of DevSecOps professionals surveyed agree that
  **AI has shifted the bottleneck from writing code to reviewing and validating it.**"
- **88% of agent pilots never reach production.** The cited blocker is governance and verification, not
  model quality. ~84% of developers use AI tools; **only ~3% highly trust the output.**
- Self-review is a *structural* conflict of interest: a model shares the blind spots of the model that
  wrote the code.
- **Lived evidence:** the author built a multi-agent delivery platform during a 2026 internship —
  transcript → requirements → tickets → code, with human review gates, 41 tests passing. It never reached
  production because the enterprise would not grant agents permission to act. That is the 88% statistic,
  first-hand.

## 3. The gap in Bob specifically

Bob 2.0 has subagents, skills, custom modes, MCP, Bobalytics, and a genuine headless interface
(`bob run --format stream-json`). What it does **not** have is **any orchestration above a single task in a
single workspace.** `bob run` is one-shot.

Meanwhile IBM's own strategy for Bob is *fleet-scale modernization* — the Premium Packages are Z (COBOL,
PL/I, JCL), i (RPG), and Java 25 migration. Those are inherently many-repository problems being served by a
one-repository tool.

**Convoy is the missing layer, and it is the layer IBM's own roadmap implies.**

---

## 4. Architecture

```
workflow.yaml  ──►  planner  ──►  parallel workers ──►  verifier ──►  gate ──►  aggregate report
   (one change)                    (bob run × N repos)   (Receipts)   (human)     (audit trail)
```

1. **Workflow definition** — one YAML file describing the change as ordered Bob steps
   (e.g. *upgrade dependency → run tests → update changelog*). Deliberately **not** a drag-drop canvas:
   a file is cheaper to build, version-controllable, and reads as more credible to engineers.
2. **Fan-out executor** — a process pool driving `bob run --format stream-json --max-cost <n>` against each
   repository concurrently. Bob is the worker; Convoy is the conductor.
3. **Verification (the Receipts component)** — per repo, reconstruct **ground truth deterministically** from
   the NDJSON event stream plus git plus the filesystem: which files were actually written, which commands
   actually exited non-zero, whether the claimed test actually exists and actually ran. Then contradict the
   agent's own summary against those facts. *No LLM in this step — these are facts.*
4. **Independent second opinion** — for anything ambiguous, a separate pass seeing only the requirement and
   the diff, never the generator's reasoning, running **Granite on watsonx.ai**. Different model family,
   different context, no shared assumptions. This is the structural fix for self-review bias.
5. **Human gate** — runs that diverge pause and route to a reviewer with the evidence attached; approve or
   reject, then resume. (The one pattern carried over from the Relay design: durable review gates.)
6. **Aggregate report** — *"37 clean · 2 need review · 1 failed"*, with a per-repo audit trail proving what
   changed and what was verified.

**Design principle to state out loud:** the harness is mostly deterministic; the model is used only where
judgment is genuinely required. That ratio is what separates this from "an LLM reviewed a diff."

---

## 5. The demo

| Time | On screen |
|---|---|
| 0:00–0:25 | The internship story, told in two sentences, ending on: *it never shipped, because nobody could supervise the agents.* Then IBM's own 85% line. |
| 0:25–0:40 | A CVE advisory. Twelve repositories, all depending on the vulnerable version. One `workflow.yaml`. |
| 0:40–1:40 | **Convoy runs.** A wall of repositories executing in parallel, live — Bob working in each. Progress, cost, and elapsed time per repo. |
| 1:40–2:15 | **The catch.** One repo's agent reports success; Convoy's verifier shows no test ever ran and the patch never landed in the lockfile. It is gated, with the raw event proving it. Granite's independent pass disagrees with the generator. |
| 2:15–2:40 | The aggregate: *9 clean, 2 gated, 1 failed.* Audit trail. Metrics vs. the manual baseline. |
| 2:40–3:00 | Bob usage on screen — `bob run`, subagents, skills, the `verifier` mode with no edit permissions — plus the CI adoption path and repo URL. |

The 1:40 beat is the whole video: **it catches the agent being wrong, at scale, with proof.**

---

## 6. Rubric fit

| Criterion | How it scores |
|---|---|
| **Completeness & feasibility** | End-to-end: definition → execution → verification → gate → audit. Adoptable as one CI job. |
| **Effectiveness & efficiency** | Baseline: patch N repos by hand, timed. Convoy: wall-clock, divergences caught, Bobcoins spent. Real numbers. |
| **Design & usability** | A live parallel-execution dashboard is the best-looking artefact available, and semantic state (clean/gated/failed) reads at a glance. |
| **Creativity & innovation** | Nobody is orchestrating Bob at fleet scale, and nobody is verifying agent claims against the agent's own event log. |

## 7. Bob usage (Archetype B — Bob is the runtime, not the assistant)

```
.bob/
  skills/apply-fleet-change/SKILL.md
  skills/reconstruct-ground-truth/SKILL.md
  skills/contradict-claims/SKILL.md
  agents/verifier                  # explore-type, read-only
  custom_modes.yaml                # `verifier`: read only, NO edit group at all
  rules/
AGENTS.md
convoy/            # fan-out executor, NDJSON parser, gate engine
workflows/         # example workflow.yaml definitions
dashboard/         # live run view + aggregate report
benchmarks/        # manual baseline vs Convoy
bob_sessions/      # required deliverable
```

**Governance detail to demo on camera:** the `verifier` custom mode declares `read` and **no `edit` group at
all** — per Bob's docs, omitting `groups` grants no tool access. The verifier structurally cannot modify what
it audits. Separation of duties in three lines of YAML.

## 8. Scope

**In:** workflow YAML, parallel fan-out, deterministic verification, watsonx/Granite second opinion, human
gate, dashboard, aggregate report, ~10 demo repos, benchmark.

**Out:** drag-drop canvas, Jira/Teams/MS Graph, LangGraph, COBOL parsing, meeting transcripts, auth/multi-user,
anything from the internship repository (nothing carries over but the lesson).

## 9. Risks

| Risk | Response |
|---|---|
| **`bob run --format stream-json` not behaving as documented** | **Validate in hour one, before anything else.** The deterministic core depends on it. If the event stream is unusable, fall back to git-diff + filesystem verification and rescope immediately. |
| Bobcoin burn across N parallel repos | `--max-cost` per run; demo with 10–12 repos, not 40; dry-run mode for iteration. |
| Verification drifting into vague "is this good code" | Keep checks factual: file exists, exit code, path in declared scope, claim vs. log. |
| Parallelism flaky on camera | Pre-record a clean run as backup footage; never let the live demo be the only take. |

## 10. Hour one

1. `bob run --format stream-json "..."` → confirm parseable NDJSON with `tool_use` / `tool_result` / `error`.
2. Confirm `--max-cost` halts a run.
3. **Take the manual baseline** — patch 3 repos by hand, timed, recording what you catch and miss. Unrecoverable later.
4. Only then build.
