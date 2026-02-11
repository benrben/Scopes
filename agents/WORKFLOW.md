# Agent Workflow — Parallel Development Pattern

Based on [Zach Wills' three core principles](https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/):

1. **Parallel Execution for Speed** — run independent agents concurrently
2. **Sequential Handoffs for Automation** — output of one feeds the next
3. **Context Isolation for Quality** — each agent gets its own dedicated context

---

## Agent Roster

| Agent | Role | Phase | Writes Code? | Background? |
|---|---|---|---|---|
| `scope-navigator` | Find relevant scopes | Planning | No | No |
| `plan-researcher` | Research codebase & constraints | Planning | No | Yes |
| `bug-scanner` | Scan hotspots & security | Investigation | No | No |
| `tdd-runner` | Implement features via TDD | Implementation | **Yes** | No |
| `code-reviewer` | Review & approve/reject code | Review | No (readonly) | No |
| `scope-writer` | Update Scopes documentation | Documentation | Docs only | No |
| `scope-auditor` | Validate Scopes accuracy | Validation | No (readonly) | Yes |

---

## Core Principle: Why Subagents?

Subagents are NOT primarily about parallelism — they are about **context isolation**.

Each agent runs in its own context window. Verbose work (reading 20 files,
running test suites, scanning for patterns) stays contained. The main
conversation only receives structured summaries, keeping it sharp and focused.

Parallelism is a bonus: when agents are independent, run them concurrently.
When they depend on each other, chain them sequentially.

---

## Workflows

### 1. New Feature Implementation

```
┌─────────── PHASE 1: PLANNING (parallel) ───────────┐
│                                                      │
│  scope-navigator ─┐                                  │
│                    ├──→ Main agent reads both briefs  │
│  plan-researcher ──┘    and plans the approach        │
│  (background)                                        │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── PHASE 2: IMPLEMENTATION (sequential) ────┐
│                                                      │
│  tdd-runner ──→ code-reviewer ──┐                    │
│       ▲                         │                    │
│       │    NEEDS REVISION       │                    │
│       └─────────────────────────┘                    │
│                                                      │
│       If APPROVED → proceed to Phase 3               │
│       Max 3 iterations, then escalate to human       │
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

**Phase 1 — Planning (parallel):**
Run `scope-navigator` and `plan-researcher` concurrently. Navigator returns
relevant scope paths + dependencies. Researcher writes a full brief to
`Scopes/Work/Planning/`. Main agent reads both summaries to plan the approach.

**Phase 2 — Implementation (sequential with feedback loop):**
`tdd-runner` implements the feature using TDD (Red-Green-Refactor) in its own
context. When done, `code-reviewer` reviews in a separate context. If NEEDS
REVISION, the main agent feeds the review back to `tdd-runner` (resumed). Loop
until APPROVED or 3 iterations (then human decides).

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
┌─────────── PHASE 2: FIX (sequential loop) ──────────┐
│                                                      │
│  tdd-runner ──→ code-reviewer ──→ APPROVED           │
│       ▲              │                               │
│       └── REVISION ──┘                               │
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
┌─────────── PARALLEL RESEARCH ───────────────────────┐
│                                                      │
│  scope-navigator ─┐                                  │
│                    ├──→ Main agent makes decisions    │
│  plan-researcher ──┘                                 │
│  (writes to Scopes/Work/Planning/)                   │
└──────────────────────────────────────────────────────┘
```

Fire both agents. Navigator returns quickly with scope paths. Researcher
runs in the background and writes a full brief to disk. Main agent reads
the brief when ready and makes planning decisions.

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
┌─────────── ALL THREE IN PARALLEL ───────────────────┐
│                                                      │
│  tdd-runner (run tests only, readonly mode)          │
│  code-reviewer                                       │
│  scope-auditor                                       │
│                                                      │
│  All three return verdicts → merge decision          │
└──────────────────────────────────────────────────────┘
```

For pre-merge, `tdd-runner` can be invoked in a readonly context (just run
tests, don't implement). All three agents are independent and can run in
parallel. If all return clean verdicts, merge.

---

## Handoff Principles

1. **Parallel when independent, sequential when dependent.** Planning agents
   have no dependencies on each other — run them concurrently. Implementation
   and review depend on each other — chain them sequentially.

2. **Context isolation preserves quality.** Each agent gets its own full context
   window. The `tdd-runner` can read 20 files and run test suites without
   bloating the main conversation. Only the structured summary returns.

3. **Structured output enables automation.** Every agent returns a parseable
   report with a clear **Verdict**. The main agent reads the verdict to decide
   the next step (proceed, loop back, or escalate).

4. **File-as-memory for handoff artifacts.** `plan-researcher` writes to
   `Scopes/Work/Planning/`, `bug-scanner` writes to `Scopes/Work/Bugs/`.
   These persist across sessions and can be read by any agent.

5. **The feedback loop has a circuit breaker.** The `tdd-runner → code-reviewer`
   loop runs at most 3 iterations. After that, escalate to human review to
   prevent infinite loops and token burn.

6. **Chain, don't nest.** Agents cannot spawn other agents. The main agent
   orchestrates by reading one agent's output and invoking the next.

---

## Orchestration Pattern (for the main agent)

When implementing a feature, the main agent follows this script:

```
1. Fire scope-navigator + plan-researcher in parallel
2. Read both summaries
3. Invoke tdd-runner with the task + scope context
4. Read tdd-runner's summary
5. Invoke code-reviewer with the changed files
6. Read the verdict:
   - APPROVED → go to step 7
   - NEEDS REVISION → resume tdd-runner with review feedback → go to step 5
   - 3 iterations exceeded → ask human
7. Invoke scope-writer + scope-auditor in parallel
8. Done
```

This is the automated engineering lifecycle: plan → implement → review →
iterate → document → validate.
