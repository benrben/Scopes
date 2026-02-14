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
- "I need to move files; plan it so Scopes links don’t break."
- "Make a green-to-green refactor plan with rollback steps."

## Prerequisites
- `Scopes/` exists with at least `INDEX.md`, `GRAPH.md`, and anchor scope for the refactor target.
- If Scopes are missing, recommend `/sync` first.
- Read `skills/_shared/SCOPES_PROTOCOL.md`.

## Mission Start
Load and follow `skills/_shared/SCOPES_PROTOCOL.md`.
Load `skills/_shared/SLICE_CONTRACT.md` for delegation rules.

Resolve `SKILLS_ROOT` using the shared snippet:
- `skills/_shared/SCRIPT_DISCOVERY.md`

---

## Workflow: Risk-Driven Refactor Planning

### Step 0: Mechanical Risk Profile (deterministic, < 3 min)

Gather four signals mechanically — no judgment calls:

**Signal 1: Blast Radius** (from GRAPH.md)
```bash
# Count downstream dependents of the refactor target
grep -c "<target scope name>" Scopes/GRAPH.md
```
Result: `blast_radius = <count of downstream scopes>`

**Signal 2: Test Coverage** (from codebase)
```bash
# Count test files that import/reference the refactor target
find . -path "*test*" -o -path "*spec*" -o -path "*__tests__*" | \
  xargs grep -l "<target module/file>" 2>/dev/null | wc -l
```
Result: `coverage = STRONG (>3 test files) | WEAK (1-2) | NONE (0)`

**Signal 3: File Movements**
Does this refactor involve moving or renaming files? `moves_files = true | false`

**Signal 4: Public API Change**
Does this refactor change any exported function signatures, endpoint paths, or database schema? `api_change = true | false`

**Risk Profile:**
```json
{
  "blast_radius": 3,
  "coverage": "STRONG",
  "moves_files": true,
  "api_change": false
}
```

---

### Step 1: Conditional Plan Depth (based on risk profile)

The risk profile determines how deep the plan needs to be:

| Risk Signal | Plan Consequence |
|---|---|
| `coverage == NONE` | **Include Phase 0**: characterization tests MUST be written first |
| `coverage == WEAK` | **Recommend Phase 0**: characterization tests strongly recommended |
| `coverage == STRONG` | **Skip Phase 0**: existing tests serve as the behavior contract |
| `moves_files == true` | **Include scope_rename_guard.py** step with rename map |
| `moves_files == true` | **Rollback plan is MANDATORY** (auto-included, no judgment call) |
| `api_change == true` | **Rollback plan is MANDATORY** |
| `blast_radius > 3` | **Include "strangler fig" phasing** (gradual migration, not big bang) |
| All signals low | **Lightweight plan**: skip Phase 0, skip rollback, minimal ceremony |

---

### Step 2: Generate the Refactor Blueprint

Write directly to `Scopes/Work/Refactors/<date>-<slug>.md`:

```markdown
# Refactor: <Title>

## Links
- **Anchor Scope**: [<scope>](path.md)
- **GRAPH.md dependents**: <list from blast radius>
- **Test coverage**: <STRONG | WEAK | NONE>
- **DEVELOPER_INFO**: [commands](Scopes/DEVELOPER_INFO.md)

## Risk Profile
```json
{ "blast_radius": N, "coverage": "...", "moves_files": bool, "api_change": bool }
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
- **Verification**: `<test command>` must pass after this phase
- **Files**: <exact file list>
- **Pattern**: follow `<existing pattern in the codebase>`

### Phase 2: <name>
...

<!-- CONDITIONAL: Include only if moves_files == true -->
## File Movement Plan
| Old Path | New Path |
|----------|----------|
| `src/old/file.ts` | `src/new/file.ts` |

### Rename Guard (Automatic)
After file movements, run:
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_rename_guard.py" \
  --map '{"Scopes/Product/Old.md":"Scopes/Product/New.md"}' --apply --repo-root .
```

### Rename Guard Preview (Dry-Run)
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_rename_guard.py" \
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

## Definition of Done
- [ ] All phases green-to-green
- [ ] No new test failures
- [ ] Scope links updated (rename_guard if files moved)
- [ ] GRAPH.md updated if dependency edges changed
```

---

### Step 3: Validation Preview (if moves_files)

If the refactor involves file movements, run the rename guard in dry-run mode and include the output in the plan:

```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_rename_guard.py" \
  --map '{"Scopes/Product/Old.md":"Scopes/Product/New.md"}' --repo-root .
```

This preview shows the user exactly which Scopes links would break and how they'd be fixed — before any code is changed.

---

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
Phases: <count>
Rollback Plan: Included | Not needed
Rename Guard: Included | Not needed
Artifact: Scopes/Work/Refactors/<date>-<slug>.md
Next: /tasks to create task files, or /develop to implement directly
```
