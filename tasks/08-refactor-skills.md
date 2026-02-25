---
title: "Refactor Skills for CLI Integration"
status: pending
phase: refactor
effort: "10 skill files"
created: 2026-02-25
depends_on: [01-phase1-wire-scripts]
upgrades_after: [02-phase2-brain-commands]
source: docs/cli-plan.md#153-per-file-refactoring-details
---

# Refactor Skills for CLI Integration

> Replace all `SCRIPT_DISCOVERY` / `SKILLS_ROOT` / raw `python3` script calls
> in skill SKILL.md files with `scopes <command>` CLI calls.

## Universal Changes (apply to all 10 files)

1. **Remove** the `Resolve SKILLS_ROOT using` block (present in every skill)
2. **Remove** all `python3 "$SKILLS_ROOT/..."` invocations
3. **Replace** with equivalent `scopes <command>` calls
4. **Remove** "If SKILLS_ROOT cannot be resolved" blocked runbook entries

---

## Task 8.1: `scopes/skills/syncing-scopes/SKILL.md` (heaviest — ALL scripts)

**Lines affected**: ~36-42, 99-101, 118-120, 166-168, 183-185, 191-193, 199-201, 213-215, 229-260, 285

### Mission Start

- [ ] Replace SKILLS_ROOT verification:
  ```
  BEFORE:
  - Resolve `SKILLS_ROOT` using `../_shared/SCRIPT_DISCOVERY.md`.
    ls "$SKILLS_ROOT/syncing-scopes/scripts/"*.py
  If SKILLS_ROOT cannot be resolved or scripts are missing, STOP.

  AFTER:
  - Verify the CLI is available:
    scopes version
  If the CLI is not available, STOP and tell the user.
  ```

### Wave Model Steps

- [ ] Replace skeleton generation:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_skeleton_generator.py" --item "Area: Cap" --format json
  AFTER:  scopes create --item "Area: Cap"
  ```
- [ ] Replace contract building (from skeletons):
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../slice_contract_builder.py" --from-skeletons output.json
  AFTER:  scopes contract --from-skeletons output.json
  ```
- [ ] Replace validate gate:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../validate_scopes.py" --all
  AFTER:  scopes validate --all
  ```
- [ ] Replace drift detection:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../drift_detector.py" --all --format json
  AFTER:  scopes drift --all
  ```
- [ ] Replace repair cycle contracts:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../slice_contract_builder.py" --from-drift ...
  AFTER:  scopes contract --from-drift ...
  ```
- [ ] Replace repair skeleton generation:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_skeleton_generator.py" ...
  AFTER:  scopes create ...
  ```
- [ ] Replace final validation:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../validate_scopes.py" --all
  AFTER:  scopes validate --all
  ```

### Script Quick Reference Table

- [ ] Replace entire table with CLI command reference:
  ```
  | CLI Command       | Purpose                            | Key Args                          |
  |-------------------|------------------------------------|-----------------------------------|
  | scopes create     | Create scope skeletons             | scope=, --item, --micro           |
  | scopes drift      | Detect stale evidence              | --all, --stale-only               |
  | scopes validate   | Full structural gate               | --all, --scope, --area            |
  | scopes map        | Query scopes by keyword            | --query, --depth                  |
  | scopes trace      | Generate trace table stubs         | scope=, --apply                   |
  | scopes rename     | Fix links after moves              | scope= --to, --map                |
  | scopes contract   | Build Slice Contracts              | --from-drift, --from-skeletons    |
  | scopes hotspot    | Hotspot analysis                   | --top, --since-days               |
  ```

### Blocked Runbook

- [ ] Replace script-not-found with CLI-not-found:
  ```
  BEFORE: Scripts not found ($SKILLS_ROOT unresolvable): set Verdict: Blocked
  AFTER:  CLI not found (scopes version fails): set Verdict: Blocked
  ```

---

## Task 8.2: `scopes/skills/querying-scopes/SKILL.md`

**Lines affected**: ~3, 9, 26-27, 49

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~26-27)
- [ ] Replace scope_map.py call:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
            --query "<keywords>" --limit 5 --format json
  AFTER:  scopes map --query "<keywords>" --limit 5
  ```
- [ ] Update description references from `scope_map.py` to `scopes map`

### Upgrade (Phase 2)

- [ ] Use `scopes read:code` to follow evidence automatically instead of manual file reading
- [ ] Use `scopes locate --intent` for intent-based routing

---

## Task 8.3: `scopes/skills/developing-tdd/SKILL.md`

