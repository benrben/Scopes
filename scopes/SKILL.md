---
name: scopes
description: Umbrella router for the Scopes toolkit. Use when the user's intent is "do something with Scopes" but they didn't pick a specific sub-skill. Routes to exactly one sub-skill (sync/query/plan/tasks/develop/tdd/refactor/scan/adr/brainstorm/cli).
model: inherit
---

# Scopes (Router)

You are the umbrella router skill for this repo's Scopes toolkit.

Your job is to (1) classify the user's intent, then (2) immediately load and follow exactly ONE sub-skill `SKILL.md`.

## Routing rules (mandatory)

1. If the user explicitly names a sub-skill (e.g. `syncing-scopes`), do NOT route — load that skill and follow it.
2. Otherwise, pick the best single match from the table below.
3. After picking, **open that skill's `SKILL.md`** and follow its **Mission Start**.
4. Only chain into a second skill if the first skill explicitly says to hand off (e.g. `planning-idea` → `writing-tasks`).

## Quick routing

| User intent | Route to sub-skill |
|---|---|
| "Scopes are missing/stale/drifted" / "generate/update Scopes docs" | `./skills/syncing-scopes/SKILL.md` |
| "Where is X / how does X work / what depends on X / what's broken" | `./skills/querying-scopes/SKILL.md` |
| "Use the CLI / run a scopes command / check status" | `./skills/scopes-cli/SKILL.md` |
| "Brainstorm a new project / explore options interactively" | `./skills/brainstorming-project/SKILL.md` |
| "Turn an idea into a plan/blueprint" | `./skills/planning-idea/SKILL.md` |
| "Write engineering tasks / break down work" | `./skills/writing-tasks/SKILL.md` |
| "Implement safely using existing tests/commands (no new tests)" | `./skills/developing-verified/SKILL.md` |
| "Implement with new tests / strict red-green-refactor" | `./skills/developing-tdd/SKILL.md` |
| "Plan a refactor (green-to-green, phases, risk)" | `./skills/planning-refactor/SKILL.md` |
| "Scan for refactor/simplification opportunities" | `./skills/scanning-refactor/SKILL.md` |
| "Make an ADR / compare options with evidence" | `./skills/researching-decisions/SKILL.md` |

## Tie-breakers (when multiple match)

- Prefer **querying** over **syncing** if the user's goal is to answer a question (not maintain Scopes).
- Prefer **cli** over **querying** if the user wants to run a specific command.
- Prefer **developing-tdd** over **developing-verified** if verification is weak or tests must be added.
- Prefer **writing-tasks** over **planning-idea** when the user wants concrete task files as the primary output.
