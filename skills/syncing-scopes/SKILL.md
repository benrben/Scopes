---
name: syncing-scopes
description: Generates or updates Scopes documentation from code, tests, config, and schema while maintaining INDEX.md, GRAPH.md, and DEVELOPER_INFO.md with evidence-backed claims. Use when Scopes are missing, stale, or drifted from code reality.
model: inherit
---

# Syncing Scopes

You generate/repair `Scopes/` from observable repo truth. No guessing: missing proof becomes `[Unknown]`.

## When to use this skill
Use when `Scopes/` is missing, stale, or you suspect scope drift (broken evidence links, outdated traces, missing capability coverage).

## Prerequisites
- Read access to the repo code/tests/config.
- Permission to write under `Scopes/`.

## Safety and confirmations
- Prefer updating existing files over churn/renames.
- Ask before destructive operations (mass deletes, large rewrites, moving many files).

## Mission Start
Load and follow the shared Scopes-first startup protocol at `skills/_shared/SCOPES_PROTOCOL.md`.
For detailed rules, load `skills/syncing-scopes/references/PROTOCOLS.md` and `skills/syncing-scopes/references/TEMPLATES.md` as needed.

## Kickoff (Automatic)
- Do **not** ask which area to focus on. Discover all capability areas from `Scopes/INDEX.md` and `Scopes/Product/**` (or from repo structure if Scopes are missing) and sync **all** areas in parallel. Only ask the user for destructive operations (see Safety) or when Scopes are missing and generation from scratch needs approval.

## Quick Start (Update Mode — all areas, automatic)
1. Discover all areas from `Scopes/INDEX.md` and `Scopes/Product/**` (one area per top-level capability or dir).
2. Capture drift + broken links (optionally in parallel per area):
   - `python3 skills/syncing-scopes/scripts/drift_detector.py --all --stale-only`
   - `python3 skills/syncing-scopes/scripts/check_evidence_links.py --broken-only --summary`
3. Spawn one `scope-auditor` per area in parallel (Phase 1), then one `scope-writer` per area in parallel (Phase 2). Update **all** areas; do not limit to 1-3 scopes.
4. Re-validate (Phase 3), then report.

Common targets to keep in sync:
- `Scopes/Product/**`, `Scopes/INDEX.md`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`

## Git Tracking Protocol (Permissioned)
- Always record `BASE_REF` (branch/sha) in the session log or plan artifact.
- Create checkpoint commits only if explicitly approved by the user.
- Diff-only fallback: if commits are not allowed, use `git diff` summaries to show what changed.

## Agent Orchestration

**Automatic, all areas, parallel.** Do not ask the user which area to sync. Discover all areas from `Scopes/INDEX.md` and `Scopes/Product/**`; spawn one auditor per area and one writer per area in parallel. Sync **all** areas — no 1-3 scope limit.

#### Phase 1: Audit (Parallel — one agent per area, all areas)
**Spawn `scope-auditor`** for **each** capability area (from INDEX.md or top-level dirs under `Scopes/Product/`):
> Audit only scopes under {area path or capability name}. Detect stale evidence, broken links, and code-doc drift. Return SCOPE AUDIT for this area.

**Handle output:** Merge audit findings from all areas. Do not reduce to "top 1-3"; keep full list for Phase 2.

#### Phase 2: Write (Parallel — one agent per area, all areas)
**Spawn `scope-writer`** for **each** area (same list as Phase 1):
> Update only scope files in {area path or capability name}. Fix broken evidence links, refresh traces, and align with current code for this area. Target files: {list from Phase 1 for this area}.

**Handle output:** Confirm each writer's changes; resolve any cross-area conflicts (e.g. GRAPH.md, INDEX.md) in the main agent.

#### Phase 3: Re-validate (after writes complete)
**Spawn `scope-auditor`:**
> Re-validate all scopes after the recent updates. Confirm drift and broken links are resolved.

**Handle output:** If new issues are found, either fix them inline or record them for a follow-up task.

## When to Stop (Mandatory)
- Stop once validators are clean for **all** areas OR you can precisely report what is blocked and why.
- No scope cap: sync all areas. Label gaps as `[Unknown]` where evidence is missing.
- If the repo is too large to sync in one run, split by capability areas and run parallel agents per area; do not arbitrarily limit to 1-3 scopes.

## Blocked Runbook (Mandatory)
- No `Scopes/` and generation from scratch is not approved: set `Verdict: Needs Narrowing` and ask for permission to generate (do not ask which area — generate all).
- Evidence links cannot be validated (missing files, permissions): record exact blocker; set `Verdict: Blocked`.
- Git history unavailable (no git metadata): use filesystem timestamps and direct evidence checks; record limitation.

## Output Contract

Return <= 20 lines:

```markdown
## SYNC
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of what was updated/generated>
Evidence:
- `Scopes/INDEX.md` | `Scopes/GRAPH.md` | `Scopes/Product/...` (as applicable)
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. run scope-auditor or proceed to implement>
Artifact: (none)
```
