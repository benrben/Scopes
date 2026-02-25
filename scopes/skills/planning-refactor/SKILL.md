---
name: planning-refactor
description: Plans safe, step-by-step refactors using mechanical risk checks (blast radius, coverage, file moves). Use when you want to restructure code without changing behavior. Do NOT use for feature work — use developing-*.
model: inherit
---

# Planning Refactor — Mechanical Risk Assessment

You plan safe, incremental refactors guided by mechanical risk signals — not judgment calls. Every refactor plan is "green-to-green": the code must pass its verification signal before AND after every step.

## When to use this skill
Use when you need to restructure code without changing behavior: extracting modules, renaming, moving files, simplifying abstractions, reducing duplication.

## Example prompts
- "Plan a safe refactor of module X without behavior changes."
- "I need to move files; plan it so Scopes links don't break."
- "Make a green-to-green refactor plan with rollback steps."

## Prerequisites
- `Scopes/` exists with at least `INDEX.md`, `GRAPH.md`, and anchor scope for the refactor target.
- If Scopes are missing, recommend `/sync` first.
- Read `../_shared/SCOPES_PROTOCOL.md`.

## Mission Start
Load and follow `../_shared/SCOPES_PROTOCOL.md`.
Load `../_shared/SLICE_CONTRACT.md` for delegation rules.
Design patterns (Full GoF catalog; use only when it helps name/compare refactor targets):
- `../_shared/GOF_PATTERNS.md`

---

## Workflow: Risk-Driven Refactor Planning

### Step -1: Upstream Artifact Intake

Before gathering fresh risk signals, check for existing upstream artifacts (reference SCOPES_PROTOCOL.md Upstream Artifact Intake):

1. **Scan reports**: `Scopes/Work/Scans/` — if invoked after a scan report, read its `## Links` and reuse hotspot data. Skip re-scanning in Step 0.
2. **Prior refactor plans**: `Scopes/Work/Refactors/` — check for plans on the same or overlapping target.
3. **Brainstorm notes**: `Scopes/Work/Notes/brainstorm-*.md` — read their `## Links` sections.

If upstream artifacts are found:
- Import their `## Links` entries directly into this plan's `## Links`.
- Reuse hotspot data, blast radius calculations, and coverage signals already established.
- Note upstream sources in the blueprint.

If no upstream artifacts exist, proceed to Step 0 with full risk profiling.

---

### Step 0: Mechanical Risk Profile (deterministic, < 3 min)

Gather signals mechanically — no judgment calls. **Spawn all signals as parallel subagents in one batch** (mandatory — no sequential fallback). Each signal uses a Slice Contract (see SLICE_CONTRACT.md) and returns a structured receipt.

**Signal 1 (subagent): Blast Radius** (from GRAPH.md)
- **Slice Contract**: count downstream dependents of the refactor target in `Scopes/GRAPH.md`.
- **Receipt**: `{ "blast_radius": <count>, "dependents": [...] }`

**Signal 2 (subagent): Test Coverage** (from codebase)
- **Slice Contract**: count test files that import/reference the refactor target. Classify as STRONG (>3), WEAK (1-2), or NONE (0).
- **Receipt**: `{ "coverage": "STRONG|WEAK|NONE", "test_files": [...], "count": <N> }`

**Signal 3 (subagent): File Movements & Public API**
- **Slice Contract**: determine if the refactor involves moving/renaming files (`moves_files`) and if it changes any exported function signatures, endpoint paths, or database schema (`api_change`).
- **Receipt**: `{ "moves_files": true|false, "api_change": true|false, "affected_exports": [...] }`

**Signal 4 (subagent): Refactor scan (Scopes-aware)**
- **MANDATORY** when `blast_radius > 3` OR `coverage == NONE`. Otherwise optional.
- **Slice Contract**: run `scanning-refactor` (or spawn `refactor-scanner`) to get evidence-backed hotspot candidates and safe green-to-green steps. Return report link.
- **Receipt**: `{ "hotspots": [...], "report_path": "...", "safe_steps": [...] }`

**Merge (mandatory):** Lead stitches all receipts into a single Risk Profile.

