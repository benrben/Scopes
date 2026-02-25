---
title: "Phase 1 — Wire Existing Scripts"
status: pending
phase: 1
effort: "~400-500 lines"
created: 2026-02-25
depends_on: []
blocks: [07-refactor-agents, 08-refactor-skills, 09-refactor-protocols-docs]
source: docs/cli-plan.md#4-phase-1--wire-existing-scripts
---

# Phase 1 — Wire Existing Scripts

> Wrap all 9 existing Python scripts under a single `scopes` CLI entry point.
> This is the foundation — everything else builds on it.

## Deliverable

`scopes/cli.py` — single Python file, zero external dependencies.

## Tasks

### 1.1 Scaffolding

- [ ] Create `scopes/cli.py` with `main()` entry point
- [ ] Set up `argparse` root parser with `--project`, `--format`, `-H` flags
- [ ] Implement project auto-detection (`_find_project_root`): walk up from cwd looking for `Scopes/INDEX.md`
- [ ] Implement script resolution (`_resolve_script`): locate scripts relative to cli.py location
- [ ] Implement scope resolution (`_resolve_scope`): wikilink-style name → path
  - Exact match in `Scopes/Product/**/`
  - Slug match (case-insensitive, underscores/hyphens normalized)
  - Substring match (unique prefix)
  - Ambiguous → error with candidates list
- [ ] Implement output helpers: `_json_out`, `_error`, `_run` (subprocess wrapper)
- [ ] Implement `_all_scope_files`: glob all .md files under `Scopes/Product/`

### 1.2 General Commands

- [ ] `scopes help` — auto-generated from subparser descriptions, grouped by category
- [ ] `scopes help <command>` — detailed help for specific command
- [ ] `scopes version` — print version + project path + scope count + last sync timestamp
- [ ] `scopes commands` — alias for help (Obsidian parity)

### 1.3 Script Bridges

Each bridge calls the existing script via subprocess, translating CLI args
to the script's argparse interface.

- [ ] **`scopes map`** → `scope_map.py`
  - Args: `--query`, `--limit`, `--area` (repeatable), `--depth`, `--from-artifact`, `--only`, `--no-summary`, `--no-evidence`, `--scope`
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes drift`** → `drift_detector.py`
  - Args: `--scope`, `--area`, `--all`, `--stale-only`, `--days`, `--limit`
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes validate`** → `validate_scopes.py`
  - Args: `--scope` (repeatable), `--area`, `--all`, `--allow-stale`
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes create`** → `scope_skeleton_generator.py`
  - Args: `scope=` (positional or `--scope`), `--area`, `--capability`, `--item` (repeatable), `--items-file`, `--items-json`, `--micro`, `--micro-scope` (repeatable), `--micro-limit`, `--force`, `--dry-run`, `--template` (alias for default template)
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes contract`** → `slice_contract_builder.py`
  - Args: mutually exclusive: `--from-drift FILE`, `--from-skeletons FILE`, `--infer`
  - Optional: `--scope`, `--target`, `--limit`
  - Pass `--repo-root` from `--project`

- [ ] **`scopes trace`** → `scope_trace_stub_from_entrypoints.py`
  - Args: `scope=` (required, repeatable), `--desc`, `--allow-missing-lines`, `--apply`
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes rename`** → `scope_rename_guard.py`
  - Args: `scope=` + `--to` (simple mode) or `--map FILE` (bulk mode)
  - Also: `--apply`, `--dry-run`, `--update-plain`, `--strict`
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes move`** → `scope_rename_guard.py` (same script, CLI sugar)
  - Same as rename but semantics imply directory change

- [ ] **`scopes hotspot`** → `hotspot_matrix.py`
  - Args: `--top`, `--since-days`, `--ext` (repeatable), `--exclude-dir` (repeatable)
  - Pass `--repo-root` from `--project`
  - Pass `--format` through

- [ ] **`scopes scopes`** → `scope_map.py --only tree`
  - Args: `--area`, `--status` (Phase 2 filter), `--limit`
  - Wraps scope_map with `--only tree`

### 1.4 Exit Codes

- [ ] Exit 0 on success
- [ ] Exit 1 on error (with JSON error on stderr)
- [ ] Exit 2 on partial result (e.g., drift found)

### 1.5 Entry Point Setup

- [ ] `python3 scopes/cli.py <command>` works directly
- [ ] Add `if __name__ == "__main__": main()` block
- [ ] Document how to symlink or alias: `alias scopes="python3 /path/to/scopes/cli.py"`

## Acceptance Criteria

```bash
# All of these must work:
python3 scopes/cli.py help
python3 scopes/cli.py version
python3 scopes/cli.py map --query "test" --format json
python3 scopes/cli.py drift --all --stale-only
python3 scopes/cli.py validate --all
python3 scopes/cli.py create --item "Auth: Login"
python3 scopes/cli.py hotspot --top 10
python3 scopes/cli.py scopes
```
