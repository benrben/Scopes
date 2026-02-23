---
name: brainstorming-project
description: >
  Brainstorms architecture and implementation approaches for this project using Scopes-first routing,
  always consulting the GoF/patterns doc, and always doing web research for up-to-date options/best practices.
  Use for interactive design discussion with the user (no file writing), tradeoff exploration, and option framing.
  Do NOT use for implementation or task breakdowns; use planning-* / writing-tasks / developing-* instead.
model: inherit
---

# Brainstorming Project (Scopes + Patterns + Web Research)

You help the user brainstorm solutions that fit this repository: you use `Scopes/` as the local source of truth, you use design-pattern vocabulary to communicate cleanly, and you use web research to avoid stale advice.

## Direct Brainstorming Rules (Mandatory)
- Define the target in one sentence. If unclear, stop and ask 1-3 clarifying questions.
- Timebox hard. 10-15 minutes max for the dump + first-pass selection.
- No speeches. Short sentences only.
- One idea = one sentence. Do not split an idea into value/path/subpoints during the dump.
- No judging during the dump. Critique comes after.
- Write everything in-chat. If it isn't written, it doesn't exist.
- Iterate in fast bursts: generate **5 ideas per iteration**, then stop for user input (quick interaction).
- Quantity first. Default target: **15 ideas** (3 iterations of 5). If it's still fuzzy, go to **20** (4 iterations).
- Push extremes. "Stupid" ideas allowed.
- Never say "it can't be done". Name the blocker and move on.
- Build, don't argue. "Add to it" beats debate.
- One person talks at a time. Avoid interruption loops.
- If you don't bring ideas, don't dominate the discussion.
- Group ideas fast. 3-6 clusters. Name them.
- Kill weak ideas fast. If no value or no path, drop it.
- Pick top 3 only.
- Define next step per top idea. One quick test each. Assign an owner.
- End with owners + deadlines. No owner means not happening.

## When to Use
- The user wants to explore approaches, architecture, or options before committing to a plan.
- The user is unsure which pattern/library/strategy fits best and wants tradeoffs.
- The user needs a "decision-ready" set of options, not code changes yet.

## When NOT to Use
- The user wants code written now: use `planning-idea`, `planning-refactor`, `writing-tasks`, `developing-tdd`, or `developing-verified`.
- The user asked for a narrow factual answer about the repo: use `querying-scopes`.

## Mission Start (Mandatory)
1. Load `skills/_shared/SCOPES_PROTOCOL.md` (Scopes-first startup).
2. Load `skills/_shared/GOF_PATTERNS.md` (pattern vocabulary + tradeoffs).
3. Resolve `SKILLS_ROOT` using `skills/_shared/SCRIPT_DISCOVERY.md`.

If `Scopes/` is missing, set `Verdict: Needs Sync` and recommend `syncing-scopes` before continuing.

### Prerequisites
- **Parallel subagents are MANDATORY** for evidence lanes: spawn Lanes A, B, and D as subagents in one batch (see `skills/_shared/SCOPES_PROTOCOL.md`). No sequential fallback.
- Lane C (pattern fit) stays with the lead agent since it's a doc lookup.

---

## Workflow (Interactive Brainstorm Loop)

This skill is a conversation. Do not write files (except the conditional brainstorm artifact — see Artifacts below). Iterate with the user:
1. Gather 3-6 key facts/questions.
2. Run the evidence lanes (below) and merge into 2-4 options.
3. Ask 1-3 pointed questions to choose between options.
4. Refine the recommendation and verify it still fits Scopes + repo precedent + web findings.

The evidence lanes are independent. **Spawn Lanes A, B, and D as parallel subagents** in a single batch and then merge. Lane C stays with the lead. Parallel delegation is mandatory — no sequential fallback (see SCOPES_PROTOCOL).

### Fast-Path Rule
IF the topic clearly maps to 1 anchor scope AND the user has a strong starting opinion, skip the full 15-idea dump and go directly to a **focused 5-idea iteration** with immediate clustering. Resume the normal flow at the cluster + vote step.

### Step -1: Upstream Artifact Intake (mandatory check)

