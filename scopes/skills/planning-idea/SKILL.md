---
name: planning-idea
description: Transforms a raw idea into a concrete implementation blueprint with risk analysis, pattern references, and sequenced TODO scopes. Use when you want a clear plan before tasks/implementation. Do NOT use when you just need to implement a small change — use developing-*.
model: inherit
---

# Planning Idea — Single-Pass Blueprint

You transform raw ideas into concrete implementation blueprints. You produce the plan artifact directly—no silent internal phases—and the `## Links` section in your output IS the handoff token for the next skill (`writing-tasks`).

## When to use this skill
Use when the user has an idea that needs to be turned into a plan before implementation.

## Example prompts
- "Turn this idea into a safe implementation plan."
- "Write a blueprint with risks, patterns, and verification."
- "Plan first, then hand off to writing-tasks."

## Prerequisites
- `Scopes/` exists (at least `INDEX.md` and some `Product/**` files).
- If Scopes are missing, recommend `/sync` first.
- Read `../_shared/SCOPES_PROTOCOL.md`.
- **Parallel subagents are MANDATORY** for context lanes AND for TODO Scope research (3+ scopes): spawn all in one batch (see SCOPES_PROTOCOL.md). No sequential fallback.

## Mission Start
Load and follow `../_shared/SCOPES_PROTOCOL.md`.
Load `../_shared/SLICE_CONTRACT.md` for delegation rules.
Design patterns (light vocabulary only; use to label patterns you actually see/choose in code):
- `../_shared/GOF_PATTERNS.md`

---

## Workflow: Artifact-First Planning

### Step -1: Upstream Artifact Intake

Before gathering fresh context, check for existing upstream artifacts (reference SCOPES_PROTOCOL.md Upstream Artifact Intake):

1. **Brainstorm notes**: `Scopes/Work/Notes/brainstorm-*.md` — read their `## Links` sections.
2. **Scan reports**: `Scopes/Work/Scans/` — reuse hotspot data and evidence links.
3. **Prior plans**: `Scopes/Work/Planning/` — check for plans on the same or overlapping topic.

If upstream artifacts are found:
- Import their `## Links` entries directly into this plan's `## Links`.
- Skip context gathering (Step 0 lanes) for any constraints already established by upstream artifacts.
- Note upstream sources in the Decision Log.

If no upstream artifacts exist, proceed to Step 0 with full context gathering.

---

### Step 0: Rapid Context Bundle (parallel, < 3 min)

These checks are independent. **Spawn all lanes as parallel subagents in one batch** (mandatory — no sequential fallback). Each lane uses a Slice Contract (see SLICE_CONTRACT.md) and returns a structured receipt.

**Lane A (subagent): Route to anchor scopes**
- **Slice Contract**: run `scope_map.py --query "<idea keywords>" --limit 5 --format json`, return top anchor scopes with relevance scores.
- **Receipt**: `{ "anchors": [...], "top_relevance": <score> }`

**Lane B (subagent): Check for prior work**
- **Slice Contract**: search `Scopes/Work/Planning/` and `Scopes/Research/` for prior plans/research matching idea keywords, read their `## Links` sections.
- **Receipt**: `{ "prior_plans": [...], "prior_research": [...], "reusable_links": [...] }`

**Lane C (subagent): Find pattern references**
- **Slice Contract**: read anchor scope evidence links, find 2-3 existing implementations structurally similar to the idea. Return file paths and pattern labels.
- **Receipt**: `{ "patterns": [{ "path": "...", "label": "...", "relevance": "..." }] }`

**Lane D (subagent): Risk extraction from anchor scopes**
- **Slice Contract**: read anchor scope `## Rules & Constraints` and `## Edge Cases` sections. Extract potential risks and acceptance-example seeds.
- **Receipt**: `{ "risks": [...], "edge_cases": [...] }`

**Merge (mandatory):** Lead stitches all receipts into a context bundle = anchor scopes + prior plans + prior research + pattern references + risk seeds.
Write the merged bundle into the plan artifact's `## Links` section so downstream skills don't re-navigate.

If prior plans exist on a similar topic, read them and build on them instead of starting from scratch.

---

### Step 0.5: TODO Scope Research (parallel, mandatory for 3+ scopes)

After the context bundle is assembled, if the blueprint will have **3 or more TODO Scopes**, spawn one subagent per TODO Scope in a single batch:

- **Each subagent** (model: `fast`) researches one TODO Scope:
  - Find the pattern reference (existing implementation to follow).
  - Gather 2+ acceptance examples from anchor scope edge cases and similar features.
  - Identify key files to modify/create.
  - Return a structured receipt: `{ "scope": "<name>", "pattern_ref": "...", "acceptance_examples": [...], "key_files": [...] }`

- **Lead** stitches all receipts into the blueprint's `## TODO Scopes` section.

**Fast-path (1-2 TODO Scopes):** Lead handles research directly without spawning subagents. Use default model for all synthesis.

---

### Step 1: Blueprint (single pass, write-as-you-go)

Write **directly** to `Scopes/Work/Planning/<date>-<idea-slug>.md` as you go. Every section is a file update — the plan IS the reasoning trace, not a hidden internal process.

Write these sections in order:

