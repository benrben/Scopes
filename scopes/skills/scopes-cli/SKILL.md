---
name: Scopes CLI
description: "Unified CLI for Scopes knowledge graph. Use for navigation, search, evidence management, session tracking, and scope maintenance."
version: "0.5.0"
activation: "When working with scopes, reading scope documentation, searching for code locations, or managing scope evidence."
---

# Scopes CLI Skill

The `scopes` command is your primary interface to the Scopes knowledge graph. Use it to navigate, search, read, and maintain scopes with evidence-backed code locations.

## Quick Start

```bash
# List all scopes
scopes scopes

# Find scopes by keyword intent
scopes locate --intent "add authentication to login flow"

# Read a scope and its evidence
scopes read scope="Auth/Login"
scopes read:code scope="Auth/Login" --section "Entry Points"

# Search across all scopes
scopes search --query "token validation"

# Check project health
scopes status
scopes orphans
scopes unresolved
```

## Command Categories

### Scope Operations (Browse & Read)

```bash
scopes read scope="Auth/Login"                    # Read full scope
scopes read scope="Auth/Login" --section "Entry Points"   # Read one section
scopes read:evidence scope="Auth/Login"           # Show evidence links
scopes read:code scope="Auth/Login"               # Follow links, show code
scopes scopes                                     # List all scopes
scopes scopes --area "Auth"                       # Filter by area
scopes areas                                      # List all areas
scopes status                                     # Project dashboard
```

### Navigation & Search

```bash
scopes map --query "auth" --limit 5               # Scope matrix view
scopes locate --intent "add rate limiting"       # Intent → scopes
scopes search --query "JWT"                       # Full-text search
scopes search:code --query "validateToken"       # Search code only
scopes backlinks scope="Auth/Login"               # What references this?
```

### Evidence & Quality

```bash
scopes evidence scope="Auth/Login"                # Evidence report
scopes evidence:verify scope="Auth/Login"         # Verify all links resolve
scopes drift --all --stale-only                   # Find stale evidence
scopes validate --all                             # Validate all scopes
scopes unresolved                                 # Broken links
scopes orphans                                    # Scopes with no backlinks
```

### Scope Management

```bash
scopes create scope="Auth/MFA"                    # Create new scope
scopes create scope="Auth/MFA" --template capability  # Use template
scopes create scope="Auth/MFA" --micro            # Create overview + micro-scopes
scopes rename scope="Auth/Login" --to "Auth/SignIn"   # Rename with rewriting
scopes move scope="Auth/Login" --to "Authentication/Login"
scopes delete scope="Auth/OldFlow"                # Delete scope
```

### Sessions & Work

```bash
scopes session:start --scope "Auth" --goal "Fix token refresh"
scopes session:read                               # Read current session
scopes session:list --limit 5                     # Recent sessions
scopes tasks                                      # List all tasks
scopes tasks --status pending                     # Filter by status
scopes task:create --scope "Auth" --title "Add rate limiting"
```

### Agents & Skills

```bash
scopes agents                                     # List all agents
scopes agent --id "slice-developer"               # Agent info
scopes skills                                     # List all skills
scopes skill --id "syncing-scopes"                # Skill info
```

### Sync & History

```bash
scopes sync:status                                # Sync dashboard
scopes history scope="Auth/Login" --limit 10      # Recent changes
scopes history:read scope="Auth/Login" --commit HEAD~1  # Past version
```

### Project Setup

```bash
scopes init                                       # Initialize new project
scopes version                                    # Version + stats
```

### Configuration

```bash
scopes profiles                                   # Available project profiles
scopes templates                                  # Available templates
scopes templates --type scope                     # Filter by type
```

## Parameter Syntax

### Scope Resolution

The `scope=` parameter resolves by name (not path):

```bash
# These all resolve the same way:
scopes read scope="Login"           # substring match
scopes read scope="Auth/Login"      # area/name
scopes read scope="login"           # case-insensitive
scopes read scope="auth-login"      # hyphens normalized
```

Resolution order:
1. Exact match (case-insensitive)
2. Slug match (underscores/hyphens normalized)
3. Substring match (unique prefix)
4. Ambiguous → error with candidates

### Line Ranges

Evidence links use line notation:

```bash
# In scope files:
[Authentication flow](src/auth.ts#L10-L45)   # lines 10 to 45
[Token validator](src/token.ts#L100)          # single line
[Something](docs/design.md)                   # whole file
```

### Output Modes

```bash
# Machine-readable (default):
scopes read scope="Auth/Login" --format json

# Human-readable:
scopes read scope="Auth/Login" -H                 # compact mode
scopes read scope="Auth/Login" --format compact
```

## Common Patterns

### Find Code Locations

