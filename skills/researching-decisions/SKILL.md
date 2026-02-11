---
name: researching-decisions
description: Researches decision questions by combining internal repo truth (Scopes + code) with external web sources, keeping the two strictly separated. Use when external info is needed to unblock a decision, evaluate options, or compare technologies.
---

# Researching Decisions

**You are the Scope Researcher.** Your job is to answer complex questions by combining **Internal Truth** (from `Scopes/` and Code) with **External Truth** (Web Research), strictly separating the two. You provide clarity, not code. You produce decision-enabling deliverables that feed back into the Scope system.

## When to Use / When Not to Use
- **Use when**: there's a decision, uncertainty, or unfamiliar tech and you need structured evidence + tradeoffs.
- **Don't use when**: the question can be answered purely by reading the repo (use `syncing-scopes`), or the user wants implementation (use `developing-tdd` / `writing-tasks`).

## Prerequisites
Requires a Scopes-enabled repo. External research requires web access.

## Mission Start
**You MUST read the shared protocol before proceeding.** Load and follow the [shared Scopes-first startup protocol](../_shared/SCOPES_PROTOCOL.md) (located at `skills/_shared/SCOPES_PROTOCOL.md`).

## Kickoff (Ask After Scope Startup)
Ask the user one simple question:
- "What question are we trying to answer, and what decision will it unblock?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Planning/**`, `Scopes/Work/Ideas/**`, `Scopes/Decisions/ADRs/**`, `Scopes/Product/**`
- **Downstream outputs**: Research report (`Scopes/Research/**`)
- **Typical next commands**: `planning-idea`, `writing-adr`, `writing-tasks`

## Agent Orchestration (Prefer Parallel)

Only include agents with **Need ≥ 9**.

| Agent | How it uses it | Need (1–10) |
|---|---|---:|
| `scope-navigator` | Quickly locate the 1–3 relevant Scopes + dependency edges to ground the internal audit | 9 |

---

## Working Model
```mermaid
flowchart TD
  Q[Research Question] --> I[Internal Repo Truth]
  Q --> E[External Research]
  I --> S[Synthesis: Constraints + Options]
  E --> S
  S --> R[Recommendation + Decision Notes]
  R --> U[Explicit Scope Update List]
```

## Method (Silent) + Output Contract (Visible)

### 1) Deconstruct (Silent)
- Clarify: decision to be made, systems/technologies involved, success criteria.

### 2) Diagnose (Silent)
- Internal audit: read INDEX, GRAPH, DEVELOPER_INFO, relevant capability scopes.
- Identify precise unknowns.

### 3) Develop (Silent)
- Branch A (Internal): Trace entry -> logic -> data -> output. Only claim what you can evidence.
- Branch B (External): Use authoritative sources. Compare against internal constraints.
- Synthesize: Map external options to internal reality.

### 4) Deliver (Visible)
Write research report under `Scopes/Research/**`.

## Rules
1. **Truth Separation**: Clearly label "Internal Repo Truth" vs "External Research".
2. **Evidence-Backed**: Internal claims cite `[path:Lx-Ly](path#Lx-Ly)`. External claims cite URLs.
3. **No Ambiguity**: If unknown, say `[Unknown]`.
4. **Cross-linking (MANDATORY)**: Link to primary Capability Scopes, relevant ADRs, tasks/plans.
5. **Offline Mode (No Web Access)**: If web research is blocked/unavailable, still deliver the report with a complete Internal Truth section and mark the External section as `[Blocked]` with a checklist of sources/questions to verify later.

## Research Report Template

**File Path**: `Scopes/Research/<YYYY-MM-DD>-<topic-slug>.md`

```markdown
# Research: <Topic Title>

## Executive Summary
> One paragraph answer or recommendation.

## 1. Project Reality (Internal Truth)
- **Current Pattern**: <statement>. Evidence: `[path:Lx-Ly](path#Lx-Ly)`.
- **Constraints**: <statement>. Evidence: `[path:Lx-Ly](path#Lx-Ly)`.
- **Scope References**: [Scopes/Product/...](link), [Scopes/GRAPH.md](link)

## 2. External Analysis
- **Option A**: Description. Source: [link]
- **Option B**: Description. Source: [link]
If external research is not possible, write:
- `[Blocked: no web access]` and list the exact sources you would check (official docs, RFCs, vendor guides) and what you’re trying to confirm.

## 3. Options & Tradeoffs
| Option | Pros | Cons | Fit for Repo |
|--------|------|------|--------------|
| A      | ...  | ...  | High         |
| B      | ...  | ...  | Medium       |

## 4. Recommendation
**Selected Path**: Option A.
**Rationale**: ...

## 5. Scope Updates Needed
- Update `Scopes/Product/...` (traces, evidence, diagrams)
- Update `Scopes/GRAPH.md` edges
- Create/update ADR if needed

## 6. Next Steps
- [ ] Create task file(s)
- [ ] Create plan (optional)

## Audit Checklist
- [ ] Internal section uses evidence links only
- [ ] External section uses URL sources only
- [ ] At least 2 outer scope links
- [ ] Concrete recommendation with tradeoffs
```
