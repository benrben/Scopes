# ScopesCommands Summary

This repo ships **Cursor slash-command prompts** (in `commands/`) that implement a **Scopes-first** workflow.

## Commands

| Slash command | Prompt file | Primary purpose | Primary outputs (in the target repo) |
|---|---|---|---|
| `/sync-scopes` | `commands/sync-scopes.md` | Generate/update Scopes from repo reality (evidence-backed) | `Scopes/Product/**`, `Scopes/INDEX.md`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md` (as discovered), plus mirror prompt to `Scopes/Prompts/sync-scopes.md` |
| `/dev-loop` | `commands/dev-loop.md` | Implement features/bugs via strict TDD while keeping Scopes synced | Code + tests, `Scopes/Work/STDD/**`, updates to `Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md` |
| `/develop` | `commands/develop.md` | Implement features/bugs via verify-as-you-go (no strict TDD) while keeping Scopes synced | Code + optional tests, `Scopes/Work/DEV/**`, updates to `Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md` |
| `/bug-hunt` | `commands/bug-hunt.md` | Find proven bugs/foot-guns with evidence and recommend minimal fixes | `Scopes/Work/Bugs/**` (+ optional `Scopes/Work/Tasks/**`) |
| `/write-tasks` | `commands/write-tasks.md` | Convert intent/plans/research/bugs into 1–4 hour engineer-ready tasks | `Scopes/Work/Tasks/**` |
| `/plan-idea` | `commands/plan-idea.md` | Turn an idea into a sequenced implementation blueprint | `Scopes/Work/Planning/**` (+ optional `Scopes/Research/**`) |
| `/ideate` | `commands/ideate.md` | Generate scope-anchored ideas ready for planning | `Scopes/Work/Ideas/**` |
| `/plan-board` | `commands/plan-board.md` | Map Scopes into an execution-ready board blueprint | `Scopes/Work/Planning/*-blueprint.md` |
| `/plan-refactor` | `commands/plan-refactor.md` | Produce safe refactor plans with verification gates | `Scopes/Work/Refactors/**` |
| `/research-loop` | `commands/research-loop.md` | Research with strict internal-vs-external truth separation | `Scopes/Research/**` |
| `/write-adr` | `commands/write-adr.md` | Capture architecture decisions and link them to Scopes | `Scopes/Decisions/ADRs/**` |
| `/write-release` | `commands/write-release.md` | Write release notes from scope delta (facts-only) | `Scopes/Releases/**` |
| `/write-onboarding` | `commands/write-onboarding.md` | Create role-based onboarding via scope traces and tours | `Scopes/Onboarding/**` |

## See also
- `commands/README.md` for global standards and prompt conventions.
