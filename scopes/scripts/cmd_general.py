"""scopes/scripts/cmd_general.py — General commands: help, version, scopes, init, profiles, templates."""
from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

from cli_helpers import (
    VERSION,
    CliContext,
    _all_scope_files,
    _error,
    _extract_title,
    _json_out,
    _run,
)


_COMMAND_HELP: dict[str, str] = {
    "map":           "scopes map [--query TEXT] [--limit N] [--area AREA] [--depth N] [--only tree|matrix] [--no-summary] [--no-evidence]\n  Matrix/tree view of all scopes. Use --query to filter by keyword.",
    "drift":         "scopes drift [--scope X] [--area AREA] [--all] [--stale-only] [--days N] [--limit N]\n  Detect stale scope evidence via git timestamps.",
    "validate":      "scopes validate [--scope X] [--area AREA] [--all] [--allow-stale]\n  Validate all scope evidence links for structural correctness.",
    "create":        "scopes create [--scope Area/Name] [--area A] [--capability C] [--item I] [--micro] [--dry-run] [--force]\n  Create one or more scope skeleton files.",
    "trace":         "scopes trace SCOPE [SCOPE...] [--desc TEXT] [--apply] [--allow-missing-lines]\n  Generate trace-stub tables from entrypoints for the given scopes.",
    "rename":        "scopes rename --scope X --to Y [--apply] [--dry-run] [--strict]\n  Rename a scope and rewrite all links pointing to it.",
    "move":          "scopes move --scope X --to Y [--apply] [--dry-run]\n  Alias for rename; implies a directory change.",
    "contract":      "scopes contract [--from-drift FILE] [--from-skeletons FILE] [--infer] [--scope X] [--limit N]\n  Build a Slice Contract from drift output or skeleton list.",
    "hotspot":       "scopes hotspot [--top N] [--since-days N] [--ext EXT] [--exclude-dir DIR]\n  Show files with the most git churn over the given window.",
    "read":          "scopes read --scope X [--section HEADING]\n  Read a scope document. Add --section to extract one section.",
    "read:evidence": "scopes read:evidence --scope X [--section HEADING]\n  List all evidence links in a scope (or one section).",
    "read:code":     "scopes read:code --scope X [--section HEADING]\n  Follow every evidence link and return the referenced code snippets.",
    "search":        "scopes search --query TEXT [--limit N]\n  Full-text search across all scope documents.",
    "locate":        "scopes locate --intent TEXT [--limit N]\n  Score and rank scopes by how well they match a free-text intent.",
    "evidence":      "scopes evidence --scope X\n  Full evidence report: each link's target, line range, staleness status.",
    "backlinks":     "scopes backlinks --scope X\n  List every other scope that references this one.",
    "status":        "scopes status\n  Project dashboard: scope count, areas, stale count, health.",
    "areas":         "scopes areas\n  List all scope areas with scope counts.",
    "orphans":       "scopes orphans\n  Scopes with no incoming references from any other scope.",
    "unresolved":    "scopes unresolved\n  Evidence links that point to missing or out-of-range files.",
    "session:start": "scopes session:start --goal TEXT [--scope X]\n  Create a new session log under Scopes/Work/Notes/.",
    "session:read":  "scopes session:read\n  Print the current (or most recent) session log.",
    "tasks":         "scopes tasks [--scope X] [--status STATUS]\n  List task files. Filterable by scope or status.",
    "task:create":   "scopes task:create --scope X --title TEXT\n  Create a new task file anchored to a scope.",
    "agents":        "scopes agents\n  List all agents with id and description.",
    "skills":        "scopes skills\n  List all skills with id and description.",
    "init":          "scopes init\n  Initialize Scopes/ directory structure for a new project.",
    "sync:status":   "scopes sync:status\n  Sync dashboard: last sync, total scopes, stale count, health.",
    "history":       "scopes history --scope X [--limit N]\n  Git log for a specific scope file.",
    "profiles":      "scopes profiles\n  List available project-type profiles.",
    "templates":     "scopes templates [--type TYPE]\n  List available scope/task/ADR templates.",
    "scopes":        "scopes scopes [--area AREA] [--limit N]\n  List all scope files. Filter by area.",
    "version":       "scopes version\n  Print version, project root, scope count, last sync timestamp.",
    "graph:impact":  "scopes graph:impact --scope X\n  List all scopes that depend on X (direct dependents).",
}


def cmd_help(ctx: CliContext, args) -> int:
    if hasattr(args, 'command') and args.command:
        cmd = args.command
        if cmd in _COMMAND_HELP:
            print(f"\n{cmd}\n" + "─" * len(cmd))
            print(_COMMAND_HELP[cmd])
        else:
            print(f"Unknown command: {cmd}")
            print("Run: scopes help  for a full list")
            return 1
        return 0
    else:
        help_text = dedent("""
            Scopes CLI v{} — Knowledge Graph Management

            General Commands:
              help [COMMAND]        Show help (this message or detailed)
              version               Show version and project info
              commands              Alias for help

            Scope Operations (browse):
              scopes                List all scopes
              map [OPTIONS]         Matrix view of scopes
              create SCOPE          Create new scope skeleton

            Validation & Maintenance:
              validate [OPTIONS]    Validate all scope evidence
              drift [OPTIONS]       Find stale scope evidence
              trace SCOPE           Trace scope from entrypoints

            Refactoring:
              rename SCOPE --to NEW Rename scope with link rewriting
              move SCOPE --to NEW   Move scope with link rewriting
              contract [OPTIONS]    Build slice contract

            Analysis:
              hotspot [OPTIONS]     Find hot files in codebase

            Use: scopes COMMAND --help  for detailed options
        """).strip().format(VERSION)
        print(help_text)
        return 0


