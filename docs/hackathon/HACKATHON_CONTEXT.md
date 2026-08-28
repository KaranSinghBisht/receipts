# IBM TechXchange 2026 Pre-conference Dev Day Hackathon — Master Context

> **Status: OFFICIAL.** Verified on **August 28, 2026** against the [Official Rules PDF](../../33893b2e0869f45c5249d408.pdf)
> (local, 15 pp.) and the [official Hackathon Guide PDF](https://watsonx-hackathons-2026.s3.us.cloud-object-storage.appdomain.cloud/IBM-TXC-2026-Pre-conference-Dev-Day-hackathon-guide.pdf)
> (41 pp.), plus the `Complete the hackathon` page copy. Facts below are quoted or paraphrased from those
> sources. Anything not in them is marked **[ASSUMPTION]** or **[UNKNOWN]**.
>
> Read [WINNING_STRATEGY.md](WINNING_STRATEGY.md) for how to actually score against the rubric.

---

## 1. Hard constraints (memorize these)

| Item | Value |
|---|---|
| Theme | **"Build with purpose using IBM Bob 2.0"** |
| Contest opens | Aug 28, 2026, **10:00 AM ET** |
| Contest closes / submission deadline | Aug 30, 2026, **10:00 AM ET** |
| Team size | 1–5 people. One team per person. One entry per team. |
| Required tech | **IBM Bob IDE** — mandatory, and must be a *core component* of the solution |
| Optional tech | watsonx Orchestrate, watsonx.ai, IBM Cloud services (NLU, STT, TTS, Cloudant) |
| Bobcoins | **40 per participant**, auto-applied. No top-ups at 100%. |
| IBM Cloud credits | **$80 per team** (optional account). Account **suspended** at 100%. |
| Language | English |
| Originality | Must NOT have existed "in any substantive form/format prior to the Contest" |
| Accounts die | IBM Bob access ends Sept 1; team IBM Cloud account closes EOD Sept 1 |

**Work must stop at the deadline.** Continuing to change the video or repo after 10:00 AM ET Aug 30 can
disqualify the project.

---

## 2. The judging rubric — VERIFIED, from the Official Rules

> "Each Submission will be scored based on the following criteria with a minimum score of 0 and maximum
> score of 20 points, with the final score being the average of the judges' scores and an assessment of the
> team's submitted deliverables."

| Criterion | Points |
|---|---|
| Completeness and feasibility | **5** |
| Effectiveness and efficiency | **5** |
| Design and usability | **5** |
| Creativity and innovation | **5** |
| **Total** | **20** |

- **A Submission must receive a minimum score of 12.5 points for prize consideration.**
- Winners = highest score. "Scores will be determined by reviewing all team deliverables."
- Judges are SMEs + technology leaders, added throughout the hackathon; subject to change.
- Sponsors may reject any submission that does "not provide a credible or feasible use of watsonx technology,"
  was pre-built, or was not "submitted honestly and in good faith."
- Winning teams **may be subject to a code review** after the contest.

**Consequence:** judges score the *deliverables*, not necessarily a live run of your repo. The video and the two
written statements carry the score. Build for the artifact set, not just the code.

---

## 3. Prizes

- **Top 50 scoring qualified submissions:** 1 ticket per team member to IBM TechXchange 2026
  (Oct 26–29, 2026, Atlanta, GA). ~$1,599 USD value. **Travel/lodging not included.**
- **1st place:** $2,000 USD + 1 ticket per member **including travel and lodging**.
- **2nd place:** $1,000 USD. **3rd place:** $500 USD.
- Prizes distributed by BeMyApp. Winners announced by email after the Judging Period.

---

## 4. The challenge statement (verbatim from the Hackathon Guide)

> **Build with purpose using IBM Bob 2.0**
>
> Create a solution that improves a specific developer workflow, such as onboarding, debugging, code review,
> testing, application maintenance, or release and deployment processes. Start by clearly defining a problem
> where time, effort, or errors are too high today. Then, using IBM Bob 2.0, build a working prototype on a real
> or sample project that demonstrates a full solution to improve the specified workflow. Leverage features like
> **Agent mode, parallel tasks, subagents, and document understanding** to manage and improve multiple steps,
> **not just assist with coding**. Clearly demonstrate impact by showing how your solution increases
> productivity, reduces manual effort, errors, and rework, or significantly shortens the time required to
> complete tasks.

Four load-bearing phrases: *specific developer workflow*, *full solution*, *not just assist with coding*,
*clearly demonstrate impact*.

---

## 5. The four deliverables (all required)

### 5.1 Video demonstration
- Public URL. **3 minutes maximum** — "Judges will not watch more than 3 minutes."
- Briefly introduce the problem, but **leave ≥ 90 seconds** showing the solution running on screen.
- Must **clearly demonstrate how IBM Bob was used**.
- Narration required. Creativity encouraged — judges will watch many screen-share videos.
- Host on YouTube / Vimeo / Google Drive to also qualify for automated AI Submission Advisor feedback.

### 5.2 Written problem and solution statement
- **500 words or less.** Must cover: the specific problem; what the solution is; target users; how they
  interact with it; why it is creative and unique; how it addresses the issue "in a new way the judges have
  never seen before."

### 5.3 Written statement on how IBM Bob was used
- "Clear and specific details on how and where your team used Bob." Also describe watsonx.ai /
  watsonx Orchestrate usage if applicable. **Be specific.** [UNKNOWN] no word limit stated.

### 5.4 Code repository + Bob session screenshots
- Public repo URL (GitHub/GitLab/Bitbucket) with all project code and artifacts.
- **Must contain a `bob_sessions/` folder** with each team member's Bob task session summary screenshots.
- Optional: the GitHub IBM Hackathon repository template (ships `.gitignore` + `.bobignore`).
- **Credential exposure = immediate IBM Cloud account suspension.** Never commit API keys.

### How to capture a Bob task session summary (exact steps from the Guide)
1. Create a folder named **`bob_sessions`** in the submission repo.
2. In Bob IDE chat, select **Tasks** to display the task list. (Use **All** to see tasks across workspaces.)
3. Select a task related to the submission — it opens in the chat panel.
4. **Select the task header** → a *task session consumption summary* is displayed.
5. Screenshot it. **PNG preferred** for text clarity.
6. Filename convention: `teamname_taskNN_short_description_summary.png`
   (guide's example: `teamalpha_task01_login_flow_summary.png`)
7. Repeat for **all** tasks related to the submission; upload every screenshot to `bob_sessions/`.

---

## 6. Submission mechanics

Submit on the **My Team → Submissions** page of the competition site.
1. Confirm team member emails (Team Lead edits roster under Team Members first).
2. Video URL. 3. Problem/solution statement. 4. Bob usage statement. 5. Repo URL. 6. Submit.

- Multiple **draft** submissions allowed until the deadline.
- **Re-submitting replaces everything** — you must re-upload *all* deliverables, not just changed ones.
- The **most recent** submission entry is the official one.
- Submit early: the confirmation email contains **AI Submission Advisor** feedback (generated by Bob +
  watsonx) flagging weak areas with "Needs a second look." It does not affect judging, but it is a free
  pre-grade. **Budget time for at least one submit → read feedback → revise → resubmit cycle.**

The Advisor checks exactly four things — mirror them:
1. Video communicates the theme fit, shows the working solution, and shows Bob's contribution.
2. Problem/solution statement explains a theme-aligned problem, the solution and technical approach, and
   its effectiveness/creativity/impact.
3. Bob/watsonx usage statement gives clear, specific evidence.
4. Repo is public, contains the implementation and artifacts, and includes the Bob session screenshots.

---

## 7. IBM Bob — what it actually is

Bob is IBM's AI-first IDE / coding agent for the enterprise SDLC (write, test, upgrade, secure software).
It works natively with watsonx and — per IBM's Oct 2025 announcement — integrates Anthropic models.
Reported: 6,000+ early adopters, ~45% average productivity gain.

- **Download:** https://bob.ibm.com/download — standalone app (.pkg on macOS; ARM vs Intel builds).
  4 GB RAM min (8 GB rec.), 500 MB disk. Sign in with **IBMid** via browser flow.
- **Login entry point for all clients:** `bob.ibm.com/login`
- **Bob Shell** (optional CLI): same capabilities for terminal/automation; 2.0.0 needs a fresh install
  (no upgrade path from 1.0.x); supports interactive and non-interactive/batch sessions and slash commands.
- **Context window: 270,000 tokens.** Auto-compaction exists but is lossy. Aim to stay under ~50%.
- Hackathon account: enterprise instance named **`ibm-coding-challenge-uat`** (region `us-east`).
  Invite email subject cue: "You have been added as a team member to ibm-hackathon-xxxx", Plan: Enterprise.
  ⚠️ Select this account, not a personal Bob account, or you burn personal quota.
- Monitor Bobcoins: Bob IDE → Settings icon → **General** section. Also `bob.ibm.com/admin/subscription`.

### 7.1 Built-in modes
| Mode | Purpose | Tool access | Subagents allowed |
|---|---|---|---|
| **Agent** | "Take your idea, or plan, and bring it to life" | Read, Edit, Execute, MCP, Skill, Todo, Subtask, Subagent, Mode | All |
| **Plan** | Analyze requirements, research, design steps | Read, Edit, MCP, Skill, Subagent, Mode | Explore only |
| **Ask** | Explanations, no file changes | Read, MCP, Skill, Subagent, Mode | Explore only |

Switch with **⌘ + .** (macOS). Plan mode begins every session by calling the `create-plan` skill.

### 7.2 Extensibility surface — the differentiators
- **Subagents** (`.bob/agents/`): isolated context, spawned on approval, return only a summary.
  Types: **explore** (read-only, lighter model) and **general** (full tools). `fork_context: true` passes
  conversation history in. Multiple concurrent subagents render in a **parallel subagents panel** showing
  completion count, tools used, combined tokens/cost/elapsed time, and failed calls — *great demo footage*.
  Subagents ≠ **subtasks** (subtasks are interactive, with their own UI breadcrumbs and threads).
- **Skills** (`.bob/skills/<name>/SKILL.md`, global `~/.bob/skills/`): reusable instruction sets =
  "recipes Bob follows … in a consistent, repeatable manner." YAML frontmatter `name` + `description`
  (**a skill with no description is ignored**). Can bundle checklists, templates, reference docs, and
  `scripts/`. Project skills override global skills of the same name. Loaded once per conversation.
- **Custom modes** (`.bob/custom_modes.yaml`, global `~/.bob/settings/custom_modes.yaml`):
  `slug`, `name`, `roleDefinition` (required); `description`, `whenToUse`, `customInstructions`,
  `groups`, `allowedSubagents`. Tool groups: `read`, `edit` (supports `fileRegex`), `execute`, `mcp`,
  `skill`, `workflow`, `todo`, `subtask`, `subagent`, `mode`. Omitting `groups` grants **no** tool access.
- **Custom rules** (`.bob/rules/`, plus `.bob/rules-agent/`, `rules-plan/`, `rules-ask/`, `rules-{slug}/`;
  global `~/.bob/rules/`). Files load alphabetically, recursively. Priority: global < workspace;
  mode-specific loads before general. **`AGENTS.md` at workspace root is auto-loaded** (toggle:
  `bob-code.useAgentRules`).
- **MCP servers** (`.bob/mcp.json` project, `~/.bob/mcp.json` global): `mcpServers` object; stdio
  (`command`/`args`/`cwd`/`env`) or `"type": "streamable-http"` with `url`/`headers`; `alwaysAllow` array
  for per-tool auto-approval; `disabled` flag. Timeout 30 s–5 min, default 1 min.
- **Document understanding:** attach `.docx`, `.pdf`, `.xlsx` directly to chat. **Explicitly named in the
  theme and rarely used by competitors — cheap differentiator.**
- **Context mentions:** `@/path/to/file.js`, `@/path/to/folder`, `@problems`, `@terminal`; ⌘+L adds selection.
- Others: auto-approve (read/write/execute tiers), `.bobignore` (gitignore syntax), Bob tips (real-time
  quality findings), **Rollback** (git-based workspace versioning), code actions, built-in **code reviews**,
  commit-message generation, **PR generation**, enhance-prompt (sparkles icon), **literate coding**
  (inline natural-language → code with diffs), **Bobalytics** (consumption tracking).

### 7.3 Official Bob best practices (from the docs)
- Plan mode first → Agent mode to implement → Ask mode for clarification.
- Use **Rollback / git** to recover rather than arguing with bad output in new prompts.
- Frequent small commits; branches for experiments.
- Be specific: say what Bob should *and shouldn't* do; give examples.
- Don't dump the whole codebase; use direct `@` file references; break work into subtasks.
- Track Bobcoin consumption via Bobalytics.

---

## 8. watsonx (optional)

Request the **team** IBM Cloud account from the `Complete the hackathon` page (one per team; ~2 h to
provision; all members get an email invite; check spam). If already having a personal IBM Cloud account on
the same IBMid, switch to the **watsonx account** via the top-right account dropdown.

- **watsonx Orchestrate** — no/low-code platform to create, deploy, manage AI agents across workflows.
  **AgentOps (Preview) is out of scope for this hackathon.**
- **watsonx.ai** — AI studio; Prompt Lab with Granite and other foundation models; can act as the
  inference provider for your agents. Save work as Prompt session / Prompt template / Notebook, and
  **export the project before Sept 1** (Overview tab → Export or import project → Export project).
- Also provisioned: Natural Language Understanding, Speech-to-Text, Text-to-Speech, Cloudant.
  You cannot add services or change permissions.
- $80 credits/team. Email alerts at 25/50/80% (hourly, so you can blow past them). **100% = suspension.**

Directly relevant IBM tutorials (Bob + Orchestrate):
- https://developer.ibm.com/tutorials/build-agents-mcp-tools-watsonx-orchestrate-using-bob/
- https://developer.ibm.com/tutorials/build-programmatic-agentic-workflows-watsonx-orchestrate-bob/
- https://developer.ibm.com/tutorials/bpmn-to-agents-bob-skills-watsonx-orchestrate/

---

## 9. Appendix: official example use cases (from the Guide)

*You are not limited to these — and because they are published, expect them to be crowded.*

1. **Smart developer onboarding assistant** — analyze repos, explain architecture, generate setup guidance,
   suggest starter tasks.
2. **Intelligent code review and quality coach** — analyze changes, identify risks, explain findings,
   recommend fixes, generate review summaries.
3. **Automated testing and validation hub** — generate unit tests, find coverage gaps, validate changes.
4. **Release readiness and deployment assistant** — analyze changes, review dependencies, summarize risks,
   generate release notes, validate deployment requirements.
5. **Legacy application modernization accelerator** — explain existing code, identify modernization
   opportunities, generate updated components, reduce migration effort.

## 10. Bob hands-on exercises worth 20 minutes (they teach demo-able mechanics)

Quickstart · Travel demo app (Galaxium Travels) · **Build agents with Bob `/init` (generates AGENTS.md)** ·
Create a commit and PR · Generate code from comments · **Plan + implement complex features** ·
Standardize Bob's behavior with rules · **Add a custom mode** · Manage the context window ·
Modernize a Node.js app (16→22) · **Inspect an unfamiliar codebase** · **Generate architecture diagrams
(Mermaid)** · **Audit code and generate SARIF/OSCAL reports via a reusable skill** ·
**Generate secure code with an actor-critic workflow**. Root: https://bob.ibm.com/docs/

---

## 11. Data rules

- Bring your own datasets. Teams are responsible for compliance.
- Public-website data OK **only if terms allow commercial use — keep a list of every site used.**
- **No** client data. **No** personal information (PI). **No** social-media-obtained data.
  **No** company-confidential data without owner permission.

---

## 12. Support

- Slack: `#support_dev_day_hackathon_aug_2026`
- **AskChallenge** — Bob-powered AI assistant for hackathon questions
- Mentors on Slack; email fallback `watsonxhackathon@ibm.com`
- Registration emails come from `noreply@watsonx-challenge.ibm.com`

## 13. Still unknown

- [UNKNOWN] Word limit (if any) on the Bob usage statement.
- [UNKNOWN] Exact judging panel membership.
- [UNKNOWN] Whether judges run the repo or only review deliverables (rules imply deliverables-first).
- [UNKNOWN] The team's current roster/size and Bobcoin pool.

## 14. Preserved source material

- Official Rules PDF: [`33893b2e0869f45c5249d408.pdf`](../../33893b2e0869f45c5249d408.pdf)
- Hackathon Guide PDF: fetched from the S3 link at the top of this document.
- Pre-event enablement screenshots: [`source-images/`](source-images/) (11 PNGs, incl. the
  Explore→Plan→Implement→Verify cycle, the 270k context-window slide, and guides-vs-sensors).

### Enablement session method (Maximilian Jesch, IBM Bob PM) — worth echoing in the write-up
- **Explore → Plan → Implement → Verify**, as a flexible cycle (10 min to 2 days), nestable.
- **Context is the scarce resource.** Treat phases as context boundaries; start new conversations at phase
  changes; best performance below ~50% of the window.
- **Guides (feedforward)** = rules, skills, modes — steer before acting.
  **Sensors (feedback)** = tests, linters, review agents — observe after acting.
- Verification should be **machine-runnable and designed during planning**, not discovered afterwards.

## 15. Rules for future updates

- Official emails/site instructions outrank this document. Record date + source for new facts.
- Separate official requirements from team decisions and assumptions.
- Preserve evidence for every before/after impact claim so the demo can quantify value.
