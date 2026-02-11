## Context Engineering (Skills + Subagents)

This repo is optimized for token-efficiency and correctness by making context control *structural*:
- Skills provide stable, repeatable workflows (static constraints).
- Subagents provide context isolation (dynamic constraints).

## Skills vs Subagents

- **Skills**: The main workflow contract. They define stop conditions, budgets, outputs, and handoffs.
- **Subagents**: Narrow, stateless roles used as a firebreak for tool-heavy exploration. They must return results, not history.

## "Return Results, Not History" Schema

Subagent returned summaries must fit their line limit and include:
- `Verdict:` `Proceed` | `Blocked` | `Needs Sync` | `Needs Narrowing`
- `Decision:` what was found/decided in 1-2 sentences
- `Evidence:` file refs / links (or `[Unknown]`)
- `Unknowns:` only if blocked/partial
- `Next:` one recommended next action
- `Artifact:` path or `(none)`

If the summary would be long, offload details to an artifact file and return only pointer + abstract + mini ToC.

## Delegation Heuristics

Delegate to a subagent when:
- You need to scan many files or run multiple commands.
- You need a narrow output (paths, counts, top-N) instead of full explanation.
- The work is mechanical (grep/rg patterns, link checking, drift checks).

Keep work in the lead thread when:
- The work is linear and requires tight iteration (edit -> verify -> edit).
- The output must be high-context synthesis that depends on user feedback.

## Parallelization Guidelines

Parallelize subagents when they do not depend on each other:
- `scope-navigator` + `bug-scanner`
- `scope-writer` + `scope-auditor`

Sequence subagents when outputs depend on each other:
- `scope-navigator` -> `code-explorer` -> `code-architect`

## Summarization Checkpoint Pattern

After any tool-heavy phase (or any multi-subagent burst), the lead thread should stabilize:
- Goals
- Constraints
- Current plan
- Key findings (with evidence)
- Unknowns (with `[Unknown]`)
- Next action

## Artifact Offloading Policy

Standard artifact roots:
- `Scopes/Work/Bugs/**`
- `Scopes/Work/Notes/**`
- `Scopes/Work/Planning/**`
- `Scopes/Work/Tasks/**`
- `Scopes/Research/**`

If an agent is about to exceed its output limit, it must write an artifact and return only a pointer.