**Lines affected**: ~34-35, 56, 145, 342

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~34-35)
- [ ] Replace scope_map.py routing:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_map.py" --query "..." --limit 5 --format json
  AFTER:  scopes map --query "..." --limit 5
  ```
- [ ] Replace validate_scopes.py gate:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../validate_scopes.py" --all
  AFTER:  scopes validate --all
  ```
- [ ] Update mermaid diagram reference from `scope_map.py` to `scopes map`

---

## Task 8.4: `scopes/skills/developing-verified/SKILL.md`

**Lines affected**: ~33-34, 52, 120, 265-268

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~33-34)
- [ ] Replace scope_map.py routing:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_map.py" --query "..." --limit 5 --format json
  AFTER:  scopes map --query "..." --limit 5
  ```
- [ ] Replace validate_scopes.py gate:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../validate_scopes.py" --all
  AFTER:  scopes validate --all
  ```
- [ ] Update mermaid diagram reference from `scope_map.py` to `scopes map`

---

## Task 8.5: `scopes/skills/planning-idea/SKILL.md`

**Lines affected**: ~31-32, 60

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~31-32)
- [ ] Replace scope_map.py:
  ```
  BEFORE: scope_map.py --query "<idea keywords>" --limit 5 --format json
  AFTER:  scopes map --query "<idea keywords>" --limit 5
  ```

### Upgrade (Phase 2)

- [ ] Use `scopes locate --intent "<idea>"` for semantic routing
- [ ] Use `scopes index` for structured INDEX access

---

## Task 8.6: `scopes/skills/writing-tasks/SKILL.md`

**Lines affected**: ~31-32, 48

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~31-32)
- [ ] Replace scope_map.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_map.py" --query "..." --limit 5 --format json
  AFTER:  scopes map --query "..." --limit 5
  ```

---

## Task 8.7: `scopes/skills/brainstorming-project/SKILL.md`

**Lines affected**: ~47, 91

- [ ] Remove SCRIPT_DISCOVERY reference (line ~47)
- [ ] Replace scope_map.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
            --query "..." --format json
  AFTER:  scopes map --query "..."
  ```

---

## Task 8.8: `scopes/skills/researching-decisions/SKILL.md`

**Lines affected**: ~27-28, 53

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~27-28)
- [ ] Replace scope_map.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_map.py" --query "..." --limit 5 --format json
  AFTER:  scopes map --query "..." --limit 5
  ```

---

## Task 8.9: `scopes/skills/scanning-refactor/SKILL.md`

**Lines affected**: ~35-36, 58, 71, 113

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~35-36)
- [ ] Replace scope_map.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_map.py" --query "..." --limit 5 --format json
  AFTER:  scopes map --query "..." --limit 5
  ```
- [ ] Replace hotspot_matrix.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/scanning-refactor/scripts/hotspot_matrix.py" \
            --repo-root . --since-days 90 --top 20 --format json
  AFTER:  scopes hotspot --since-days 90 --top 20
  ```
- [ ] Replace scope_rename_guard.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_rename_guard.py" --map ... --dry-run
  AFTER:  scopes rename --map "..." --dry-run
  ```

### Upgrade (Phase 2)

- [ ] Use `scopes graph:impact` for dependency analysis in refactor planning

---

## Task 8.10: `scopes/skills/planning-refactor/SKILL.md`

**Lines affected**: ~30-31, 176, 182, 259

- [ ] Remove SCRIPT_DISCOVERY reference (lines ~30-31)
- [ ] Replace scope_rename_guard.py calls (3 locations):
  ```
  BEFORE: python3 "$SKILLS_ROOT/.../scope_rename_guard.py" --map ... --dry-run
  AFTER:  scopes rename --map "..." --dry-run

  BEFORE: python3 "$SKILLS_ROOT/.../scope_rename_guard.py" --map ... --apply
  AFTER:  scopes rename --map "..." --apply
  ```

### Upgrade (Phase 2)

- [ ] Use `scopes graph:impact` and `scopes graph:path` for dependency analysis

---

## Verification

```bash
# After all skill refactoring:
rg "SKILLS_ROOT" scopes/skills/ --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'
# Expected: 0 matches

rg 'python3.*scripts/' scopes/skills/ --glob '!*cli-plan*'
# Expected: 0 matches

rg "SCRIPT_DISCOVERY" scopes/skills/ --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'
# Expected: 0 matches (except deprecation notice in SCRIPT_DISCOVERY.md itself)
```
