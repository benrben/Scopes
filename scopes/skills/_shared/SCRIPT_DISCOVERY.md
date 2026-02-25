# Script Discovery (DEPRECATED)

> **This file is deprecated.** Use the `scopes` CLI instead.
>
> All scripts previously accessed via `$SKILLS_ROOT` are now available
> as `scopes <command>` subcommands. Run `scopes help` to see all commands.

## Migration Guide

| Old (SKILLS_ROOT) | New (CLI) |
|---|---|
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --query ...` | `scopes map --query ...` |
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --all` | `scopes drift --all` |
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all` | `scopes validate --all` |
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_skeleton_generator.py" ...` | `scopes create ...` |
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/slice_contract_builder.py" ...` | `scopes contract ...` |
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_trace_stub_from_entrypoints.py" ...` | `scopes trace ...` |
| `python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_rename_guard.py" ...` | `scopes rename ...` |
| `python3 "$SKILLS_ROOT/scanning-refactor/scripts/hotspot_matrix.py" ...` | `scopes hotspot ...` |

## Installation

The `scopes` CLI is automatically available as:

```bash
python3 /path/to/scopes/cli.py <command>
```

Or create an alias:

```bash
alias scopes="python3 /path/to/scopes/cli.py"
```

## Quick Start

```bash
scopes help                    # List all commands
scopes version                 # Show version
scopes status                  # Project dashboard
scopes map --query "auth"      # Find scopes
scopes read scope="Auth"       # Read scope
scopes validate --all          # Validate all
```

See `scopes/skills/scopes-cli/SKILL.md` for complete documentation.
