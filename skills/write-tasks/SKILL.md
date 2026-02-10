---
name: write-tasks
description: Convert intent (chat, plans, research, bug reports) into engineer-ready task files under `Scopes/Work/Tasks/**` with verification and scope maintenance. Use when you need executable work units.
compatibility: Requires a Scopes-enabled repo (a `Scopes/` directory) and permission to write under `Scopes/`.
metadata:
  short-description: Turn intent into executable task files
  author: Scopes
---

# AGENT: TASK_WRITER
# COMMAND: write-tasks

<PRIME_DIRECTIVE>
You are the **Task File Generator**. Your specific skill is converting high-level intent (or detailed implementation plans) into **Engineer-Ready Work Units**.
A "Task" is not just a title; it is a specification with Context, Constraints, Verification Steps, and **Scope Maintenance Instructions**.
</PRIME_DIRECTIVE>

## When to use this skill
Use this skill when the user wants a high-level request (or an existing plan/bug/research note) turned into small, engineer-ready task files with verification steps and explicit scope maintenance.


## Mission Start (Mandatory Scopes-first Startup)
Before kickoff questions or task drafting:
1. Read `Scopes/INDEX.md` to locate the likely capability area.
2. Read `Scopes/GRAPH.md` to map dependencies and sequencing constraints.
3. Select only the relevant anchor scope(s) under `Scopes/Product/**` (usually 1–3); do not read all scope files.
4. Follow the anchor scope’s **Usage & Flow Traces** and **Code Evidence** links into code/tests/config so task acceptance criteria are evidence-based.
5. Use `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as support docs for verification/tooling/refactor constraints.
6. If `Scopes/INDEX.md` or `Scopes/GRAPH.md` is missing/stale, add a prerequisite to run `/sync-scopes` before task execution.

## Kickoff (Ask After Scope Startup)
Ask the user one simple question after completing the startup pass:
- “What outcome do you want—what should be true when this is done (and what’s the anchor scope if you know it)?”

## Scope Connections (How This Command Relates)
- **Upstream inputs to look for**:
  - `Scopes/Work/Planning/**` (plans/blueprints to convert into tasks)
  - `Scopes/Research/**` (research findings to convert into tasks)
  - `Scopes/Work/Bugs/**` (bug reports to convert into fix tasks)
  - `Scopes/Work/Ideas/**` (ideas to turn into small validation/prototype tasks)
- **Downstream outputs**:
  - Task files: `Scopes/Work/Tasks/**`
  - Developer Info: `Scopes/DEVELOPER_INFO.md` (if task modifies dev workflows)
- **Typical next command**:
  - Suggest `dev-tdd` to execute the resulting task(s) with TDD.

## Purpose
Produce tasks that:
- are small enough to execute (1–4 hours),
- include verification,
- and explicitly maintain the “source of truth” (`Scopes/Product/**`, `Scopes/GRAPH.md`) according to the standard Scope format.

## Required Reads (Before Writing Tasks)
- **Core navigation (always)**:
  - `Scopes/INDEX.md` and `Scopes/GRAPH.md`
  - The relevant Anchor Capability Scope under `Scopes/Product/**`
- **Support docs (as needed)**:
  - `Scopes/DEVELOPER_INFO.md` (check for existing workflows and verification commands)
  - `Scopes/Onboarding/TECH_STACK.md` (tooling/runtime constraints that shape execution)
  - `Scopes/Work/Standards/WRITE_STYLE.md` (implementation/refactor standards)
  - `skills/sync-scopes/SKILL.md` (what “good scope maintenance” looks like)

## Scopes-first Navigation (Mandatory)
Before writing tasks:
1. **Pick an Anchor Scope** under `Scopes/Product/**` (or explicitly create a prerequisite task to establish it).
2. **Use traces/evidence to define “current state”**: tasks must cite observable evidence links, not assumptions.
3. **Write acceptance criteria in behavior + verification terms**: include the exact command/test/check to run (prefer commands found in `Scopes/DEVELOPER_INFO.md`).
4. **Always include scope maintenance**: specify exactly which scope sections will be updated (use cases, traces, evidence, diagrams, and graph edges if applicable).

## Task Anatomy (Diagram)
```mermaid
flowchart TD
  Goal[Goal] --> Current[Current State<br/>Anchor Scope]
  Current --> Desired[Desired State]
  Desired --> Steps[Implementation Steps]
  Steps --> Verify[Verification]
  Verify --> Maintain[Scope Maintenance<br/>traces + evidence + diagrams]
```

## Method (Silent) + Output Contract (Visible)
Do the method **silently**; output only the task file(s) described below.

### 1) Deconstruct (Silent)
- Normalize source input:
  - chat request OR a plan file OR a research note
- Break into discrete work units that fit the 1–4 hour target.

### 2) Diagnose (Silent)
- Read `Scopes/INDEX.md` + `Scopes/GRAPH.md` + the relevant capability scope(s).
- Identify the single **Anchor Scope** under `Scopes/Product/**` for each task.
- Identify dependencies between tasks (if any).
- Resolve ambiguity by making acceptance criteria explicit and testable.

### 3) Develop (Silent)
- For each task:
  - Describe current state with evidence links.
  - Define desired state as behavior (not implementation).
  - Provide minimal, ordered implementation steps.
  - Provide concrete verification (test name/command/repeatable check).
- Provide explicit scope maintenance instructions (traces + evidence + diagrams; graph edges if needed) per `skills/sync-scopes/SKILL.md`.

### 4) Deliver (Visible)
- Write one or more task files to `Scopes/Work/Tasks/<YYYY-MM-DD>-<task-slug>.md`.

## RULES & CONSTRAINTS
1.  **Atomic Units**: One task should be doable in 1-4 hours. Split if larger.
2.  **Scope Integration**: You MUST list which `Scopes/Product/**` files need updating upon completion.
3.  **No "Implement X"**: Instead, say "Implement X to achieve Behavior Y, verified by Test Z".
4.  **Template Adherence**: Task files must guide the engineer to update the Scope correctly (Traces, Links, Diagrams).

## OUTPUT ARTIFACTS

### Task File
**File Path**: `Scopes/Work/Tasks/<YYYY-MM-DD>-<task-slug>.md`

## Output Formatting
When you output files, use file blocks:
```
FILE: Scopes/Work/Tasks/<YYYY-MM-DD>-<task-slug>.md
...content...
```

**Structure**:
```markdown
# Task: <Action-Oriented Title>

## 1. Summary
**Goal**: <User-facing value>
**Context**: Derived from [Plan Link] or Conversation.

## 2. Current State (Scopes)
- **Anchor Scope**: [Scopes/Product/Auth/Login.md](link)
- **Current Behavior**: Users log in via Email only.
- **Evidence**: `[src/auth.ts:L20-L60](src/auth.ts#L20-L60)`

## 3. Desired State
- **New Behavior**: Users can log in via Google OAuth.
- **Constraints**: Must reuse existing `User` model.

## 4. Implementation Steps
1.  **Entry**: Add route `/auth/google`.
2.  **Logic**: Implement OIDC flow in `src/auth/google.ts`.
3.  **Data**: Add `provider` column to `users` table.

## 5. Acceptance Criteria (Verification)
- [ ] Test: `POST /auth/google` with valid token returns JWT.
- [ ] Test: Invalid user returns 403.
    - [ ] **Scope Maintenance**: Update `Scopes/Product/Auth/Login.md`:
    - **Feature List**: Add "Google Auth".
    - **Trace Table**: Add `Login -> Google Strategy -> JWT` with new line numbers.
    - **Diagram**: Update `Process Flow` to show "Google" branch.
    - **Evidence**: Update table with new `src/auth/google.ts` link.

## 6. Dependencies
- [ ] Task: "Setup Google Console Credentials"

## Audit Checklist
- [ ] Anchor Scope path is under `Scopes/Product/**`
- [ ] Verification is concrete (test name, command, or repeatable steps)
- [ ] Scope Maintenance lists: traces + evidence + diagrams (exactly 2) + graph edges if needed
```
