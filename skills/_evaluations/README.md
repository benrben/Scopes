# Skill Evaluations

Evaluation scenarios for testing Scopes skills. Use these to measure skill effectiveness, catch regressions, and guide iteration.

## How to use

Each evaluation defines:
- **skills**: Which skill(s) to activate.
- **query**: The user prompt to test with.
- **files** (optional): Test files to include in the working directory.
- **expected_behavior**: A checklist of observable behaviors that indicate success.

Run each evaluation with a fresh Claude instance (the "Claude B" pattern). Observe whether all expected behaviors are met. Score pass/fail per behavior and iterate on the skill if behaviors are missed.

---

## Evaluation: syncing-scopes (Generation Mode)

```json
{
  "skills": ["syncing-scopes"],
  "query": "Generate Scopes documentation for this repository from scratch.",
  "files": ["(any repo without a Scopes/ directory)"],
  "expected_behavior": [
    "Creates Scopes/INDEX.md with a scope tree",
    "Creates Scopes/GRAPH.md with relationships and an evidence table",
    "Creates Scopes/DEVELOPER_INFO.md with run/test/build commands sourced from package.json or equivalent",
    "Creates Scopes/Onboarding/TECH_STACK.md with evidence-backed entries",
    "Creates Scopes/Work/Standards/WRITE_STYLE.md",
    "Creates at least one Capability Scope under Scopes/Product/ with exactly 2 Mermaid diagrams",
    "Every claim in Capability Scopes has an evidence link in [path:Lx-Ly](path#Lx-Ly) format",
    "Does not invent filenames or functions that do not exist"
  ]
}
```

## Evaluation: syncing-scopes (Update Mode)

```json
{
  "skills": ["syncing-scopes"],
  "query": "Update Scopes to reflect the current state of the codebase.",
  "files": ["(a repo with an existing but stale Scopes/ directory)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and Scopes/GRAPH.md before making changes",
    "Identifies at least one drift item (stale evidence link or missing capability)",
    "Updates evidence links to point to current line numbers",
    "Does not delete valid, up-to-date scope content",
    "Creates a git checkpoint commit before starting",
    "Produces a final git diff summary covering Scopes/**"
  ]
}
```

## Evaluation: hunting-bugs

```json
{
  "skills": ["hunting-bugs"],
  "query": "Scan the auth module for security issues and bugs.",
  "files": ["(a repo with an auth module containing at least one known issue)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and Scopes/GRAPH.md first",
    "Asks a kickoff question about scope/risk tolerance",
    "Produces a bug report under Scopes/Work/Bugs/",
    "Every finding has at least one evidence link",
    "Findings are ranked by severity",
    "Fix suggestions are minimal and testable",
    "Does not modify product code (documentation only)"
  ]
}
```

## Evaluation: developing-tdd

```json
{
  "skills": ["developing-tdd"],
  "query": "Add input validation to the /api/users endpoint that rejects emails without an @ symbol.",
  "files": ["(a repo with an existing /api/users endpoint and a test suite)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and relevant capability scope before coding",
    "Runs existing tests first to capture baseline (preflight)",
    "Writes a failing test BEFORE any production code",
    "Shows the RED signal (exact command + failing output)",
    "Implements minimal code to make the test pass",
    "Shows the GREEN signal (exact command + passing output)",
    "Performs a refactor step (even if minor)",
    "Updates the relevant Scopes/Product/** file with new traces/evidence",
    "Creates or updates a session log under Scopes/Work/STDD/"
  ]
}
```

## Evaluation: querying-scopes

```json
{
  "skills": ["querying-scopes"],
  "query": "How does authentication work in this project?",
  "files": ["(a repo with populated Scopes/ including auth-related scopes)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md first to locate auth capability",
    "Reads the relevant capability scope under Scopes/Product/",
    "Does NOT read all scope files",
    "Provides a structured answer with Scope Paths Used and Evidence sections",
    "Includes a Confidence rating",
    "Does not implement or modify any code",
    "If scopes are stale, recommends syncing-scopes"
  ]
}
```

## Evaluation: writing-tasks

```json
{
  "skills": ["writing-tasks"],
  "query": "Break this plan into executable tasks: We need to add Google OAuth login alongside our existing email login.",
  "files": ["(a repo with Scopes/ and an existing auth capability scope)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and the auth anchor scope",
    "Produces task files under Scopes/Work/Tasks/",
    "Each task is scoped to 1-4 hours",
    "Each task has concrete verification (test name or command)",
    "Each task includes Scope Maintenance instructions",
    "Tasks have an Anchor Scope reference under Scopes/Product/",
    "Dependencies between tasks are clearly listed"
  ]
}
```