**Risk Profile:**
```json
{
  "blast_radius": 3,
  "coverage": "STRONG",
  "moves_files": true,
  "api_change": false,
  "scan_report": "<path or null>"
}
```

---

### Step 1: Conditional Plan Depth (based on risk profile)

The risk profile determines how deep the plan needs to be:

| Risk Signal | Plan Consequence |
|---|---|
| `coverage == NONE` | **Deterministic branch**: include Phase 0 and run `developing-tdd` to create characterization tests first |
| `coverage == WEAK` | **Deterministic branch**: include Phase 0 and run `developing-tdd` to strengthen verification before refactor phases |
| `coverage == STRONG` | **Skip Phase 0**: existing tests serve as the behavior contract |
| `moves_files == true` | **Include scope_rename_guard.py** step with rename map |
| `moves_files == true` | **Rollback plan is MANDATORY** (auto-included, no judgment call) |
| `api_change == true` | **Rollback plan is MANDATORY** |
| `blast_radius > 3` | **Include "strangler fig" phasing** (gradual migration, not big bang) |
| All signals low | **Lightweight plan**: skip Phase 0, skip rollback, minimal ceremony |

**Fast-path (low-risk refactors):** When `blast_radius <= 2` AND `coverage == STRONG` AND `moves_files == false`: skip Phase 0, skip rollback plan, use the lightweight blueprint template (omit Strangler Fig, File Movement Plan, and Rollback Plan sections). Lead handles directly.

---

### Step 2: Generate the Refactor Blueprint

Write directly to `Scopes/Work/Refactors/<date>-<slug>.md`:

```markdown
# Refactor: <Title>

## Links
<!-- Standardized handoff format for downstream skills -->
- **Anchor Scope**: [<scope>](path.md) — <relevance>
- **GRAPH.md dependents**: <list from blast radius>
- **Test coverage**: <STRONG | WEAK | NONE>
- **Upstream Artifacts**: [<artifact>](path.md) — <what was reused from Step -1>
- **Scan Report**: [<report>](path.md) — <hotspot data> (if applicable)
- **DEVELOPER_INFO**: [commands](Scopes/DEVELOPER_INFO.md)

## Risk Profile
```json
{
  "blast_radius": N,
  "coverage": "STRONG|WEAK|NONE",
  "moves_files": true|false,
  "api_change": true|false,
  "scan_report": "<path or null>",
  "fast_path": true|false
}
```

## Current State (Code Snapshot)
- <What the code looks like now, with evidence links>
- <Key patterns/structures being refactored>

## Desired State
- <What the code should look like after refactoring>
- <Why this is better>

<!-- CONDITIONAL: Include only if coverage == NONE or WEAK -->
## Phase 0: Characterization Tests
Before touching production code, capture existing behavior:
1. Write tests that pass against the current code
2. These tests ARE the behavior contract
3. Verify: all new tests pass before proceeding

## Refactor Phases (Green-to-Green)
### Phase 1: <name> (The Seam)
- **What**: <describe the structural change>
- **Pattern**: follow `<existing pattern in the codebase>` (MANDATORY)
- **Verification**: `<test command>` must pass after this phase
- **Files**: <exact file list>
- **Rollback**: `<rollback command if phase fails>`

### Phase 2: <name>
- **What**: ...
- **Pattern**: follow `<existing pattern in the codebase>` (MANDATORY)
- **Verification**: ...
- **Files**: ...
- **Rollback**: ...

<!-- CONDITIONAL: Include only if moves_files == true -->
## File Movement Plan
| Old Path | New Path |
|----------|----------|
| `src/old/file.ts` | `src/new/file.ts` |

### Rename Guard (Automatic)
After file movements, run:
```bash
scopes rename \
  --map '{"Scopes/Product/Old.md":"Scopes/Product/New.md"}' --apply --repo-root .
```

### Rename Guard Preview (Dry-Run)
```bash
scopes rename \
  --map '{"Scopes/Product/Old.md":"Scopes/Product/New.md"}' --repo-root .
