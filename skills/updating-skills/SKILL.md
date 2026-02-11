---
name: updating-skills
description: Refreshes installed Scopes skills in a project by syncing packaged skill folders from upstream. Use when the user wants the latest upstream skills, needs to update or refresh skills, or sync skill versions.
---

# Updating Skills

This skill refreshes **Skills only**.

## When to use this skill
Use when installed Scopes skills are stale and you want to refresh them locally from upstream.

## Safety and confirmations
- This workflow clones a repo and overwrites target folders; ask before running if the user has local modifications.
- Always run `--dry-run` first and keep a backup copy of the existing skills folder before syncing.

## Helper scripts
- `scripts/update-skills.sh`: Refresh installed skills from upstream `skills/`.

## Suggested Update Flow (Safe)
1. **Dry run** (see what would change): `bash <skills-root>/updating-skills/scripts/update-skills.sh --dry-run -v`
2. **Backup safety**: by default the script backs up overwritten folders under `<target>/.scopes-backups/<timestamp>/` (disable with `--no-backup`).
3. **Sync**: `bash <skills-root>/updating-skills/scripts/update-skills.sh -v`
4. **Post-update validation**:
   - Verify `skills/_shared/SCOPES_PROTOCOL.md` exists in the target skills root.
   - Spot-check one skill: confirm “Mission Start” still points to the shared protocol.
   - If your assistant caches skills/plugins, reload/restart it.

## Scopes-first Policy Check (Post-update)
After syncing skills, verify that execution/planning/research skills keep this startup contract:
- Start every mission by navigating `Scopes/INDEX.md` and `Scopes/GRAPH.md`.
- Read only relevant anchor capability scopes under `Scopes/Product/**`.
- Follow scope trace/evidence links into code/tests/config before acting.
- Treat `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as supporting docs.

## Usage

From your project root, run the script from the folder you installed this skill into:

- Cursor:
```bash
bash .cursor/skills/updating-skills/scripts/update-skills.sh
```

- Claude:
```bash
bash .claude/skills/updating-skills/scripts/update-skills.sh
```

- Antigravity:
```bash
bash .agent/skills/updating-skills/scripts/update-skills.sh
```

### Common targets
- Cursor skills: `.cursor/skills`
- Claude skills: `.claude/skills`
- Antigravity skills: `.agent/skills`

**In Cursor**, use `.cursor/skills` only. If a link opens `.claude/skills/...`, close it and use the same skill under `.cursor/skills/...`.

## Notes
- This skill is self-contained. It updates skills by cloning the Scopes repo and syncing packaged skill folders.
- If your project doesn't have this skill yet, copy `skills/updating-skills/` from the repo.
