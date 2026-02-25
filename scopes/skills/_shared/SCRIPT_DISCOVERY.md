# Script Discovery Snippet

Resolve `SKILLS_ROOT` before invoking helper scripts:

```bash
if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -d "$CLAUDE_PLUGIN_ROOT/scopes/skills" ]]; then
  SKILLS_ROOT="$CLAUDE_PLUGIN_ROOT/scopes/skills"
elif [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -d "$CLAUDE_PLUGIN_ROOT/skills" ]]; then
  SKILLS_ROOT="$CLAUDE_PLUGIN_ROOT/skills"
else
  for d in \
    .claude/skills/scopes/skills \
    .cursor/skills/scopes/skills \
    .agent/skills/scopes/skills \
    scopes/skills \
    .claude/skills \
    .cursor/skills \
    .agent/skills \
    skills; do
    if [[ -d "$d" ]]; then
      SKILLS_ROOT="$d"
      break
    fi
  done
fi
echo "SKILLS_ROOT=$SKILLS_ROOT"
```
