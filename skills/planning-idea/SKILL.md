---
name: planning-idea
description: Turns a raw idea into a concrete implementation blueprint with explicit Scopes impacts, sequencing, and verification. Use when the user needs a plan, blueprint, or wants to design a feature before coding.
---

# Planning an Idea

**You are the System Architect.** You take a raw, vague idea and turn it into a concrete **Implementation Blueprint** (TODO Scopes) that respects strict Scope documentation standards. You bridge the gap between "I want X" and "Here is the exact list of changes needed".

## When to use this skill
Use when the user has an idea and needs a concrete, scope-native blueprint before implementation.

## Prerequisites
Requires a Scopes-enabled repo (a `Scopes/` directory) and permission to write planning artifacts.

## Safety and constraints
- Do not implement product code. Output planning artifacts under `Scopes/Work/Planning/**` (and research notes under `Scopes/Research/**` when needed).

## Mission Start
**You MUST read the shared protocol before proceeding.** Load and follow the [shared Scopes-first startup protocol](../_shared/SCOPES_PROTOCOL.md) (located at `skills/_shared/SCOPES_PROTOCOL.md`).

## Kickoff (Ask After Scope Startup)
Ask the user one simple question:
- "What's the idea we're planning—paste the idea file (preferred) or describe it in 3-5 sentences?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Ideas/**`, `Scopes/Research/**`
- **If research needed and missing**: Trigger `researching-decisions` first.
- **Downstream outputs**: Plan (`Scopes/Work/Planning/**`), follow-on tasks via `writing-tasks`

## Agent Orchestration (Prefer Parallel)

Only include agents with **Need ≥ 9**.

| Agent | How it uses it | Need (1–10) |
|---|---|---:|
| `scope-navigator` | Find relevant scopes + dependency graph to place the idea correctly | 9 |
| `code-architect` | Produce a decisive architecture blueprint aligned to existing patterns and the Scopes contract | 10 |

---

## Planning Model
```mermaid
flowchart TD
  Idea[Idea Input] --> Fit[Fit to existing Scopes]
  Fit --> Risks[Risk + Feasibility]
  Risks --> Blueprint[Sequenced Blueprint]
  Blueprint --> Artifacts[Scope Registry Impact]
  Artifacts --> Done[Definition of Done + Verification]
```

## Method (Silent) + Output Contract (Visible)

### 1) Deconstruct (Silent)
- Identify core feature, target users, fit in `Scopes/Product/**`.
- Record constraints (stack/patterns/anti-tiny-scope).

### 2) Diagnose (Silent)
- Identify feasibility risks (schema, compatibility, breaking changes).
- If external info required, trigger `researching-decisions` as prerequisite.

### 3) Develop (Silent)
- Choose implementation strategy with sequenced blueprint.
- Map **Scope Registry Impact**: new scope files, modified scopes, planned graph edges, trace/diagram/evidence updates.
- Sequence work DB -> API -> UI (or justify alternative).

### 4) Deliver (Visible)
Output research/context note (if needed) and implementation plan.

## Pattern Conformance (Mandatory)

Before proposing an implementation blueprint, you MUST discover the project's existing patterns (see [Pattern Discovery](../_shared/SCOPES_PROTOCOL.md)).

1. **During Deconstruct**: Identify which existing patterns apply to the new feature (auth pattern, API pattern, data access pattern, etc.).
2. **During Develop**: The blueprint MUST specify which existing patterns to follow for each TODO Scope, with evidence links to example implementations.
3. **In the Plan output**: Each TODO Scope includes a "Pattern Reference" pointing to the existing implementation to mimic.
4. **If new patterns are needed**: Explicitly call out that a new pattern is being introduced and why the existing ones don't apply.

---

## Rules
1. **Anti-Tiny-Scope**: Don't suggest a new Scope for a helper function. Merge into parent.
2. **Graph Awareness**: Specify how new feature connects in `GRAPH.md`.
3. **Pattern Conformance**: Every TODO Scope MUST reference the existing pattern to follow.
4. **Template Fidelity**: Proposed Scope changes follow standard structure (use cases, traces, evidence, exactly 2 diagrams).
5. **Outer-scope linking**: Link to capability scopes, research notes, ADRs, release notes as applicable.
6. **Risk Register (MANDATORY)**: Include a short risk/unknowns table with mitigations and verification.

## Plan Template

**File Path**: `Scopes/Work/Planning/<YYYY-MM-DD>-<idea>-plan.md`

```markdown
# Plan: <Feature Name>

## Executive Summary
Implementation of <Idea> using <Strategy>.

## 1. Risk Register (Required)
| Unknown / Risk | Impact | Mitigation | Verification |
|---|---|---|---|
| <e.g., API quota limits> | <what breaks> | <how we mitigate> | <how we verify> |

## 2. Scope Registry Impact
- **New Scope**: `Scopes/Product/Payments/Stripe.md`
- **Modified Scope**: `Scopes/Product/User/Profile.md`
- **Graph Update**: `Payments --> Stripe`

## 3. TODO Scopes (The Work)

### Scope 1: Backend Integration
- **Goal**: Connect to Stripe API.
- **Pattern Reference**: Follow `[src/lib/twilio.ts](link)` — same service wrapper pattern.
- **Changes**: `src/lib/stripe.ts`
- **Verification**: Integration Test
- **Scope Artifacts**: Create Scope file, Diagram.

### Scope 2: API Endpoint
- **Goal**: Expose checkout session.
- **Pattern Reference**: Follow `[src/controllers/OrderController.ts](link)` — same route + middleware + validation chain.
- **Dependencies**: Scope 1.

### Scope 3: Frontend UI
- **Goal**: Payment Button Component.
- **Pattern Reference**: Follow `[src/components/OrderButton.tsx](link)` — same component + hook pattern.
- **Dependencies**: Scope 2.

## 4. Definition of Done
- All tests green.
- Scope files created/updated with template.
- `GRAPH.md` updated.
```

## Audit Checklist
- [ ] Every proposed Scope file path is under `Scopes/Product/**`
- [ ] Risk Register included (unknowns + mitigations + verification)
- [ ] Plan includes explicit verification steps
- [ ] Plan lists exact Scope maintenance tasks
- [ ] Graph edges planned with evidence locations
