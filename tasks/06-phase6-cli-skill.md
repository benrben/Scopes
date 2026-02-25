---
title: "Phase 6 — The scopes-cli Skill"
status: pending
phase: 6
effort: "Skill file + updates"
created: 2026-02-25
depends_on: [05-phase5-profiles-templates]
blocks: []
source: docs/cli-plan.md#9-phase-6--the-scopes-cli-skill
---

# Phase 6 — The `scopes-cli` Skill

> The final piece: teach agents how to use the CLI they've been given.
> Follows the same pattern as Obsidian's `obsidian-cli` skill.

## Tasks

### 6.1 Create the Skill File

- [ ] Create `scopes/skills/scopes-cli/SKILL.md`
  - Frontmatter: name, description (when to activate)
  - Command reference section (run `scopes help`)
  - Syntax guide (parameters, flags, scope resolution)
  - Common patterns section (most-used commands with examples)
  - File targeting section (scope= vs path=)
  - Output modes section (--format json vs -H)
  - Categories: scope ops, search, evidence, graph, session, tasks, agents, sync

### 6.2 Skill Content — Command Cheat Sheet

The skill should include these commonly used patterns:

```markdown
## Scope Operations
scopes read scope="My Scope"
scopes read:code scope="My Scope" --section "Entry Points"
scopes create scope="Auth/MFA" --template capability
scopes append scope="My Scope" --section "Evidence" --content "..."

## Navigation & Search
scopes map --query "<keywords>" --limit 5
scopes locate --intent "<what you want to do>"
scopes search --query "<term>" --limit 10
scopes search:code --query "<code pattern>"

## Evidence & Links
scopes evidence scope="My Scope"
scopes evidence:verify scope="My Scope"
scopes backlinks scope="My Scope"
scopes graph:impact scope="My Scope"
scopes drift --stale-only --limit 10

## Sessions
scopes session:start --scope "My Scope" --goal "What you're doing"
scopes session:append --content "- Finding or decision"
scopes session:read

## Tasks
scopes tasks --status pending
scopes task:create --scope "My Scope" --title "Task title"

## Agents & Skills
scopes agents
scopes agent:describe --id "agent-name"
scopes skills

## Health & Status
scopes status
scopes validate --all
scopes sync:status
```

### 6.3 Update Umbrella Router

- [ ] Update `scopes/SKILL.md` routing table to include scopes-cli:
  ```markdown
  | "Run a CLI command / use the scopes tool / check status" | `./skills/scopes-cli/SKILL.md` |
  ```

### 6.4 Update README.md

- [ ] Add CLI section to README.md
  - Installation: how to set up the `scopes` command (symlink/alias)
  - Quick start: 5-6 most useful commands
  - Link to `scopes help` for full reference
- [ ] Replace all raw script references with CLI commands (see task 09)

### 6.5 Update docs/automations.md

- [ ] Rewrite automation snippets to use CLI commands
  - Remove SCRIPT_DISCOVERY preamble
  - Replace `python3 "$SKILLS_ROOT/..."` with `scopes <command>`

### 6.6 Update Makefile

- [ ] Add CLI compilation check to `make lint`:
  ```makefile
  lint:
  	python3 -m compileall -q scopes/skills/*/scripts
  	python3 -m compileall -q scopes/cli.py
  	python3 scopes/cli.py help > /dev/null
  ```

### 6.7 Update Plugin Manifest

- [ ] Add CLI entry to `.claude-plugin/plugin.json`:
  ```json
  "cli": {
    "entry": "scopes/cli.py",
    "commands_prefix": "scopes"
  }
  ```

### 6.8 CHANGELOG Entry

- [ ] Add version entry to `CHANGELOG.md` documenting:
  - CLI addition
  - SCRIPT_DISCOVERY deprecation
  - All file updates for CLI integration

## Acceptance Criteria

- [ ] `scopes/skills/scopes-cli/SKILL.md` exists and follows docs/contracts.md
- [ ] Router includes scopes-cli route
- [ ] README documents the CLI
- [ ] `make lint` passes with CLI check
- [ ] An agent loading the skill can call CLI commands successfully
