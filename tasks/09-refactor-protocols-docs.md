---
title: "Refactor Protocols, Docs & Config"
status: pending
phase: refactor
effort: "8 files"
created: 2026-02-25
depends_on: [01-phase1-wire-scripts]
source: docs/cli-plan.md#153-per-file-refactoring-details
---

# Refactor Protocols, Docs & Config

> Update shared protocols, documentation, README, and config files
> for CLI integration. Deprecate SCRIPT_DISCOVERY.md.

---

## Shared Protocols (3 files)

### Task 9.1: `scopes/skills/_shared/SCOPES_PROTOCOL.md`

**Lines affected**: ~13-16, 81

This is the most impactful single file — read by EVERY skill at Mission Start.

- [ ] Replace scope_map.py call in Scopes-First Navigation:
  ```
  BEFORE:
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
    --query "<keywords from user request>" --limit 5 --format json

  AFTER:
  scopes map --query "<keywords from user request>" --limit 5
  ```

- [ ] Update upstream artifact intake text:
  ```
  BEFORE: Before running `scope_map.py` or reading `INDEX.md`...
  AFTER:  Before running `scopes map` or reading `INDEX.md`...
  ```

- [ ] Add CLI health check to Mission Start (new):
  ```markdown
  ## Pre-Flight (new addition)
  Verify the CLI is available before proceeding:
    scopes version
  ```

### Task 9.2: `scopes/skills/_shared/DEVELOPING_PROTOCOL.md`

**Lines affected**: ~61, 66

- [ ] Replace validate_scopes.py reference:
  ```
  BEFORE:
  - IF output is non-empty: update affected scopes + run `validate_scopes.py` as the gate
  - `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all`

  AFTER:
  - IF output is non-empty: update affected scopes + run `scopes validate` as the gate
  - `scopes validate --all`
  ```

### Task 9.3: `scopes/skills/_shared/SCRIPT_DISCOVERY.md` — DEPRECATE

- [ ] Replace entire file content with deprecation notice:
  ```markdown
  # Script Discovery (DEPRECATED)

  > **This file is deprecated.** Use the `scopes` CLI instead.
  >
  > All scripts previously accessed via `$SKILLS_ROOT` are now available
  > as `scopes <command>` subcommands. Run `scopes help` to see all commands.
  >
  > ## Migration
  >
  > | Old (SKILLS_ROOT) | New (CLI) |
  > |---|---|
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --query ...` | `scopes map --query ...` |
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --all` | `scopes drift --all` |
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all` | `scopes validate --all` |
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_skeleton_generator.py" ...` | `scopes create ...` |
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/slice_contract_builder.py" ...` | `scopes contract ...` |
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_trace_stub_from_entrypoints.py" ...` | `scopes trace ...` |
  > | `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_rename_guard.py" ...` | `scopes rename ...` |
  > | `python3 "$SKILLS_ROOT/scanning-refactor/scripts/hotspot_matrix.py" ...` | `scopes hotspot ...` |
  ```

---

## Documentation (3 files)

### Task 9.4: `docs/automations.md`

Full rewrite of automation snippets.

- [ ] Remove SCRIPT_DISCOVERY preamble (line ~7):
  ```
  BEFORE: Before running any helper scripts, resolve `SKILLS_ROOT`
          (see `scopes/skills/_shared/SCRIPT_DISCOVERY.md`).
  AFTER:  (Remove entirely)
  ```

- [ ] Replace Drift Audit (Weekly):
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
            --all --stale-only --limit 50
  AFTER:  scopes drift --all --stale-only --limit 50
  ```

