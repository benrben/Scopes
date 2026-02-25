---
title: "Phase 4 — Sync Engine"
status: pending
phase: 4
effort: "~300-500 lines"
created: 2026-02-25
depends_on: [03-phase3-sessions-agents]
blocks: []
source: docs/cli-plan.md#7-phase-4--sync-engine
---

# Phase 4 — Sync Engine

> The CLI becomes the interface for keeping the brain truthful.
> Git-powered history, sync status, and the eval/log developer commands.

## Tasks

### 4.1 Sync Commands

- [ ] **`scopes sync`** — full Scopes sync entry point
  - Run `scopes drift --all` + `scopes validate --all` as lightweight sync check
  - Print guidance for triggering full sync via syncing-scopes skill
  - Record timestamp in `.scopes/last_sync`
- [ ] **`scopes sync:dry`** — preview what sync would change
  - Run drift + validate in read-only mode, report findings
- [ ] **`scopes sync:scope scope="Auth/Login"`** — sync check for one scope
  - Run drift + validate for single scope
- [ ] **`scopes sync:status`** — sync dashboard
  - Return: last_sync timestamp, total_scopes, stale_scopes, validation_errors, health
- [ ] **`scopes sync:history --limit 10`** — recent sync runs
  - Read from `.scopes/sync_history.json` (appended by each `scopes sync` run)
- [ ] **`scopes sync:diff scope="Auth/Login"`** — what changed since last sync
  - Git diff between last sync timestamp and now for scope file + evidence targets
- [ ] **`scopes sync:restore scope="Auth/Login" --version "2026-02-24"`** — restore synced version
  - Git checkout of scope file at specified date/commit
- [ ] **`scopes sync:removed`** — evidence pointing to files that no longer exist
  - Walk all evidence links across all scopes, check file existence

### 4.2 History Commands (git-powered)

- [ ] **`scopes diff scope="Auth/Login"`** — git diff for a scope file since last commit
  - `--since "7d"` — changes in time window (translates to git date)
- [ ] **`scopes history scope="Auth/Login"`** — git log for a scope file
- [ ] **`scopes history:list scope="Auth/Login" --limit 10`** — list commits touching this scope
  - Return: commit hash, date, message (one-line)
- [ ] **`scopes history:read scope="Auth/Login" --commit "abc123"`** — read scope at a point in time
  - Uses `git show <commit>:<path>`
- [ ] **`scopes history:restore scope="Auth/Login" --commit "abc123"`** — restore scope to previous version
  - Uses `git checkout <commit> -- <path>`
  - Warn before overwriting
- [ ] **`scopes history:evidence scope="Auth/Login"`** — how evidence links evolved
  - Parse evidence links at multiple commits, show added/removed/changed
- [ ] **`scopes history:blame scope="Auth/Login" --line 15`** — who last changed a scope line
  - Uses `git blame`

### 4.3 Index & Graph Regeneration

- [ ] **`scopes index:update`** — regenerate INDEX.md from Product/ directory structure
  - Scan all scope files, rebuild area/scope tree
  - Write updated INDEX.md
- [ ] **`scopes graph:update`** — regenerate GRAPH.md from evidence links
  - Scan all scope files for cross-scope references
  - Write updated GRAPH.md

### 4.4 Developer Commands

- [ ] **`scopes eval --code "..."`** — run Python expression in Scopes context
  - Import cli helpers, expose project_root, scope list, etc.
  - Print result as JSON
- [ ] **`scopes log --level error`** — show recent agent logs/receipts
  - Scan `Scopes/Work/` for recent JSON receipt files
  - Filter by level/status

### 4.5 Agent History

- [ ] **`scopes agent:history --id "slice-developer" --limit 5`** — recent agent invocations
  - Scan receipt files for agent name matches
  - Return: timestamp, target, status, verdict

## Acceptance Criteria

```bash
scopes sync:status
scopes sync --dry
scopes diff scope="SomeScope"
scopes history scope="SomeScope" --limit 5
scopes history:read scope="SomeScope" --commit HEAD~1
scopes history:blame scope="SomeScope" --line 10
scopes index:update
scopes eval --code "len(_all_scope_files(project))"
```
