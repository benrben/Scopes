---
name: syncing-scopes
description: Generates or updates Scopes documentation from code, tests, config, and schema while maintaining INDEX.md, GRAPH.md, and DEVELOPER_INFO.md with evidence-backed claims. Use when Scopes are missing, stale, or drifted from code reality.
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

## Kickoff (Ask Next)
- "Are we generating Scopes from scratch, or updating existing Scopes (and which area should we focus on first)?"

## Quick Start (Update Mode, 30 minutes)
1. Capture drift + broken links:
   - `python3 skills/syncing-scopes/scripts/drift_detector.py --all --stale-only --limit 10`
   - `python3 skills/syncing-scopes/scripts/check_evidence_links.py --broken-only --summary`
2. Pick the top 1-3 scope files to fix.
3. Update those scopes (traces + evidence + diagrams), then re-run the checks.

Common targets to keep in sync:
- `Scopes/Product/**`, `Scopes/INDEX.md`, `Scopes/GRAPH.md`, `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`

## Git Tracking Protocol (Permissioned)
- Always record `BASE_REF` (branch/sha) in the session log or plan artifact.
- Create checkpoint commits only if explicitly approved by the user.
- Diff-only fallback: if commits are not allowed, use `git diff` summaries to show what changed.

## Agent Orchestration

### Phase 1: Audit (before main work)
**Spawn `scope-auditor`:**
> Detect stale evidence, broken links, and code-doc drift across all scopes. Return SCOPE AUDIT with the worst offenders.

**Handle output:** Use the audit findings to prioritize which scopes to fix first. The worst 1-3 items become your immediate targets.

### Phase 2: Write (after main agent processes audit results)
**Spawn `scope-writer`:**
> Update these scope files: {worst items from Phase 1 audit}. Fix broken evidence links, refresh traces, and align with current code.

**Handle output:** Confirm the writer's changes address the audit findings.

### Phase 3: Re-validate (after writes complete)
**Spawn `scope-auditor`:**
> Re-validate all scopes after the recent updates. Confirm drift and broken links are resolved.

**Handle output:** If new issues are found, either fix them inline or record them for a follow-up task.

## When to Stop (Mandatory)
- Stop once validators are clean for the targeted area OR you can precisely report what is blocked and why.
- Default caps (unless user asks broader): 1-3 anchor scopes, 3-7 evidence links, 3-10 code files; label gaps as `[Unknown]`.
- If Scopes require a repo-wide regeneration beyond the budget, stop and propose a sequenced plan artifact under `Scopes/Work/Planning/**`.

## Blocked Runbook (Mandatory)
- No `Scopes/` and generation is not approved: set `Verdict: Needs Narrowing` and ask for permission/scope.
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