- [ ] Replace Artifact Router:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
            --from-artifact Scopes/Work/Tasks/<file>.md --depth 3 --only tree
  AFTER:  scopes map --from-artifact "Scopes/Work/Tasks/<file>.md" --depth 3
  ```

- [ ] Replace Pre-Merge Quality Gate:
  ```
  BEFORE: python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
            --all --stale-only --limit 20
  AFTER:  scopes drift --all --stale-only --limit 20
  ```

### Task 9.5: `docs/context-engineering.md`

**Line affected**: ~68

- [ ] Replace scope_map.py reference:
  ```
  BEFORE: Before any skill runs `scope_map.py` or reads `INDEX.md`...
  AFTER:  Before any skill runs `scopes map` or reads `INDEX.md`...
  ```

### Task 9.6: `docs/settings.md`

**Line affected**: ~39

- [ ] Replace SCRIPT_DISCOVERY reference:
  ```
  BEFORE: - `scopes/skills/_shared/SCRIPT_DISCOVERY.md`
  AFTER:  - The `scopes` CLI (see `scopes help` for all commands)
  ```

---

## Meta Files (2 files)

### Task 9.7: `README.md`

**Lines affected**: ~94-99, 129, 262, 302

- [ ] Replace helper scripts section (~94-99):
  ```
  BEFORE:
  Helper scripts included under `scopes/skills/syncing-scopes/scripts/`:
  - `scope_map.py` — compact scope matrix view...
  - `drift_detector.py` — stale evidence detection...
  - `scope_skeleton_generator.py` — generate fill-ready capability scope skeletons...
  - `slice_contract_builder.py` — build Slice Contracts...
  - `scope_trace_stub_from_entrypoints.py` — generate trace-table stubs...
  - `scope_rename_guard.py` — rewrite scope links...

  AFTER:
  All helper functionality is available via the `scopes` CLI:
  - `scopes map` — compact scope matrix view with JSON output
  - `scopes drift` — stale evidence detection via git timestamps
  - `scopes create` — generate fill-ready capability scope skeletons
  - `scopes contract` — build Slice Contracts from drift, skeletons, or inference
  - `scopes trace` — generate trace-table stubs from evidence links
  - `scopes rename` — rewrite scope links after renames/moves
  - `scopes hotspot` — refactor hotspot matrix (size, churn, TODOs)
  - `scopes validate` — structural validation gate

  Run `scopes help` for the full command list.
  ```

- [ ] Update shared infrastructure list (~129):
  ```
  BEFORE: - `scopes/skills/_shared/SCRIPT_DISCOVERY.md` — SKILLS_ROOT resolution snippet
  AFTER:  - `scopes/cli.py` — unified CLI for all Scopes operations (`scopes help`)
  ```

- [ ] Replace scope_map.py tip (~262):
  ```
  BEFORE: Use `scope_map.py --query "<keywords>"` if you need a fast route...
  AFTER:  Use `scopes map --query "<keywords>"` (or `scopes locate --intent "<intent>"`)
          if you need a fast route to related scopes.
  ```

- [ ] Replace pre-merge snippet (~302):
  ```
  BEFORE: python3 scopes/skills/syncing-scopes/scripts/drift_detector.py --all --stale-only --limit 20
  AFTER:  scopes drift --all --stale-only --limit 20
  ```

- [ ] Add new CLI section (after "Getting started"):
  ```markdown
  ## CLI

  The `scopes` CLI provides a unified interface for all operations:

  \```bash
  python3 scopes/cli.py help        # List all commands
  scopes map --query "auth"          # Navigate scopes
  scopes drift --all --stale-only    # Check evidence freshness
  scopes validate --all              # Structural validation
  scopes read:code scope="Login"     # Follow evidence to code
  scopes locate --intent "add caching" # Intent-based routing
  \```

  Set up an alias for convenience:
  \```bash
  alias scopes="python3 /path/to/Scopes/scopes/cli.py"
  \```
  ```

### Task 9.8: `scopes/skills/syncing-scopes/references/PROTOCOLS.md`

**Line affected**: ~61

- [ ] Replace validate_scopes.py reference:
  ```
  BEFORE: - `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all`
  AFTER:  - `scopes validate --all`
  ```

---

## Config Updates

### Task 9.9: `scopes/skills/_evaluations/README.md`

**Line affected**: ~44

- [ ] Update evaluation criteria:
  ```
  BEFORE: {"id": "runs-validators", "weight": 3, "desc": "Runs drift_detector.py (or records blockers)"}
  AFTER:  {"id": "runs-validators", "weight": 3, "desc": "Runs scopes drift (or records blockers)"}
  ```

### Task 9.10: `Makefile`

- [ ] Add CLI compilation check:
  ```makefile
  .PHONY: lint

  lint:
  	python3 -m compileall -q scopes/skills/*/scripts
  	python3 -m compileall -q scopes/cli.py
  	python3 scopes/cli.py help > /dev/null
  ```

### Task 9.11: `.claude-plugin/plugin.json`

- [ ] Add CLI entry and bump version:
  ```json
  {
    "name": "scopes",
    "version": "1.1.0",
    "cli": {
      "entry": "scopes/cli.py",
      "commands_prefix": "scopes"
    }
  }
  ```

### Task 9.12: `CHANGELOG.md`

- [ ] Add version entry:
  ```markdown
  ## 1.1.0 — CLI

  - Add `scopes/cli.py` — unified CLI for all Scopes operations.
  - Replace all `SKILLS_ROOT` / `SCRIPT_DISCOVERY` references with `scopes <command>` calls.
  - Deprecate `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.
  - Add `scopes-cli` skill for teaching agents the CLI.
  - Add `.scopes/` state directory for session tracking and runtime state.
  - Update all 10 skills, 7 agents, 3 shared protocols, and 5 docs files for CLI integration.
  ```

---

## Final Verification (run after ALL refactoring tasks complete)

```bash
# 1. Zero remaining SKILLS_ROOT references
rg "SKILLS_ROOT" agents/ scopes/skills/ docs/ README.md \
  --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'
# Expected: 0 matches

# 2. Zero remaining python3 script invocations
rg 'python3.*scripts/' agents/ scopes/skills/ docs/ README.md \
  --glob '!*cli-plan*'
# Expected: 0 matches

# 3. Zero remaining SCRIPT_DISCOVERY references (except deprecation)
rg "SCRIPT_DISCOVERY" agents/ scopes/skills/ docs/ README.md \
  --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'
# Expected: 0 matches

# 4. CLI works
python3 scopes/cli.py help

# 5. Makefile passes
make lint

# 6. Count: all CLI commands exist
python3 scopes/cli.py help | wc -l
```
