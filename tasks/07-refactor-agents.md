---
title: "Refactor Agents for CLI Integration"
status: pending
phase: refactor
effort: "7 files"
created: 2026-02-25
depends_on: [01-phase1-wire-scripts]
upgrades_after: [02-phase2-brain-commands]
source: docs/cli-plan.md#153-per-file-refactoring-details
---

# Refactor Agents for CLI Integration

> Replace all `SCRIPT_DISCOVERY` / `SKILLS_ROOT` / raw `python3` script calls
> in agent files with `scopes <command>` CLI calls.

## Universal Changes (apply to all 7 files)

1. **Remove** all `SCRIPT_DISCOVERY` references and resolution instructions
2. **Remove** all `SKILLS_ROOT` environment variable mentions
3. **Remove** all "If script is not available, fall back to..." blocks
4. **Replace** `python3 "$SKILLS_ROOT/..."` with `scopes <command>`

---

## Task 7.1: `agents/bug-scanner.md`

**Lines affected**: ~72-131

### Mechanical replacements (Phase 1)

- [ ] Remove SCRIPT_DISCOVERY block (lines ~72-73)
- [ ] Replace `scope_map.py` call with CLI:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --depth 2
  AFTER:  scopes map --depth 2
  ```
- [ ] Remove fallback block: `If scope_map.py is not available, fall back to: find Scopes/Product...`
- [ ] Replace `drift_detector.py` call with CLI:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --area <area> --stale-only
  AFTER:  scopes drift --area "<area>" --stale-only
  ```
- [ ] Remove fallback block: `If drift_detector.py is not available, compare file timestamps...`

### Upgrade (Phase 2)

- [ ] Replace manual GRAPH.md grep with graph command:
  ```
  BEFORE: grep -A5 "<component>" Scopes/GRAPH.md
  AFTER:  scopes graph:impact scope="<component>"
  ```
- [ ] Consider using `scopes search:code` for pattern scanning (eval, TODO/FIXME)

---

## Task 7.2: `agents/code-reviewer.md`

**Lines affected**: ~37-41

### Mechanical replacements (Phase 1)

- [ ] Replace `drift_detector.py` + SCRIPT_DISCOVERY:
  ```
  BEFORE:
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
    --scope <anchor_scope> --stale-only --format json 2>/dev/null || true
  Resolve `SKILLS_ROOT` using `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.

  AFTER:
  scopes drift --scope "<anchor_scope>" --stale-only
  ```

---

## Task 7.3: `agents/code-simplifier.md`

**Lines affected**: ~66-79

### Mechanical replacements (Phase 1)

- [ ] Remove SCRIPT_DISCOVERY block (line ~68)
- [ ] Replace scope_map.py + multi-file reads:
  ```
  BEFORE:
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --depth 2 2>/dev/null || true
  cat Scopes/INDEX.md 2>/dev/null || true
  cat Scopes/GRAPH.md 2>/dev/null || true
  cat CLAUDE.md 2>/dev/null || true

  AFTER:
  scopes map --depth 2
  scopes index
  ```
- [ ] Replace manual rg for scope references:
  ```
  BEFORE: rg -n "<changed-file-path>" Scopes/Product Scopes/GRAPH.md 2>/dev/null || true
  AFTER:  scopes backlinks scope="<affected-scope>"
  ```

---

## Task 7.4: `agents/context-summarizer.md`

**Lines affected**: ~37-41

### Mechanical replacements (Phase 1)

- [ ] Replace scope_map.py + SCRIPT_DISCOVERY:
  ```
  BEFORE:
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
    --query "<topic keywords>" --limit 3 --format json
  Resolve `SKILLS_ROOT` using `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.

  AFTER:
  scopes map --query "<topic keywords>" --limit 3
  ```

### Upgrade (Phase 2)

- [ ] Use `scopes locate` for more semantic routing:
  ```
  scopes locate --intent "<topic being summarized>"
  ```

### Upgrade (Phase 3)

- [ ] Use session commands for session-aware summarization:
  ```
  scopes session:read
  scopes session:summarize
  ```

---

## Task 7.5: `agents/evidence-verifier.md`

**Lines affected**: ~32-44

### Mechanical replacements (Phase 1)

- [ ] Replace drift_detector.py + SCRIPT_DISCOVERY:
  ```
  BEFORE:
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
    --scope <scope-path> --stale-only --format json
  Resolve `SKILLS_ROOT` using `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.

  AFTER:
  scopes drift --scope "<scope-path>" --stale-only
  ```

### Upgrade (Phase 2)

- [ ] Replace manual multi-step evidence verification with single CLI call:
  ```
  BEFORE:
  Step 1: Pre-filter with drift_detector.py
  Step 2: Walk evidence links manually
  Step 3: For each link, read source file, check lines...

  AFTER:
  scopes evidence:verify scope="<scope>"
  # Returns: [{link, status: ok|stale|missing|content_mismatch, ...}]
  ```
  (Agent still does deeper content-level analysis, but CLI handles the mechanical parts)

---

## Task 7.6: `agents/refactor-scanner.md`

**Lines affected**: ~46-71

### Mechanical replacements (Phase 1)

- [ ] Remove SCRIPT_DISCOVERY block (lines ~46-47)
- [ ] Replace scope_map.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
            --query "<target keywords>" --limit 5 --format json
  AFTER:  scopes map --query "<target keywords>" --limit 5
  ```
- [ ] Replace hotspot_matrix.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/scanning-refactor/scripts/hotspot_matrix.py" \
            --repo-root . --since-days 90 --top 20 --format json
  AFTER:  scopes hotspot --since-days 90 --top 20
  ```

---

## Task 7.7: `agents/scope-filler.md`

**Lines affected**: ~55-82 (heaviest script user)

### Mechanical replacements (Phase 1)

- [ ] Remove SCRIPT_DISCOVERY block (lines ~58-59)
- [ ] Replace trace stub call:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_trace_stub_from_entrypoints.py" \
            --scope <scope.md> --apply
  AFTER:  scopes trace scope="<scope>" --apply
  ```
- [ ] Replace scope_map.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --depth 3 --format json
  AFTER:  scopes map --depth 3
  ```
- [ ] Replace validate_scopes.py:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" \
            --scope "<scope-file-path>" 2>/dev/null || true
  AFTER:  scopes validate --scope "<scope>"
  ```

---

## Also Update: `agents/WORKFLOW.md`

**Lines affected**: ~119, 128, 164, 277-280, 307, 328, 394

- [ ] Replace `slice_contract_builder.py` references → `scopes contract`
- [ ] Replace `drift_detector.py` references → `scopes drift`
- [ ] Replace `scope_map.py` references → `scopes map`
- [ ] Update workflow diagram boxes
- [ ] Update upstream intake text: `scope_map.py` → `scopes map`

---

## Verification

```bash
# After all agent refactoring:
rg "SKILLS_ROOT" agents/ --glob '!*cli-plan*'
# Expected: 0 matches

rg 'python3.*scripts/' agents/ --glob '!*cli-plan*'
# Expected: 0 matches

rg "SCRIPT_DISCOVERY" agents/ --glob '!*cli-plan*'
# Expected: 0 matches
```
