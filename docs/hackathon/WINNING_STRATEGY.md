# Winning Strategy — 20-point rubric playbook

> Companion to [HACKATHON_CONTEXT.md](HACKATHON_CONTEXT.md). Written Aug 28, 2026, ~11:30 ET,
> with **~46 hours** to the 10:00 AM ET Aug 30 deadline.

---

## 0. The single most important insight

Judging is **4 equal 5-point criteria**. Not 60% technical. Design/usability is worth exactly as much as
creativity, which is worth exactly as much as completeness. Most dev-tooling hackathon projects are a pile of
Markdown plus a CLI and quietly forfeit ~5 of 20 points on **Design and usability**, then forfeit most of
**Effectiveness and efficiency** because they never measured anything.

**You win by not forfeiting.** A merely-good idea that scores 4/4/4/4 = 16 beats a brilliant engine that
scores 5/2/1/5 = 13. Allocate your 46 hours across all four axes, not just the engine.

Second insight: **the rules say scores "will be determined by reviewing all team deliverables."** Judges grade
the video and the two written statements. The repo is evidence, not the experience. Build the artifact set
deliberately — do not treat the video as a 30-minute afterthought at 3 AM.

---

## 1. The archetype that wins

| | Archetype A | Archetype B ✅ |
|---|---|---|
| Pitch | "We used Bob to build App X" | "We built a Bob-native system that transforms workflow Y — and used Bob to build it" |
| Bob's role | Code generator | Runtime **and** tool |
| Theme fit | Fails "not just assist with coding" | Directly satisfies it |
| Reusability | One-off app | A skill/mode pack any team can install |
| `bob_sessions/` screenshots | Proof of homework | Proof the product works |

The theme literally says: *"Leverage features like Agent mode, parallel tasks, subagents, and document
understanding to manage and improve multiple steps, not just assist with coding."* That sentence is a
specification. Build against it.

**Concretely, Archetype B means your repo ships:**
```
.bob/
  skills/<your-workflow>/SKILL.md + checklists + scripts/
  agents/<your-subagent-personas>
  custom_modes.yaml
  rules/ and rules-<mode>/
  mcp.json          # if you expose your own tool surface
AGENTS.md           # generated via Bob /init
bob_sessions/       # required deliverable
```
…plus the thing that makes it usable and pretty (§4).

**The double loop to say out loud in the video:** *"Bob built the system, and the system is made of Bob."*

---

## 2. Criterion-by-criterion attack plan

### 2.1 Completeness and feasibility — 5 pts
**Definition of done:** the workflow runs end-to-end, unattended, on a real or sample project, including the
verification step. No "and then you'd manually…".

- Pick **one narrow workflow** and finish 100% of it. Never 60% of three workflows.
- Run it on a **real or sample project** (the guide says exactly this). A public OSS repo with a permissive
  licence, or IBM's own Galaxium Travels demo app, is ideal — and free of data-compliance risk.
- Feasibility for an **enterprise** audience (your judges are IBM SMEs): show governance. Audit trail,
  approval gates, `.bobignore` for sensitive paths, deterministic tool restrictions via mode `fileRegex`,
  cost visibility. One slide/section on "how a team adopts this on Monday" buys real points.
- ❌ Kill risks: hardcoded happy path, a demo that only works on one input, unhandled errors on camera.

### 2.2 Effectiveness and efficiency — 5 pts  ← *most commonly forfeited*
This is the **measurement** criterion. The theme says "clearly demonstrate impact." Show numbers or lose points.

**Do this in the first 4 hours, before you build anything:**
1. Screen-record a human (you) doing the workflow manually on the sample project.
2. Log: wall-clock minutes · number of manual steps/context switches · errors made or missed ·
   files touched · anything domain-specific (coverage %, findings count, review comments).
3. Save it as `benchmarks/baseline.md` + the raw recording. **You cannot recreate this later.**

Then after building, run the identical task through your solution and produce:

| Metric | Manual baseline | With our solution | Delta |
|---|---|---|---|
| Wall-clock time | 62 min | 7 min | **−89%** |
| Manual steps | 23 | 2 | **−91%** |
| Issues found | 4 | 11 | **+175%** |
| Bobcoins consumed | — | 1.8 | — |

Put that table in three places: README, on screen in the video, and in the 500-word statement.

**Efficiency has a second meaning here — resource efficiency.** Explicitly design for it and say so:
cheap read-only **explore** subagents for fan-out, the full model only for synthesis; phase boundaries to keep
context under ~50% of the 270k window; skills instead of re-prompting. This flatters the product *and* is
a genuinely sophisticated engineering argument that most teams will not make.

### 2.3 Design and usability — 5 pts  ← *the cheapest 5 points on the board*
Your competitors are shipping terminal output. Ship an interface.

- **Something visual must exist.** Ranked by effort/impact: a clean web dashboard (Next.js/Vite + Tailwind) >
  a beautifully generated HTML/Markdown report artifact > a polished TUI > raw CLI.
- Design the **output artifact** too — if your workflow produces a report, make it a genuinely handsome
  document (severity colour-coding, diff views, Mermaid diagrams — Bob generates Mermaid natively).
