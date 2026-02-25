---
title: "Scopes CLI — Task Overview"
status: pending
created: 2026-02-25
source: docs/cli-plan.md
---

# Scopes CLI — Task Overview

> Build a single `scopes` CLI (one Python file, zero external dependencies)
> that makes the Scopes layer the cell brain of an AI assistant for any project.

## Task Files

### Implementation

| Task File | Phase | Effort | Description |
|---|---|---|---|
| [01-phase1-wire-scripts.md](01-phase1-wire-scripts.md) | 1 | ~400-500 lines | Wire existing 9 scripts under unified CLI |
| [02-phase2-brain-commands.md](02-phase2-brain-commands.md) | 2 | ~800-1000 lines | Core brain: read:code, locate, evidence, graph |
| [03-phase3-sessions-agents.md](03-phase3-sessions-agents.md) | 3 | ~500-700 lines | Sessions, tasks, agent/skill discovery, init |
| [04-phase4-sync-engine.md](04-phase4-sync-engine.md) | 4 | ~300-500 lines | Sync, history, git-powered commands |
| [05-phase5-profiles-templates.md](05-phase5-profiles-templates.md) | 5 | ~300-400 lines | Profiles, templates, config customization |
| [06-phase6-cli-skill.md](06-phase6-cli-skill.md) | 6 | Skill file | Teach agents how to use the CLI |

### Refactoring (Perfect Integration)

| Task File | Files | Description |
|---|---|---|
| [07-refactor-agents.md](07-refactor-agents.md) | 7 agent files | Replace script calls with CLI in all agents |
| [08-refactor-skills.md](08-refactor-skills.md) | 10 skill files | Replace script calls with CLI in all skills |
| [09-refactor-protocols-docs.md](09-refactor-protocols-docs.md) | 8 files | Update protocols, docs, README, config |

## Dependency Graph

```
Phase 1 ──→ Refactor agents (07)
   │    ──→ Refactor skills (08)
   │    ──→ Refactor protocols/docs (09)
   │
   ▼
Phase 2 ──→ Upgrade agents (evidence:verify, graph:impact, read:code)
   │    ──→ Upgrade skills (locate, read:code, graph:*)
   │
   ▼
Phase 3 ──→ Upgrade context-summarizer (session:*)
   │
   ▼
Phase 4
   │
   ▼
Phase 5
   │
   ▼
Phase 6 (final: skill file + router update)
```

## Verification (run after all tasks complete)

```bash
# Zero remaining SKILLS_ROOT references
rg "SKILLS_ROOT" agents/ scopes/skills/ docs/ README.md \
  --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'

# Zero remaining python3 script invocations
rg 'python3.*scripts/' agents/ scopes/skills/ docs/ README.md \
  --glob '!*cli-plan*'

# Zero remaining SCRIPT_DISCOVERY references
rg "SCRIPT_DISCOVERY" agents/ scopes/skills/ docs/ README.md \
  --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'

# CLI works
python3 scopes/cli.py help

# Makefile passes
make lint
```