```
This shows which Scopes links would break and how they'd be fixed.

<!-- CONDITIONAL: Include if moves_files or api_change -->
## Rollback Plan
If any phase breaks verification:
1. `git stash` or `git checkout -- <files>`
2. Verify tests pass (green baseline)
3. Re-plan the failing phase with a smaller step

<!-- CONDITIONAL: Include if blast_radius > 3 -->
## Strangler Fig Strategy
Instead of a big-bang refactor, introduce the new structure alongside the old:
1. Create the new module/structure
2. Redirect callers one at a time
3. Remove the old code only after all callers are migrated
4. Each step must be green-to-green

## Scope Maintenance
After the refactor is complete:
- Update evidence links in affected scopes
- If files moved: scope_rename_guard.py updates links
- If behavior didn't change: only links need updating (not behavioral descriptions)

## Plan Gate (mandatory, automated checks)

Spawn `plan-gate-checker` (see `agents/plan-gate-checker.md`) to validate the blueprint:

> **SLICE CONTRACT — Plan Gate**
> - **Target**: Validate refactor blueprint at `Scopes/Work/Refactors/<date>-<slug>.md`
> - **Ownership**: Read-only on the blueprint file
> - **Acceptance**: Return JSON receipt with pass/fail per check

The `plan-gate-checker` validates:
- Every phase has an explicit verification command and expected PASS condition.
- Every phase has a **Pattern** reference (existing codebase pattern to follow).
- Rollback steps are present when required (moves_files or api_change).
- Rename guard preview is included when moves_files is true (dry-run output captured).
- Scope maintenance steps are complete (which scopes to update, which validators to run).
- No ownership collisions across phases.
- All evidence links in the blueprint reference existing files.

IF `plan-gate-checker` returns failures, fix the blueprint before proceeding.

## Definition of Done
- [ ] All phases green-to-green
- [ ] No new test failures
- [ ] Scope links updated (rename_guard if files moved)
- [ ] GRAPH.md updated if dependency edges changed
```

---

### Step 2a: Phase Research (parallel, mandatory for 4+ phases)

If the blueprint has **4 or more refactor phases**, spawn one subagent per phase in a single batch:

- **Each subagent** (model: `fast`) investigates one phase:
  - Identify exact files affected and their current state.
  - Check test coverage for those specific files.
  - Determine the verification command for that phase.
  - Find the existing codebase pattern to follow.
  - Return a structured receipt: `{ "phase": "<name>", "files": [...], "coverage": "...", "verification": "<cmd>", "pattern_ref": "..." }`

- **Lead** stitches all receipts into the blueprint's `## Refactor Phases` section.

For blueprints with fewer than 4 phases, lead handles research directly.

---

### Step 3: Validation Preview (if moves_files)

If the refactor involves file movements, run the rename guard in dry-run mode and include the output in the plan:

```bash
scopes rename \
  --map '{"Scopes/Product/Old.md":"Scopes/Product/New.md"}' --repo-root .
```

This preview shows the user exactly which Scopes links would break and how they'd be fixed — before any code is changed.

---

## Lifecycle / Hygiene (mandatory rule)

Refactor plan artifacts are not an archive. After the refactor is implemented and verified:
- Delete the executed refactor plan file under `Scopes/Work/Refactors/`.
- Delete completed refactor task files under `Scopes/Work/Tasks/`.
- Keep a short durable completion note (and updated Scopes/ADRs/Notes as needed).

## Blocked Runbook
- No test coverage and characterization tests can't be written: set `Verdict: Blocked`.
- Target module is too tangled (circular deps): recommend breaking into smaller refactors.
- Scopes are stale for the target area: recommend `/sync` first, set `Verdict: Needs Sync`.

## Output Contract

Return <= 20 lines:

```markdown
## REFACTOR PLAN
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary>
Risk Profile: blast_radius=N, coverage=STRONG|WEAK|NONE, moves_files=T/F, api_change=T/F
Fast-Path: yes|no
Phases: <count>
Rollback Plan: Included | Not needed
Rename Guard: Included | Not needed
Artifact: Scopes/Work/Refactors/<date>-<slug>.md
Next: /tasks to create task files, or /develop to implement directly
```
