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
- Read `../_shared/SCOPES_PROTOCOL.md` for Scopes-first startup.

## Mission Start
Load `../_shared/SCOPES_PROTOCOL.md`.
Design patterns (Full GoF catalog; use as the shared vocabulary in ADR comparisons):
- `../_shared/GOF_PATTERNS.md` (names, intent, tradeoffs, common confusions)

Resolve `SKILLS_ROOT` using the shared snippet:
- `../_shared/SCRIPT_DISCOVERY.md`

---

## Workflow

### Step 0: Intake

Check for upstream artifacts before framing (see SCOPES_PROTOCOL.md § Upstream Artifact Intake):
1. If invoked after brainstorm/plan (e.g., from `planning-refactor` or `querying-scopes`), read the incoming `## Links` section for pre-resolved anchor scopes, constraints, and option candidates.
2. If upstream provides constraints and pre-framed options, **skip Step 1 framing** — proceed directly to Step 2 (Research Each Option) using the upstream data.
3. If no upstream artifact, proceed normally to Step 1.

**Fast-path for 2 options**: When exactly 2 options are identified (from upstream or framing), spawn 2 parallel researcher subagents (one per option) and skip agent teams. This avoids overhead for simple binary decisions.

### Step 1: Frame the Decision

1. Identify what decision needs to be made (1 sentence).
2. List the constraints from Scopes (anchor scope, tech stack, existing patterns).
3. Identify 2-4 options to evaluate.

Run **3 explicit parallel evidence lanes** (mandatory, not optional):

**Lane A: Scope Route**
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<decision topic>" --limit 5 --format json
```

**Lane B: Precedent ADR Scan**
```bash
ls Scopes/Decisions/ADRs/ 2>/dev/null | head -20
# Read any ADRs related to the decision topic for precedent
```

**Lane C: Codebase Pattern Scan**
```bash
rg -n "<decision keywords>" . -S \
  -g'*.ts' -g'*.tsx' -g'*.js' -g'*.jsx' -g'*.py' -g'*.go' -g'*.rs' \
  -g'!node_modules/**' -g'!.venv/**' | head -20
```

Merge all three lanes into a short option list (2-4 max) with clear constraints.

### Step 2: Research Each Option

For each option, gather:
- **Pros**: concrete benefits with evidence
- **Cons**: concrete risks with evidence
- **Pattern conformance**: does it match existing codebase patterns?
- **Migration cost**: what changes are needed to adopt?
- **Reversibility**: how easy is it to change course later?

Parallelism (mandatory): See `../_shared/SCOPES_PROTOCOL.md`.
- If evaluating 2-4 options, you MUST run **one `scope-investigator` per option in parallel** (see `agents/scope-investigator.md`; spawn all in one batch). No sequential fallback.
- Each investigator gets a full Slice Contract with exclusive option ownership:

> **SLICE CONTRACT — Per-Option Researcher**
> - **Target**: Research `{option_name}` for decision `{decision_title}`
> - **investigation_type**: `deep_dive`
> - **Ownership**: Exclusive — this investigator owns the `### Option {N}` section of the ADR. No other researcher may write to this section.
> - **Context**: Decision framing: `{framing}`, option: `{option_name}`, anchor scopes: `{scope_paths}`, constraints: `{constraints}`
> - **Acceptance**: Return JSON receipt with findings, evidence bundle, and architecture layer mapping. Minimum 2 evidence links required per option.
> - **WIP Limit**: Max 4 researchers in parallel (one per option)

- Each investigator returns a JSON receipt per `scope-investigator` output contract, plus option-specific fields:
  ```json
  { "option": "<name>", "pros": [...], "cons": [...], "evidence": ["path:Lx-Ly", ...], "migration_cost": "low|medium|high", "reversibility": "easy|moderate|hard", "scope_impact": [...], "layers_touched": [...] }
  ```
- The lead merges receipts into a single ADR.

**Mandatory for ADR section writing**: When writing the final ADR, spawn one agent per option section in parallel for speed. Each writes its assigned `### Option` section only.

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
- **Evidence**: ... (minimum 2 evidence links per option)

## Consequences
- **Positive**: ...
- **Negative**: ...
- **Scopes impact**: which scopes need updating if accepted?

## Verification Strategy
- **How to validate**: <concrete steps to verify the chosen option works — e.g., test commands, metrics to check, integration points to exercise>
- **Rollback trigger**: <specific condition(s) under which to revert — e.g., "if latency exceeds 500ms p99" or "if test suite fails on X">
- **Rollback plan**: <concrete steps to revert to the prior state>

## Links
- **Anchor Scopes**: [Scopes/Product/...](path)
- **Related ADRs**: ...
- **External Docs**: ...
- **Upstream Artifact**: <path to upstream brainstorm/plan/query, if any>
- **Downstream Consumers**: <skills/tasks that will read this ADR — e.g., planning-refactor, developing-verified>
- **Researcher Receipts**: <JSON receipts from per-option researchers, inline or linked>
```

### Step 3.5: Gate ADR Completeness (mandatory)

Before recommending, run the **automated ADR completeness gate**. ALL checks must pass:

**Automated checks (mechanical, no judgment):**
1. `## Status` section exists and is non-empty
2. `## Verification Strategy` section exists with rollback trigger
3. `## Links` section exists with at least Anchor Scopes and Downstream Consumers
4. **Minimum 2 evidence links per option** — count `[path:Lx-Ly]` references in each `### Option` section. If any option has < 2, flag it and attempt to find more evidence before proceeding.
5. Spawn `evidence-verifier` (see `agents/evidence-verifier.md`) to validate all evidence links in the ADR:
   > **SLICE CONTRACT — ADR Evidence Verification**
   > - **Target**: Verify all evidence links in the ADR at `Scopes/Decisions/ADRs/<date>-<slug>.md`
   > - **Ownership**: Read-only on the ADR and its evidence targets
   > - **Acceptance**: Return JSON receipt classifying links as ok/stale/shifted/broken/deleted
   If any links are broken/deleted, fix before finalizing. If shifted/stale, document in the ADR.

**Manual checks:**
- Constraints from Scopes/tech stack and scope impact are documented
- Migration cost and reversibility for the recommended option
- Clear next steps (tasks or implementation path)

If any automated check fails, fix before finalizing. If unfixable, document the gap in the ADR.

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
