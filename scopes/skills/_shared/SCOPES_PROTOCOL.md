# Shared Scopes-first Protocol

This file contains the common startup, navigation, and rules protocol shared by all Scopes skills.
Skills reference this file instead of duplicating these sections.

---

## Mission Start (Mandatory Scopes-first Startup)

Before any kickoff questions, planning, or code edits:

**Pre-flight check:**
```bash
scopes version
```
If the CLI is not available, STOP and tell the user to install it.

**Fast Route (preferred):**
```bash
scopes map --query "<goal keywords>" --limit 5
```
This instantly returns ranked anchor scopes + code paths + evidence counts. Use this instead of manually reading INDEX.md when you have a clear goal.

**Full Navigation (when fast route returns nothing, or for broad exploration):**
1. Read `Scopes/INDEX.md` to locate the relevant capability area.
2. Read `Scopes/GRAPH.md` to understand dependency relationships and blast radius.
3. Select only the relevant anchor scope(s) under `Scopes/Product/**` (usually 1-3). Do not read all scope files.
4. Follow the anchor scope's **Usage & Flow Traces** and **Code Evidence** links into code/tests/config. Code evidence is source of truth if scope prose lags.
5. Use `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as support docs for commands/tooling/refactor standards.
6. If `Scopes/INDEX.md` or `Scopes/GRAPH.md` is missing/stale, treat that as drift and recommend running `scopes sync` before proceeding.

## Required Reads (Before Acting)

- **Core navigation (always)**:
  - `Scopes/INDEX.md` (find the right scope "home")
  - `Scopes/GRAPH.md` (dependency edges + impacts)
  - The relevant Capability Scopes under `Scopes/Product/**` (current contract)
- **Support docs (as needed)**:
  - `Scopes/DEVELOPER_INFO.md` (how to run/test in this repo)
  - `Scopes/Onboarding/TECH_STACK.md` (stack/tooling context + official docs links)
  - `Scopes/Work/Standards/WRITE_STYLE.md` (code style + engineering standards)
  - Relevant ADRs under `Scopes/Decisions/ADRs/**` (only when they constrain options)

If `Scopes/Onboarding/TECH_STACK.md` is missing, treat it as drift and create it early (evidence-backed) before making tool/framework assumptions.

## Scopes-first Navigation (Mandatory)

Before deep work (code, planning, research, writing):

1. **Locate the Anchor Scope**: start at `Scopes/INDEX.md`, then pick the most relevant capability file(s) under `Scopes/Product/**`.
2. **Check dependencies**: read `Scopes/GRAPH.md` to identify upstream/downstream scopes involved.
3. **Use traces/evidence as the router**: follow **Usage & Flow Traces** and **Code Evidence** links from the anchor scope into code/tests/config.
4. **If Scopes are missing/drifty**: treat that as a first-class finding and recommend running `syncing-scopes` or creating a scope-repair task.

## Pattern Discovery (Mandatory for Implementation/Planning Skills)

Before implementing or planning changes, discover the project's established code patterns so you **follow conventions rather than inventing new approaches**.

### How to Discover Patterns

1. **Read `Scopes/DEVELOPER_INFO.md`** — look for documented patterns, conventions, and "how to add a new X" guides.
2. **Read the anchor scope's "Implementation Patterns" section** (if present in `Scopes/Product/**` files) — this documents the established way to extend that capability.
3. **Read `Scopes/Work/Standards/WRITE_STYLE.md`** — code style and structural conventions.
4. **Examine existing code in the same area** — find 2-3 existing implementations that are similar to what you're about to build (e.g., if adding a new API endpoint, look at how existing endpoints are structured; if adding a new pipeline stage, look at existing stages).
5. **Use shared design-pattern vocabulary (optional)** — when naming or comparing design patterns (GoF + common modern patterns), use `GOF_PATTERNS.md` for consistent names + tradeoffs. Do not force patterns that the codebase doesn’t need.

### Pattern Categories to Look For

- **Auth / authorization patterns**: How the project handles authentication, middleware, guards, decorators, role checks.
- **Entity / model patterns**: How new types (classes, structs, interfaces) are created, registered, and wired together.
- **API / endpoint patterns**: How routes are defined, validated, documented (e.g., controller pattern, handler pattern).
- **Data access patterns**: How the project reads/writes data (repository pattern, ORM conventions, query builders).
- **Pipeline / workflow patterns**: How multi-step processes are structured (middleware chains, event pipelines, job queues).
- **Error handling patterns**: How errors are caught, wrapped, logged, and surfaced to users.
- **Configuration patterns**: How env vars, feature flags, and settings are managed.
- **Testing patterns**: How tests are structured, what helpers exist, naming conventions.

### Pattern Conformance Rule

**When you implement something new, it MUST follow the existing pattern for that category in this project.** If no pattern exists, propose one explicitly and document it. Never silently introduce a second way of doing the same thing.

---

## Upstream Artifact Intake (Mandatory Check — Fix X1)

Before running `scope_map.py` or reading `INDEX.md`, check if you were invoked with a reference to an upstream artifact (plan, scan report, brainstorm note, task file, ADR). If so:

1. Read the artifact's `## Links` section.
2. Extract: anchor scopes, pattern references, prior research, verification signals.
3. **SKIP scope navigation entirely** — the upstream skill already did this work.
4. Only re-navigate if the artifact's Links section is missing or incomplete.

This applies to ALL skills. The chain `brainstorm → plan → tasks → develop` should never re-discover what a prior skill already found.

---

## Agent Delegation Threshold (Mandatory — Fix X3)

**Every task MUST use parallel execution.** Delegate to agents for every unit of work — no lead-only execution. This applies to ALL skill types — not just `developing-*` and `syncing-*`.

Independent work units include:
- Evidence-gathering lanes (research, web search, scope reading, risk extraction)
- Per-scope investigation (reading + following evidence for different scopes)
- Per-item research (TODO Scopes, options, hotspots, risk signals, refactor phases)
- Per-file task generation

**Thresholds (parallel mandatory in all cases):**
- **1 unit**: spawn one subagent in a single batch (still use parallel delegation; no lead executes directly).
- **2-3 units**: spawn subagents in one batch. Every subagent gets a Slice Contract.
- **4+ units**: use agent teams (max 4-6 per batch). Every teammate gets a Slice Contract.

**Model selection guidance:**
- Use `fast` model for well-scoped, mechanical work (evidence lane searches, pattern-reference lookups, hotspot analysis per module, task file generation from clear upstream TODO Scopes).
- Use default model for synthesis work (blueprint writing, ADR option analysis, complex investigation, test writing).

---

## Agent Invocation Rules

When a skill specifies Agent Orchestration phases:

0. **Parallel per unit (MANDATORY)**: For every task/phase, you MUST use parallel execution: spawn **one agent instance per unit** (same agent type, different prompt per unit), in a single tool-call batch. This applies to 1 unit as well as 2+ — never have the lead execute work directly; always delegate via subagents in a batch. **Sequential fallback is not permitted.** The environment must support spawning subagents in a batch.
1. **Slice Contracts for every delegation**: Every subagent/teammate MUST receive a Slice Contract (see `SLICE_CONTRACT.md`). No naked prompts — always include target, ownership, context, acceptance, and artifact requirements.
2. **Spawn agents as subagents/subtasks** in your environment (e.g., Task tool in Cursor/Claude Code).
3. **Parallel phases**: Spawn all listed agents at the same time in a single tool-call batch; wait for all to complete.
4. **Sequential phases**: Wait for the previous phase's outputs before spawning the next.
5. **Prompt templates**: Fill in `{placeholders}` with concrete values from the current session (user's goal, scope paths, file lists, etc.).
6. **Handle outputs**: Follow the "Handle output" instruction for each phase before proceeding to the next method step.
7. **Deterministic triggers (not judgment calls)**: Agent invocations should be triggered by mechanical thresholds, not subjective decisions. Examples: `code-simplifier` ALWAYS runs in the REFACTOR phase; `code-reviewer` ALWAYS runs as final gate.
8. **WIP limits**: Never run more than 6 subagents/teammates for scope-filling, 4 concurrent behavior slices for development, or 3 concurrent reviewers. Queue the rest.

### Parallelism Rules (Mandatory for All Skills)

**Parallel execution is MANDATORY for every task.** Every unit of work must be delegated to a subagent in a batch — no lead-only execution, no sequential execution of units.

⚠️ **Spawn ALL subagents in a SINGLE tool-call batch** for parallelism. Spawning one per turn makes them sequential and violates this protocol.

**Subagents (1 task):** Still spawn via parallel batch (one subagent). Do not have the lead execute the task directly.
**Agent Teams (2+ tasks):** Spawn all in one batch. Required when 2+ units.
**Parallel Subagents:** Always spawn in one batch. No sequential fallback.

**Claude Code:** Enable `{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }` in settings.json. Each teammate gets their own Slice Contract with **exclusive file ownership**. Lead monitors via shared task list; wait for teammates to complete; clean up when done; use `TeammateIdle` and `TaskCompleted` hooks for quality gates.

**Cursor:** Cursor does not use agent teams. To get true parallel execution, the lead MUST issue **multiple `mcp_task` (or equivalent) tool calls in the same turn** — one per slice/subagent. Do NOT spawn one task, wait for its result, then spawn the next (that is sequential and violates the protocol). Same turn = same tool-call batch = parallel. Each task gets a Slice Contract and exclusive file ownership.

---

## Automated Gate Checks (Fix X4)

Skills should use deterministic, scriptable gate checks wherever possible instead of manual "verify the following checklist" steps:

1. **Plan Gate**: verify a plan artifact contains required sections (Links, Risk Register, TODO Scopes with >= 2 acceptance examples each, pattern references, verification commands). Check that no two TODO Scopes share file ownership.
2. **Task Gate**: verify task files contain required fields (acceptance examples, verification command, ownership, dependencies). Detect ownership collisions across tasks (extract `## Ownership` paths and flag duplicates).
3. **Scan Gate**: validate output caps (max 5 targets, <= 12 opportunities, every opportunity has at least one proof link). Verify proof-link files exist.
4. **ADR Gate**: verify ADR contains required sections (Status, Context, Options with >= 2 evidence links each, Consequences, Verification Strategy).

When a gate check fails, the skill MUST revise the artifact until it passes — do not proceed to the next step with a failing gate.

---

## Common Rules

These rules apply across all Scopes skills:

1. **Evidence-Only**: Every claim must have an evidence link or be labeled `[Unknown]`.
2. **No Hallucinations**: Do not reference files, functions, or outputs you have not observed.
3. **Scope Hygiene**: If you find drift between scope docs and code, flag it and recommend `syncing-scopes`.
4. **Reality over prose**: If scope prose conflicts with code evidence, treat code evidence as source of truth.
5. **No full-scan by default**: Do not read every scope file unless the user explicitly asks for a complete audit.
6. **Artifact Persistence**: Every skill invocation MUST leave at least one durable artifact (scope file, session log, plan, task file, research note, or JSON receipt). Summaries in conversation are insufficient — they vanish between sessions.
7. **Artifact-Driven Chaining**: When one skill's output feeds another (plan → tasks → develop), use the `## Links` section in the output artifact as the routing token. The downstream skill reads `## Links` to self-route, avoiding redundant scope navigation.

## Tone (User-Friendly)

When talking to the user, assume they are not technical:
- Keep it friendly and simple (no heavy jargon).
- Explain what changed and why it matters in plain language.
- If you include evidence links, call them “proof links” and only include a few high-signal ones.

## Preflight Protocol (For Implementation Skills)

If the repo has tests, run them before any code changes to capture a baseline signal:

1. Read `Scopes/DEVELOPER_INFO.md` to find canonical test command(s).
2. Read `Scopes/Onboarding/TECH_STACK.md` to understand test tooling stack.
3. Identify **all distinct test suites** and the **runner/engine** each uses.
4. Run the canonical command for **each suite** (don't assume one covers all).
5. Record per suite: command(s) run, key pass/fail signal, blocking reasons if unable to run.
6. If no tests documented/detected, note "No tests detected" and continue.

## Output Root Rules

- Capability documentation updates live under `Scopes/Product/**`
- Developer guides live in `Scopes/DEVELOPER_INFO.md`
- Session logs live under `Scopes/Work/STDD/**` (TDD) or `Scopes/Work/DEV/**` (verify)
- Shared standards live under `Scopes/Work/Standards/**`
- Bug reports live under `Scopes/Work/Bugs/**`
- Task files live under `Scopes/Work/Tasks/**`
- Plans live under `Scopes/Work/Planning/**`
- Research reports live under `Scopes/Research/**`
- ADRs live under `Scopes/Decisions/ADRs/**`
- Refactor plans live under `Scopes/Work/Refactors/**`