```bash
# Get entry points for a scope
scopes read:code scope="Auth/Login" --section "Entry Points"

# Get test files
scopes read:code scope="Auth/Login" --section "Tests"

# Get all evidence code snippets
scopes read:code scope="Auth/Login"
```

### Audit Scope Quality

```bash
# Check what's broken
scopes unresolved

# Find orphaned scopes
scopes orphans

# Check overall health
scopes status

# Find stale evidence
scopes drift --all --stale-only --limit 20
```

### Navigate Related Scopes

```bash
# What depends on this?
scopes graph:impact scope="Auth/Login"

# What does this depend on?
scopes backlinks scope="Auth/Login"

# Dependency chain
scopes graph:path --from "Auth/Login" --to "DB/Users"
```

### Manage Work

```bash
# Start a focused session
scopes session:start --scope "Auth/MFA" --goal "Implement TOTP"

# Log findings
scopes session:append --content "- Found JWT lib in use"

# Read session
scopes session:read

# Create task for follow-up
scopes task:create --scope "Auth/MFA" --title "Add backup codes"
```

### Explore Codebase

```bash
# Find hot files (frequently changed)
scopes hotspot --top 10

# Find all evidence pointing to a pattern
scopes search:evidence --pattern "*.test.ts"

# Full-text search
scopes search --query "authentication" --limit 20
```

## Flags & Options

### Filtering

```bash
--query TEXT          Search/map query term
--scope SCOPE         Single scope (resolves by name)
--area AREA           Filter by area (repeatable)
--status STATUS       Filter by status (pending|active|done)
--limit N             Limit results (default varies by command)
```

### Evidence & Links

```bash
--section "NAME"      Work with specific section only
--lines N             Context lines for search:context
--pattern "*.ext"     File pattern for search:evidence
```

### Output

```bash
--format json         JSON output (default)
-H                    Human-readable compact output
--project /path       Explicit project root
```

### Sync & History

```bash
--all                 Process all items
--dry                 Preview changes without applying
--stale-only          Show only stale/problematic items
--since-days N        Time window filter
--commit HASH         Specific git commit
```

## Error Handling

All errors output JSON to stderr:

```json
{
  "error": "Scope not found",
  "scope": "Auth/Nonexistent",
  "hint": "Run: scopes scopes"
}
```

Exit codes:
- `0` → Success
- `1` → Error
- `2` → Partial result (e.g., drift found but non-blocking)

## Tips & Tricks

1. **Scope name matching is flexible** — use simple names (`Login`), paths (`Auth/Login`), or patterns that uniquely identify a scope.

2. **JSON output for scripting** — all commands output JSON by default, making them easy to pipe to `jq` or other tools.

3. **Use intent-based routing** — if you're not sure which scope to look at, `scopes locate --intent "what you want"` will score and rank scopes.

4. **Check health regularly** — `scopes status`, `scopes orphans`, and `scopes unresolved` give you a quick health check.

5. **Session logs for continuity** — use `scopes session:start` to create work logs that track findings and decisions across sessions.

6. **Task management is simple** — `scopes task:create` followed by `scopes tasks --status pending` keeps you organized.

## Project Structure

Scopes assumes this structure:

```
project/
├── Scopes/
│   ├── INDEX.md                 # Area index
│   ├── GRAPH.md                 # Dependency graph
│   ├── Product/
│   │   ├── Area1/
│   │   │   ├── Capability1.md
│   │   │   └── Capability2.md
│   │   └── Area2/
│   └── Work/
│       ├── Tasks/
│       ├── Notes/
│       │   └── session-*.md
│       ├── Bugs/
│       └── Planning/
└── .scopes/                     # CLI state (gitignored)
    ├── current_session
    └── bookmarks.json
```

Use `scopes init` to create this structure.

## Getting Help

```bash
scopes help                       # List all commands
scopes help <command>             # Detailed help
scopes <command> --help           # Argparse help for command
scopes version                    # Version + project info
```

## Installation (if `scopes` command not found)

The CLI is a local script — not a pip package. Run the `activate` script that lives
alongside `cli.py` in the `scopes/` folder, wherever it has been placed:

```bash
# Locate the activate script relative to this SKILL.md file, then run it:
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SKILL_DIR/../../activate"
```

Or, if you know the path to the `scopes/` folder:

```bash
bash path/to/scopes/activate          # install wrapper
source path/to/scopes/activate        # install + export SCOPES_DIR for current shell
```

**Recommended agent pre-check** — put this at the top of any runbook:

```bash
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v scopes &>/dev/null || bash "$SKILL_DIR/../../activate"
```

The script is fully location-independent and idempotent — safe to run on every boot.
`cli.py` is always resolved relative to the `activate` script itself, so it works
whether `scopes/` lives in a repo root, a skills dir, a submodule, or anywhere else.
