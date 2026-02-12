---
name: writing-tasks
description: Converts intent (chat, plans, research, bug reports) into engineer-ready task files under Scopes/Work/Tasks with verification and scope maintenance. Use when the user needs executable work units, task breakdowns, or actionable tickets.
model: inherit
---

# Writing Tasks

**You are the Task File Generator.** You convert high-level intent (or detailed plans) into **Engineer-Ready Work Units**. A task is not just a title — it includes Context, Constraints, Verification Steps, and Scope Maintenance Instructions.

## When to use this skill
Use when the user wants a request, plan, bug, or research note turned into small, engineer-ready task files.

## Prerequisites
Requires a Scopes-enabled repo and permission to write under `Scopes/`.

## Mission Start
**You MUST read the shared protocol before proceeding.** Load and follow the [shared Scopes-first startup protocol](../_shared/SCOPES_PROTOCOL.md) (located at `skills/_shared/SCOPES_PROTOCOL.md`).

## Kickoff (Ask After Scope Startup)
Ask the user one simple question:
- "What outcome do you want—what should be true when this is done (and what's the anchor scope if you know it)?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Planning/**`, `Scopes/Research/**`, `Scopes/Work/Bugs/**`, `Scopes/Work/Ideas/**`
- **Downstream outputs**: Task files (`Scopes/Work/Tasks/**`), `Scopes/DEVELOPER_INFO.md` if workflow changes
- **Typical next command**: `developing-tdd` to execute tasks.
- **Scope artifacts often impacted**: `Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`

## Agent Orchestration

Default: when the intent spans multiple capability areas or outcomes, spawn one `scope-navigator` per area in parallel; use a single navigator for narrow scope (1-3 scopes).

### Phase 1: Navigation (before Diagnose)
**Spawn `scope-navigator`:**
> Find the 1-3 scopes relevant to this intent: "{user's stated outcome}". Include dependency edges and existing pattern references.

**Handle output:** Use the returned scope paths as the Anchor Scope for each generated task. Pattern references from the navigator feed into the task's "Pattern Reference" section.

---

## Task Anatomy
```mermaid
flowchart TD
  Goal[Goal] --> Current["Current State: Anchor Scope"]
  Current --> Desired["Desired State"]
  Desired --> Steps["Implementation Steps"]
  Steps --> Verify[Verification]
  Verify --> Maintain["Scope Maintenance"]
```

## Method (Silent) + Output Contract (Visible)

### 1) Deconstruct (Silent)
- Normalize source input (chat, plan, research, bug report).
- Break into discrete work units (1-4 hours each).

### 2) Diagnose (Silent)
- Find Anchor Scope under `Scopes/Product/**` for each task.
- Identify dependencies and an execution order. Resolve ambiguity with explicit acceptance criteria.

### 3) Develop (Silent)
- Describe current state with evidence links.
- Define desired state as behavior (not implementation).
- Provide minimal implementation steps + concrete verification.
- Include explicit scope maintenance instructions.

### 4) Deliver (Visible)
Write task files to `Scopes/Work/Tasks/<YYYY-MM-DD>-<task-slug>.md`.

## Pattern Conformance (Mandatory)

Before writing task steps, you MUST discover the project's existing patterns (see [Pattern Discovery](../_shared/SCOPES_PROTOCOL.md)).

1. **During Diagnose**: Identify the relevant project pattern for each task (e.g., "follows the existing controller pattern", "uses the standard pipeline stage interface").
2. **In Implementation Steps**: Reference the pattern explicitly: "Follow the pattern in `src/controllers/UserController.ts` — create a new controller with the same middleware chain, validation, and response format."
3. **In each task file**: Include a "Pattern Reference" field pointing to an existing implementation that serves as the template.

**Hard constraint**: Every task that creates new code MUST include a pattern reference. Tasks should say "Implement X **following the pattern in** Y" — never just "Implement X".

---

## Rules
1. **Atomic Units**: One task = 1-4 hours. Split if larger.
2. **Scope Integration**: List which `Scopes/Product/**` files need updating.
3. **No "Implement X"**: Say "Implement X **following the pattern in** Y to achieve Behavior Z, verified by Test/Sandbox W".
4. **Pattern Reference Required**: Every task that creates code MUST reference an existing implementation as the pattern to follow.
5. **Template Adherence**: Guide engineer to update traces, links, diagrams.
6. **Ordering (MANDATORY for multi-task sets)**: If you generate 2+ tasks, include explicit ordering and cross-links (“Depends on”) so engineers run tasks in the intended sequence.

## Token-Safety Budget (Mandatory)
- Default max tasks per batch: 8. If more are needed, stop and ask to continue in a second batch.
- Default max total estimated hours per batch: 16. If exceeded, stop and ask for confirmation.

## When to Stop (Mandatory)
- Stop once tasks are written with: Anchor Scope, Pattern Reference, concrete verification, and scope maintenance steps.
- Default caps: 1-3 anchor scopes, 3-7 evidence links, 3-10 code files; mark gaps as `[Unknown]`.
- If the intent cannot be broken into verifiable tasks, stop and set `Verdict: Needs Narrowing`.

## Blocked Runbook (Mandatory)
- Missing/empty `Scopes/`: set `Verdict: Needs Sync` and recommend `syncing-scopes` first.
- No pattern references exist: mark `[Unknown]` and write tasks that first establish a pattern via a small, verified example.
- Verification steps unknown: mark `[Unknown]` and point to `Scopes/DEVELOPER_INFO.md` as the source of truth to update.

## Output Contract

Return <= 20 lines:

```markdown
## TASKS
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of what was produced>
Evidence:
- `Scopes/Work/Tasks/YYYY-MM-DD-<task-slug>.md` (and any dependencies)
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. hand off to developing-tdd>
Artifact: (none)
```

## Task Template

**File Path**: `Scopes/Work/Tasks/<YYYY-MM-DD>-<task-slug>.md`

```markdown
# Task: <Action-Oriented Title>

## 0. Task Set (Only if part of a multi-task set)
**Set**: <shared set name / goal>
**Order**: <1 of N>
**Depends On**: <links to other task file(s), if any>

## 1. Summary
**Goal**: <User-facing value>
**Context**: Derived from [Plan Link] or Conversation.

## 2. Current State (Scopes)
- **Anchor Scope**: [Scopes/Product/Auth/Login.md](link)
- **Current Behavior**: ...
- **Evidence**: `[src/auth.ts:L20-L60](src/auth.ts#L20-L60)`

## 3. Desired State
- **New Behavior**: ...
- **Constraints**: ...

## 4. Pattern Reference
- **Pattern**: <name of the pattern, e.g., "Controller + Service + Repository">
- **Example Implementation**: `[src/controllers/UserController.ts:L10-L50](src/controllers/UserController.ts#L10-L50)`
- **Follow**: Same middleware chain, validation, error handling, and response format.

## 5. Implementation Steps
1. ...
2. ...

## 6. Acceptance Criteria (Verification)
- [ ] Test: ...
- [ ] **Scope Maintenance**: Update traces, diagrams, evidence in anchor scope.

## 7. Dependencies
- [ ] ...

## Audit Checklist
- [ ] Anchor Scope path under `Scopes/Product/**`
- [ ] Pattern Reference included with evidence link to existing implementation
- [ ] Verification is concrete
- [ ] Scope Maintenance lists traces + evidence + diagrams + graph edges
```
