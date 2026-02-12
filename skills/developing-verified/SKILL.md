---
name: developing-verified
description: Implements features and fixes via terminal verification (run existing tests/scripts/REPL/curl) and updates Scopes. Does NOT write new test files; use developing-tdd for strict TDD.
model: inherit
---

# Developing (Verified)

You implement minimal changes and verify them by executing existing commands in a sandbox terminal.
Shared rules live in `skills/_shared/DEVELOPING_PROTOCOL.md`.

## When to use this skill
Use when the user wants implementation with verification, but does not require writing new tests first.

## Prerequisites
- A Scopes-enabled repo (a `Scopes/` directory), or permission to create/repair it via `syncing-scopes`.
- A runnable verification signal: tests, scripts, REPL, curl, or a documented manual checklist.

## Safety and confirmations
- Ask before destructive ops or expensive commands.
- Verify after every micro-step; stop if verification cannot be run.

## Mission Start
Load and follow the shared Scopes-first startup protocol at `skills/_shared/SCOPES_PROTOCOL.md`.
Also follow `skills/_shared/DEVELOPING_PROTOCOL.md` for the shared develop/verify/scope loop.

## Kickoff (Ask Next)
- "What behavior should change, and what terminal command should prove it worked?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Tasks/**`, `Scopes/Work/Bugs/**`
- **Downstream outputs**: session log (`Scopes/Work/DEV/**`), scope updates (`Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`)
- **Typical handoffs**: `scope-navigator` (find anchor scopes), `scope-writer` + `scope-auditor` (after verified)

## Agent Orchestration

Default: when changes affect multiple scopes/areas, use parallel in both phases — one `scope-navigator` per area in Phase 1, one `scope-writer` per scope/area and one `scope-auditor` (or one per area) in Phase 2. For narrow scope (1-3 scopes), use one navigator, then one writer + one auditor in parallel.

### Phase 1: Navigation (Parallel when multiple areas — before implementation)
**Spawn `scope-navigator`** (one per area when multiple areas; otherwise one):
> Find the 1-3 scopes relevant to: "{behavior to change}" in {area if multiple}. Include dependency edges and verification commands from DEVELOPER_INFO.md.

**Handle output:** The returned scope paths are your anchor scopes. Merge if multiple navigators. Read them to understand the current behavior before editing.

### Phase 2: Documentation (Parallel — after verification passes)
**Spawn `scope-writer`** (one per affected scope/area when multiple; otherwise one):
> Update the scopes affected by these changes: {list of changed files and behaviors}. Anchor scopes: {paths from Phase 1}.

**Spawn `scope-auditor`** (one per area when many scopes; otherwise one):
> Validate all scopes for drift and broken evidence links after the recent changes.

**Handle outputs:** If the auditor finds issues the writer missed, fix them before finishing.

### Optional Agents (invoke only when the stated condition applies)
- **`code-explorer`** — Before editing, if you need to trace existing behavior: "Trace how {behavior} works starting from {scope evidence links}."
- **`code-architect`** — Before editing, if the change is non-trivial: "Design implementation for {feature} given scopes {paths}."
- **`code-simplifier`** — After verification, if recent changes need cleanup: "Simplify the changes in {files} while preserving behavior."
- **`code-reviewer`** — After verification, for a confidence check: "Review the diff for bugs, security issues, and convention violations."

## When to Stop (Mandatory)
- Stop once the requested behavior is verified with an execution signal.
- Stop early when budgets are exceeded: 1-3 anchor scopes, 3-7 evidence links, 3-10 code files; mark gaps as `[Unknown]`.
- Stop and set `Verdict: Needs Narrowing` if "done" cannot be expressed as a checkable signal.

## Blocked Runbook (Mandatory)
- Missing/empty `Scopes/`: set `Verdict: Needs Sync` and recommend `syncing-scopes` first.
- No verification signal is runnable: record the exact command(s) you would run + blocker; set `Verdict: Blocked`.
- Missing test coverage discovered: set `Verdict: Proceed` but add `Next:` a follow-up task for `developing-tdd`.

## Output Contract

Return <= 25 lines:

```markdown
## VERIFIED RESULT
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of the change>
Evidence:
- `<command>` -> <PASS/FAIL signal>
- `[path:Lx-Ly](path#Lx-Ly)` — key code change (optional)
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. run full suite, update scopes, or open PR>
Artifact: <session log path, or (none)>
```
