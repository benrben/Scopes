---
name: update-skills
description: Refresh installed Scopes skills in a project by syncing packaged skill folders from upstream. Use when you want the latest upstream skills locally.
compatibility: Requires `bash` + `git` and write access to `.cursor/skills`, `.claude/skills`, or `.agent/skills`.
metadata:
  short-description: Refresh installed Scopes skills in a project
  author: Scopes
  disable-model-invocation: "true"
---

# Update Scopes Skills

This skill refreshes **Skills only**.

## When to use this skill
Use this skill when your installed Scopes skills are stale and you want to refresh them locally from upstream.

## Safety and confirmations
- This workflow clones a repo and overwrites target skill folders; ask before running it if the user has local modifications they want to keep.

## Helper scripts (optional)
- `skills/update-skills/scripts/update-skills.sh`: refresh installed skills from upstream `skills/`.

## Scopes-first Policy Check (Post-update)
After syncing skills, verify that execution/planning/research skills keep this startup contract:
- Start every mission by navigating `Scopes/INDEX.md` and `Scopes/GRAPH.md`.
- Read only relevant anchor capability scopes under `Scopes/Product/**` (not all scopes).
- Follow scope trace/evidence links down into code/tests/config before acting.
- Treat `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` as supporting docs for implementation/refactoring/tooling.

## Usage

From your project root, run the script from the folder you installed this skill into:

- Cursor:

```bash
bash .cursor/skills/update-skills/scripts/update-skills.sh
```

- Claude:

```bash
bash .claude/skills/update-skills/scripts/update-skills.sh
```

- Antigravity:

```bash
bash .agent/skills/update-skills/scripts/update-skills.sh
```

### Common targets

- Cursor skills: `.cursor/skills`
- Claude skills: `.claude/skills`
- Antigravity skills: `.agent/skills`

**In Cursor**, use `.cursor/skills` only. If a link or tab opens `.claude/skills/...`, that path is for Claude; close it and use the same skill under `.cursor/skills/...`.

## Notes

- This skill is self-contained. It updates skills by cloning the Scopes repo and syncing packaged skill folders under `skills/`.
- If your project doesn’t have the `update-skills` skill yet, copy the `skills/update-skills/` folder from this repo.
