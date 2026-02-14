# Slice Contract Protocol

This file defines the **Slice Contract** — the standardized handoff format used when delegating work to subagents or agent-team teammates.

Every skill that delegates work to a subagent or teammate MUST provide a Slice Contract. This eliminates redundant discovery, prevents coordination overhead, and gives each worker exactly the context it needs.

---

## Why Slice Contracts?

Without a contract, every subagent/teammate must:
1. Re-navigate `Scopes/INDEX.md` and `Scopes/GRAPH.md` from scratch
2. Discover the tech stack, test commands, and patterns on its own
3. Guess at ownership boundaries (what files it may/may not edit)

This wastes tokens, creates context duplication, and risks coordination failures. A Slice Contract solves all three.

---

## Slice Contract Format

```json
{
  "target": "<what to work on — scope path, file, behavior description>",
  "ownership": ["<files/paths this agent may edit — nothing else>"],
  "context": {
    "anchor_scope": "<path to the relevant Scopes/Product/** file>",
    "tech_stack_summary": "<2-3 lines from TECH_STACK.md relevant to this slice>",
    "test_command": "<exact verification command for this area>",
    "pattern_reference": "<path to an existing implementation to follow>",
    "likely_entrypoints": ["<file paths where this capability starts>"],
    "related_scopes": ["<paths to upstream/downstream scopes>"]
  },
  "acceptance": {
    "done_when": "<clear, checkable definition of done>",
    "guard_command": "<command to run after every edit to ensure behavior is preserved>",
    "artifact_required": "<what the agent MUST leave behind (file, JSON receipt, log entry)>"
  },
  "priority": "<high | medium | low>",
  "wip_slot": "<1 of N — which parallel slot this uses>"
}
```

---

## When to Use

| Scenario | Use Slice Contract? |
|---|---|
| Spawning a `scope-filler` for a new scope skeleton | Yes — include entrypoints + tech stack |
| Delegating to `code-simplifier` after implementation | Yes — include exact file list + guard command |
| Delegating to `code-reviewer` for final gate | Yes — include diff file list + anchor scope |
| Delegating to `bug-scanner` for diagnostics | Yes — include area + related scope paths |
| Agent-team teammates working in parallel | Yes — each teammate gets their own contract |
| Main agent doing inline work (no delegation) | No — contracts are for handoffs only |

---

## Rules

1. **Ownership is exclusive**: No two agents/teammates may have overlapping ownership paths. This prevents file conflicts.
2. **Context is pre-gathered**: The orchestrator/lead gathers context BEFORE spawning. Subagents should NOT need to navigate `INDEX.md` or `GRAPH.md`.
3. **Acceptance is checkable**: "Done" must be expressible as a terminal command result or file existence check.
4. **Artifacts are mandatory**: Every delegated task MUST produce a durable artifact. Summaries alone are insufficient.

---

## WIP Limits

| Task Type | Max Concurrent |
|---|---|
| Scope filling (`scope-filler`) | 6 teammates/subagents |
| Behavior implementation (TDD/Verified) | 4 slices |
| Code review | 3 reviewers (different focus areas) |
| Bug scanning | 3 scanners (different areas) |
| Planning/Research | No limit (read-only, no conflicts) |

---

## JSON Receipt Format (Agent Output)

Every subagent/teammate that receives a Slice Contract MUST return a JSON receipt alongside its human-friendly summary. The receipt enables automated orchestration decisions.

```json
{
  "slice_target": "<what was worked on>",
  "status": "complete | partial | blocked",
  "files_changed": ["<list of files actually modified>"],
  "evidence_count": 0,
  "unknowns": 0,
  "verdict": "Proceed | Blocked | Needs Sync | Needs Narrowing",
  "graph_edges_found": [
    {"from": "<scope>", "to": "<scope>", "relation": "<type>"}
  ],
  "follow_ups": ["<deferred work items>"],
  "guard_result": "PASS | FAIL | NOT_RUN"
}
```

The orchestrator reads the receipt to decide next steps:
- `status: complete` + `guard_result: PASS` → proceed to next phase
- `status: partial` → check `unknowns` and decide if acceptable
- `status: blocked` → surface to user with the follow_ups as suggested actions
