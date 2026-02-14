# Agent Workflow — Micro-Swarm Orchestration Pattern

> **Skills embed their own Agent Orchestration** with concrete prompts, parallel
> groupings, and output-handling instructions. This document is the architectural
> reference for the agent system. See individual `skills/*/SKILL.md` files for
> the executable orchestration steps that implement these patterns.

Based on three orchestration primitives:

1. **Skills** = reusable SOPs (the `SKILL.md` files — what to do)
2. **Subagents** = focused contractors with context isolation (the `agents/*.md` files — who does it)
3. **Agent Teams** = multiple Claude Code sessions coordinating via shared tasks + messaging (for heavy parallel work)

And four hard constraints:

1. **Coordination overhead is real** → minimize handoffs; use Slice Contracts to give each worker everything upfront
2. **Context must be decomposed hard** → each subagent/teammate gets a tiny, self-contained slice
3. **Agent teams are experimental** → enforce ownership (one slice = one agent), no cross-agent file edits
4. **Long-running work needs artifacts** → every cycle MUST leave a structured artifact, not just a summary

---

## Agent Roster

| Agent | Role | Phase | Writes Code? | Background? |
|---|---|---|---|---|
| `bug-scanner` | Scan hotspots & security | Investigation | No | No |
| `code-reviewer` | Review changes (high-confidence) | Review (Final Gate) | No | No |
| `code-simplifier` | Simplify recent changes | Refinement | Yes | No |
| `context-summarizer` | Stabilize working set | Support | Docs only | No |
| `scope-filler` | Fill new scope skeletons | Scope maintenance | Scopes only | No |

---

## Core Principle: Context Isolation + Slice Contracts

Subagents and teammates are about **context isolation**: verbose work (reading 20 files, running test suites, scanning patterns) stays contained. The orchestrator only receives structured JSON receipts.

**Every delegation MUST use a Slice Contract** (see `skills/_shared/SLICE_CONTRACT.md`):
- **Target**: what to work on
- **Ownership**: files this agent may edit (exclusive — no overlaps)
- **Context bundle**: pre-gathered info so the agent doesn't re-discover
- **Acceptance**: checkable definition of done + guard command
- **Artifact required**: what the agent MUST leave behind

---

## When to Use Subagents vs Agent Teams vs Lead-Only

⚠️ **Spawn ALL subagents in a SINGLE tool-call batch** for parallelism. Spawning one per turn makes them sequential.

| Situation | Approach | Why |
|---|---|---|
| 1 scope fill | **Subagent** (single) | Low overhead |
| 2+ scope fills | **Agent Team** (Preferred) | Guaranteed parallelism |
| Feature Implementation (TDD/Verified) | **Subagents** (parallel batches) | Lead orchestrates, agents do the work |
| Simple/Tiny edit (< 5 mins) | **Lead only** | Subagent overhead exceeds benefit |
| Multi-aspect review (security + perf + coverage) | **Agent Team** (3 reviewers) | Each reviewer is independent, can share findings |
| Bug investigation with competing hypotheses | **Agent Team** (investigators) | Can debate and disprove each other |
| Needs user choice / product decision | **Lead only** | Decisions can't be delegated |
| code-simplifier after implementation | **Subagent** (single) | One focused task, clear ownership |
| code-reviewer as final gate | **Subagent** (single) | One focused task, clear verdict |
| Need stable summary after tool-heavy work | **Subagent** (`context-summarizer`) | Context compression |

---

## Agent Teams — When and How

Agent teams coordinate multiple Claude Code sessions with shared tasks and messaging.

### Enable