- Usability of the developer experience counts: one-command install, obvious affordances, real empty states,
  real error states, sensible defaults.
- The **video is also judged on design.** High contrast, large fonts, no 8pt terminal text, no dead air.
- Reuse the local `frontend-design-guidelines` / `ui-styling` skills in *this* workspace to get there fast.

### 2.4 Creativity and innovation — 5 pts
The submission page wants a solution that addresses the issue "in a new way the judges have never seen before."

- **The 5 published example use cases (onboarding, code review, testing hub, release readiness, legacy
  modernization) will be the most crowded lanes in the hackathon.** They're printed in the guide that every
  participant reads. Doing one of them straight caps your creativity score. If you do one, you need an
  unexpected *mechanism* or an unexpected *domain*.
- Cheap, high-signal differentiators — all explicitly named in the theme, all rarely used:
  - **Document understanding.** Attach a real `.pdf` / `.docx` / `.xlsx` and make it load-bearing —
    a compliance standard, an RFC, a runbook, a legacy spec, a vendor API PDF, an incident postmortem.
    Almost nobody will do this. It is named in the theme sentence.
  - **Parallel subagents.** The parallel-subagents panel (completion count, combined tokens/cost/elapsed,
    failed calls) is *outstanding* demo footage and visually proves "multi-step, not just coding."
  - **Bob generating Bob artifacts** — a system that emits skills/modes/subagent personas is meta,
    memorable, and directly showcases 2.0's extensibility.
  - **Actor–critic / sensor loops.** IBM's own tutorial covers actor-critic for secure code; a closed
    feedback loop (generate → adversarial critic → re-generate until a machine-checkable gate passes) maps
    perfectly onto the enablement session's *guides vs. sensors* framing.
- Echo the PM's own vocabulary in the write-up: **Explore → Plan → Implement → Verify**, *guides
  (feedforward)* vs *sensors (feedback)*, *phases as context boundaries*, *machine-runnable verification
  designed during planning*. The judges include the people who taught that.

---

## 3. Candidate directions, scored

Each scored /5 per criterion as a rough prior. Pick one in the first two hours and do not change.

| # | Direction | Comp | Eff | Design | Creat | Crowding |
|---|---|---|---|---|---|---|
| 1 | **Runbook/SOP → executable Bob workflow compiler.** Ingest a real ops runbook or process doc (PDF/DOCX) via document understanding; Bob emits a working `.bob/` skill pack + custom mode + subagent team; run it live on a sample repo. | 4 | 5 | 4 | **5** | Very low |
| 2 | **Compliance-standard → verified codebase.** Attach a real standard (OWASP ASVS, an internal policy PDF); parallel explore subagents fan out over the repo; actor–critic loop fixes findings until a machine gate passes; emits SARIF + a designed report. | 4 | **5** | 5 | 4 | Low |
| 3 | **Incident → reproduction → fix → PR.** Feed a stack trace + logs + postmortem doc; subagents localize, write a *failing* test, patch, verify, open the PR. MTTR as the headline metric. | 4 | 5 | 4 | 3 | Medium |
| 4 | Straight onboarding / code-review / test-hub assistant (guide examples) | 5 | 3 | 3 | 2 | **High** |

**Recommendation: #1 or #2.** Both are Archetype B, both make document understanding load-bearing, both
produce a crisp before/after number, and both leave room for a genuinely designed output artifact. #2 is the
safer build (clear machine-checkable gate = easy metrics); #1 is the higher creativity ceiling.

If the team already has an idea, don't discard it — instead run it through this checklist:
*Is it Archetype B? · Does a document feed it? · Do subagents run in parallel visibly? · What is the one
number? · What does the UI look like? · Can it finish in 20 working hours?*

---

## 4. The 46-hour schedule (all times ET)

| When | Block | Output |
|---|---|---|
| **Aug 28, 11:30–12:00** | Accounts | Bob IDE installed, `ibm-coding-challenge-uat` account selected, team confirmed on the site |
| 11:30 (parallel) | **Request the team IBM Cloud account NOW** | ~2 h provisioning lag; free option value even if unused |
| **12:00–14:00** | Lock scope | Write the **500-word statement first, as the spec.** If you can't write it, the idea isn't sharp |
| **14:00–16:00** | **BASELINE** | `benchmarks/baseline.md` + screen recording of the manual workflow |
| **16:00–00:00** | Core loop, ugly but end-to-end | `.bob/` skills + modes + agents + rules; `AGENTS.md` via `/init`; it runs |
| **Aug 29, 00:00–06:00** | Sleep / buffer | — |
| **06:00–14:00** | **Design pass** | The UI / report artifact. This is 5 points. Do not skip it |
| **14:00–17:00** | Measure "after" | Metrics table, filled in with real runs |
| **17:00–21:00** | **Video** | Script → record → cut to **< 3:00**. Upload public (YouTube unlisted-public/Vimeo/Drive) |
| **21:00–23:00** | Repo hygiene | README, `bob_sessions/` screenshots, licence, secret scan |
| **~23:00** | **SUBMIT #1** | Triggers the AI Submission Advisor pass |
| **Aug 30, 06:00–09:00** | Read Advisor email, fix flagged items, **resubmit ALL fields** | Final entry |
| **09:00** | Hard stop | 1 h buffer before 10:00 |

