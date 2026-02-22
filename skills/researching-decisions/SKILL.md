---
name: researching-decisions
description: Researches a technical decision, compares options, and writes an evidence-backed ADR under Scopes/Decisions/ADRs/. Use when you need to choose between approaches. Do NOT use for simple implementation work — use developing-*.
model: inherit
---

# Researching Decisions — Evidence-Backed ADR Generation

You research technical decisions by gathering evidence, comparing approaches, and producing structured ADRs. Every recommendation must cite evidence from the codebase, official docs, or experiments.

## When to use this skill
Use when the user needs to make a technical decision — choosing between approaches, evaluating a library, deciding on architecture, or assessing trade-offs.

## Example prompts
- "Compare Option A vs B and write an ADR."
- "What’s the best approach here given our current patterns?"
- "Research this library choice and document the tradeoffs."

## Prerequisites
- Read `skills/_shared/SCOPES_PROTOCOL.md` for Scopes-first startup.

## Mission Start
Load `skills/_shared/SCOPES_PROTOCOL.md`.
Design patterns (Full GoF catalog; use as the shared vocabulary in ADR comparisons):
- `skills/_shared/GOF_PATTERNS.md` (names, intent, tradeoffs, common confusions)

Resolve `SKILLS_ROOT` using the shared snippet:
- `skills/_shared/SCRIPT_DISCOVERY.md`

---

## Workflow

### Step 1: Frame the Decision

1. Identify what decision needs to be made (1 sentence).
2. List the constraints from Scopes (anchor scope, tech stack, existing patterns).
3. Identify 2-4 options to evaluate.

```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<decision topic>" --limit 5 --format json
```

Parallel evidence lanes (optional but preferred when available):
- Route to anchor scopes + constraints (scope_map).
- Read precedent ADRs and prior Work Planning notes on similar topics.
- `rg` the codebase for existing patterns/implementations in the anchor scope paths.
Merge into a short option list (2-4 max) with clear constraints.

### Step 2: Research Each Option

For each option, gather:
- **Pros**: concrete benefits with evidence
- **Cons**: concrete risks with evidence
- **Pattern conformance**: does it match existing codebase patterns?
- **Migration cost**: what changes are needed to adopt?
- **Reversibility**: how easy is it to change course later?

Parallelism (mandatory): See `skills/_shared/SCOPES_PROTOCOL.md`.
- If evaluating 2-4 options, you MUST run **one researcher per option in parallel** (spawn all in one batch; subagents or agent-team members). No sequential fallback.
- Each researcher returns a short receipt: `{ option, pros, cons, evidence, migration_cost, reversibility, scope_impact }`.
- The lead merges receipts into a single ADR.

Sources to check (in order):
1. Existing codebase patterns (`rg` for similar implementations)
2. `Scopes/Onboarding/TECH_STACK.md` for current stack constraints
3. Official documentation (use your environment’s web-browsing tool if available; otherwise note the blocker and rely on repo evidence/experiments)
4. Prior ADRs under `Scopes/Decisions/ADRs/` for precedent

### Step 3: Write the ADR

Write to `Scopes/Decisions/ADRs/<YYYY-MM-DD>-<slug>.md`:

```markdown
# ADR: <Title>

## Status
Proposed | Accepted | Rejected | Superseded by [ADR-xxx]

## Context
<What problem or decision prompted this? Include evidence links.>

## Decision
<What was decided and why.>

## Options Considered

### Option A: <Name>
- **Pros**: ...
- **Cons**: ...
- **Evidence**: `[path:Lx-Ly](path#Lx-Ly)`
- **Pattern fit**: matches/conflicts with existing pattern at `<path>`

### Option B: <Name>
- **Pros**: ...
- **Cons**: ...
- **Evidence**: ...

## Consequences
- **Positive**: ...
- **Negative**: ...
- **Scopes impact**: which scopes need updating if accepted?

## Links
- **Anchor Scopes**: [Scopes/Product/...](path)
- **Related ADRs**: ...
- **External Docs**: ...
```

### Step 3.5: Gate ADR Completeness (mandatory)

Before recommending, ensure the ADR contains:
- Status (Proposed/Accepted/Rejected/Superseded)
- Evidence links for key claims (repo evidence or external docs/experiments)
- Constraints from Scopes/tech stack and scope impact
- Migration cost and reversibility for the recommended option
- Clear next steps (tasks or implementation path)

### Step 4: Recommend

State your recommendation clearly with rationale. If the evidence is inconclusive, say so — don't force a recommendation.

---

## Lifecycle / Hygiene (mandatory rule)

After an ADR is accepted and the resulting work is implemented:
- Delete completed task files under `Scopes/Work/Tasks/`.
- Delete any executed plans/refactor plans created to implement the ADR.
- Keep the ADR + a short durable completion note (and updated Scopes as needed).

## Blocked Runbook
- No clear decision to research: ask for clarification, set `Verdict: Needs Narrowing`.
- Not enough evidence to compare options: document what you found, set `Verdict: Partial`.
- Decision depends on product/business context you don't have: recommend the user decide, present the trade-offs.

## Output Contract

Return <= 15 lines:

```markdown
## RESEARCH
Verdict: Proceed | Blocked | Needs Narrowing
Decision: <one sentence summary of recommendation>
Options Evaluated: <count>
Evidence:
- `[path:Lx-Ly](path#Lx-Ly)` — <key finding>
Recommendation: <option name> — <one line why>
Unknowns:
- <only if blocked/partial>
Artifact: Scopes/Decisions/ADRs/<date>-<slug>.md
Next: <one action>
```
