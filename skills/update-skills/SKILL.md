---
name: update-skills
description: 'Updates the installed Scopes skills (not commands) in this project. Use when you want to refresh Skills under .cursor/.claude/.agent.'
disable-model-invocation: true
---

# Update Scopes Skills

This skill refreshes **Skills only** (not `.cursor/commands`).

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

- This skill is self-contained. It updates skills by cloning the ScopesCommands repo and regenerating skills from `commands/*.md`, plus syncing any bundled skill folders under `skills/`.
- If your project doesn’t have the `update-skills` skill yet, re-run the interactive installer (`./install-scopes.sh`) and choose **Skills** (or **Both**).

