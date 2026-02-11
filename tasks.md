# ScopesCommands — “10/10” Hardening Task List

This repo is a **skills/agents package**. “Perfect” here means: **deterministic, evidence-first, token-bounded prompts** with **automation that prevents drift**.

## Definition of “Perfect” (measurable)

- **Contracts enforced**: every `skills/*/SKILL.md` and `agents/*.md` conforms to a repo-wide contract (validated by CI).
- **Deterministic**: every skill/agent has explicit stop conditions + scan budgets (and uses `[Unknown]` instead of guessing).
- **Composable**: standardized *verdict vocabulary*, output contracts, and artifact paths across skills/agents.
- **Runnable**: every workflow ends with a verification signal *or* a precise blocker + next action.
- **Regression-proof**: lint + scorecards prevent quality drift over time.

### Standard defaults to enforce repo-wide

- **Budgets** (unless user explicitly asks to go broader):
  - 1–3 anchor scopes
  - 3–7 evidence links
  - 3–10 code files
  - stop and label gaps as `[Unknown]`
- **Verdict vocabulary** (skills + agents): `Proceed`, `Blocked`, `Needs Sync`, `Needs Narrowing`
- **Evidence format**: `[path:Lx-Ly](path#Lx-Ly)` (no invented files/functions)

### Scoring formulas (for an eventual scorecard)

- **AgentScore (0–100)** = `10 * (0.15*Clarity + 0.20*ScopesAlignment + 0.20*OutputContract + 0.15*TokenEfficiency + 0.20*Safety + 0.10*OpsGuidance)` (each subscore 0–10)
- **SkillScore (0–100)** = `10 * (0.25*ScopesFirst + 0.15*EvidenceDiscipline + 0.20*VerificationGates + 0.15*Artifacts+Templates + 0.15*TokenEfficiency + 0.10*Safety)` (each subscore 0–10)

---

## P0 — Contracts + Automated Enforcement (highest leverage)

- [ ] Create `docs/contracts.md` defining REQUIRED structure for:
  - skills (`skills/*/SKILL.md`): frontmatter (`name`, `description`), “Mission Start” → `skills/_shared/SCOPES_PROTOCOL.md`, explicit “When to Stop”, explicit output contract, failure/blocked runbook, and required handoffs.
  - agents (`agents/*.md`): frontmatter (`name`, `description`, tools/readonly), explicit output contract including `Verdict:` + line limit, and standardized sections.
- [ ] Add `scripts/` folder at repo root (for repo maintenance tooling).
- [ ] Implement `scripts/lint_prompts.py` (contract linter) that fails on:
  - missing frontmatter fields
  - missing “Mission Start” reference to `skills/_shared/SCOPES_PROTOCOL.md`
  - missing “When to Stop”/budget section (skills)
  - missing `Verdict:` line + allowed vocabulary (skills + agents)
  - missing explicit max-line constraint in output contracts (agents)
  - mismatched/incorrect artifact paths (e.g., bug reports not under `Scopes/Work/Bugs/**`)
- [ ] Implement `scripts/lint_package.py` (package consistency linter) that checks:
  - every `skills/*/SKILL.md` exists and `name:` matches folder name
  - every `commands/*.md` references an existing `skills/<skill>/SKILL.md`
  - README’s Skills/Agents lists match `skills/*` + `agents/*.md`
  - every skill’s “Mission Start” references the canonical shared protocol path
  - no broken internal links to missing files (esp. protocol paths)
- [ ] Add a single command to run all checks locally:
  - `make lint` **or** `bash scripts/lint.sh` (pick one and document it).
- [ ] Add CI (GitHub Action) to run the linters on PRs and fail when contracts are violated.
- [ ] Document the “quality gates” in `README.md` (how to run `lint`, what it enforces).

---

## P1 — Token Reduction: de-duplicate the big skills (biggest token win)

- [ ] Create one shared “Developing Protocol” doc under `skills/_shared/` that contains the repeated loop/rules/audit/stop-condition content currently duplicated in:
  - `skills/developing-tdd/SKILL.md`
  - `skills/developing-verified/SKILL.md`