```markdown
# <Idea Title>

## Links
<!-- This section IS the handoff token for writing-tasks -->
- **Anchor Scopes**: [<scope>](path.md) — <relevance>
- **Prior Plans**: [<plan>](path.md) — <what to reuse>
- **Prior Research**: [<research>](path.md) — <findings>
- **Pattern References**: [<implementation>](path) — <what pattern to follow>
- **Upstream Artifacts**: [<artifact>](path.md) — <what was reused from Step -1>
- **DEVELOPER_INFO**: [commands](Scopes/DEVELOPER_INFO.md) — verification signals

## Risk Register
| Risk | Likelihood | Impact | Mitigation | Evidence |
|------|-----------|--------|------------|----------|
| <risk> | High/Med/Low | High/Med/Low | <strategy> | [path:Lx](path#Lx) |

## Scope Registry Impact
| Scope | Status | What Changes |
|-------|--------|-------------|
| <scope> | New / Modified / Unaffected | <description> |

## TODO Scopes (Sequenced)
### 1. <Scope Name>
- **Pattern Reference**: follow `<existing implementation path>`
- **Key Files**: `<files to modify/create>`
- **Verification**: `<test/build command from DEVELOPER_INFO.md>`
- **Acceptance Examples**:
  - Given X, when Y, then Z
  - Given A, when B, then C
- **Depends On**: (none) | <other scope>

### 2. <Scope Name>
...

## Definition of Done
- [ ] All TODO Scopes implemented and verified
- [ ] All tests pass
- [ ] Scopes documentation updated
- [ ] No `[Unknown]` markers in affected scopes

## Decision Log
| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| <choice> | <why> | <what else was weighed> |

## Machine-Readable TODO Scope List
<!-- Consumed by writing-tasks for automated task file generation -->
```json
{
  "todo_scopes": [
    {
      "name": "<Scope Name>",
      "pattern_ref": "<path>",
      "key_files": ["<file1>", "<file2>"],
      "verification": "<command>",
      "acceptance_examples": ["<example1>", "<example2>"],
      "depends_on": [],
      "risk_level": "low|medium|high"
    }
  ]
}
```
```

**Rules:**
- Write the file AS you analyze. Don't hold information in memory — commit it to the artifact immediately.
- Every TODO Scope MUST have a Pattern Reference (an existing implementation to follow).
- Every TODO Scope MUST have acceptance examples that can become test cases.
- If you can't find a pattern reference for a scope, mark it as `[No existing pattern — new ground]`.

---

### Step 2: Gate Plan Completeness (mandatory, before `/tasks`)

Spawn `plan-gate-checker` (see `agents/plan-gate-checker.md`) to validate the blueprint:

> **SLICE CONTRACT — Plan Gate**
> - **Target**: Validate plan blueprint at `Scopes/Work/Planning/<date>-<idea-slug>.md`
> - **Ownership**: Read-only on the plan file
> - **Context**: Check all TODO Scopes for completeness, ownership collisions, and evidence links
> - **Acceptance**: Return JSON receipt with pass/fail per check

The `plan-gate-checker` validates:
- Every TODO Scope has: (1) pattern reference, (2) verification command, (3) 2-5 acceptance examples, (4) explicit dependencies.
- No duplicate scopes or overlapping ownership intent (merge/simplify if two scopes would edit the same files).
- **Ownership collision check**: verify no two TODO Scopes modify the same files. If overlap is detected, merge the scopes or sequence them with an explicit dependency edge.
- **Acceptance-example count validation**: reject any TODO Scope with fewer than 2 acceptance examples. Revise until it has at least 2.
- **New-ground risk flag**: if a TODO Scope has `[No existing pattern — new ground]`, auto-flag it as higher risk in the Risk Register (add a row with Likelihood=Med, Impact=High).
- Slices are realistically 1-4 hours each (split anything larger).
- Risks include mitigations and at least one evidence link where possible.
- All evidence links in the plan reference existing files.

IF `plan-gate-checker` returns failures, revise the plan artifact and re-run the checker until it passes.

---

### Step 3: Risk Analysis Using Anchor Scopes (while writing)

As you write TODO Scopes, check the anchor scope's `## Rules & Constraints` and `## Edge Cases` sections:
- Each rule/constraint → a potential risk if violated
- Each edge case → a potential acceptance example
- Add these to the Risk Register and acceptance examples as you go

---

### Step 4: Downstream Handoff (automatic)

The plan artifact's `## Links` section IS the routing protocol for `writing-tasks`:
- `writing-tasks` reads `## Links` → extracts anchor scopes, patterns, and risks
- `writing-tasks` reads `## TODO Scopes` → converts each into a task file
- `writing-tasks` reads `## Machine-Readable TODO Scope List` → uses JSON for automated task generation
- No re-navigation needed — the plan already did the discovery work

Report to user:
```
Plan written to: Scopes/Work/Planning/<date>-<slug>.md
Next: /tasks to convert this plan into task files
```

---

## Lifecycle / Hygiene (mandatory rule)

Plans are not an archive. After the resulting work is implemented:
- Delete the executed plan file under `Scopes/Work/Planning/`.
- Delete completed task files under `Scopes/Work/Tasks/`.
- Delete any executed refactor-plan artifacts derived from this plan.
- Keep a short durable completion note (and updated Scopes/ADRs/Notes as needed).

## Blocked Runbook
- No Scopes/ exists: recommend `/sync` first, set `Verdict: Needs Sync`.
- Idea is too vague: ask for 2-3 concrete acceptance examples, set `Verdict: Needs Narrowing`.
- Anchor scope is stale: note staleness in Risk Register, recommend re-sync after planning.

## Output Contract

Return <= 20 lines:

```markdown
## PLAN
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of the blueprint>
TODO Scopes: <count>
Risk Items: <count>
Pattern References: <count>
Artifact: Scopes/Work/Planning/<date>-<slug>.md
Next: /tasks to create task files from this plan
```
