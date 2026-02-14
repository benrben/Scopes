# Plugin Settings (Claude Code)

Claude Code supports per-repo local configuration via:

- `.claude/settings.local.json` — machine-readable settings (including environment variables)
- `.claude/settings.local.md` — prompt-style instructions that apply to the repo

This repo is the **source package** for Scopes. When you install Scopes as a Claude Code plugin, you typically set these files in the **target repo you are working in** (not inside this Scopes source repo).

## Quick start (copy templates)

Templates live here:

- `docs/templates/claude/settings.local.json`
- `docs/templates/claude/settings.local.md`

Copy them into your target repo:

```bash
mkdir -p .claude
cp docs/templates/claude/settings.local.json .claude/settings.local.json
cp docs/templates/claude/settings.local.md .claude/settings.local.md
```

## Recommended env vars

If you maintain your own fork or pinned reference, prefer configuring your install/update process outside this repo (for example in your plugin manager or your own scripts).

## Notes

- For Claude Code plugin installs, prefer script paths rooted at `$CLAUDE_PLUGIN_ROOT` so commands work regardless of where the plugin is installed.
- For manual installs (Cursor/other assistants), use the skills directory in the target project (for example `.cursor/skills/` or `.claude/skills/`).

If you need a single variable for helper scripts (used in skill/agent docs), resolve `SKILLS_ROOT` like this:

```bash
if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -d "$CLAUDE_PLUGIN_ROOT/skills" ]]; then
  SKILLS_ROOT="$CLAUDE_PLUGIN_ROOT/skills"
else
  for d in .claude/skills .cursor/skills .agent/skills skills; do
    if [[ -d "$d" ]]; then
      SKILLS_ROOT="$d"
      break
    fi
  done
fi
```
