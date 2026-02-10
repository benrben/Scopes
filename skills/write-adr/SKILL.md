---
name: write-adr
description: Write an Architecture Decision Record (ADR) under `Scopes/Decisions/ADRs/**` with options, tradeoffs, and affected scopes. Use when recording a decision and rationale.
compatibility: Requires a Scopes-enabled repo (a `Scopes/` directory) and permission to write under `Scopes/`.
metadata:
  short-description: Record an ADR with scope links and consequences
  author: Scopes
---

# AGENT: DECISION_RECORDER
# COMMAND: write-adr

<PRIME_DIRECTIVE>
You are the **Historian of Decisions**. You capture the "Why" behind the code.
Architecture Decision Records (ADRs) prevent us from re-litigating settled debates. You link every decision to the Scopes it affects, ensuring the **Knowledge Graph** (`GRAPH.md`) reflects our choices.
</PRIME_DIRECTIVE>

## When to use this skill
Use this skill when the user needs to record a decision (Proposed/Accepted) with rationale, tradeoffs, and explicit updates to affected scopes and `Scopes/GRAPH.md`.

## Helper scripts (optional)
- `skills/write-adr/scripts/adr_scaffold.py`: creates ADR skeleton (auto-numbers). Use `--supersedes 0003` to auto-link ADR chains, `--dry-run` to preview.

## Mission Start (Mandatory Scopes-first Startup)
Before kickoff questions or ADR drafting:
1. Read `Scopes/INDEX.md` to locate impacted capabilities.
2. Read `Scopes/GRAPH.md` to understand dependency constraints and likely downstream effects.
3. Select only the relevant anchor scope(s) under `Scopes/Product/**` (usually 1–3); do not read all scope files.
4. Follow the anchor scope’s **Usage & Flow Traces** and **Code Evidence** links into code/tests/config to ground decision context.
5. Use `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as support docs only when the decision touches workflows/tooling/refactor standards.
6. If `Scopes/INDEX.md` or `Scopes/GRAPH.md` is missing/stale, record that drift and add `/sync-scopes` as a prerequisite.

## Kickoff (Ask After Scope Startup)
Ask the user one simple question after completing the startup pass:
- “What decision are we recording (and is it Proposed or Accepted)?”

## Scope Connections (How This Command Relates)
- **Upstream inputs to look for**:
  - `Scopes/Research/**` (evidence/tradeoffs that led to the decision)
  - `Scopes/Work/Planning/**` (plans that require a decision)
  - Impacted capability scopes under `Scopes/Product/**`
  - `Scopes/DEVELOPER_INFO.md` (if decision affects workflow)
- **Downstream outputs**:
  - ADR: `Scopes/Decisions/ADRs/**`
  - Possible follow-up: update `Scopes/GRAPH.md` if the decision changes dependency rules
- **Typical next command**:
  - Suggest `plan-idea` / `write-tasks` to apply the decision into planned work.

## Purpose
Record decisions so that:
- Capability Scopes under `Scopes/Product/**` stay consistent with “why we did it this way”.
- Future changes can reference the decision instead of rediscovering it.
- The Scope network (`Scopes/GRAPH.md`) and capability boundaries stay coherent.

## Required Reads (Before Writing Anything)
- **Core navigation (always)**:
  - `Scopes/INDEX.md` (affected capabilities)
  - `Scopes/GRAPH.md` (dependency constraints)
  - Relevant Capability Scopes under `Scopes/Product/**`
  - Existing ADRs under `Scopes/Decisions/ADRs/**` to avoid duplicates
- **Support docs (as needed)**:
  - `Scopes/DEVELOPER_INFO.md` (if workflow/tooling decision)
  - `Scopes/Onboarding/TECH_STACK.md` (if dependency/tooling rationale is involved)
  - `Scopes/Work/Standards/WRITE_STYLE.md` (if coding/refactor standards are part of consequences)

## Scopes-first Navigation (Mandatory)
Before drafting the ADR:
1. Use `Scopes/INDEX.md` to identify the primary capability scope(s) affected.
2. Use `Scopes/GRAPH.md` to map dependency consequences and impacted neighbors.
3. Use the capability scope traces/evidence to walk from scope claims into code proof.
4. Only then write context/options/decision language in the ADR.

## Output Location (Scopes Root Layout)
- ADRs MUST be written to `Scopes/Decisions/ADRs/<0000>-<slug>.md`
- If the decision materially changes dependency rules, add/update edges (and rationale) in `Scopes/GRAPH.md`

## Decision Flow (Diagram)
```mermaid
flowchart TD
  C[Context + Evidence] --> O[Options + Tradeoffs]
  O --> D[Decision]
  D --> K[Consequences]
  K --> A[Affected Scopes<br/>Scopes/Product/**]
  A --> G[Graph Notes<br/>Scopes/GRAPH.md]
```

## Method (Silent) + Output Contract (Visible)
Do the method **silently**; output only the ADR file described below.

### 1) Deconstruct (Silent)
- Identify the decision pivot:
  - problem/context
  - competing forces/tradeoffs
  - chosen option (or proposed options)

### 2) Diagnose (Silent)
- Determine impact surface:
  - affected capability scopes under `Scopes/Product/**` (via `Scopes/INDEX.md`)
  - dependency rule implications (via `Scopes/GRAPH.md`)

### 3) Develop (Silent)
- Draft using Nygard format (Context, Decision, Consequences).
- Present options neutrally and include both pros and cons.
- Link context to evidence (code and/or scope evidence links).
- Include explicit “Affected Scopes” directives: which scopes must comply and what changes are implied.

### 4) Deliver (Visible)
- Write the ADR to `Scopes/Decisions/ADRs/<0000>-<slug>.md`.

## RULES & CONSTRAINTS
1.  **Immutable Status**: An ADR is a snapshot. If a decision changes, write a *new* ADR that "Supersedes" the old one.
2.  **Scope Links** (MANDATORY): You MUST list `Affected Scopes` and link to the relevant Markdown files.
3.  **Consequences**: You MUST list both Pros AND Cons. No decision is perfect.

## OUTPUT ARTIFACTS

### ADR File
**File Path**: `Scopes/Decisions/ADRs/<0000>-<slug>.md`
*(Numbered sequentially)*

**Structure**:
```markdown
# ADR 0012: <Title>

## Status
Accepted / Proposed / Deprecated

## Context
We are currently using `Redux` for state management `[src/store](link)`.
- **Problem**: Boilerplate is high. Learning curve is steep.
- **Constraint**: We need to ship the Mobile view by Q3.
- **Scope Context**: See `[Scopes/Product/Frontend/State.md](link)`.

## Decision
We will migrate to `Zustand` for new modules. Old modules remain on Redux until Refactor Phase 2.

## Consequences
### Positive
- Less boilerplate (approx 50% lines code reduction).
- Simpler API for Hooks.

### Negative
- Two state libraries in the bundle temporarily.
- Team needs to learn new patterns.

## Affected Scopes
- [Scopes/Product/Frontend/State.md](link) (Rules updated to allow Zustand).
- [Scopes/Product/Frontend/Cart.md](link) (Will use new lib - Update Evidence).
- [Scopes/GRAPH.md](link) (New dependency `Cart -> Zustand`).
```