Before running evidence lanes, check for prior brainstorm notes:
```bash
find Scopes/Work/Notes/ -name "brainstorm-*.md" | xargs grep -li "<topic keywords>" 2>/dev/null
```
IF found for a similar topic: load prior Top 3 and constraints — build on them instead of starting from scratch.

Also check for upstream artifacts (plan, scan report, ADR) that may provide anchor scopes and constraints. If found, read their `## Links` section and skip Lane A routing (see `skills/_shared/SCOPES_PROTOCOL.md` Upstream Artifact Intake).

### Mini Format (Use This Default)
1. 2 min: goal + constraints.
2. 6-8 min: rapid-fire idea dump (no critique) in 5-idea iterations (3-4 iterations).
3. After each iteration: user gives 1-2 signals (direction, constraint, "more like #7", "avoid #3").
4. 3-5 min: cluster + vote. 3-6 clusters. Kill weak ideas.
5. 2 min: assign next steps. Top 3 only. One quick test each. Owners + deadlines.

### Lane A: Scopes Route + Evidence Bundle ⟨`scope-investigator` subagent⟩
Use `scope-investigator` (see `agents/scope-investigator.md`) for deep evidence gathering:
- Route to 1-3 anchor scopes:
  ```bash
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
    --query "<user topic keywords>" --limit 5 --format json
  ```
- For each anchor scope, spawn a `scope-investigator`:
  > **SLICE CONTRACT — Brainstorm Evidence**
  > - **Target**: Gather evidence bundle from `{scope_path}` for brainstorm topic `{topic}`
  > - **investigation_type**: `explainer`
  > - **Ownership**: Exclusive read-only on `{scope_path}` and its evidence files
  > - **Acceptance**: Return evidence bundle with constraints, entrypoints, patterns, and architecture layers
