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

Delegate to [agents](../agents/) following the [parallel development pattern](../agents/WORKFLOW.md). The main agent orchestrates; agents do the heavy lifting in isolated contexts.

### Phase 1: Research — PARALLEL

Fire **both agents simultaneously** to gather context before planning:
- **`scope-navigator`** — finds relevant scopes, dependency graph, and capability boundaries
- **`plan-researcher`** *(background)* — investigates codebase patterns, git history, existing ADRs, and constraints; writes brief to `Scopes/Work/Planning/`

Read both summaries before proceeding. The navigator's scope map tells you WHERE to fit the idea; the researcher's brief tells you HOW the codebase currently works.

### Phase 2: Blueprint — MAIN AGENT

The main agent synthesizes agent findings into the Implementation Blueprint using the Planning Model below. No further agent delegation needed for this phase.

### Phase 3: Validation (optional) — SINGLE AGENT

If the plan touches many scopes, fire **`scope-auditor`** *(background)* to verify that referenced scopes are current before the plan is finalized.

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

## Plan Template

**File Path**: `Scopes/Work/Planning/<YYYY-MM-DD>-<idea>-plan.md`

```markdown
# Plan: <Feature Name>

## Executive Summary
Implementation of <Idea> using <Strategy>.

## 1. Scope Registry Impact
- **New Scope**: `Scopes/Product/Payments/Stripe.md`
- **Modified Scope**: `Scopes/Product/User/Profile.md`
- **Graph Update**: `Payments --> Stripe`

## 2. TODO Scopes (The Work)

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

## 3. Definition of Done
- All tests green.
- Scope files created/updated with template.
- `GRAPH.md` updated.
```

## Audit Checklist
- [ ] Every proposed Scope file path is under `Scopes/Product/**`
- [ ] Plan includes explicit verification steps
- [ ] Plan lists exact Scope maintenance tasks
- [ ] Graph edges planned with evidence locations
