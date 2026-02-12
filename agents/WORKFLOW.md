# Agent Workflow — Parallel Development Pattern

> **Skills embed their own Agent Orchestration** with concrete prompts, parallel
> groupings, and output-handling instructions. This document is the architectural
> reference for the agent system. See individual `skills/*/SKILL.md` files for
> the executable orchestration steps that implement these patterns.

Based on [Zach Wills' three core principles](https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/):

1. **Parallel Execution for Speed** — run independent agents concurrently
2. **Sequential Handoffs for Automation** — output of one feeds the next
3. **Context Isolation for Quality** — each agent gets its own dedicated context

---

## Agent Roster

| Agent | Role | Phase | Writes Code? | Background? |
|---|---|---|---|---|
| `scope-navigator` | Find relevant scopes | Planning | No | No |
| `bug-scanner` | Scan hotspots & security | Investigation | No | No |
| `code-architect` | Produce architecture blueprint | Planning | No | No |
| `code-explorer` | Trace feature implementations | Investigation | No | No |
| `code-reviewer` | Review changes (high-confidence) | Review | No | No |
| `code-simplifier` | Simplify recent changes | Refinement | Yes | No |
| `scope-writer` | Update Scopes documentation | Documentation | Docs only | No |
| `scope-auditor` | Validate Scopes accuracy | Validation | No (readonly) | Yes |
| `context-summarizer` | Stabilize working set | Support | Docs only | No |

---

## Core Principle: Why Subagents?

Subagents are NOT primarily about parallelism — they are about **context isolation**.

Each agent runs in its own context window. Verbose work (reading 20 files,
running test suites, scanning for patterns) stays contained. The main
conversation only receives structured summaries, keeping it sharp and focused.

Parallelism is a bonus: when agents are independent, run them concurrently.
When they depend on each other, chain them sequentially.

---

## When to Delegate vs Keep in Lead

| Situation | Use a subagent? | Recommended agent(s) |
|---|---|---|
| Need 1-3 scope entry points fast | Yes | `scope-navigator` |
| Need deep end-to-end trace | Yes | `code-explorer` |
| Need decisive architecture + file plan | Yes | `code-architect` |
| Need mechanical hotspot scan | Yes | `bug-scanner` |
| Need behavior-preserving cleanup | Yes | `code-simplifier` |
| Need drift/link validation | Yes | `scope-auditor` |
| Tool-heavy phase just finished; need stable summary | Yes | `context-summarizer` |
| Tight edit -> verify -> edit loop | No | main agent |
| Needs user choice / product decision | No | main agent |

## Summarization Checkpoint (Mandatory Pattern)

After any tool-heavy phase or multi-agent burst, stabilize the working set:
- Goals
- Constraints
- Current plan
- Key findings (with evidence)
- Unknowns (use `[Unknown]`)
- Next action

If the summary would be long, invoke `context-summarizer` to write a durable note to `Scopes/Work/Notes/**` and return only a pointer.

---

## Workflows

### 1. New Feature Implementation

```
┌─────────── PHASE 1: PLANNING ───────────────────────┐
│                                                      │
│  scope-navigator ──→ code-architect ──→ blueprint     │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2: IMPLEMENTATION ─────────────────┐
│                                                      │
│  Main agent implements + verifies in terminal         │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2.5: SIMPLIFY (optional) ──────────┐
│                                                      │
│  code-simplifier ──→ behavior-preserving refactor     │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2.75: REVIEW (optional) ───────────┐
│                                                      │
│  code-reviewer ──→ high-confidence issues only        │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 3: DOCUMENTATION (parallel) ───────┐
│                                                      │
│  scope-writer ───┐                                   │
│                   ├──→ Scopes updated & validated     │
│  scope-auditor ──┘                                   │
│  (background)                                        │
└──────────────────────────────────────────────────────┘
```

**Phase 1 — Planning:**
Run `scope-navigator` to locate relevant Scopes and dependency context, then
invoke `code-architect` to produce the architecture blueprint.

**Phase 3 — Documentation (parallel):**
Run `scope-writer` and `scope-auditor` concurrently. Writer updates affected
scope docs. Auditor validates all scopes are still accurate.

---

### 2. Bug Investigation & Fix

```
┌─────────── PHASE 1: INVESTIGATION (parallel) ───────┐
│                                                       │
│  bug-scanner ─────┐                                   │
│                    ├──→ Main agent reviews both        │
│  scope-navigator ─┘    and diagnoses the issue        │
│                                                       │
└───────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2: FIX ────────────────────────────┐
│                                                      │
│  Main agent implements + verifies in terminal         │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2.5: SIMPLIFY (optional) ──────────┐
│                                                      │
│  code-simplifier ──→ behavior-preserving refactor     │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2.75: REVIEW (optional) ───────────┐
│                                                      │
│  code-reviewer ──→ high-confidence issues only        │
│                                                      │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 3: CLEANUP (parallel) ─────────────┐
│                                                      │
│  scope-writer + scope-auditor (if scopes affected)   │
└──────────────────────────────────────────────────────┘
```

---

### 3. Planning / Research Only

```
┌─────────── RESEARCH ─────────────────────────────────┐
│                                                      │
│  scope-navigator ──→ Main agent makes decisions       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

Fire `scope-navigator`. It returns quickly with scope paths. The main agent
does any deeper reading directly as needed.

---

### 3.5. Feature Deep Dive (Understanding)

Use when you need to understand an existing feature deeply before changing it:
`scope-navigator` → `code-explorer` → main agent synthesizes.

---

### 4. Scope Maintenance

```
scope-auditor (background) → scope-navigator → scope-writer → scope-auditor
```

Auditor finds stale scopes. Navigator maps affected areas. Writer updates
the drifted scopes. Auditor re-validates.

---

### 5. Pre-Merge Validation (parallel)

```
┌─────────── VALIDATION ──────────────────────────────┐
│                                                      │
│  scope-auditor                                       │
│                                                      │
│  Returns verdict → merge decision                     │
└──────────────────────────────────────────────────────┘
```

For pre-merge, run `scope-auditor` to ensure Scopes evidence links and drift
checks are clean before merging.

---

## Handoff Principles

1. **Parallel when independent, sequential when dependent.** If you have both
   documentation updates and validation, run `scope-writer` and `scope-auditor`
   in parallel.

2. **Context isolation preserves quality.** Each agent gets its own full context
   window. Verbose scanning and validation stays contained; only structured
   summaries return.

3. **Structured output enables automation.** Every agent returns a parseable
   report with a clear **Verdict**. The main agent reads the verdict to decide
   the next step (proceed, loop back, or escalate).

4. **File-as-memory for handoff artifacts.** `bug-scanner` writes to
   `Scopes/Work/Bugs/`.
   These persist across sessions and can be read by any agent.

5. **Chain, don't nest.** Agents cannot spawn other agents. The main agent
   orchestrates by reading one agent's output and invoking the next.

---

## Orchestration Pattern (for the main agent)

When implementing a feature, the main agent follows this script:

```
1. Fire scope-navigator
2. Read its summary and open the referenced scopes/evidence
3. (Optional) Invoke code-explorer for a deep feature trace
4. (Optional) Invoke code-architect for a full blueprint
5. Implement the change and verify in terminal
6. (Optional) Invoke code-simplifier on the changed files
7. (Optional) Invoke code-reviewer on the diff (confidence ≥ 80 only)
8. Invoke scope-writer + scope-auditor in parallel (if Scopes are affected)
9. Done
```

This is the engineering lifecycle: plan → implement → document → validate.
