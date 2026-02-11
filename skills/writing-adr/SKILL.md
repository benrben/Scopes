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
- **Scope artifacts often impacted**: `Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`

## Agent Orchestration (Prefer Parallel)

Only include agents with **Need ≥ 9**.

| Agent | How it uses it | Need (1–10) |
|---|---|---:|
| *(none; all agents are < 9 for this skill)* | *(not used)* | 1 |

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
4. **Decision Drivers (MANDATORY)**: Explicitly list the forces that matter (e.g., latency, security, complexity, team skill).
5. **Rejected Options (MANDATORY)**: Include at least one rejected alternative and why it was rejected.
6. **Evidence for internal context (MANDATORY)**: Any repo-specific context claims must include code/config evidence links (not just scope links). Missing proof becomes `[Unknown]`.

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

## Decision Drivers
- <driver 1>
- <driver 2>

## Options Considered
### Option A (Selected / Rejected)
- **Summary**: ...
- **Pros**: ...
- **Cons**: ...

### Option B (Rejected / Selected)
- **Summary**: ...
- **Pros**: ...
- **Cons**: ...

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

## When to Stop (Mandatory)
- Stop once Status, Context (with evidence where applicable), Options/Tradeoffs, Decision, Consequences, and Affected Scopes are complete.
- Default caps: 1-3 anchor scopes, 3-7 evidence links, 3-10 code files; mark gaps as `[Unknown]`.
- If the decision is unclear or multiple decisions are being mixed, stop and set `Verdict: Needs Narrowing`.

## Blocked Runbook (Mandatory)
- Missing/empty `Scopes/`: set `Verdict: Needs Sync` and recommend `syncing-scopes`.
- No evidence for key context: mark `[Unknown]`, list what you searched, and stop.
- ADR numbering/scaffold tooling missing: write the ADR manually with a placeholder number and note the blocker.

## Output Contract

Return <= 20 lines:

```markdown
## ADR
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of the recorded decision>
Evidence:
- `Scopes/Decisions/ADRs/<0000>-<slug>.md`
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. update scopes or create tasks>
Artifact: `Scopes/Decisions/ADRs/<0000>-<slug>.md`
```