- [ ] Refactor `skills/developing-tdd/SKILL.md` to be lean:
  - keep only TDD-specific deltas (RED/GREEN/REFACTOR/SCOPE mechanics)
  - reference the shared developing protocol for everything else
- [ ] Refactor `skills/developing-verified/SKILL.md` to be lean:
  - keep only verified-specific deltas (sandbox verification ladder, no-test-writing constraint)
  - reference the shared developing protocol for everything else
- [ ] Refactor `skills/syncing-scopes/SKILL.md` into a lean operator manual:
  - move long protocols (git, audits, patterns, templates details) into `skills/syncing-scopes/references/`
  - keep `SKILL.md` focused on: when to use, quick start, strict invariants, and *which references to load when*

---

## P2 — Stop Conditions + Budgets (standardize across every skill/agent)

- [ ] Add explicit “When to Stop” sections to skills that don’t have them (or tighten ones that do) with repo-standard caps:
  - 1–3 anchor scopes, ~3–7 evidence links, 3–10 code files; stop and label `[Unknown]`
- [ ] Add a token-safety budget to `skills/writing-tasks/SKILL.md`:
  - default max tasks per batch
  - default max total estimated hours (stop once ≤ N hours or require user confirmation)
- [ ] Add a stop condition to `skills/planning-idea/SKILL.md`:
  - stop once Risk Register + Scope Registry Impact + TODO Scopes + Definition of Done are complete
- [ ] Add a stop condition to `skills/planning-refactor/SKILL.md`:
  - stop once phases + verification gates + rollback plan + scope maintenance are complete (avoid over-phasing)
- [ ] Add a stop condition to `skills/researching-decisions/SKILL.md`:
  - **internal-only mode** (max 3 scopes, max 10 files) when web access is unavailable/unneeded
  - **external source cap** (e.g., max 5 sources unless user asks for more)

---

## P3 — Sync Correctness: make drift/link validation “default”

- [ ] Update `agents/scope-writer.md` to include default post-write validation:
  - `check_evidence_links.py --broken-only --summary`
  - `drift_detector.py --stale-only --limit <N>` (where applicable)
- [ ] Update `agents/bug-scanner.md` to:
  - require evidence-link format in every finding (no exceptions)
  - include broken-link + drift summary counts in the saved report
- [ ] Update `skills/hunting-bugs/SKILL.md` to include a mandatory post-step:
  - run `check_evidence_links.py --broken-only --summary` and include summary in the bug report (keeps Scopes trustworthy)
- [ ] Add a “post-move/rename link-rot checklist” line anywhere file moves/renames are likely (esp. `skills/planning-refactor/SKILL.md`):
  - after any move/rename: run `scope-auditor` or `check_evidence_links.py` and record results
- [ ] Add a documented “pre-merge validation” recipe to `README.md`:
  - `check_evidence_links.py --summary --fail-on-missing-scopes` (or closest supported behavior)
  - `drift_detector.py --all --stale-only --limit 20`

---

## P4 — Permissioned Git Behavior (avoid policy mismatch across environments)

- [ ] Update `skills/syncing-scopes/SKILL.md` “Git Tracking Protocol”:
  - always record `BASE_REF`
  - create checkpoint commits **only if explicitly allowed/approved**
  - maintain a “diff-only mode” fallback (no git write operations)
- [ ] Update `skills/_evaluations/README.md` to remove/relax any **required** checkpoint commit expectation (“commit only if approved”).

---

## P5 — Output Standardization (verdicts, line limits, filenames)

### Repo-wide (skills + agents)
- [ ] Standardize `Verdict:` to exactly one of: `Proceed`, `Blocked`, `Needs Sync`, `Needs Narrowing`.
- [ ] Ensure every output contract has an explicit max-line constraint and is consistent with its own rules.

