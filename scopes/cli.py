#!/usr/bin/env python3
"""scopes/cli.py — Thin entry point for the Scopes CLI.

Wires argparse subcommands to command implementations in scopes/scripts/.

Invocation:
  python3 scopes/cli.py <command> [args...]
  alias scopes="python3 /path/to/scopes/cli.py"
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import dedent

# Ensure scopes/scripts/ is on the path before any local imports.
_SCRIPTS_DIR = Path(__file__).resolve().parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from cli_helpers import (  # noqa: E402
    CliContext,
    VERSION,
    _error,
    _find_project_root,
    _resolve_scopes_root,
    _scripts_dir,
)
from cmd_bridges import (  # noqa: E402
    cmd_contract,
    cmd_create,
    cmd_drift,
    cmd_hotspot,
    cmd_map,
    cmd_move,
    cmd_rename,
    cmd_trace,
    cmd_validate,
)
from cmd_general import (  # noqa: E402
    cmd_commands,
    cmd_help,
    cmd_init,
    cmd_profiles,
    cmd_scopes,
    cmd_templates,
    cmd_version,
)
from cmd_links import (  # noqa: E402
    cmd_areas,
    cmd_backlinks,
    cmd_evidence,
    cmd_graph_impact,
    cmd_orphans,
    cmd_status,
    cmd_unresolved,
)
from cmd_read import (  # noqa: E402
    cmd_locate,
    cmd_read,
    cmd_read_code,
    cmd_read_evidence,
    cmd_search,
)
from cmd_sync import cmd_history, cmd_sync_status  # noqa: E402
from cmd_work import (  # noqa: E402
    cmd_agents,
    cmd_session_read,
    cmd_session_start,
    cmd_skills,
    cmd_task_create,
    cmd_tasks,
)


def main() -> int:
    root_parser = argparse.ArgumentParser(
        prog="scopes",
        description="Scopes CLI — Knowledge Graph Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
            Examples:
              scopes help
              scopes version
              scopes map --query "auth" --limit 5
              scopes drift --all --stale-only
              scopes validate --scope "Auth/Login"
              scopes create scope="Auth/MFA" --area Auth
              scopes hotspot --top 10

            Use: scopes COMMAND --help  for detailed options
        """).strip(),
    )

    root_parser.add_argument(
        "--project", type=Path, default=None,
        help="Project root (auto-detected if not specified).",
    )
    root_parser.add_argument(
        "--format", choices=["json", "compact"], default="json",
        help="Output format (default: json).",
    )
    root_parser.add_argument(
        "-H", dest="format_compact", action="store_true",
        help="Alias for --format compact (human-readable).",
    )

    subparsers = root_parser.add_subparsers(dest="command", help="Subcommand")

    # ─────────────────────────────────────────────────────────────────────
    # General Commands
    # ─────────────────────────────────────────────────────────────────────

    help_parser = subparsers.add_parser("help", help="Show help (all commands or specific)")
    help_parser.add_argument("command", nargs="?", default=None, help="Specific command for details")
    help_parser.set_defaults(func=cmd_help)

    subparsers.add_parser("commands", help="Alias for help").set_defaults(func=cmd_commands)
    subparsers.add_parser("version", help="Show version and project info").set_defaults(func=cmd_version)

    # ─────────────────────────────────────────────────────────────────────
    # Scope Operations
    # ─────────────────────────────────────────────────────────────────────

    scopes_parser = subparsers.add_parser("scopes", help="List all scopes")
    scopes_parser.add_argument("--area", default=None, help="Filter by area")
    scopes_parser.add_argument("--limit", type=int, default=0, help="Limit results")
    scopes_parser.set_defaults(func=cmd_scopes)

    map_parser = subparsers.add_parser("map", help="Matrix view of scopes")
    map_parser.add_argument("--query", default="", help="Search query")
    map_parser.add_argument("--limit", type=int, default=0, help="Limit results")
    map_parser.add_argument("--area", action="append", help="Filter by area (repeatable)")
    map_parser.add_argument("--depth", type=int, default=0, help="Tree depth")
    map_parser.add_argument("--from-artifact", default="", help="Route from artifact")
    map_parser.add_argument("--only", default="", help="Output format (tree|matrix|...)")
    map_parser.add_argument("--no-summary", action="store_true", help="Omit summaries")
    map_parser.add_argument("--no-evidence", action="store_true", help="Omit evidence")
    map_parser.add_argument("--scope", default="", help="Single scope")
    map_parser.set_defaults(func=cmd_map)

    create_parser = subparsers.add_parser("create", help="Create scope skeleton")
    create_parser.add_argument("--scope", default="", help="Scope name (Area/Capability format)")
    create_parser.add_argument("--area", default="", help="Area name")
    create_parser.add_argument("--capability", default="", help="Capability name")
    create_parser.add_argument("--item", action="append", help="Add item (repeatable)")
    create_parser.add_argument("--items-file", default="", help="Load items from file")
    create_parser.add_argument("--items-json", default="", help="Load items from JSON")
    create_parser.add_argument("--micro", action="store_true", help="Create micro-scopes")
    create_parser.add_argument("--micro-scope", action="append", help="Micro-scope (repeatable)")
    create_parser.add_argument("--micro-limit", type=int, default=0, help="Micro limit")
    create_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    create_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    create_parser.add_argument("--template", default="", help="Template name")
    create_parser.set_defaults(func=cmd_create)

    # ─────────────────────────────────────────────────────────────────────
    # Validation & Maintenance
    # ─────────────────────────────────────────────────────────────────────

    validate_parser = subparsers.add_parser("validate", help="Validate scope evidence")
    validate_parser.add_argument("--scope", action="append", help="Scope (repeatable)")
    validate_parser.add_argument("--area", default="", help="Filter by area")
    validate_parser.add_argument("--all", action="store_true", help="Validate all")
    validate_parser.add_argument("--allow-stale", action="store_true", help="Allow stale")
    validate_parser.set_defaults(func=cmd_validate)

    drift_parser = subparsers.add_parser("drift", help="Find stale scope evidence")
    drift_parser.add_argument("--scope", default="", help="Single scope")
    drift_parser.add_argument("--area", default="", help="Filter by area")
    drift_parser.add_argument("--all", action="store_true", help="All scopes")
    drift_parser.add_argument("--stale-only", action="store_true", help="Show only stale")
    drift_parser.add_argument("--days", type=int, default=0, help="Stale threshold (days)")
    drift_parser.add_argument("--limit", type=int, default=0, help="Limit results")
    drift_parser.set_defaults(func=cmd_drift)

    trace_parser = subparsers.add_parser("trace", help="Trace scope from entrypoints")
    trace_parser.add_argument("scope", nargs="*", help="Scope(s) to trace")
    trace_parser.add_argument("--desc", default="", help="Description")
    trace_parser.add_argument("--allow-missing-lines", action="store_true", help="Allow missing lines")
    trace_parser.add_argument("--apply", action="store_true", help="Apply changes")
    trace_parser.set_defaults(func=cmd_trace)

    # ─────────────────────────────────────────────────────────────────────
    # Refactoring
    # ─────────────────────────────────────────────────────────────────────

    rename_parser = subparsers.add_parser("rename", help="Rename scope with link rewriting")
    rename_parser.add_argument("--scope", default="", help="Scope to rename")
    rename_parser.add_argument("--to", default="", help="New name")
    rename_parser.add_argument("--map", default="", help="Bulk rename map file")
    rename_parser.add_argument("--apply", action="store_true", help="Apply changes")
    rename_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    rename_parser.add_argument("--update-plain", action="store_true", help="Update plain text")
    rename_parser.add_argument("--strict", action="store_true", help="Strict mode")
    rename_parser.set_defaults(func=cmd_rename)

    move_parser = subparsers.add_parser("move", help="Move scope with link rewriting")
    move_parser.add_argument("--scope", default="", help="Scope to move")
    move_parser.add_argument("--to", default="", help="New location")
    move_parser.add_argument("--map", default="", help="Bulk move map file")
    move_parser.add_argument("--apply", action="store_true", help="Apply changes")
    move_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    move_parser.add_argument("--update-plain", action="store_true", help="Update plain text")
    move_parser.add_argument("--strict", action="store_true", help="Strict mode")
    move_parser.set_defaults(func=cmd_move)

    contract_parser = subparsers.add_parser("contract", help="Build slice contract")
    contract_parser.add_argument("--from-drift", default="", help="Build from drift file")
    contract_parser.add_argument("--from-skeletons", default="", help="Build from skeletons file")
    contract_parser.add_argument("--infer", action="store_true", help="Infer from code")
    contract_parser.add_argument("--scope", default="", help="Single scope")
    contract_parser.add_argument("--target", default="", help="Target module")
    contract_parser.add_argument("--limit", type=int, default=0, help="Limit results")
    contract_parser.set_defaults(func=cmd_contract)

    # ─────────────────────────────────────────────────────────────────────
    # Analysis
    # ─────────────────────────────────────────────────────────────────────

    hotspot_parser = subparsers.add_parser("hotspot", help="Find hot files in codebase")
    hotspot_parser.add_argument("--top", type=int, default=10, help="Top N files")
    hotspot_parser.add_argument("--since-days", type=int, default=30, help="Days to look back")
    hotspot_parser.add_argument("--ext", action="append", help="File extensions (repeatable)")
    hotspot_parser.add_argument("--exclude-dir", action="append", help="Exclude dirs (repeatable)")
    hotspot_parser.set_defaults(func=cmd_hotspot)

    # ─────────────────────────────────────────────────────────────────────
    # Scope Reading
    # ─────────────────────────────────────────────────────────────────────

    read_parser = subparsers.add_parser("read", help="Read scope document")
    read_parser.add_argument("--scope", required=True, help="Scope name")
    read_parser.add_argument("--section", default="", help="Section name")
    read_parser.set_defaults(func=cmd_read)

    read_evidence_parser = subparsers.add_parser("read:evidence", help="Extract evidence links")
    read_evidence_parser.add_argument("--scope", required=True, help="Scope name")
    read_evidence_parser.add_argument("--section", default="", help="Section name")
    read_evidence_parser.set_defaults(func=cmd_read_evidence)

    read_code_parser = subparsers.add_parser("read:code", help="Follow evidence, get code snippets")
    read_code_parser.add_argument("--scope", required=True, help="Scope name")
    read_code_parser.add_argument("--section", default="", help="Section name")
    read_code_parser.set_defaults(func=cmd_read_code)

    # ─────────────────────────────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────────────────────────────

    search_parser = subparsers.add_parser("search", help="Full-text search")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Limit results")
    search_parser.set_defaults(func=cmd_search)

    locate_parser = subparsers.add_parser("locate", help="Intent-based routing")
    locate_parser.add_argument("--intent", required=True, help="What you want to do")
    locate_parser.add_argument("--limit", type=int, default=5, help="Limit results")
    locate_parser.set_defaults(func=cmd_locate)

    # ─────────────────────────────────────────────────────────────────────
    # Evidence & Links
    # ─────────────────────────────────────────────────────────────────────

    evidence_parser = subparsers.add_parser("evidence", help="Evidence report")
    evidence_parser.add_argument("--scope", required=True, help="Scope name")
    evidence_parser.set_defaults(func=cmd_evidence)

    backlinks_parser = subparsers.add_parser("backlinks", help="Find referencing scopes")
    backlinks_parser.add_argument("--scope", required=True, help="Scope name")
    backlinks_parser.set_defaults(func=cmd_backlinks)

    # ─────────────────────────────────────────────────────────────────────
    # Status & Info
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("status", help="Project dashboard").set_defaults(func=cmd_status)
    subparsers.add_parser("areas", help="List all areas").set_defaults(func=cmd_areas)
    subparsers.add_parser("orphans", help="Scopes with no backlinks").set_defaults(func=cmd_orphans)
    subparsers.add_parser("unresolved", help="Broken evidence links").set_defaults(func=cmd_unresolved)

    graph_impact_parser = subparsers.add_parser("graph:impact", help="What scopes are affected if X changes?")
    graph_impact_parser.add_argument("--scope", required=True, help="Scope name")
    graph_impact_parser.set_defaults(func=cmd_graph_impact)

    # ─────────────────────────────────────────────────────────────────────
    # Sessions
    # ─────────────────────────────────────────────────────────────────────

    session_start_parser = subparsers.add_parser("session:start", help="Create session log")
    session_start_parser.add_argument("--scope", default="", help="Scope anchor")
    session_start_parser.add_argument("--goal", required=True, help="Session goal")
    session_start_parser.set_defaults(func=cmd_session_start)

    subparsers.add_parser("session:read", help="Read current session").set_defaults(func=cmd_session_read)

    # ─────────────────────────────────────────────────────────────────────
    # Tasks
    # ─────────────────────────────────────────────────────────────────────

    tasks_parser = subparsers.add_parser("tasks", help="List tasks")
    tasks_parser.add_argument("--scope", default="", help="Filter by scope")
    tasks_parser.add_argument("--status", default="", help="Filter by status")
    tasks_parser.set_defaults(func=cmd_tasks)

    task_create_parser = subparsers.add_parser("task:create", help="Create task")
    task_create_parser.add_argument("--scope", required=True, help="Scope name")
    task_create_parser.add_argument("--title", required=True, help="Task title")
    task_create_parser.set_defaults(func=cmd_task_create)

    # ─────────────────────────────────────────────────────────────────────
    # Agents & Skills
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("agents", help="List agents").set_defaults(func=cmd_agents)
    subparsers.add_parser("skills", help="List skills").set_defaults(func=cmd_skills)

    # ─────────────────────────────────────────────────────────────────────
    # Init
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("init", help="Initialize Scopes structure").set_defaults(func=cmd_init)

    # ─────────────────────────────────────────────────────────────────────
    # Sync & History
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("sync:status", help="Sync dashboard").set_defaults(func=cmd_sync_status)

    history_parser = subparsers.add_parser("history", help="Git history for scope")
    history_parser.add_argument("--scope", required=True, help="Scope name")
    history_parser.add_argument("--limit", type=int, default=10, help="Limit commits")
    history_parser.set_defaults(func=cmd_history)

    # ─────────────────────────────────────────────────────────────────────
    # Profiles & Templates
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("profiles", help="List available profiles").set_defaults(func=cmd_profiles)

    templates_parser = subparsers.add_parser("templates", help="List available templates")
    templates_parser.add_argument("--type", default="", help="Filter by type")
    templates_parser.set_defaults(func=cmd_templates)

    # ─────────────────────────────────────────────────────────────────────
    # Parse and dispatch
    # ─────────────────────────────────────────────────────────────────────

    args = root_parser.parse_args()

    if args.format_compact:
        args.format = "compact"

    if not hasattr(args, "func"):
        root_parser.print_help()
        return 0

    try:
        project_root = args.project or _find_project_root()
        scopes_root = _resolve_scopes_root(project_root)
        scripts_dir = _scripts_dir()

        ctx = CliContext(
            project_root=project_root,
            scopes_root=scopes_root,
            scripts_dir=scripts_dir,
            format=args.format,
        )

        return args.func(ctx, args)
    except FileNotFoundError as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
    except Exception as e:
        print(_error(f"Unexpected error: {str(e)}"), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
