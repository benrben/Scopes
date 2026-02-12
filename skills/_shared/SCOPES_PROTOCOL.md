# Shared Scopes-first Protocol

This file contains the common startup, navigation, and rules protocol shared by all Scopes skills.
Skills reference this file instead of duplicating these sections.

---

## Mission Start (Mandatory Scopes-first Startup)

Before any kickoff questions, planning, or code edits:

1. Read `Scopes/INDEX.md` to locate the relevant capability area.
2. Read `Scopes/GRAPH.md` to understand dependency relationships and blast radius.
3. Select only the relevant anchor scope(s) under `Scopes/Product/**` (usually 1-3). Do not read all scope files.
4. Follow the anchor scope's **Usage & Flow Traces** and **Code Evidence** links into code/tests/config. Code evidence is source of truth if scope prose lags.
5. Use `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as support docs for commands/tooling/refactor standards.
6. If `Scopes/INDEX.md` or `Scopes/GRAPH.md` is missing/stale, treat that as drift and recommend `syncing-scopes` before proceeding.

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

## Agent Invocation Rules

When a skill specifies Agent Orchestration phases:

0. **Default — parallel per unit**: When a phase's work can be split by area, scope, or independent task, spawn **one agent instance per unit in parallel** (same agent type, different prompt per unit). Use a single agent only when scope is narrow (e.g. 1-3 targets). Skills may override this with a single-stream option for narrow scope.
1. **Spawn agents as subagents/subtasks** in your environment (e.g., Task tool in Cursor/Claude Code).
2. **Parallel phases**: Spawn all listed agents at the same time in a single tool-call batch; wait for all to complete. You may list multiple instances of the same agent type with different tasks (e.g. one auditor per area, one writer per area); each is spawned in parallel with its own prompt.
3. **Sequential phases**: Wait for the previous phase's outputs before spawning the next.
4. **Prompt templates**: Fill in `{placeholders}` with concrete values from the current session (user's goal, scope paths, file lists, etc.).
5. **Handle outputs**: Follow the "Handle output" instruction for each phase before proceeding to the next method step.
6. **Optional agents**: Only spawn when the stated condition applies — do not invoke by default.

---

## Common Rules

These rules apply across all Scopes skills:

1. **Evidence-Only**: Every claim must have an evidence link or be labeled `[Unknown]`.
2. **No Hallucinations**: Do not reference files, functions, or outputs you have not observed.
3. **Scope Hygiene**: If you find drift between scope docs and code, flag it and recommend `syncing-scopes`.
4. **Reality over prose**: If scope prose conflicts with code evidence, treat code evidence as source of truth.
5. **No full-scan by default**: Do not read every scope file unless the user explicitly asks for a complete audit.

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