### Agents (targeted fixes)
- [ ] `agents/scope-navigator.md`: default to `scope_map.py --depth 1` when repos are huge; narrow using `--area` before `--depth 2`.
- [ ] `agents/scope-auditor.md`: make “Worst (max 3)” extraction explicit; fix whitespace-unsafe fallback loop (avoid `for f in $(find ...)`).
- [ ] `agents/code-reviewer.md`:
  - add a hard stop: stop after ≥ N high-confidence issues
  - always include “Scopes impact → exact files to update” (even when verdict is OK)
- [ ] `agents/code-architect.md`: add a hard stop condition and explicit handoff guidance to `writing-tasks` + scope updates when blueprint is complete.
- [ ] `agents/code-explorer.md`: add a 1-line “Evidence gaps searched (rg patterns)” and an explicit `Confidence:` line.
- [ ] `agents/code-simplifier.md`: add a “Scope maintenance handoff” line (which scope files likely need evidence-link updates after refactors) + explicit “no public API changes” reminder.
- [ ] `agents/bug-scanner.md`:
  - resolve the ≤14 vs ≤30 line-limit mismatch (pick one limit and enforce it)
  - standardize bug report naming with `skills/hunting-bugs/SKILL.md` (single filename convention)

### Skills (targeted fixes)
- [ ] Make “Need ≥ 9” tables meaningful:
  - remove agent rows that are never actually needed
  - avoid “all 9s” tables (either adjust Need values or remove the section)
- [ ] `skills/querying-scopes/SKILL.md`: enforce the “max evidence links = 7” cap as a hard rule.
- [ ] `skills/researching-decisions/SKILL.md`: cap total sources by default (unless user asks).
- [ ] `skills/writing-adr/SKILL.md`: require internal-context claims to include evidence links (not just scope links).

---

## P6 — Failure Modes as First-Class (Blocked Runbooks everywhere)

- [ ] Add a “Blocked Runbook” section to every skill with deterministic next actions, e.g.:
  - missing/empty `Scopes/` → run `syncing-scopes`
  - stale/broken evidence links → `scope-auditor` then `scope-writer`
  - no tests present → establish minimal harness (or switch to `developing-verified` + create a follow-up test task)
  - no web access → “offline mode” template (internal truth only + `[Blocked]` external section)
- [ ] Ensure every skill/agent returns the next actionable move when blocked (never silently stalls).

---

## P7 — Naming/Path Compatibility Aliases (reduce user confusion)

- [ ] Add compatibility stub(s) so common but non-canonical paths resolve:
  - `skills/_protocols/STARTUP.md` → points to `skills/_shared/SCOPES_PROTOCOL.md`
  - `skills/ask-scopes/**` and `skills/asking-scopes/**` → point to `skills/querying-scopes/` (or redirect docs)
- [ ] Update `README.md` to clearly state canonical protocol path and list the compatibility aliases.

---

## P8 — Evaluations → Numeric Scorecards (prove “10/10” and prevent regression)

- [ ] Convert `skills/_evaluations/README.md` from checklists to a scored scorecard:
  - pass/fail per bullet → weighted score
  - publish thresholds (e.g., 90+ Excellent, 80–89 Very Good, 70–79 Good)
  - map to AgentScore/SkillScore formulas
- [ ] Add at least one evaluation per agent/skill that specifically tests:
  - budgets/stop conditions are honored (no over-scan)
  - verdict vocabulary is correct
  - evidence links are present and correctly formatted
- [ ] (Optional) Add `scripts/score_evals.py` to compute scores from a JSON result file (manual run → machine-readable trend).

---

## P9 — Paper Cuts / Quick Wins (do anytime)

- [ ] Ensure every skill references `skills/_shared/SCOPES_PROTOCOL.md` consistently (no drifting “Mission Start” paths).
- [ ] Ensure every doc-writing workflow explicitly lists which Scopes artifacts may need updates:
  - `Scopes/Product/**`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`
- [ ] Add/standardize “evidence gaps” reporting to reduce re-tracing:
  - include `rg` patterns used when something is `[Unknown]`.