- Extract from receipts (copy into your working notes):
  - constraints/rules
  - entrypoints + evidence links
  - verification signals (`Scopes/DEVELOPER_INFO.md` if present)
  - blast radius hints (`Scopes/GRAPH.md` if present)
  - architecture layers touched (from `scope-investigator`'s layer mapping)

### Lane B: Repo Precedent Scan (Mechanical) ⟨subagent · `fast` model⟩
- Find similar implementations (don't invent new architecture if precedent exists):
  ```bash
  rg -n "<key term>" . -S -g'!node_modules/**' -g'!.venv/**' -g'!venv/**'
  ```
- Collect 2-5 concrete precedent links (paths) that show "how this repo already does it".

### Lane C: Pattern Fit (Design Pattern Doc) ⟨lead agent⟩
- Use `skills/_shared/GOF_PATTERNS.md` to label candidate shapes (Strategy/Adapter/Facade/etc.) only when it clarifies tradeoffs.
- Prefer "simpler than patterns" when the doc suggests the pattern would be overkill.
- For each option you propose, answer:
  - What pattern name fits (if any)?
  - What common failure mode applies here (per the doc)?
  - What would you do to keep it incremental/reversible?

### Lane D: Web Research (Mandatory) ⟨subagent · default model⟩
You MUST do web research for any brainstorming session so advice isn't stale.

- Search for:
  - current best practices
  - library/tool options and their maintenance status
  - pitfalls and security notes
  - migration/compatibility constraints
- Prefer authoritative sources (official docs, maintainers, standards bodies, well-known engineering blogs).
- Timebox this lane. Keep it fast. Prefer 2-6 sources max.

If the environment has a web-search tool (e.g., `web.run`), use it. If not, attempt via allowed tooling (browser automation or CLI). If web access is blocked, state the blocker and proceed with repo evidence only.

### Slice Contracts (Lane Agent Boundaries)

Each lane subagent receives a **Slice Contract** with an exclusive research domain:

| Lane | Exclusive Domain | May NOT |
|------|-----------------|---------|
| A | Scope routing + evidence extraction from `Scopes/` | Do web research or grep source code |
| B | Codebase pattern search (`rg`, file reads outside `Scopes/`) | Read Scopes files or do web research |
| D | Web research only (search, fetch URLs) | Read any Scopes files or local repo files |

The lead agent validates that each lane's receipts fall within its domain before merging. Out-of-domain evidence is discarded with a warning.

### Quality Gate: Pre-Dump (after lane merge, before idea dump)
- [ ] Target defined in 1 sentence
- [ ] Constraints listed (3-7 bullets)
- [ ] Evidence lanes complete with receipts (lane agent returned results within its Slice Contract domain)

IF any check fails, fix before proceeding to the idea dump.

### Merge: Option Set (Discuss)
After the lanes finish, present a merged option set to the user:
- 2-4 options max (avoid option spam)
- explicit tradeoffs (pros/cons)
- how it fits Scopes constraints and repo precedent
- verification strategy (how would we prove it works)
- recommended next step (which skill to run next)

### Quality Gate: Cluster (after clustering, before Top 3 selection)
- [ ] Every cluster has >= 2 ideas
- [ ] Every Top 3 idea has a one-sentence test + owner + deadline
- [ ] At least 1 Top 3 idea has a pattern reference from Lane C

IF any check fails, iterate (add ideas, refine clusters, or add pattern references) before finalizing Top 3.

---

## Artifacts (conditional-mandatory)

IF the brainstorm produced a Top 3 with next steps:
- Write `Scopes/Work/Notes/brainstorm-<date>-<slug>.md` with: target, constraints, iterations summary, clusters, Top 3, next tests, anchor scopes, web sources.
- This is NOT a plan — it's a decision breadcrumb for the next session.
- Add a `## Links` section with anchor scopes and pattern references for downstream consumption.

IF the brainstorm did NOT produce actionable Top 3:
- No artifact needed. Note the outcome in the output contract.

### Lifecycle
Delete brainstorm notes that led to accepted plans (keep the plan, delete the breadcrumb).

---

## Output Contract

### Quality Gate: Output (before finishing)
- [ ] Brainstorm brief artifact passes completeness check (all required sections present: Verdict, Target, Constraints, Brainstorm log, Clusters, Top 3, Next tests, Anchor scopes, Precedent, Web sources, Next, Artifact)
- [ ] If Top 3 produced, artifact written to `Scopes/Work/Notes/brainstorm-<date>-<slug>.md`

Return an interactive brainstorm (ask questions and propose options), then append:

```markdown
## BRAINSTORM
Verdict: Proceed | Needs Sync | Needs Narrowing | Blocked
Target (1 sentence): <one line>
Constraints: <3-7 bullets>
Iteration size: 5 ideas
Brainstorm log (dump):
- Iteration 1: ideas 1-5 (one sentence each; no critique)
- Iteration 2: ideas 6-10 (one sentence each; no critique)
- Iteration 3: ideas 11-15 (one sentence each; no critique)
- Iteration 4 (optional): ideas 16-20 (one sentence each; no critique)
User signals after each iteration:
- Iteration 1: <1-2 short signals>
- Iteration 2: <1-2 short signals>
- Iteration 3: <1-2 short signals>
Clusters:
- <name>: <idea numbers>
Killed: <idea numbers and 1-line reason>
Top 3:
- #1 <one sentence idea>
- #2 <one sentence idea>
- #3 <one sentence idea>
Next tests:
- Idea #1: <one sentence quick test> | Owner: <name> | Deadline: <YYYY-MM-DD>
- Idea #2: <one sentence quick test> | Owner: <name> | Deadline: <YYYY-MM-DD>
- Idea #3: <one sentence quick test> | Owner: <name> | Deadline: <YYYY-MM-DD>
Anchor scopes: <0-3 scope paths or "(none)">
Precedent (repo): `<path>` / `<path>`
Web sources: <2-6 short titles (and links if available)>
Next: querying-scopes | planning-idea | planning-refactor | writing-tasks | developing-tdd | developing-verified
Artifact: Scopes/Work/Notes/brainstorm-<date>-<slug>.md (if Top 3 produced)
```

## Rules
- Do not edit source code in this skill. This is decision support, not execution.
- Do not write any files besides the conditional brainstorm artifact (see Artifacts above). Keep everything else in-chat.
- Never contradict Scopes silently: if web advice disagrees with repo constraints, call it out explicitly.
- Cap outputs: 2-4 options, top 3 risks, top 2-5 repo precedents, 2-6 web sources.
- Keep sentences short. No speeches.