def cmd_commands(ctx: CliContext, args) -> int:
    return cmd_help(ctx, args)


def cmd_version(ctx: CliContext, args) -> int:
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        count = len(all_scopes)

        last_sync = "unknown"
        try:
            result = _run(
                ["git", "log", "-1", "--format=%aI", str(ctx.scopes_root)],
                cwd=str(ctx.project_root),
            )
            if result.returncode == 0 and result.stdout.strip():
                last_sync = result.stdout.strip()[:19]
        except Exception:
            pass

        output = {
            "version": VERSION,
            "project_root": str(ctx.project_root),
            "scopes_root": str(ctx.scopes_root),
            "scope_count": count,
            "last_sync": last_sync,
        }

        if ctx.format == "json":
            print(_json_out(output))
        else:
            print(f"Scopes CLI v{VERSION}")
            print(f"Project: {ctx.project_root}")
            print(f"Scopes: {count} documented")
            print(f"Last sync: {last_sync}")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_scopes(ctx: CliContext, args) -> int:
    try:
        all_files = _all_scope_files(ctx.scopes_product)

        scopes_list = []
        for f in all_files:
            rel = f.relative_to(ctx.scopes_product)
            title = _extract_title(f) or rel.stem
            area = rel.parts[0] if rel.parts else "Root"

            if hasattr(args, 'area') and args.area and args.area != area:
                continue

            scopes_list.append({
                "path": rel.as_posix(),
                "title": title,
                "area": area,
                "status": "pending",
            })

        if hasattr(args, 'limit') and args.limit:
            scopes_list = scopes_list[:args.limit]

        if ctx.format == "json":
            print(_json_out(scopes_list))
        else:
            for scope in scopes_list:
                print(f"{scope['path']:50} {scope['area']:20} {scope['title']}")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_init(ctx: CliContext, args) -> int:
    try:
        scopes_root = ctx.scopes_root

        dirs = [
            scopes_root / "Product",
            scopes_root / "Work" / "Tasks",
            scopes_root / "Work" / "Notes",
            scopes_root / "Work" / "Bugs",
            scopes_root / "Work" / "Planning",
            scopes_root / "Onboarding",
            ctx.scopes_root.parent / ".scopes",
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        index_file = scopes_root / "INDEX.md"
        if not index_file.exists():
            index_file.write_text(dedent("""---
title: Scopes Index
description: Knowledge graph for this project
---

# Scopes Index

## Areas

### (Add your areas here)

Use `scopes map` to view all scopes.
""").strip())

        graph_file = scopes_root / "GRAPH.md"
        if not graph_file.exists():
            graph_file.write_text(dedent("""---
title: Scopes Dependency Graph
description: Cross-scope relationships
---

# Dependency Graph

| From | To | Type | Evidence |
|------|----|----|----------|

Use `scopes graph` to update this.
""").strip())

        gitignore_file = ctx.project_root / ".gitignore"
        gitignore_content = gitignore_file.read_text() if gitignore_file.exists() else ""
        if ".scopes/" not in gitignore_content:
            gitignore_content += "\n.scopes/\n"
            gitignore_file.write_text(gitignore_content)

        if ctx.format == "json":
            print(_json_out({"status": "initialized", "scopes_root": str(scopes_root)}))
        else:
            print("✓ Scopes structure initialized")
            print(f"  Created: {scopes_root}/Product/")
            print(f"  Created: {scopes_root}/Work/Tasks/")
            print(f"  Next: Run `scopes create --scope Area/Feature`")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_profiles(ctx: CliContext, args) -> int:
    try:
        profiles = [
            {
                "id": "python-api",
                "name": "Python API",
                "description": "Python API with routes, models, services",
            },
            {
                "id": "fullstack",
                "name": "Full Stack",
                "description": "Frontend + backend + database",
            },
            {
                "id": "data-pipeline",
                "name": "Data Pipeline",
                "description": "Data processing and ETL workflows",
            },
        ]

        print(_json_out(profiles))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_templates(ctx: CliContext, args) -> int:
    try:
        templates = [
            {
                "id": "capability",
                "name": "Capability Scope",
                "type": "scope",
                "description": "Standard capability scope template",
            },
            {
                "id": "micro",
                "name": "Micro-scope",
                "type": "scope",
                "description": "Small focused scope",
            },
            {
                "id": "task",
                "name": "Task",
                "type": "task",
                "description": "Work task template",
            },
            {
                "id": "adr",
                "name": "Architecture Decision Record",
                "type": "adr",
                "description": "ADR for major decisions",
            },
        ]

        template_type = getattr(args, 'type', '')
        if template_type:
            templates = [t for t in templates if t['type'] == template_type]

        print(_json_out(templates))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
