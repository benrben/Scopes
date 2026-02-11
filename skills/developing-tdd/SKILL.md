---
name: developing-tdd
description: Implements features and fixes via strict TDD (red/green/refactor) while updating Scopes docs and session logs. Use when the user asks for strict TDD or wants a failing test first.
---

# Developing (TDD)

You implement changes via strict RED -> GREEN -> REFACTOR, then keep `Scopes/` truthful.
Shared rules live in `skills/_shared/DEVELOPING_PROTOCOL.md`.

## When to use this skill
Use when the user wants strict TDD: failing test first, minimal fix, refactor, then scope maintenance.

## Prerequisites
- A Scopes-enabled repo (a `Scopes/` directory), or permission to create it via `syncing-scopes`.
- A runnable test suite, or permission to establish the smallest safe harness.

## Safety and confirmations
- Ask before destructive ops or expensive commands.
- Keep changes small and continuously verifiable; stop if the test harness is blocked.

## Mission Start
Load and follow the shared Scopes-first startup protocol at `skills/_shared/SCOPES_PROTOCOL.md`.
Also follow `skills/_shared/DEVELOPING_PROTOCOL.md` for the shared develop/verify/scope loop.

## Kickoff (Ask Next)
- "What behavior should we change, and what should the failing test assert?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Tasks/**`, `Scopes/Work/Bugs/**`
- **Downstream outputs**: session log (`Scopes/Work/STDD/**`), scope updates (`Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`)
- **Typical handoffs**: `scope-navigator` (find anchor scopes), `scope-writer` + `scope-auditor` (after verified)

## Agent Orchestration (Guidance)

Need scores are intentionally not uniform; only invoke what you need.

| Agent | How it uses it | Need (1-10) |
|---|---|---:|
| `scope-navigator` | Find 1-3 anchor scopes + deps | 10 |
| `code-explorer` | Trace existing behavior/tests before writing RED | 7 |
| `code-architect` | Blueprint when non-trivial | 6 |
| `code-simplifier` | Behavior-preserving cleanup after GREEN | 6 |
| `code-reviewer` | High-confidence issues after changes | 6 |
| `scope-writer` | Update affected `Scopes/**` with evidence | 8 |
| `scope-auditor` | Validate drift/broken links after scope edits | 8 |

## If the Repo Has No Tests (Phase 0: Establish a Harness)
If there is no test suite yet, create the smallest safe characterization harness before feature work:
1. Look for existing verification (`Scopes/DEVELOPER_INFO.md`, CI configs, `Makefile`, `package.json`, `pyproject.toml`, `go.mod`). If none, record `[Unknown]`.
2. Choose the most native runner for the repo (do not introduce a second framework if one exists).
3. Write one characterization test at a boundary (HTTP handler, CLI command, pure function).
4. Run it and record the command as the baseline RED/GREEN signal.
5. Update `Scopes/DEVELOPER_INFO.md` with the command you ran.

If you cannot establish any repeatable harness safely, stop and recommend `developing-verified` plus a follow-up task to add tests.

## When to Stop (Mandatory)
- Stop after the requested behaviors are complete and tests are green.
- Stop early when budgets are exceeded: 1-3 anchor scopes, 3-7 evidence links, 3-10 code files; mark gaps as `[Unknown]`.
- Stop and set `Verdict: Needs Narrowing` if the behavior cannot be stated as a testable assertion.

## Blocked Runbook (Mandatory)
- Missing/empty `Scopes/`: set `Verdict: Needs Sync` and recommend `syncing-scopes` first.
- Tests will not run: record the exact blocker + command tried; set `Verdict: Blocked`; propose the smallest environment fix.
- No tests exist: run Phase 0 harness; if blocked, switch to `developing-verified` and create a task to add tests.

## Output Contract

Return <= 25 lines:

```markdown
## TDD RESULT
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of the change>
Evidence:
- `[path:Lx-Ly](path#Lx-Ly)` — failing test (RED)
- `[path:Lx-Ly](path#Lx-Ly)` — fix (GREEN)
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. run full suite, update scopes, or open PR>
Artifact: <session log path, or (none)>
```