Submitting ~11 hours early to harvest Advisor feedback is close to free extra points. Take it.

---

## 5. Bobcoin economics (40/person, no refills)

- Use **Plan mode once** per phase, write the plan to a file, then start a **fresh conversation** to implement.
  Phases are context boundaries (the PM's own guidance).
- Fan out with **explore** subagents (lighter model, read-only) — never read a codebase in the main thread.
- Never paste a whole codebase. Use `@/path/file`, `@problems`, `@terminal`.
- Use **Rollback / git** to undo bad output instead of spending three more turns arguing with it.
- **Reserve ~25% of coins for the final clean demo runs** — you want screenshot-worthy sessions at the end.
- **Name your tasks deliberately.** The Tasks list is literally what you screenshot for deliverable 4.
  `Generate ASVS skill pack from standard PDF` reads like a product. `test 3` reads like a student.
- Split work across teammates' accounts by *workstream* (engine / UI / benchmark+video) to pool the 40s.

---

## 6. Deliverable templates

### 6.1 Video — 3:00 hard cap
| Time | Beat |
|---|---|
| 0:00–0:20 | **Hook with a number.** "We timed it: this takes a senior engineer 62 minutes, every release." |
| 0:20–0:35 | One sentence: what we built. |
| 0:35–2:15 | **LIVE DEMO — ≥ 90 s.** Document going in → parallel subagents panel → artifact coming out → the UI. Real screen, real run. |
| 2:15–2:40 | Before/after metrics table on screen. |
| 2:40–3:00 | How Bob was used (modes, skills, subagents named on screen) + adoption path + repo URL end card. |

Narrate throughout. Judges see dozens of screen-shares — open on the *number*, not on "hi, we're team X."

### 6.2 Problem & solution statement — ≤ 500 words
Problem with a measured cost (~100 w) · Solution + technical approach (~180 w) · Target users and how they
interact (~70 w) · Why it's creative and unique — name the thing nobody else is doing (~100 w) ·
Impact numbers (~50 w).

### 6.3 IBM Bob usage statement — be relentlessly specific
A mapping table, not prose. For each: **capability → where used → what it produced.**
Cover modes used, custom modes created, skills authored, subagents spawned (count and type), document
understanding (which documents), MCP servers, rules/`AGENTS.md`, code review, PR generation, Rollback,
Bob Shell if used. Quote **actual task session names that match the filenames in `bob_sessions/`**, and
include Bobcoin consumption. If watsonx.ai / Orchestrate were used, say exactly which model, which agent,
which tool.

### 6.4 Repository
```
README.md            # problem, demo GIF, metrics table, architecture, install, adoption path
.bob/                # skills, agents, custom_modes.yaml, rules/, mcp.json
AGENTS.md
bob_sessions/        # REQUIRED — teamname_taskNN_description_summary.png
benchmarks/          # baseline.md, results.md, raw evidence
docs/                # architecture, Mermaid diagrams
.gitignore .bobignore LICENSE
```

---

## 7. Disqualifier / risk register

| Risk | Mitigation |
|---|---|
| Work predates the contest | Fresh repo; all commits timestamped inside the window; don't import an old project |
| **Credentials in the repo → IBM Cloud suspension** | `.gitignore` + `.bobignore`; `git secrets`/grep scan before every push; never paste an API key into chat |
| Missing `bob_sessions/` | Capture screenshots *as you go*, not at the end — the Advisor explicitly checks for this |
| Video > 3:00 | Hard-cut. Judges stop at 3:00 |
| Bob not a core component | Ineligible. Bob must be visible in the architecture and the video |
| Resubmitting only changed fields | **Re-upload every deliverable** — the latest entry is the whole official submission |
| Bobcoins hit 100% | §5 budget; split across teammates; the guide suggests falling back to watsonx |
| Data compliance | No client data, no PI, no social-media data. Keep a list of every public site used |
| Repo not public / video not public | Check both in an incognito window before submitting |

---

## 8. Pre-submit checklist

- [ ] Repo public, opens in incognito; video link opens in incognito
- [ ] `bob_sessions/` has screenshots from **every** team member, PNG, named per convention
- [ ] Video ≤ 3:00, ≥ 90 s of live solution, narrated, Bob visibly used
- [ ] Statement ≤ 500 words (count it)
- [ ] Bob usage statement names specific modes/skills/subagents/documents and matches the screenshots
- [ ] Metrics table appears in README + video + statement, with a stated baseline method
- [ ] No secrets anywhere in history (`git log -p | grep -iE 'api[_-]?key|apikey|password|token'`)
- [ ] Team roster correct on the My Team page
- [ ] Submitted once early for Advisor feedback, then resubmitted **in full**
- [ ] Everything frozen before 10:00 AM ET Aug 30
