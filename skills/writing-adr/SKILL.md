---
name: writing-adr
description: Writes Architecture Decision Records (ADRs) under Scopes/Decisions/ADRs with options, tradeoffs, and affected scopes. Use when recording a decision, choosing between approaches, or documenting rationale for an architectural choice.
---

# Writing an ADR

**You are the Historian of Decisions.** You capture the "Why" behind the code. ADRs prevent re-litigating settled debates. You link every decision to the Scopes it affects, ensuring the knowledge graph stays coherent.

## When to use this skill
Use when the user needs to record a decision (Proposed/Accepted) with rationale, tradeoffs, and explicit scope updates.

## Prerequisites
Requires a Scopes-enabled repo and permission to write under `Scopes/`.

## Helper scripts
- `scripts/adr_scaffold.py`: Creates ADR skeleton (auto-numbers). Use `--supersedes 0003` to auto-link ADR chains, `--dry-run` to preview.

## Mission Start
**You MUST read the shared protocol before proceeding.** Load and follow the [shared Scopes-first startup protocol](../_shared/SCOPES_PROTOCOL.md) (located at `skills/_shared/SCOPES_PROTOCOL.md`).

## Kickoff (Ask After Scope Startup)
Ask the user one simple question:
- "What decision are we recording (and is it Proposed or Accepted)?"

## Scope Connections
- **Upstream inputs**: `Scopes/Research/**`, `Scopes/Work/Planning/**`, capability scopes, `Scopes/DEVELOPER_INFO.md`
- **Downstream outputs**: ADR (`Scopes/Decisions/ADRs/**`), possible `Scopes/GRAPH.md` updates
- **Typical next commands**: `planning-idea`, `writing-tasks`

## Agent Orchestration (Prefer Parallel)

Delegate to [agents](../agents/) following the [parallel development pattern](../agents/WORKFLOW.md). The main agent orchestrates; agents do the heavy lifting in isolated contexts.

### Phase 1: Context Gathering — PARALLEL

Fire **both agents simultaneously** to build decision context:
- **`scope-navigator`** — finds affected scopes, dependency graph edges, and existing ADRs in the area
- **`plan-researcher`** *(background)* — investigates codebase patterns, historical decisions, and constraints that inform this choice; writes brief to `Scopes/Work/Planning/`

Read both summaries before drafting. Navigator tells you WHAT scopes are affected; researcher tells you WHY the current state exists.

### Phase 2: ADR Drafting — MAIN AGENT

The main agent drafts the ADR using the Decision Flow below. No further agent delegation needed.

---

## Decision Flow
```mermaid
flowchart TD
  C[Context + Evidence] --> O[Options + Tradeoffs]
  O --> D[Decision]
  D --> K[Consequences]
  K --> A[Affected Scopes]
  A --> G[Graph Notes]
```

## Method (Silent) + Output Contract (Visible)

### 1) Deconstruct (Silent)
- Identify: problem/context, competing forces, chosen option.

### 2) Diagnose (Silent)
- Determine impact: affected capability scopes, dependency rule implications.

### 3) Develop (Silent)
- Draft using Nygard format (Context, Decision, Consequences).
- Present options neutrally with pros and cons.
- Link context to evidence. Include "Affected Scopes" directives.

### 4) Deliver (Visible)
Write ADR to `Scopes/Decisions/ADRs/<0000>-<slug>.md`.

## Rules
1. **Immutable Status**: If a decision changes, write a new ADR that "Supersedes" the old one.
2. **Scope Links (MANDATORY)**: List Affected Scopes with links.
3. **Consequences**: List both Pros AND Cons.

## ADR Template

**File Path**: `Scopes/Decisions/ADRs/<0000>-<slug>.md`

```markdown
# ADR 0012: <Title>

## Status
Accepted / Proposed / Deprecated

## Context
- **Problem**: ...
- **Constraint**: ...
- **Scope Context**: See `[Scopes/Product/...](link)`.

## Decision
We will...

## Consequences
### Positive
- ...

### Negative
- ...

## Affected Scopes
- [Scopes/Product/Frontend/State.md](link) — rules updated.
- [Scopes/GRAPH.md](link) — new dependency edge.
```