Set in your `settings.json`:
```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

### Spawn Patterns

**Scope filling (4+ scopes):**
> Create an agent team with {N} teammates. Each teammate fills one scope file.
> Assign each teammate a scope from this list: {scope_list}.
> Each teammate reads their Slice Contract from `{contract_file}`.
> Use Sonnet for each teammate.

**Parallel code review:**
> Create an agent team with 3 reviewers:
> - One focused on security (token handling, input validation, secrets)
> - One on performance (N+1 queries, unnecessary allocations, blocking calls)
> - One on test coverage (missing edge cases, brittle assertions)
> Each reviewer reads the diff: `git diff {base}..HEAD`
> Report findings with confidence ≥ 80%.

**Bug investigation:**
> Spawn {N} teammates to investigate different hypotheses for: {bug_description}.
> Have them talk to each other to disprove each other's theories.
> Update `Scopes/Work/Bugs/{slug}.md` with consensus.

### Rules

1. **WIP limits**: max 6 teammates for scope filling, max 3 for reviews, max 4 for implementation slices
2. **Exclusive ownership**: each teammate owns specific files — no overlapping edits
3. **Slice Contracts**: every teammate gets a pre-built contract (from `slice_contract_builder.py` or manually)
4. **Wait for completion**: always tell the lead to wait for teammates before proceeding
5. **Clean up**: always clean up the team when done: `Clean up the team`
6. **No nested teams**: teammates cannot spawn their own teams

### Quality Gates (Hooks)

Use `TeammateIdle` and `TaskCompleted` hooks to enforce standards:
- `TeammateIdle`: check if the teammate actually wrote a JSON receipt → if not, send feedback
- `TaskCompleted`: run `drift_detector.py --scope {target}` → if stale, prevent completion

---

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

### 1. New Feature Implementation (Micro-Swarm per Behavior)

```
┌─────────── STEP 1: SLICE (Lead only) ─────────────────┐
│                                                        │
│  scope_map.py --query "<goal>" → anchor scope(s)       │
│  Break goal into independent behavior slices           │
│  Each slice = { behavior, inputs, outputs,             │
│                 acceptance examples, test command }     │
│  WIP LIMIT: max 4 active slices                        │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 2: PARALLEL PHASE-GATED TDD ──────────┐
│                                                        │
│  Lead acts as ORCHESTRATOR (runs tests/gates only)     │
│                                                        │
│  For each phase (RED → GREEN → REFACTOR):              │
│  1. Spawn parallel subagents (one per slice)           │
│     "Spawn ALL in a SINGLE tool-call batch"            │
│  2. Agents do the work (write test / impl / refactor)  │
│  3. Wait for all to complete                           │
│  4. GATE: Orchestrator runs full test suite            │
│     IF pass → next phase                               │
│     IF fail → route back to agent                      │
│                                                        │
│  Refactor ALWAYS runs via `code-simplifier`            │
│  (one per slice, in parallel).                         │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 3: FINAL GATE (always) ───────────────┐
│                                                        │
│  Spawn code-reviewer on complete diff (subagent)       │
│  Confidence ≥ 80 filter. Must report Scopes impact.    │
│  IF issues found → fix cycle (lead)                    │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 4: SCOPE SYNC (conditional) ──────────┐
│                                                        │
│  IF scope-linked files in git diff:                    │
│  └── Update affected scope(s) + drift_detector.py     │
│  ELSE: skip scope update                               │
│                                                        │
│  Leave durable artifacts:                              │
│  - Session log in Scopes/Work/STDD/ or DEV/           │
│  - Parking lot → task files                            │
│  - context-summarizer if session was large              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Step 2 details:**
- Each slice exits as **green + simplified** before the next starts (no queues)
- Refactor is "now" not "later"
- `code-simplifier` gets a tight Slice Contract: exact file list + guard command
- The session log entry is mandatory, not optional

---

### 2. Bug Investigation & Fix

