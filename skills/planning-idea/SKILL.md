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
- Read `skills/_shared/SCOPES_PROTOCOL.md`.

## Mission Start
Load and follow `skills/_shared/SCOPES_PROTOCOL.md`.
Load `skills/_shared/SLICE_CONTRACT.md` for delegation rules.

Resolve `SKILLS_ROOT` using the shared snippet:
- `skills/_shared/SCRIPT_DISCOVERY.md`

---

## Workflow: Artifact-First Planning

### Step 0: Rapid Context Bundle (parallel, < 3 min)

These checks are independent. If your environment supports true parallel subagents/teammates, you can run them in parallel (spawn all in one batch). Otherwise, run them one after the other.

**Lane A: Route to anchor scopes**
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<idea keywords>" --limit 5 --format json
```

**Lane B: Check for prior work**
```bash
# Prior plans on similar topics
find Scopes/Work/Planning/ -name "*.md" | xargs grep -li "<idea keywords>" 2>/dev/null

# Prior research
find Scopes/Research/ -name "*.md" | xargs grep -li "<idea keywords>" 2>/dev/null
```

**Lane C: Find pattern references**
```bash
# Find 2-3 existing implementations that are structurally similar
# Read anchor scope evidence links → grep for similar patterns in those paths
```

**Merge:** context bundle = anchor scopes + prior plans + prior research + pattern references.

If prior plans exist on a similar topic, read them and build on them instead of starting from scratch.

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
```

**Rules:**
- Write the file AS you analyze. Don't hold information in memory — commit it to the artifact immediately.
- Every TODO Scope MUST have a Pattern Reference (an existing implementation to follow).
- Every TODO Scope MUST have acceptance examples that can become test cases.
- If you can't find a pattern reference for a scope, mark it as `[No existing pattern — new ground]`.

---

### Step 2: Risk Analysis Using Anchor Scopes (while writing)

As you write TODO Scopes, check the anchor scope's `## Rules & Constraints` and `## Edge Cases` sections:
- Each rule/constraint → a potential risk if violated
- Each edge case → a potential acceptance example
- Add these to the Risk Register and acceptance examples as you go

---

### Step 3: Downstream Handoff (automatic)

The plan artifact's `## Links` section IS the routing protocol for `writing-tasks`:
- `writing-tasks` reads `## Links` → extracts anchor scopes, patterns, and risks
- `writing-tasks` reads `## TODO Scopes` → converts each into a task file
- No re-navigation needed — the plan already did the discovery work

Report to user:
```
Plan written to: Scopes/Work/Planning/<date>-<slug>.md
Next: /tasks to convert this plan into task files
```

---

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
