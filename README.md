# Scopes: Evidence‑Backed AI Skills for Real Codebases

**Stop pasting folders. Stop guessing. Start shipping with proof.**

Scopes is a set of **skills** and **agents** that turns your repo into a map your AI assistant can reliably navigate. It adds an opinionated, evidence-backed layer (“Scopes”) that translates **human intent** (features, capabilities, flows) into **code truth** (exact files + line ranges, tests, config, schemas).

If you’ve ever watched an assistant “sound confident” while looking in the wrong place, this is the fix.

![Scopes map](docs/assets/scopes_hero.png)

## Who this is for

- Engineers using AI assistants on real repos (not toy projects)
- Teams that care about correctness, maintainability, and repeatable workflows
- Anyone tired of paying tokens to brute-force “context”

---

## The problem Scopes solves

When a developer asks an AI assistant to *“update the login flow”* or *“fix the payment bug”*, the assistant usually struggles with:

- **Intent ambiguity**: the request names a capability, but the assistant sees thousands of files.
- **Where-to-look failure**: you end up manually pointing to directories, hoping it’s enough.
- **Token waste**: you paste large chunks of code to compensate.
- **Doc drift**: the “docs” don’t match what the code actually does today.
- **Hallucinations**: when evidence is missing, the model fills the gap.

---

## The solution: a translation layer (Intent → Evidence → Code)

Scopes adds a first-class **navigation + compression layer** inside your repo:

- `Scopes/INDEX.md` — the map (what exists)
- `Scopes/GRAPH.md` — the dependency graph (what touches what)
- `Scopes/Product/**` — capability docs written from *observable reality*, with evidence links like:
  - `[path/to/file.ts:L20-L45](path/to/file.ts#L20-L45)` *(example)*
- `Scopes/DEVELOPER_INFO.md` — “how to run/test/build” discovered in repo truth
- `Scopes/Onboarding/TECH_STACK.md` — evidence-backed stack inventory
- `Scopes/Work/Standards/WRITE_STYLE.md` — engineering defaults for maintainable changes

Instead of dumping code into context, the assistant loads **one anchor Scope**, follows **traces**, then jumps to the **exact evidence** it needs.

Want the deeper explanation? Start here: [docs/why-scopes.md](docs/why-scopes.md)

![Intent to Code](docs/assets/intent_to_code.png)
```mermaid
flowchart LR
  I["Intent (what you want)"] --> S["Scope (where to look)"]
  S --> T["Trace (how it flows)"]
  T --> E["Evidence (proof links)"]
  E --> C["Code changes (safe + verified)"]
```

---

## The flagship skill: `sync-scopes` (the Truth Engine)

![Sync Scopes Engine](docs/assets/sync_scopes_engine.png)

`sync-scopes` is the core of the system. It’s a “Project Archivist” workflow that reads your codebase (tests/config/schema/impl) and generates or repairs `Scopes/` so it stays trustworthy.

What it enforces:

- **Observable reality only**: no guessing; missing proof becomes `[Unknown]`.
- **Evidence-backed claims**: important statements must link to code/tests/config with line ranges.
- **Drift repair**: treat existing `Scopes/` as potentially stale; fix what code changes made wrong.
- **Graph, not just tree**: keep `INDEX.md` and `GRAPH.md` as the canonical navigation surfaces.
- **Token-efficiency by design**: prefer the smallest scope slice needed to answer or implement.

Helper scripts included under `skills/sync-scopes/scripts/` (scope map, drift detection, evidence link generation, link checking).

---

## What you get in this repo

This repository is the **source package** for Scopes skills/agents you install into a coding assistant environment.

### Skills (commands)

- `sync-scopes` — generate/update `Scopes/` from code + git reality
- `ask-scopes` — answer “how/where/what depends on what” from `Scopes/` + evidence
- `plan-idea` — turn an idea into a scope-native implementation blueprint
- `write-tasks` — convert intent into engineer-ready tasks under `Scopes/Work/Tasks/**`
- `dev-verify` / `dev-tdd` — implement changes with verification gates (and update Scopes as part of the workflow)
- `plan-refactor` — plan safe green-to-green refactors with scope link maintenance
- `bug-hunt` — evidence-backed bug scanning → reports + tasks
- `write-adr` — record decisions under `Scopes/Decisions/ADRs/**`
- `research-loop` — separate internal repo truth from external web research
- `update-skills` — keep your installed skills fresh from upstream

### Agents (roles)

- `scope-navigator` — find the 1–3 relevant scopes fast (read-only)
- `scope-writer` — write/update Scopes using the canonical templates
- `scope-auditor` — detect drift + broken evidence links (read-only)
- `plan-researcher` — gather repo/scope/git context to support planning
- `tdd-runner` — run strict red→green→refactor implementation loops
- `bug-scanner` — hotspot scan + scope context (read-only)

---

## Getting started (recommended path)

### 1) Install the skills into your assistant

This repo is the source; your *project* is the target. Typical targets:

- Cursor: `.cursor/skills/`
- Claude: `.claude/skills/`
- Other setups: `.agent/skills/`

Copy or sync this repo’s `skills/` (and optionally `agents/`) into your target skills directory. Then keep them updated with `update-skills`.

Example (Cursor):
```bash
mkdir -p .cursor/skills
cp -R /path/to/ScopesCommands/skills/* .cursor/skills/
bash .cursor/skills/update-skills/scripts/update-skills.sh
```

### 2) Run `sync-scopes` in your project repo

Generate or repair `Scopes/` so the rest of the system has a trustworthy map to route through.

### 3) Use Scopes-first workflows day to day

Examples:

- “Where is the payment validation logic?” → `ask-scopes` / `scope-navigator`
- “Plan the new retry strategy” → `plan-idea` → `write-tasks`
- “Implement the change safely” → `dev-verify` or `dev-tdd`
- “Did docs drift?” → `scope-auditor`

---

## Why this reduces tokens (and increases correctness)

Scopes changes the retrieval unit from “files/folders” to “capabilities with evidence”.

You provide:
- **One intent** (“Login”, “Payments”, “Retry policy”)

Scopes provides:
- **One anchor document** (`Scopes/Product/...`)
- **One trace** (end-to-end flow table)
- **A handful of evidence links** (exact code/test/config lines)

That’s less context, higher signal, and dramatically less room for guessing.

---

## The promise

Scopes doesn’t make models smarter.

It makes them **better grounded**: they know what you mean, where to look, what changed, and what is proven—so they can help with real Day‑2 engineering work: refactors, bugs, plans, tasks, and decisions.

**Build better. Document automatically. Scope everything.**
