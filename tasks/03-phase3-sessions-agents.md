---
title: "Phase 3 — Session & Agent Management"
status: pending
phase: 3
effort: "~500-700 lines"
created: 2026-02-25
depends_on: [02-phase2-brain-commands]
blocks: []
source: docs/cli-plan.md#6-phase-3--session--agent-management
---

# Phase 3 — Session & Agent Management

> Cross-session continuity, agent/skill discoverability, task management,
> and project initialization.

## Tasks

### 3.1 State Directory Setup

- [ ] Create `.scopes/` state directory on first use (gitignored)
  - `current_session` — path to active session log
  - `last_sync` — timestamp of last full sync
  - `bookmarks.json` — bookmarked scopes
- [ ] Add `.scopes/` to project `.gitignore` if not already present

### 3.2 Session Log Commands

Session logs live in `Scopes/Work/Notes/session-<YYYY-MM-DD>-<topic>.md`.

- [ ] **`scopes session`** — show current session log info (path, goal, scope, line count)
- [ ] **`scopes session:path`** — return path to current session log
- [ ] **`scopes session:read`** — read current session log content
- [ ] **`scopes session:read --date "2026-02-24"`** — read a specific session log
- [ ] **`scopes session:start --scope "Auth/Login" --goal "Fix token refresh"`**
  - Create new session log file from template
  - Set as current session in `.scopes/current_session`
  - Template includes: date, goal, scope anchors, ## Findings, ## Decisions, ## Next
- [ ] **`scopes session:append --content "- Found: auth uses JWT"`** — append to current session
- [ ] **`scopes session:prepend --content "## Priority Change"`** — prepend to current session
- [ ] **`scopes session:list --limit 5`** — list recent session logs (by date, with goal)
- [ ] **`scopes session:summarize`** — print guidance for invoking context-summarizer agent

### 3.3 Agent Commands

Agents live in `agents/*.md`.

- [ ] **`scopes agents`** — list all agents
  - Return: id, description, tools, model, readonly
  - Skip WORKFLOW.md
- [ ] **`scopes agent --id "slice-developer"`** — get agent summary
  - Return: name, description, tools, model, readonly, allowed_output_roots
- [ ] **`scopes agent:describe --id "bug-scanner"`** — full agent description
  - Return: all frontmatter + all section headings + output contract

### 3.4 Skill Commands

Skills live in `scopes/skills/*/SKILL.md`.

- [ ] **`scopes skills`** — list all skills
  - Return: id, description
  - Include sub-skills only (skip _shared, _evaluations)
- [ ] **`scopes skill --id "syncing-scopes"`** — get skill summary
- [ ] **`scopes skill:describe --id "syncing-scopes"`** — full skill description

### 3.5 Task Management Commands

Tasks live in `Scopes/Work/Tasks/**`.

- [ ] **`scopes tasks`** — list all task files
  - Parse frontmatter for title, scope, status
  - Support `--scope`, `--status` filters
- [ ] **`scopes task --id "task-rate-limit"`** — get specific task details
- [ ] **`scopes task:create --scope "Auth/Login" --title "Add rate limiting"`**
  - Create task file from template in `Scopes/Work/Tasks/`
  - Include scope anchor, status=pending, created date
- [ ] **`scopes task:status --id "task-rate-limit" --value "in-progress"`** — update status property
- [ ] **`scopes task:close --id "task-rate-limit"`** — mark task complete (status=done)

### 3.6 Contract & Receipt Commands

- [ ] **`scopes contract:validate --path "task-rate-limit.md"`** — validate Slice Contract fields
  - Check required fields: target, ownership, context, acceptance
- [ ] **`scopes receipt --path "receipt.json"`** — parse/validate a JSON receipt
  - Check required fields per SLICE_CONTRACT.md
- [ ] **`scopes receipt:list --scope "Auth/Login"`** — list recent receipts for a scope

### 3.7 Artifact Creation Commands

- [ ] **`scopes create:note --name "summary-auth" --type summary`**
  - Create note in `Scopes/Work/Notes/`
  - Types: summary, research, scratch
- [ ] **`scopes create:task --scope "Auth/Login" --title "Add rate limiting"`**
  - Alias for `scopes task:create`
- [ ] **`scopes create:adr --title "Session storage choice"`**
  - Create ADR skeleton in `Scopes/Work/ADRs/` (or `Scopes/Research/`)
- [ ] **`scopes create:unique --prefix "ZK"`**
  - Create unique-ID note (Zettelkasten-style timestamp)

### 3.8 Init Command

- [ ] **`scopes init`** — initialize Scopes/ structure for a new project
  - Create directories: `Scopes/Product/`, `Scopes/Work/Tasks/`, `Scopes/Work/Notes/`, `Scopes/Work/Bugs/`, `Scopes/Work/Planning/`, `Scopes/Onboarding/`
  - Create starter `Scopes/INDEX.md` (empty template)
  - Create starter `Scopes/GRAPH.md` (empty template)
  - Create starter `Scopes/DEVELOPER_INFO.md` (fill guidance)
  - Create `.scopes/` state directory
  - Print next steps guidance

### 3.9 Bookmarks

- [ ] **`scopes bookmarks`** — list bookmarked scopes (from `.scopes/bookmarks.json`)
- [ ] **`scopes bookmark scope="X"`** — add/remove bookmark toggle

### 3.10 Aliases

- [ ] **`scopes aliases scope="X"`** — list aliases for a scope (from frontmatter)

## Acceptance Criteria

```bash
scopes session:start --scope "Auth" --goal "Test sessions"
scopes session:append --content "- Testing CLI"
scopes session:read
scopes session:list
scopes agents
scopes agent --id "slice-developer"
scopes skills
scopes tasks
scopes task:create --scope "Auth" --title "Test task"
scopes tasks --status pending
scopes init --project /tmp/test-repo
scopes bookmarks
```
