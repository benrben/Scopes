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

```mermaid
flowchart TD
    Task["New Request / Task"] --> Q1{"Is it tool-heavy or mechanical scan?"}
    Q1 -- Yes --> Subagent["Delegate to narrow Subagent (e.g., bug-scanner)"]
    Subagent --> Limit{"Output close to line limit?"}
    Limit -- Yes --> Artifact["Write context to Artifact file"]
    Artifact --> Lead1["Return Verdict + Pointer to Lead Thread"]
    Limit -- No --> Lead2["Return Verdict + Summary to Lead Thread"]
    
    Q1 -- No --> Lead["Keep in Lead Thread"]
    Lead --> Synthesis["Synthesize and Edit Code"]
```

**Delegate to a subagent when:**
- You need to scan many files or run multiple commands.
- You need a narrow output (paths, counts, top-N) instead of full explanation.
- The work is mechanical (grep/rg patterns, link checking, drift checks).

**Keep work in the lead thread when:**
- The work is linear and requires tight iteration (edit -> verify -> edit).
- The output must be high-context synthesis that depends on user feedback.

## Parallelization Guidelines

**Mandatory parallel delegation** applies to ALL skill types when 2+ independent work units exist — not just development/sync skills. This includes:
- Evidence-gathering lanes in planning/brainstorming (scope routing, web research, precedent scan)
- Per-scope investigation in querying (each scope gets its own subagent)
- Per-option research in decision-making (each option gets its own researcher)
- Per-module hotspot analysis in scanning (each module gets its own scanner)
- Per-file task generation in writing-tasks

Parallelize subagents when they do not depend on each other:
- `bug-scanner` + `code-reviewer` (independent scan + review)
- Evidence Lane A + Lane B + Lane D (independent research channels)
- Per-scope investigators (each reads a different scope)

Sequence subagents when outputs depend on each other:
- `bug-scanner` -> main agent diagnosis (when scan results drive next steps)
- Context lanes merge -> blueprint writing (needs all lane receipts)

## Upstream Artifact Intake

Before any skill runs `scope_map.py` or reads `INDEX.md`, it must check for upstream artifacts. The chain `brainstorm → plan → tasks → develop` should never re-discover what a prior skill already found. See `skills/_shared/SCOPES_PROTOCOL.md` — Upstream Artifact Intake.

## Summarization Checkpoint Pattern

After any tool-heavy phase (or any multi-subagent burst), the lead thread should stabilize:
- Goals
- Constraints
- Current plan
- Key findings (with evidence)
- Unknowns (with `[Unknown]`)
- Next action

### Standard Artifact Roots (by type)

If an agent is about to exceed its output limit, it must write an artifact here and return only a pointer.

| Artifact Type | Path | Purpose |
|---|---|---|
| Bugs | `Scopes/Work/Bugs/**` | Hotspot analysis, bug scans, crash reports. |
| Notes | `Scopes/Work/Notes/**` | Temporary session notes, context summarization. |
| Plans | `Scopes/Work/Planning/**` | System architecture, feature refactoring plans. |
| Tasks | `Scopes/Work/Tasks/**` | Engineer-ready actionable steps to implement. |
| Research | `Scopes/Research/**` | Tech choices, comparisons (ADRs). |
