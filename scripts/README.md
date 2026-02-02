# scripts/

Scripts used by **install-scopes.sh**. Do not remove them from this repo.

**What gets copied to the target project**

- **Commands only**: The installer copies **sync-scopes-commands.sh** into the target’s `./scripts/` so the user can refresh commands later (`./scripts/sync-scopes-commands.sh`).
- **Skills**: The installer **runs** update-skill.sh from the clone during install (syncs skills into `.cursor/skills` etc.). It does **not** copy update-skill.sh or update-skill into the target’s `./scripts/`. To refresh skills after install, the user runs the **bundled update-skills skill** (e.g. `bash .cursor/skills/update-skills/scripts/update-skills.sh`).

**Why these files must stay in this repo**

- **sync-scopes-commands.sh**: Copied to target for command refresh; also run during install when user chooses Commands.
- **update-skill.sh** (and **update-skill**): Run from the clone during install when user chooses Skills. Not copied to target.