```
┌─────────── STEP 1: INVESTIGATE (parallel) ────────────┐
│                                                        │
│  IF simple (one area):                                 │
│    Spawn bug-scanner (subagent)                        │
│                                                        │
│  IF complex (multiple hypotheses):                     │
│    Spawn Agent Team with 2-4 investigators             │
│    Each investigates a different hypothesis             │
│    They message each other to debate/disprove          │
│    Converge on consensus → write findings artifact     │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 2: FIX (lead, micro-swarm loop) ──────┐
│                                                        │
│  Same RED → GREEN → REFACTOR micro-swarm as features   │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 3: FINAL GATE + ARTIFACTS ────────────┐
│                                                        │
│  code-reviewer (subagent) + conditional scope sync     │
│  Write bug report to Scopes/Work/Bugs/                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 3. Scope Maintenance (Discovery Micro-Swarm)

```
┌─────────── STEP 1: DISCOVER (lead only) ──────────────┐
│                                                        │
│  IF Scopes/ is empty/missing:                          │
│    Infer areas from repo structure                      │
│    Build Slice Contracts: slice_contract_builder.py    │
│    Bootstrap META files first (DEVELOPER_INFO, etc.)   │
│  ELSE:                                                 │
│    drift_detector.py --all --format json               │
│    Build Slice Contracts from drift output              │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 2: FILL (Parallel, WIP ≤ 6) ──────────┐
│                                                        │
│  1 scope:    Subagent                                  │
│  2+ scopes:  Agent Team (Preferred)                    │
│  Fallback:   Parallel Subagents (ALL in one batch)     │
│                                                        │
│  Each filler gets a full Slice Contract:               │
│  - Scope path + likely entrypoints + tech stack        │
│  - Test command + related scopes                       │
│  - Must return JSON receipt                            │
│                                                        │
│  All workers run simultaneously → receipts feed S3     │
│                                                        │
└────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────── STEP 3: STITCH (lead, incremental) ────────┐
│                                                        │
│  Read JSON receipts from all fillers                   │
│  Update INDEX.md with new scope references             │
│  Update GRAPH.md from graph_edges_found                │
│  Run drift_detector.py as final validation gate        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 4. Planning / Research (Artifact-First)

```
┌─────────── SINGLE PASS: BLUEPRINT ────────────────────┐
│                                                        │
│  scope_map.py --query → anchor scopes (instant route)  │
│  rg for prior plans + research (parallel)              │
│  Write plan directly to Scopes/Work/Planning/          │
│  Plan's ## Links section IS the handoff for next skill │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 5. Pre-Merge Validation (Parallel Review Team)

```
┌─────────── AGENT TEAM: 3 REVIEWERS ──────────────────┐
│                                                       │
│  Reviewer 1: Security focus                           │
│  Reviewer 2: Performance focus                        │
│  Reviewer 3: Test coverage focus                      │
│                                                       │
│  Each reads `git diff` independently                  │
│  Confidence ≥ 80 filter                               │
│  Merge verdicts → go/no-go                            │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## Handoff Principles

1. **Slice Contracts for every delegation.** No naked prompts — always include target, ownership, context, acceptance, and artifact requirements.

2. **Micro-swarms, not assembly lines.** Each slice exits as green + simplified. No queues, no "refactor later" debt.

3. **Artifact-driven chaining.** The output of one skill feeds the next through `## Links` sections, JSON receipts, and session logs — not through re-navigation.

4. **Deterministic triggers, not judgment calls.** `code-simplifier` ALWAYS runs in the REFACTOR phase. `code-reviewer` always runs as final gate. Scope sync triggers when scope-linked files are in the diff.

5. **WIP limits prevent coordination breakdown.** Max 6 fillers, max 4 behavior slices, max 3 reviewers.

6. **Exclusive ownership prevents conflicts.** When using agent teams, no two teammates may edit the same file.

7. **JSON receipts enable orchestration.** Every subagent/teammate returns a machine-parseable receipt. The lead uses it to make deterministic next-step decisions.

---

## Orchestration Pattern (for the lead agent)

When implementing a feature, the lead follows this script:

```
1. Route: scope_map.py --query "<goal>" → anchor scope(s)
2. Slice: break into ≤ 2 active behavior slices with acceptance examples
3. Per phase (RED → GREEN → REFACTOR):
   a. Spawn parallel subagents for all slices
   b. Orchestrator gates with test suite
4. After all phases: code-reviewer on full diff (ALWAYS, not optional)
5. Conditional scope sync: only if scope-linked files are in the diff
6. Leave artifacts: session log + parking lot → task files + context summary
7. Done
```

This is the engineering lifecycle: **slice → implement → refactor → review → document → validate**.
