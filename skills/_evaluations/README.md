# Evaluations (Scored Scorecards)

These scenarios are regression tests for Scopes skills and agents.
Each evaluation is a **weighted scorecard** (not a pure checklist) to prevent drift.

## Scores and Thresholds

Scores are computed as: `sum(weight for passed checks) / sum(weight for all checks)`.

Suggested thresholds:
- 90+ Excellent
- 80-89 Very Good
- 70-79 Good
- <70 Needs work

Optional helper: aggregate scores with your preferred JSON scoring tool.

## What We Test (Defaults)

Every skill/agent evaluation should include checks for:
- Budgets/stop conditions are honored (no over-scan by default)
- Verdict vocabulary is correct: `Proceed`, `Blocked`, `Needs Sync`, `Needs Narrowing`
- Evidence discipline: internal claims use evidence links; missing proof becomes `[Unknown]`
- Firebreak: no tool dumps; artifact pointer used when output would be long
- Least-privilege behavior: read-only agents do not write/edit

---

## Skill Evaluations

### syncing-scopes (Update Mode)

```json
{
  "name": "syncing-scopes-update",
  "kind": "skill",
  "skills": ["syncing-scopes"],
  "query": "Update Scopes to reflect the current state of the codebase.",
  "files": ["(a repo with an existing but stale Scopes/ directory)"],
  "checks": [
    {"id": "uses-protocol", "weight": 2, "desc": "Mission Start references skills/_shared/SCOPES_PROTOCOL.md"},
    {"id": "records-base-ref", "weight": 2, "desc": "Records BASE_REF; does not assume commits are allowed"},
    {"id": "mode-selection", "weight": 2, "desc": "Selects Full vs Light mode deterministically; records mode and any intentional partial coverage"},
    {"id": "runs-validators", "weight": 3, "desc": "Runs drift_detector.py (or records blockers)"},
    {"id": "evidence-only", "weight": 3, "desc": "Updates use evidence links; unknowns are labeled [Unknown]"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns Verdict in allowed vocabulary"}
  ]
}
```

### syncing-scopes (Full vs Light)

```json
{
  "name": "syncing-scopes-full-sync",
  "kind": "skill",
  "skills": ["syncing-scopes"],
  "query": "Run a full sync of Scopes (full mirror of the repo).",
  "files": ["(a repo with Scopes/; may be large)"],
  "checks": [
    {"id": "full-sync", "weight": 4, "desc": "Runs Full Sync when explicitly requested (does not silently downgrade to Light)"},
    {"id": "all-areas", "weight": 3, "desc": "Updates all capability areas (no arbitrary 1–3 scope cap)"},
    {"id": "validators", "weight": 3, "desc": "Runs validators after writes (or records blockers)"}
  ]
}
```

```json
{
  "name": "syncing-scopes-light-sync",
  "kind": "skill",
  "skills": ["syncing-scopes"],
  "query": "Sync Scopes for this very large repo (use Light Sync if needed; keep navigation/truth surfaces accurate).",
  "files": ["(a very large repo with Scopes/)"],
  "checks": [
    {"id": "light-sync", "weight": 4, "desc": "Uses Light Sync when repo is too large; records what was intentionally partial"},
    {"id": "truth-surfaces", "weight": 3, "desc": "Keeps INDEX/GRAPH/DEVELOPER_INFO/TECH_STACK accurate"},
    {"id": "selective-updates", "weight": 3, "desc": "Updates stale/broken scopes first; avoids unnecessary churn"}
  ]
}
```

### querying-scopes

```json
{
  "name": "querying-scopes",
  "kind": "skill",
  "skills": ["querying-scopes"],
  "query": "How does authentication work in this project?",
  "files": ["(a repo with populated Scopes/ including auth-related scopes)"],
  "checks": [
    {"id": "budgets", "weight": 3, "desc": "Uses 1-3 anchor scopes and <= 7 evidence links by default"},
    {"id": "unknowns", "weight": 2, "desc": "Missing proof is labeled [Unknown] (no guessing)"},
    {"id": "structured-output", "weight": 3, "desc": "Returns Decision/Evidence/Next/Artifact fields with allowed Verdict"},
    {"id": "no-code-changes", "weight": 2, "desc": "Does not implement or modify code"}
  ]
}
```

### developing-tdd

```json
{
  "name": "developing-tdd",
  "kind": "skill",
  "skills": ["developing-tdd"],
  "query": "Add input validation to /api/users rejecting emails without '@'.",
  "files": ["(a repo with /api/users and a test suite)"],
  "checks": [
    {"id": "red-first", "weight": 4, "desc": "Shows a failing test before production code"},
    {"id": "green-then-refactor", "weight": 3, "desc": "Makes minimal fix, then refactors with tests green"},
    {"id": "scope-maintenance", "weight": 2, "desc": "Updates affected Scopes evidence/traces after verified change"},
    {"id": "budgets", "weight": 1, "desc": "Stops without over-scanning; uses [Unknown] for gaps"}
  ]
}
```

### developing-verified

```json
{
  "name": "developing-verified",
  "kind": "skill",
  "skills": ["developing-verified"],
  "query": "Add exponential backoff retries to the HTTP client fetch method.",
  "files": ["(a repo with Scopes/ and repeatable verification)"],
  "checks": [
    {"id": "baseline-signal", "weight": 3, "desc": "Establishes baseline verification command before edits"},
    {"id": "micro-steps", "weight": 3, "desc": "Edits in small steps with verification after each"},
    {"id": "no-new-tests", "weight": 2, "desc": "Does not create new test files/functions"},
    {"id": "scope-maintenance", "weight": 2, "desc": "Updates affected Scopes evidence/traces after verified change"}
  ]
}
```

