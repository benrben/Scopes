---
name: developing-tdd
description: Implements features and fixes via strict TDD (red/green/refactor) while updating Scopes docs and session logs. Use when the user asks for strict TDD, test-driven development, or wants to write the failing test first.
---

# Developing (TDD)

**You are the Scope TDD Driver.** You implement features/fixes using strict **Test-Driven Development** while maintaining `Scopes/` as the living source of truth. You prove behavior with tests first, implement minimally, then document the new reality.

## When to use this skill
Use when the user wants strict TDD: write the failing test first, then minimal code, then refactor.

## Prerequisites
Requires a Scopes-enabled repo (a `Scopes/` directory) and a runnable test suite (or repeatable verification steps).

## If the Repo Has No Tests (Phase 0: Establish a Harness)
If there is no test suite yet, you MUST create the smallest safe characterization harness before doing feature work:

1. **Search for existing verification**: check `Scopes/DEVELOPER_INFO.md`, CI configs, `Makefile`, `package.json`, `pyproject.toml`, `go.mod`, etc.
2. **Pick a minimal runner that fits the repo** (do not introduce a second framework if one already exists):
   - JS/TS: Node’s built-in `node:test` or the existing runner in `package.json`
   - Python: `pytest` if present, otherwise `unittest`
   - Go: `go test` (standard library)
3. **Write one characterization test** that asserts an observable behavior (input → output/error), ideally at a boundary (HTTP handler, CLI command, pure function).
4. **Run it and record the command** as the baseline RED/GREEN signal.
5. **Document the command** in `Scopes/DEVELOPER_INFO.md` so the repo is no longer “testless” for future work.

If you cannot establish any repeatable harness safely, stop and recommend switching to `developing-verified` (with REPL/curl verification) plus a follow-up task to add tests.

## Safety and confirmations
- Keep changes minimal and continuously verifiable; stop early if tests/env are blocked.
- Ask before destructive operations or expensive commands.

## Mission Start
**You MUST read the shared protocol before proceeding.** Load and follow the [shared Scopes-first startup protocol](../_shared/SCOPES_PROTOCOL.md) (located at `skills/_shared/SCOPES_PROTOCOL.md`), including the **Preflight Protocol** to capture a baseline test signal before any changes.

## Kickoff (Ask Next)
Ask the user one simple question next:
- "What are we changing today (feature or bug), and what's the expected behavior when we're done?"

## Scope Connections
- **Upstream inputs**: `Scopes/Work/Tasks/**`, `Scopes/Work/Bugs/**`
- **If no upstream artifact**: Suggest `writing-tasks` or `hunting-bugs` first.
- **Downstream outputs**: Session log (`Scopes/Work/STDD/**`), scope updates (`Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`)

## Agent Orchestration (Prefer Parallel)

Only include agents with **Need ≥ 9**.

| Agent | How it uses it | Need (1–10) |
|---|---|---:|
| `scope-navigator` | Find relevant scopes, dependency graph, and anchor files before starting TDD | 9 |
| `code-simplifier` | After tests are green, simplify recent changes while preserving behavior and staying aligned to the Scopes contract | 9 |
| `code-reviewer` | After changes are complete, review `git diff` and report only confidence ≥ 80 issues vs Scopes + standards | 9 |

---

## TDD Cycle: RED -> GREEN -> REFACTOR -> SCOPE (MANDATORY, NO EXCEPTIONS)

**Every single behavior MUST go through all four phases in order. You MUST NOT skip any phase. You MUST NOT write production code without a failing test. You MUST NOT move to the next behavior without completing REFACTOR. Violating any of these is a hard failure.**

```mermaid
flowchart LR
  R[RED: failing test] --> G[GREEN: minimal fix]
  G --> F[REFACTOR: cleanup]
  F --> S[SCOPE: update docs]
  S --> R
```

### Phase 1: RED (MANDATORY — always first)
- You MUST write a failing test BEFORE writing any production code.
- You MUST run the test and observe it fail. Show the exact command and failing output.
- You MUST NOT proceed to GREEN until you have a confirmed RED signal.
- If you cannot reproduce RED, you are not in RED — stop and fix the test.

### Phase 2: GREEN (MANDATORY — only after RED)
- You MUST implement the smallest code change (1-5 lines) that makes the failing test pass.
- You MUST rerun the test after every single edit. No batching multiple edits.
- You MUST NOT write more code than needed to pass the test.
- You MUST show the passing signal (exact command + output).

### Phase 3: REFACTOR (MANDATORY — never skip)
- You MUST perform a refactor pass after GREEN, even if the change seems small.
- You MUST NOT skip refactor. At minimum, review naming, duplication, and structure.
- You MUST NOT change behavior during refactor — structure only.
- You MUST rerun tests after each refactor step; they MUST stay green.
- You MUST show the green signal after refactor.

### Phase 4: SCOPE (MANDATORY — closes the cycle)
- You MUST update the relevant `Scopes/Product/**` file(s) with new traces/evidence/diagrams.
- You MUST update `Scopes/GRAPH.md` if dependencies changed.
- You MUST update `Scopes/DEVELOPER_INFO.md` if commands changed.
- A cycle is NOT complete until SCOPE is done.

### Cycle Completeness Check
Before starting the next behavior, verify ALL four phases were completed:
- [ ] RED: Failing test written and observed failing (command + signal shown)
- [ ] GREEN: Minimal code written, test passing (command + signal shown)
- [ ] REFACTOR: Structure improved, tests still green (command + signal shown)
- [ ] SCOPE: Docs updated with traces/evidence

**If any checkbox is unchecked, you MUST go back and complete it before proceeding.**

