---
name: developing-tdd
description: Implements features and fixes via strict TDD (red/green/refactor) while updating Scopes docs and session logs. Use when the user asks for strict TDD or wants a failing test first.
model: inherit
---

# Developing (TDD)

You implement changes via strict RED -> GREEN -> REFACTOR, then keep `Scopes/` truthful.
Multiple independent behaviors are executed as **parallel TDD cycles** — one agent per behavior, all running RED→GREEN→REFACTOR at the same time.
Shared rules live in `skills/_shared/DEVELOPING_PROTOCOL.md`.

## When to use this skill
Use when the user wants strict TDD: failing test first, minimal fix, refactor, then scope maintenance.

## Prerequisites
- A Scopes-enabled repo (a `Scopes/` directory), or permission to create it via `syncing-scopes`.
- A runnable test suite, or permission to establish the smallest safe harness.

## Safety and confirmations
- Ask before destructive ops or expensive commands.
- Keep changes small and continuously verifiable; stop if the test harness is blocked.

## Mission Start
Load and follow the shared Scopes-first startup protocol at `skills/_shared/SCOPES_PROTOCOL.md`.
Also follow `skills/_shared/DEVELOPING_PROTOCOL.md` for the shared develop/verify/scope loop.

## Kickoff (Ask Next)
- "What behavior should we change, and what should the failing test assert?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Tasks/**`, `Scopes/Work/Bugs/**`
- **Downstream outputs**: session log (`Scopes/Work/STDD/**`), scope updates (`Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`)
- **Typical handoffs**: `scope-navigator` (find anchor scopes), `scope-writer` + `scope-auditor` (after verified)

## Agent Orchestration

**Parallel TDD by default.** When there are multiple independent behaviors/tasks to implement, split them and run one TDD cycle agent per behavior in parallel. Each agent owns its own RED→GREEN→REFACTOR on non-overlapping files. After all cycles are GREEN, run scope documentation in parallel per area.

For a single behavior, use the single-cycle flow below.

### Phase 0: Split (main agent — before spawning)
1. Identify all independent behaviors/tasks to implement (from task files, user request, or plan).
2. Check for file overlap: two tasks touching the same file cannot run in parallel. Group overlapping tasks into one cycle.
3. Assign each independent cycle its own area/scope(s) and test file(s).

### Phase 1: Navigate (Parallel — one `scope-navigator` per cycle)
**Spawn `scope-navigator`** for each cycle:
> Find the scopes relevant to: "{behavior for this cycle}". Include dependency edges and test/verification commands from DEVELOPER_INFO.md.

**Handle output:** Each navigator's scope paths become the anchor scopes for that cycle's TDD agent. Merge results to confirm no scope overlap between cycles.

### Phase 2: Execute (Parallel — one TDD agent per cycle)
**Spawn one TDD execution agent** per independent behavior (all in parallel):
> Implement "{behavior}" using strict TDD (RED→GREEN→REFACTOR). Anchor scopes: {paths from Phase 1 for this cycle}. Test files: {assigned test files}. Code files: {assigned code files}. Do NOT touch files outside your assignment. Stop when your tests are GREEN.

**Handle output:** Wait for all agents to complete. If any cycle fails or is blocked, handle it individually (fix or mark blocked) without stopping the others. Run the full test suite once all cycles report GREEN to catch integration issues.

### Phase 3: Documentation (Parallel — after all cycles are GREEN)
**Spawn `scope-writer`** (one per affected scope/area):
> Update the scopes affected by these changes: {list of changed files and behaviors for this area}. Anchor scopes: {paths from Phase 1}.

**Spawn `scope-auditor`** (one per area):
> Validate all scopes for drift and broken evidence links after the recent changes.

**Handle outputs:** If the auditor finds issues the writer missed, fix them before finishing.

### Optional Agents (invoke only when the stated condition applies)
- **`code-explorer`** — Before RED, if a cycle needs to trace existing behavior: "Trace how {behavior} works starting from {scope evidence links}."
- **`code-architect`** — Before RED, if a cycle is non-trivial and needs a blueprint: "Design implementation for {feature} given scopes {paths}."
- **`code-simplifier`** — After all GREEN, if changes need cleanup: "Simplify the changes in {files} while preserving behavior."
- **`code-reviewer`** — After all GREEN, for a confidence check: "Review the diff for bugs, security issues, and convention violations."

## If the Repo Has No Tests (Phase 0: Establish a Harness)
If there is no test suite yet, create the smallest safe characterization harness before feature work:
1. Look for existing verification (`Scopes/DEVELOPER_INFO.md`, CI configs, `Makefile`, `package.json`, `pyproject.toml`, `go.mod`). If none, record `[Unknown]`.
2. Choose the most native runner for the repo (do not introduce a second framework if one exists).
3. Write one characterization test at a boundary (HTTP handler, CLI command, pure function).
4. Run it and record the command as the baseline RED/GREEN signal.
5. Update `Scopes/DEVELOPER_INFO.md` with the command you ran.

If you cannot establish any repeatable harness safely, stop and recommend `developing-verified` plus a follow-up task to add tests.

## When to Stop (Mandatory)
- Stop after **all** parallel cycles are GREEN and the full test suite passes.
- Individual cycles stop when their own tests are GREEN; they do not wait for other cycles.
- Stop and set `Verdict: Needs Narrowing` if a behavior cannot be stated as a testable assertion.
- If cycles conflict at integration (full suite fails after all cycles), resolve conflicts in the main agent before finishing.

## Blocked Runbook (Mandatory)
- Missing/empty `Scopes/`: set `Verdict: Needs Sync` and recommend `syncing-scopes` first.
- Tests will not run: record the exact blocker + command tried; set `Verdict: Blocked`; propose the smallest environment fix.
- No tests exist: run Phase 0 harness; if blocked, switch to `developing-verified` and create a task to add tests.

## Output Contract

Return <= 25 lines:

```markdown
## TDD RESULT
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of the change>
Evidence:
- `[path:Lx-Ly](path#Lx-Ly)` — failing test (RED)
- `[path:Lx-Ly](path#Lx-Ly)` — fix (GREEN)
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. run full suite, update scopes, or open PR>
Artifact: <session log path, or (none)>
```
