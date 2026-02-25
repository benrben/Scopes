# Developing Protocol (Shared)

This file contains shared rules for the `developing-*` skills (`developing-tdd`, `developing-verified`).
Both skills use the same micro-swarm loop, differing only in how the "RED" phase works:

- **TDD mode**: WRITE a failing test (new test)
- **Verified mode**: FIND an existing verification signal (existing test/script/REPL/curl)

Everything else — slicing, GREEN, REFACTOR, artifacts, final gate — is identical.

---

## Shared Defaults (Budgets)

Unless the user explicitly requests broader scanning:
- 1-3 anchor scopes
- 3-7 evidence links
- 3-10 code files
- Stop and label gaps as `[Unknown]`

## Micro-Swarm Loop (Shared Shape)

Every behavior slice follows the same 3-Amigos micro-swarm:

1. **Slice Contract**: define one behavior with 2-5 acceptance examples, anchor scope, verification command, and pattern reference.
2. **RED** (mode-specific):
   - TDD: write failing test(s) for the acceptance examples
   - Verified: identify existing verification signal (test suite, script, curl, REPL, build)
3. **GREEN**: implement minimal code so verification passes.
4. **REFACTOR** (required):
   - ALWAYS spawn `code-simplifier` (subagent with Slice Contract) for each slice
5. **ARTIFACT** (mandatory, every slice):
   - Append to session log: decision, tradeoffs, follow-ups, files changed
6. **Repeat** for next slice (WIP limit: max 4 active slices)

## Pattern Conformance (Mandatory)

Before writing production code:
- Use `Scopes/DEVELOPER_INFO.md` and the anchor scope's traces/evidence to find 2-3 similar implementations.
- Follow the repo's existing pattern; do not introduce a second approach.
- If no pattern exists, propose one explicitly and document it (with evidence) after verification.

## Final Gate (Always Runs)

After ALL slices complete:
1. Run full test suite / full verification command
2. Spawn `code-reviewer` (subagent with Slice Contract):
   - Review only files from the session's slices
   - Confidence ≥ 80 filter
   - Must report Scopes impact
3. Fix high-severity findings before completing

## Scope Maintenance (Conditional, Not Always)

Scope maintenance is triggered **conditionally**, not unconditionally:

```bash
git diff --name-only | xargs -I{} rg -l "{}" Scopes/Product/ 2>/dev/null
```

- **IF output is non-empty** (scope-linked files were changed): update affected scopes + run `scopes validate` as the gate
- **IF output is empty**: skip scope update entirely — not every code change needs a scope update
- **IF behavior changed** (not just internal refactor): always update, even if the grep is empty

After scope edits, validate:
- `scopes validate --all`

## Artifact Persistence (Mandatory)

Every developing session MUST leave:
1. **Session log**: `Scopes/Work/STDD/<slug>.md` (TDD) or `Scopes/Work/DEV/<slug>.md` (Verified)
   - Per-slice entries: decision, tradeoffs, follow-ups, files changed
   - Parking lot: deferred items that don't belong in this session
2. **Parking lot → task files**: any deferred items become task files in `Scopes/Work/Tasks/`
3. **Context summary**: if session was tool-heavy (>10 tool calls), invoke `context-summarizer`

These artifacts enable session resumption and prevent context loss between conversations.

## Deterministic Triggers (Replace Judgment Calls)

| Trigger | Threshold | Action |
|---|---|---|
| `code-simplifier` | ALWAYS after each slice GREEN | Spawn as subagent with Slice Contract |
| `code-reviewer` | ALWAYS after all slices | Spawn as subagent |
| Scope update | scope-linked files in git diff | Update affected scopes |
| `context-summarizer` | > 10 tool calls in session | Spawn to write durable note |

## Evidence Discipline

- Do not claim things you did not observe.
- Missing proof becomes `[Unknown]`.
- Evidence link format: `[path:Lx-Ly](path#Lx-Ly)`