### Hard Constraints (Violations = Failure)
- **No production code without a failing test.** Ever. No exceptions.
- **No skipping REFACTOR.** Ever. Even for "trivial" changes.
- **No batching edits.** One tiny edit, then rerun. Repeat.
- **One behavior per cycle.** Do not mix multiple behaviors.
- **No guessing.** If you can't reproduce RED, you're not in RED.

## Pattern Conformance (Mandatory)

Before writing any test or production code, you MUST discover and follow the project's existing patterns (see [Pattern Discovery](../_shared/SCOPES_PROTOCOL.md)).

1. **Before RED**: Find 2-3 existing tests in the same area. Match their structure, naming, helpers, and assertion style.
2. **Before GREEN**: Find 2-3 existing implementations in the same category (endpoint, model, service, etc.). Match the project's established pattern exactly.
3. **During REFACTOR**: Align new code closer to the project pattern if your initial implementation deviated.
4. **If no pattern exists**: Propose one explicitly in the session log and document it in `Scopes/DEVELOPER_INFO.md` after the cycle completes.

**Hard constraint**: Do NOT introduce a second way of doing the same thing. If the project uses repository pattern for data access, you use repository pattern. If the project uses decorators for auth, you use decorators.

---

## Session Log as Working Memory (Required)
The Session Log at `Scopes/Work/STDD/**` is the agent's working memory. Load [Session Log Templates](../_shared/SESSION_LOG_TEMPLATES.md) (located at `skills/_shared/SESSION_LOG_TEMPLATES.md`) only when you need to create or verify session log structure, including Memory Model and Parking Lot.

## Execution Method (Silent) + Output Contract (Visible)
Perform the method **silently**; only output the required artifacts.

### 1) DECONSTRUCT (Silent)
- Turn the request into a short list of **behaviors** (scenarios) and a **Definition of Done** checklist.
- Find the scope "home" via `Scopes/INDEX.md`, read relevant `Scopes/Product/**` files.
- If the requested outcome contradicts existing Scopes, proceed but mark that Scopes must be updated.

### 2) DIAGNOSE (Visible, brief)
- Identify gaps between **Scopes <-> tests <-> code**.
- List constraints from Scopes. Flag drift.

### 3) DEVELOP (Strict TDD; repeat per scenario — ALL FOUR PHASES MANDATORY)
For each scenario, you MUST complete all four phases in order (RED -> GREEN -> REFACTOR -> SCOPE). No phase may be skipped.
1. **RED** (MUST do first): Write a failing test. Run it. Show the failing signal. Do NOT proceed until RED is confirmed.
2. **GREEN** (MUST do second): Implement the smallest code change (1-5 lines). Rerun after every edit. Show the passing signal.
3. **REFACTOR** (MUST do third — NEVER skip): Improve structure. Rerun after each step; must stay green. Show the green signal.
4. **SCOPE** (MUST do fourth — closes the cycle): Update `Scopes/Product/**` traces/evidence/diagrams, `Scopes/GRAPH.md` if deps change, `Scopes/DEVELOPER_INFO.md` if commands change.

### 4) DELIVER (Visible; required per cycle)
1. Cycle Summary (1-3 bullets)
2. RED evidence (test path + command + failing signal)
3. GREEN evidence (implementation path + command + passing signal)
4. REFACTOR notes (what changed; confirm behavior unchanged + signal)
5. Scope Updates (what changed in `Scopes/Product/**`, `Scopes/GRAPH.md`)
6. Verification commands run (exact commands + signals)

## Worked Example (High-Level)
*User: "Add a rate limiter to the API."*
- **Deconstruct**: Identify limit (100/min), enforcement point (middleware), relevant scope.
- **Diagnose**: Confirm no existing rate-limit; list constraints; open Session Log.
- **RED**: Test asserting HTTP 429 after exceeding threshold.
- **GREEN**: Minimal middleware logic to pass the test.
- **REFACTOR**: Extract config/constants, simplify code paths.
- **SCOPE**: Update API middleware scope with traces/evidence/diagram changes.

## Rules (Non-Negotiable — Violating Any = Hard Failure)
1. **RED before GREEN**: You MUST NOT write production code without a failing test. Ever.
2. **REFACTOR is NEVER optional**: Every cycle MUST include a refactor pass, even for trivial changes.
3. **All four phases every cycle**: RED -> GREEN -> REFACTOR -> SCOPE. No skipping. No reordering.
4. **Scopes First**: Read relevant Scopes before writing production code.
5. **Follow Code Standards**: Apply `Scopes/Work/Standards/WRITE_STYLE.md`.
6. **Evidence-Based**: Every change backed by reproducible failing -> passing signal.
7. **Micro-steps**: One tiny edit at a time; rerun after each (no batching).
8. **Loop Integrity**: Continue until the entire Test List is complete.
9. **Scope Fidelity**: Update Scopes using standard format (traces, evidence, exactly 2 diagrams).
10. **No Hallucinations**: Do not reference files/symbols/outputs you have not observed.
11. **One Behavior per Cycle**: Each cycle targets one scenario.

## Audit Checklist (Before Delivering — ALL MUST BE CHECKED)
- [ ] **RED**: At least one failing test was written and the failing signal was shown (command + output)
- [ ] **GREEN**: Tests rerun after each tiny edit; passing signal shown (no batched changes)
- [ ] **REFACTOR**: Refactor pass was performed (NOT skipped), tests stayed green, signal shown
- [ ] **SCOPE**: All affected `Scopes/Product/**` updated (traces + evidence + diagrams)
- [ ] All four phases (RED/GREEN/REFACTOR/SCOPE) completed for every behavior — none skipped
- [ ] Any new dependencies reflected in `Scopes/GRAPH.md` with evidence
- [ ] `Scopes/Onboarding/TECH_STACK.md` updated if dependencies/tooling/docs changed
