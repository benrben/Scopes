# Developing Protocol (Shared)

This file contains shared rules for the `developing-*` skills.
Skill files should reference this instead of duplicating long loop/rules text.

## Shared Defaults (Budgets)

Unless the user explicitly requests broader scanning:
- 1-3 anchor scopes
- 3-7 evidence links
- 3-10 code files
- stop and label gaps as `[Unknown]`

## Verification-First Loop

Every change follows the same shape:
1. Pick one scenario/behavior.
2. Establish a baseline verification signal (tests or terminal command).
3. Make minimal edits (micro-steps).
4. Re-verify after each micro-step.
5. Polish (refactor/cleanup) with verification.
6. Scope maintenance (update `Scopes/**` as needed).

## Pattern Conformance (Mandatory)

Before writing production code:
- Use `Scopes/DEVELOPER_INFO.md` and the anchor scope's traces/evidence to find 2-3 similar implementations.
- Follow the repo's existing pattern; do not introduce a second approach.
- If no pattern exists, propose one explicitly and document it (with evidence) after verification.

## Scope Maintenance (Mandatory)

If you change behavior or touch files referenced by Scopes evidence:
- Update the relevant `Scopes/Product/**` files (traces + evidence).
- Update `Scopes/GRAPH.md` if dependencies changed.
- Update `Scopes/DEVELOPER_INFO.md` if commands/verification steps changed.
- Update `Scopes/Onboarding/TECH_STACK.md` if tooling/deps changed.

After scope edits, validate:
- `python3 skills/syncing-scopes/scripts/check_evidence_links.py --broken-only --summary`
- `python3 skills/syncing-scopes/scripts/drift_detector.py --stale-only --limit 20`

## Evidence Discipline

- Do not claim things you did not observe.
- Missing proof becomes `[Unknown]`.
- Evidence link format: `[path:Lx-Ly](path#Lx-Ly)`
