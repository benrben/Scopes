# Commands (ScopesCommands)

This folder contains the Cursor slash-command prompts that implement the **Scopes-first** workflow.

## The big idea
- **Navigate by Scope, not by code**: start from `Scopes/INDEX.md` and `Scopes/GRAPH.md`, then open the relevant `Scopes/Product/**` capability scope to find traces and evidence links.
- **Scopes are the truth**: capability behavior lives in `Scopes/Product/**`, backed by evidence links into code/tests/config.
- **One constitution**: `commands/sync-scopes.md` defines the canonical structure and quality bar. It also requires mirroring itself into `Scopes/Prompts/sync-scopes.md` inside the target repo so all other commands can reference a stable in-repo “constitution”.

## Command list (current)
| Slash command | File | Primary output |
|---|---|---|
| `/sync-scopes` | `commands/sync-scopes.md` | `Scopes/INDEX.md`, `Scopes/GRAPH.md`, `Scopes/Product/**` (+ mirror to `Scopes/Prompts/sync-scopes.md`) |
| `/dev-loop` | `commands/dev-loop.md` | Code + tests + `Scopes/Work/STDD/**` + updated `Scopes/Product/**` |
| `/bug-hunt` | `commands/bug-hunt.md` | `Scopes/Work/Bugs/**` (+ optional tasks) |
| `/write-tasks` | `commands/write-tasks.md` | `Scopes/Work/Tasks/**` |
| `/plan-idea` | `commands/plan-idea.md` | `Scopes/Work/Planning/**` (+ optional `Scopes/Research/**`) |
| `/ideate` | `commands/ideate.md` | `Scopes/Work/Ideas/**` |
| `/plan-board` | `commands/plan-board.md` | `Scopes/Work/Planning/*-blueprint.md` |
| `/plan-refactor` | `commands/plan-refactor.md` | `Scopes/Work/Refactors/**` |
| `/research-loop` | `commands/research-loop.md` | `Scopes/Research/**` |
| `/write-adr` | `commands/write-adr.md` | `Scopes/Decisions/ADRs/**` |
| `/write-release` | `commands/write-release.md` | `Scopes/Releases/**` |
| `/write-onboarding` | `commands/write-onboarding.md` | `Scopes/Onboarding/**` |

## Global standards (applies to every command)
- **Scopes root layout**: all generated artifacts must live under `Scopes/` (see `commands/sync-scopes.md`).
- **Evidence links**: always include real line ranges: `[path/to/file:L10-L20](path/to/file#L10-L20)`.
- **No hallucinations**: if a claim can’t be evidenced, mark it `[Unknown]` or omit it.
- **Maintenance operations**: when a prompt requires deletions/moves, use the protocol defined in `commands/sync-scopes.md` (e.g. `DELETE FILE:` / `MOVE FILE:`) so it’s machine-actionable.

