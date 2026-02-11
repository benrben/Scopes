---
name: updating-skills
description: Refreshes installed Scopes skills in a project by syncing packaged skill folders from upstream. Use when the user wants to update or refresh their installed skills version.
---

# Updating Skills

This skill refreshes **Skills only** (and optionally `agents/` if the user requests).

## When to use this skill
Use when installed Scopes skills are stale and you want to refresh them locally from upstream.

## Prerequisites
- A target skills root directory (e.g. `.cursor/skills/`, `.claude/skills/`, `.agent/skills/`).
- Network access and git access to the upstream repo (if required by your update method).

## Safety and confirmations
- This workflow can overwrite target folders; ask before running if the user has local modifications.
- Always run `--dry-run` first and keep backups enabled unless explicitly disabled.

## Mission Start
This is a maintenance workflow, but still follow the shared protocol reference for consistency: `skills/_shared/SCOPES_PROTOCOL.md`.
Do not assume repo tooling; discover the correct skills root and update method from observable files/paths.

## Kickoff (Ask Next)
- "Where are your skills installed (e.g. `.cursor/skills/`), and should we update `agents/` too?"

## Scope Connections
- **Upstream inputs**: current installed skills directory
- **Downstream outputs**: refreshed skill folders; optional note under `Scopes/Work/Notes/**` (only if the target repo has Scopes)

## When to Stop (Mandatory)
- Stop once the update is complete and you've verified the canonical protocol file exists in the target: `skills/_shared/SCOPES_PROTOCOL.md`.
- If `--dry-run` shows unexpected deletes/overwrites, stop and ask for confirmation.

## Blocked Runbook (Mandatory)
- No network/git auth: record the exact error; set `Verdict: Blocked`; suggest the smallest credential fix.
- Target skills root unknown: set `Verdict: Needs Narrowing` and ask for the exact path.
- Local modifications detected: set `Verdict: Needs Narrowing` and ask whether to proceed, merge, or abort.

## Output Contract

Return <= 20 lines:

```markdown
## UPDATE
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of what was updated>
Evidence:
- <target skills root path>
Unknowns:
- <only if blocked/partial>
Next: <one action; e.g. reload assistant/plugin>
Artifact: (none)
```

## Suggested Update Flow (Safe)
1. Dry run: `bash <skills-root>/updating-skills/scripts/update-skills.sh --dry-run -v`
2. Backup safety: verify backups are enabled (or explicitly approved to disable).
3. Sync: `bash <skills-root>/updating-skills/scripts/update-skills.sh -v`
4. Post-update checks:
   - Verify `skills/_shared/SCOPES_PROTOCOL.md` exists in the target skills root.
   - Spot-check one skill: confirm its Mission Start references the canonical protocol path.
