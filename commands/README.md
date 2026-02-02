# Scopes Commands & Conventions

This folder contains prompt files that Cursor (and other tools) can expose as slash commands.

## Command list

| Command | File | What it does |
|---|---|---|
| `/ask-scopes` | `commands/ask-scopes.md` | Answer questions about the project using `Scopes/` as truth (repair drift only when required) |
| `/bug-hunt` | `commands/bug-hunt.md` | Find bugs/anti-patterns with evidence; output a bug report (and optional tasks) |
| `/dev-loop` | `commands/dev-loop.md` | Implement a feature/bug via strict TDD and update Scopes as you go |
| `/develop` | `commands/develop.md` | Implement a feature/bug via verify-as-you-go (no strict TDD) and update Scopes as you go |
| `/ideate` | `commands/ideate.md` | Generate scope-anchored ideas that are ready to plan |
| `/plan-board` | `commands/plan-board.md` | Turn `Scopes/` into an execution board blueprint |
| `/plan-idea` | `commands/plan-idea.md` | Turn an idea into a sequenced plan (and create/reuse research if needed) |
| `/plan-refactor` | `commands/plan-refactor.md` | Plan a safe refactor with verification gates and scope maintenance |
| `/research-loop` | `commands/research-loop.md` | Research with strict internal-vs-external truth separation |
| `/sync-scopes` | `commands/sync-scopes.md` | The core agent: generate/update Scopes (truth) from code |
| `/write-adr` | `commands/write-adr.md` | Write ADRs linked to affected scopes (and graph implications) |
| `/write-onboarding` | `commands/write-onboarding.md` | Role-based onboarding path driven by scope traces |
| `/write-release` | `commands/write-release.md` | Release notes from scope delta (facts-only) |
| `/write-tasks` | `commands/write-tasks.md` | Turn intent/plans/research/bugs into 1–4 hour engineer-ready tasks |

## Source of truth

This repo treats `commands/*.md` as the **single source of truth**.

If users prefer Skills, generate skills from these commands using `scripts/update-skill.sh` (no duplicated hand-maintained content).

