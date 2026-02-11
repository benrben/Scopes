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

Optional helper: `python3 scripts/score_evals.py <results.json>`

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
    {"id": "runs-validators", "weight": 3, "desc": "Runs check_evidence_links.py and drift_detector.py (or records blockers)"},
    {"id": "evidence-only", "weight": 3, "desc": "Updates use evidence links; unknowns are labeled [Unknown]"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns Verdict in allowed vocabulary"}
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
    {"id": "budgets", "weight": 2, "desc": "Uses budgets and [Unknown] instead of over-scanning"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns allowed Verdict vocabulary"}
  ]
}
```

### hunting-bugs

```json
{
  "name": "hunting-bugs",
  "kind": "skill",
  "skills": ["hunting-bugs"],
  "query": "Scan the auth module for security issues and bugs.",
  "files": ["(a repo with Scopes/ and an auth module)"],
  "checks": [
    {"id": "bug-report", "weight": 3, "desc": "Writes a bug report under Scopes/Work/Bugs/ with ranked findings"},
    {"id": "evidence-links", "weight": 3, "desc": "Every finding has at least one evidence link (or [Unknown])"},
    {"id": "post-step-validators", "weight": 2, "desc": "Runs check_evidence_links.py --broken-only --summary (or records blocker)"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns allowed Verdict vocabulary"}
  ]
}
```

### researching-decisions

```json
{
  "name": "researching-decisions",
  "kind": "skill",
  "skills": ["researching-decisions"],
  "query": "Should we migrate from REST to GraphQL for our public API?",
  "files": ["(a repo with Scopes/ and an existing REST API)"],
  "checks": [
    {"id": "truth-separation", "weight": 3, "desc": "Separates Internal Repo Truth from External Research"},
    {"id": "source-cap", "weight": 2, "desc": "Uses <= 5 external sources by default"},
    {"id": "offline-mode", "weight": 2, "desc": "If web blocked, marks external section [Blocked] and proceeds internal-only"},
    {"id": "verdict-vocab", "weight": 3, "desc": "Returns allowed Verdict vocabulary"}
  ]
}
```

### writing-adr

```json
{
  "name": "writing-adr",
  "kind": "skill",
  "skills": ["writing-adr"],
  "query": "Record the decision to use Redis for session storage.",
  "files": ["(a repo with Scopes/ and session/auth code)"],
  "checks": [
    {"id": "format", "weight": 3, "desc": "ADR includes Context, Options, Decision, Consequences, Affected Scopes"},
    {"id": "internal-evidence", "weight": 3, "desc": "Repo-specific context includes code/config evidence links or [Unknown]"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns allowed Verdict vocabulary"},
    {"id": "stop-condition", "weight": 2, "desc": "Stops once ADR sections are complete (no extra exploration)"}
  ]
}
```

### updating-skills

```json
{
  "name": "updating-skills",
  "kind": "skill",
  "skills": ["updating-skills"],
  "query": "Update my installed Scopes skills to the latest version.",
  "files": ["(a project with skills installed under a known root)"],
  "checks": [
    {"id": "dry-run", "weight": 3, "desc": "Runs or recommends --dry-run first; warns about overwrites"},
    {"id": "protocol-file", "weight": 3, "desc": "Verifies skills/_shared/SCOPES_PROTOCOL.md exists in the target skills root"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Returns allowed Verdict vocabulary"},
    {"id": "blocked-runbook", "weight": 2, "desc": "If auth/network fails, records exact blocker and next action"}
  ]
}
```

---

## Agent Evaluations

These are intentionally narrow: they test budgets, output schema, verdict vocabulary, and least-privilege behavior.

### scope-navigator

```json
{
  "name": "scope-navigator",
  "kind": "agent",
  "agents": ["scope-navigator"],
  "query": "Find the 1-3 most relevant scopes for 'authentication'.",
  "checks": [
    {"id": "budget", "weight": 3, "desc": "Returns <= 5 scope paths and <= 3 deps"},
    {"id": "schema", "weight": 3, "desc": "Includes Verdict/Decision/Evidence/Unknowns/Next/Artifact fields"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Uses allowed Verdict vocabulary"},
    {"id": "readonly", "weight": 2, "desc": "Does not write/edit files"}
  ]
}
```

### bug-scanner

```json
{
  "name": "bug-scanner",
  "kind": "agent",
  "agents": ["bug-scanner"],
  "query": "Scan src/auth for hotspots and write a bug scan report.",
  "checks": [
    {"id": "artifact-path", "weight": 3, "desc": "Writes report under Scopes/Work/Bugs/ with standard naming"},
    {"id": "evidence-format", "weight": 3, "desc": "Findings use [path:Lx-Ly](path#Lx-Ly) evidence format"},
    {"id": "schema", "weight": 2, "desc": "Returned summary uses the standard schema + Verdict vocab"},
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
    {"id": "stability", "weight": 3, "desc": "Includes goals/constraints/plan/findings/unknowns/next"},
    {"id": "schema", "weight": 2, "desc": "Returned summary includes pointer + abstract fields"}
  ]
}
```

### scope-auditor

```json
{
  "name": "scope-auditor",
  "kind": "agent",
  "agents": ["scope-auditor"],
  "query": "Validate Scopes drift and broken evidence links.",
  "checks": [
    {"id": "budget", "weight": 3, "desc": "Returns counts + worst 3 items (no long dumps)"},
    {"id": "schema", "weight": 3, "desc": "Includes Verdict/Decision/Evidence/Unknowns/Next/Artifact fields"},
    {"id": "readonly", "weight": 2, "desc": "Does not write/edit files"},
    {"id": "verdict-vocab", "weight": 2, "desc": "Uses allowed Verdict vocabulary"}
  ]
}
```

### scope-writer

```json
{
  "name": "scope-writer",
  "kind": "agent",
  "agents": ["scope-writer"],
  "query": "Update the auth capability scope after a verified change.",
  "checks": [
    {"id": "templates", "weight": 2, "desc": "Uses TEMPLATES.md structure (exact sections/diagrams/traces)"},
    {"id": "validators", "weight": 3, "desc": "Runs check_evidence_links.py and drift_detector.py (or records blocker)"},
    {"id": "schema", "weight": 3, "desc": "Returns standard schema + Verdict vocabulary"},
    {"id": "write-roots", "weight": 2, "desc": "Writes only under Scopes/ allowed roots"}
  ]
}
```

### code-architect

```json
{
  "name": "code-architect",
  "kind": "agent",
  "agents": ["code-architect"],
  "query": "Design an implementation blueprint for adding rate limiting.",
  "checks": [
    {"id": "single-decision", "weight": 3, "desc": "Picks one approach (no option sprawl)"},
    {"id": "evidence", "weight": 3, "desc": "Cites patterns with evidence links or [Unknown]"},
    {"id": "schema", "weight": 2, "desc": "Uses standard schema + Verdict vocabulary"},
    {"id": "stop-condition", "weight": 2, "desc": "Stops once files/sequence/verification are specified"}
  ]
}
```

### code-explorer

```json
{
  "name": "code-explorer",
  "kind": "agent",
  "agents": ["code-explorer"],
  "query": "Trace how login works end-to-end.",
  "checks": [
    {"id": "essential-files", "weight": 3, "desc": "Limits to 3-10 essential files by default"},
    {"id": "gaps-searched", "weight": 2, "desc": "Includes 'Evidence gaps searched (rg patterns)' when needed"},
    {"id": "confidence", "weight": 2, "desc": "Includes explicit Confidence"},
    {"id": "schema", "weight": 3, "desc": "Uses standard schema + Verdict vocabulary"}
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