### writing-tasks

```json
{
  "name": "writing-tasks",
  "kind": "skill",
  "skills": ["writing-tasks"],
  "query": "Break this plan into tasks: Add Google OAuth alongside email login.",
  "files": ["(a repo with Scopes/ and an auth anchor scope)"],
  "checks": [
    {"id": "task-budget", "weight": 2, "desc": "Respects max tasks per batch and hours per batch defaults"},
    {"id": "links", "weight": 2, "desc": "Every task file includes a Links section with 1-3 anchor scopes under Scopes/Product/**"},
    {"id": "pattern-reference", "weight": 3, "desc": "Every code-creating task includes a Pattern Reference"},
    {"id": "verification", "weight": 3, "desc": "Tasks have concrete verification steps"},
    {"id": "scope-maintenance", "weight": 2, "desc": "Tasks list scope maintenance impacts explicitly"}
  ]
}
```

### planning-idea

```json
{
  "name": "planning-idea",
  "kind": "skill",
  "skills": ["planning-idea"],
  "query": "Plan a notifications system that supports email and in-app channels.",
  "files": ["(a repo with populated Scopes/)"],
  "checks": [
    {"id": "stop-condition", "weight": 3, "desc": "Stops once Risk Register + Scope Registry Impact + TODO Scopes + DoD are complete"},
    {"id": "links", "weight": 2, "desc": "Plan artifact includes Links section with 1-3 anchor scopes under Scopes/Product/**"},
    {"id": "pattern-evidence", "weight": 3, "desc": "Blueprint cites existing patterns with evidence links or marks [Unknown]"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns allowed Verdict vocabulary"},
    {"id": "no-implementation", "weight": 2, "desc": "Does not implement product code"}
  ]
}
```

### planning-refactor

```json
{
  "name": "planning-refactor",
  "kind": "skill",
  "skills": ["planning-refactor"],
  "query": "Refactor the monolithic UserService into separate services without changing behavior.",
  "files": ["(a repo with Scopes/ and a test suite)"],
  "checks": [
    {"id": "phases-and-gates", "weight": 3, "desc": "Has phases + verification gates + rollback plan"},
    {"id": "link-rot-checklist", "weight": 3, "desc": "Includes post-move/rename link validation step"},
    {"id": "links", "weight": 2, "desc": "Refactor plan includes Links section with 1-3 anchor scopes under Scopes/Product/**"},
    {"id": "budgets", "weight": 2, "desc": "Uses budgets and [Unknown] instead of over-scanning"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns allowed Verdict vocabulary"}
  ]
}
```

---

## Agent Evaluations

These are intentionally narrow: they test budgets, output schema, verdict vocabulary, and least-privilege behavior.

### bug-scanner

```json
{
  "name": "bug-scanner",
  "kind": "agent",
  "agents": ["bug-scanner"],
  "query": "Scan src/auth for hotspots and write a bug scan report.",
  "checks": [
    {"id": "artifact-path", "weight": 3, "desc": "Writes report under Scopes/Work/Bugs/ with standard naming and a Links section"},
    {"id": "evidence-format", "weight": 3, "desc": "Findings use [path:Lx-Ly](path#Lx-Ly) evidence format"},
    {"id": "schema", "weight": 2, "desc": "Returned summary uses the standard schema + Verdict vocab + Confidence"},
    {"id": "no-code-edits", "weight": 2, "desc": "Does not edit product code"}
  ]
}
```

### context-summarizer

```json
{
  "name": "context-summarizer",
  "kind": "agent",
  "agents": ["context-summarizer"],
  "query": "Summarize the current work state after a tool-heavy phase.",
  "checks": [
    {"id": "artifact-path", "weight": 3, "desc": "Writes summary under Scopes/Work/Notes/ with standard naming"},
    {"id": "stability", "weight": 3, "desc": "Includes links/goals/constraints/plan/findings/unknowns/next"},
    {"id": "schema", "weight": 2, "desc": "Returned summary includes pointer + abstract fields + Confidence"}
  ]
}
```

### code-reviewer

```json
{
  "name": "code-reviewer",
  "kind": "agent",
  "agents": ["code-reviewer"],
  "query": "Review the current git diff for high-confidence issues.",
  "checks": [
    {"id": "confidence-gate", "weight": 3, "desc": "Reports only issues with confidence >= 80"},
    {"id": "hard-stop", "weight": 2, "desc": "Stops after >= 8 issues or offloads to artifact"},
    {"id": "scopes-impact", "weight": 3, "desc": "Always lists exact scope files to update when relevant"},
    {"id": "schema", "weight": 2, "desc": "Uses standard schema + Verdict vocabulary"}
  ]
}
```

### code-simplifier

```json
{
  "name": "code-simplifier",
  "kind": "agent",
  "agents": ["code-simplifier"],
  "query": "Simplify recent changes without behavior changes.",
  "checks": [
    {"id": "no-behavior-change", "weight": 4, "desc": "Does not change external behavior; proposes risky changes instead"},
    {"id": "verification", "weight": 3, "desc": "Runs at least one verification command or records blocker"},
    {"id": "scope-handoff", "weight": 2, "desc": "Calls out exact Scopes/Product/** files to update when needed"},
    {"id": "schema", "weight": 1, "desc": "Uses standard schema + Verdict vocabulary"}
  ]
}
```