## Evaluation: developing-verified

```json
{
  "skills": ["developing-verified"],
  "query": "Add a retry with exponential backoff to the HTTP client's fetch method.",
  "files": ["(a repo with an existing HTTP client module, Scopes/, and a test suite or repeatable verification)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and relevant capability scope before coding",
    "Runs existing tests first to capture baseline (preflight)",
    "Establishes a baseline verification signal before making changes",
    "Implements in micro-steps with verification after every edit",
    "Performs a polish/refactor pass with verification after each step",
    "Does not introduce unused functionality (YAGNI enforced)",
    "Updates the relevant Scopes/Product/** file with new traces/evidence",
    "Creates or updates a session log under Scopes/Work/DEV/"
  ]
}
```

## Evaluation: planning-idea

```json
{
  "skills": ["planning-idea"],
  "query": "Plan a notifications system that supports email and in-app channels.",
  "files": ["(a repo with populated Scopes/ and existing user/auth capability scopes)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and Scopes/GRAPH.md first",
    "Asks a kickoff question about the idea",
    "Produces a plan file under Scopes/Work/Planning/",
    "Plan includes a Scope Registry Impact section (new/modified scopes, graph edges)",
    "Plan includes sequenced TODO Scopes with verification steps",
    "Plan includes a Definition of Done checklist",
    "Does not implement product code (planning artifacts only)",
    "Respects Anti-Tiny-Scope rule (no separate scope for < 2 behaviors)"
  ]
}
```

## Evaluation: planning-refactor

```json
{
  "skills": ["planning-refactor"],
  "query": "Refactor the monolithic UserService into separate AuthService and ProfileService classes.",
  "files": ["(a repo with a large UserService, Scopes/, and a test suite)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md, Scopes/GRAPH.md, and the relevant capability scope",
    "Asks a kickoff question about the refactor target and behavior invariants",
    "Produces a refactor plan under Scopes/Work/Refactors/",
    "Includes Phase 0 (Characterization Tests) if coverage is weak",
    "Every phase ends in a green test suite checkpoint",
    "Includes explicit Scope Maintenance steps for evidence link updates after moves/renames",
    "Uses Scopes/GRAPH.md to identify downstream dependents",
    "Does not implement code (plan only)"
  ]
}
```

## Evaluation: researching-decisions

```json
{
  "skills": ["researching-decisions"],
  "query": "Should we migrate from REST to GraphQL for our public API? Research the tradeoffs.",
  "files": ["(a repo with an existing REST API, Scopes/, and Scopes/Onboarding/TECH_STACK.md)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md, Scopes/GRAPH.md, and relevant capability scopes",
    "Asks a kickoff question about the decision to unblock",
    "Produces a research report under Scopes/Research/",
    "Clearly separates Internal Repo Truth from External Research",
    "Internal claims use evidence links; external claims use URLs",
    "Includes an Options & Tradeoffs table with Fit for Repo column",
    "Includes a concrete recommendation with rationale",
    "Lists explicit Scope Updates Needed"
  ]
}
```

## Evaluation: writing-adr

```json
{
  "skills": ["writing-adr"],
  "query": "Record the decision to use Redis for session storage instead of database-backed sessions.",
  "files": ["(a repo with Scopes/ and an existing auth/session capability scope)"],
  "expected_behavior": [
    "Reads Scopes/INDEX.md and relevant capability scopes",
    "Asks a kickoff question about the decision and its status (Proposed/Accepted)",
    "Produces an ADR under Scopes/Decisions/ADRs/",
    "ADR follows Nygard format (Context, Decision, Consequences)",
    "Includes both Positive and Negative consequences",
    "Includes Affected Scopes section with links to capability scopes",
    "Context section links to code evidence"
  ]
}
```

## Evaluation: updating-skills

```json
{
  "skills": ["updating-skills"],
  "query": "Update my installed Scopes skills to the latest version.",
  "files": ["(a project with skills installed under .cursor/skills/ or .claude/skills/)"],
  "expected_behavior": [
    "Identifies the correct skills root directory",
    "Runs the update-skills.sh script",
    "Reports which skills were added or updated",
    "Does not corrupt existing skill folders during sync",
    "Handles network/auth errors gracefully"
  ]
}
```
