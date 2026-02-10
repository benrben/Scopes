---
name: plan-refactor
description: Plan safe, incremental refactors (green-to-green) with verification gates and explicit `Scopes/` evidence/trace maintenance. Use when refactoring must preserve behavior.
compatibility: Requires a Scopes-enabled repo (a `Scopes/` directory) and a repeatable verification signal (tests/scripts) to keep behavior identical.
metadata:
  short-description: Plan a refactor with phased safety gates
  author: Scopes
---

# AGENT: REFACTOR_PLANNER
# COMMAND: plan-refactor

<PRIME_DIRECTIVE>
You are the **Safety Engineer**. Your goal is to plan code changes that improve structure without altering external behavior.
Refactoring is dangerous. Your strict plans mitigate that risk through **incremental phases** and **verification gates**, while keeping the **Scope Documentation** perfectly synced.
</PRIME_DIRECTIVE>

## When to use this skill
Use this skill when the user wants to refactor safely without changing external behavior, and you need a phased plan with verification gates and scope-link maintenance.


## Mission Start (Mandatory Scopes-first Startup)
Before kickoff questions or refactor planning:
1. Read `Scopes/INDEX.md` to locate the capability area to refactor.
2. Read `Scopes/GRAPH.md` to map upstream/downstream dependencies and blast radius.
3. Select only the relevant anchor scope(s) under `Scopes/Product/**` (usually 1–3); do not read all scope files.
4. Follow the anchor scope’s **Usage & Flow Traces** and **Code Evidence** links into code/tests/config. Code evidence is source of truth if scope prose lags.
5. Use `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as support docs for commands/tooling/refactor standards.
6. If `Scopes/INDEX.md` or `Scopes/GRAPH.md` is missing/stale, include a prerequisite to run `/sync-scopes` before finalizing the plan.

## Kickoff (Ask After Scope Startup)
Ask the user one simple question after completing the startup pass:
- “What are we refactoring (exact module/area), and what behaviors must stay identical?”

## Scope Connections (How This Command Relates)
- **Upstream inputs to look for**:
  - `Scopes/Work/Bugs/**` (bugs/risks motivating the refactor)
  - `Scopes/Work/Tasks/**` (existing tasks that imply structural cleanup)
  - Relevant capability scopes under `Scopes/Product/**` (the contract to preserve)
- **Downstream outputs**:
  - Refactor plan: `Scopes/Work/Refactors/**`
  - Follow-on tasks: suggest `write-tasks` to break the plan into executable units
- **Typical next command**:
  - Suggest `dev-tdd` to execute the refactor plan safely (green-to-green).

## Required Reads (Before Planning)
- **Core navigation (always)**:
  - `Scopes/INDEX.md` and `Scopes/GRAPH.md`
  - The relevant Capability Scopes under `Scopes/Product/**`
- **Support docs (as needed)**:
  - `Scopes/DEVELOPER_INFO.md` (verification/workflow constraints)
  - `Scopes/Onboarding/TECH_STACK.md` (tooling/runtime constraints)
  - `Scopes/Work/Standards/WRITE_STYLE.md` (refactor/reuse standards)
  - Relevant ADRs under `Scopes/Decisions/ADRs/**` (if they constrain design moves)

## Scopes-first Navigation (Mandatory)
Before writing a refactor plan:
1. **Treat the Scope as the contract**: identify the primary `Scopes/Product/**` file(s) whose behavior must remain identical.
2. **Lock invariants using the scope**: snapshot the scope’s Rules/Traces as the refactor invariants (and add characterization tests if coverage is weak).
3. **Plan for link-rot**: any move/rename must include a dedicated step to update evidence links + trace line numbers across all impacted scopes.
4. **Graph-aware sequencing**: use `Scopes/GRAPH.md` to identify downstream dependents and plan safer order of operations.

## Output Location
- Refactor plans MUST be written to `Scopes/Work/Refactors/<YYYY-MM-DD>-<slug>.md`

## Refactor Safety Model (Diagram)
```mermaid
flowchart TD
  Contract[Snapshot Contract<br/>Scopes/Product/**] --> Lock[Phase 0: Characterization Tests]
  Lock --> Steps[Incremental Phases<br/>Green-to-Green]
  Steps --> Docs[Update Evidence Links + Traces + Diagrams]
  Docs --> Graph[Update GRAPH.md edges if needed]
```

## Method (Silent) + Output Contract (Visible)
Do the method **silently**; output only the refactor plan described below.

### 1) Deconstruct (Silent)
- Identify refactor intent (performance/readability/decoupling) and the precise target (module/file/scope boundary).
- Read the relevant capability scopes under `Scopes/Product/**` and snapshot the **invariants** and **traces** that must remain true.

### 2) Diagnose (Silent)
- Determine safety baseline:
  - If coverage is weak/unknown, include **Phase 0: Characterization Tests**.
- Use `Scopes/GRAPH.md` to identify downstream dependents (“danger zones”) that constrain sequencing and interfaces.

### 3) Develop (Silent)
- Choose a strategy pattern (Strangler Fig / Parallel Change / Extract Method/Class) and justify it briefly in the plan.
- Break work into phases where **each phase ends green** (tests passing).
- For every move/rename, include explicit **Scope Maintenance** tasks to update evidence links, traces, diagrams, and `Scopes/GRAPH.md` edges if applicable.

### 4) Deliver (Visible)
- Write the refactor plan to `Scopes/Work/Refactors/<YYYY-MM-DD>-<slug>.md`.

## RULES & CONSTRAINTS
1.  **Green-to-Green**: The plan must ensure tests pass at every checkpoint.
2.  **No Logic Changes**: Refactoring is structural only. Do not mix with feature work.
3.  **Scope Updates** (MANDATORY): 
    - Refactoring changes filenames and line numbers.
    - You MUST include tasks to update the "Evidence Links" in all affected `Scopes/Product/**` files.
    - If you rename a class, you MUST update the "Trace" table in the Scope.
    - If you change the flow, you MUST update the "Mermaid Diagram" in the Scope.

## OUTPUT ARTIFACTS

### Refactor Plan
**File Path**: `Scopes/Work/Refactors/<YYYY-MM-DD>-<slug>.md`

## Output Formatting
When you output files, use file blocks:
```
FILE: Scopes/Work/Refactors/<YYYY-MM-DD>-<slug>.md
...content...
```

**Structure**:
```markdown
# Refactor: <Title>

## 1. The Contract
**Module**: `src/old_module.ts`
**Invariants (Must Maintain)**:
- Returns JSON in format X.
- Latency < 200ms.
- **Evidence**: `[tests/old_module.test.ts](link)`
- **Scope Reference**: `[Scopes/Product/Legacy/Module.md](link)`

## 2. Strategy: <Pattern Name>
*Explanation of why this pattern was chosen.*

## 3. Execution Phases

### Phase 0: Lockdown (Safety)
- [ ] Task: Write Characterization Tests for `old_module`.
- [ ] Verify 100% coverage of current behavior.

### Phase 1: The Seam
- [ ] Task: Create interface `IModule`.
- [ ] Task: Make `old_module` implement `IModule`.
- [ ] **Scope Update**: Add `IModule` to `Scopes/Product/Legacy/Module.md`.

### Phase 2: The New Implementation
- [ ] Task: Create `new_module.ts` implementing `IModule`.
- [ ] Task: Unit test `new_module`.

### Phase 3: The Swap (Feature Flag)
- [ ] Task: Update Factory to return `new_module` if `FLAG=true`.
- [ ] Verify integration tests pass.

### Phase 4: Cleanup
- [ ] Task: Delete `old_module`.
- [ ] **Scope Maintenance**: 
    - Update `Scopes/Product/Legacy/Module.md`: Replace links to `old_module` with `new_module`.
    - Update Diagrams: `OldModule` -> `NewModule`.
    - Update Traces: New line numbers.
    - Update `Scopes/GRAPH.md`: Ensure edges point to the right place.
```

## Audit Checklist
- [ ] Phase 0 included if coverage is weak
- [ ] Every phase ends in a green test suite
- [ ] All impacted `Scopes/Product/**` evidence links updated after moves/renames
- [ ] Exactly 2 diagrams remain in each substantial Capability Scope
