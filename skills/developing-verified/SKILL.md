---
name: developing-verified
description: Implements features and fixes via terminal verification (run existing tests/scripts/REPL/curl) and updates Scopes. Does NOT write new test files; use developing-tdd for strict TDD.
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

## Agent Orchestration (Guidance)

| Agent | How it uses it | Need (1-10) |
|---|---|---:|
| `scope-navigator` | Find 1-3 anchor scopes + deps | 10 |
| `code-explorer` | Trace existing behavior/patterns before editing | 7 |
| `code-architect` | Blueprint when non-trivial | 6 |
| `code-simplifier` | Behavior-preserving cleanup after verification | 6 |
| `code-reviewer` | High-confidence issues after changes | 6 |
| `scope-writer` | Update affected `Scopes/**` with evidence | 8 |
| `scope-auditor` | Validate drift/broken links after scope edits | 8 |

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
