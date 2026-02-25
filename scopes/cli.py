#!/usr/bin/env python3
"""scopes/cli.py — Unified CLI for Scopes knowledge graph management.

A single Python file (zero external dependencies) that wires all existing
scripts and provides a cohesive interface for the Scopes layer.

Architecture:
  - main()              ← argparse root + subparsers
  - cmd_*()             ← one per command (bridges to existing scripts or new logic)
  - Helper functions    ← scope resolution, output formatting, subprocess wrappers

Invocation:
  python3 scopes/cli.py <command> [args...]
  alias scopes="python3 /path/to/scopes/cli.py"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from textwrap import dedent


# ─────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────

VERSION = "0.1.0"
SCOPES_DIR_NAME = "Scopes"
INDEX_FILE_NAME = "INDEX.md"


# ─────────────────────────────────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class CliContext:
    """Execution context for a CLI invocation."""
    project_root: Path
    scopes_root: Path
    scripts_dir: Path
    format: str = "json"  # json | compact

    @property
    def scopes_product(self) -> Path:
        """Path to Scopes/Product/."""
        return self.scopes_root / "Product"


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Project Resolution
# ─────────────────────────────────────────────────────────────────────────

def _find_project_root(start_path: Path = None) -> Path:
    """Walk up from start_path looking for Scopes/INDEX.md or Scopes/."""
    start = Path(start_path or os.getcwd())
    current = start.resolve()

    for _ in range(50):  # safety limit
        if (current / SCOPES_DIR_NAME / INDEX_FILE_NAME).exists():
            return current
        if (current / SCOPES_DIR_NAME).is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    raise FileNotFoundError(
        f"No {SCOPES_DIR_NAME}/ found walking up from {start.resolve()}. "
        f"Run: scopes init"
    )


def _resolve_scopes_root(project_root: Path) -> Path:
    """Return path to Scopes/ directory."""
    scopes_root = project_root / SCOPES_DIR_NAME
    if not scopes_root.is_dir():
        raise FileNotFoundError(f"Scopes directory not found: {scopes_root}")
    return scopes_root


def _scripts_dir() -> Path:
    """Return path to scopes/skills/*/scripts directory (root of script locations)."""
    cli_file = Path(__file__).resolve()
    scopes_dir = cli_file.parent
    return scopes_dir


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Scope Resolution (wikilink-style)
# ─────────────────────────────────────────────────────────────────────────

def _all_scope_files(scopes_product: Path) -> list[Path]:
    """Recursively find all .md files under Scopes/Product/."""
    return sorted(scopes_product.glob("**/*.md"))


def _normalize_slug(s: str) -> str:
    """Normalize name for slug matching (lowercase, underscores → hyphens)."""
    return s.lower().replace("_", "-").replace(" ", "-")


def _resolve_scope(scopes_product: Path, scope_name: str) -> Path:
    """Resolve scope by name to file path.

    Resolution order:
    1. Exact match (case-insensitive) in Scopes/Product/**/
    2. Slug match (underscores/hyphens normalized)
    3. Substring match (unique prefix)
    4. Ambiguous → error with candidates

    Args:
        scopes_product: path to Scopes/Product/
        scope_name: wikilink-style name (e.g. "Auth/Login" or "Login")

    Returns:
        Path to scope file

    Raises:
        FileNotFoundError: if not found or ambiguous
    """
    all_files = _all_scope_files(scopes_product)
    scope_name_lower = scope_name.lower()
    scope_slug = _normalize_slug(scope_name)

    # Pass 1: Exact relative path match (case-insensitive)
    for f in all_files:
        rel = f.relative_to(scopes_product).as_posix().lower()
        stem = rel.replace(".md", "")
        if stem == scope_name_lower or stem.endswith("/" + scope_name_lower):
            return f

    # Pass 2: Slug match
    for f in all_files:
        rel = f.relative_to(scopes_product).as_posix().lower()
        stem = rel.replace(".md", "")
        stem_slug = _normalize_slug(stem)
        if stem_slug == scope_slug or stem_slug.endswith("/" + scope_slug):
            return f

    # Pass 3: Substring match (file name only, case-insensitive)
    candidates = []
    for f in all_files:
        rel = f.relative_to(scopes_product).as_posix()
        rel_lower = rel.lower()
        if scope_name_lower in rel_lower:
            candidates.append(f)

    if len(candidates) == 1:
        return candidates[0]
    elif candidates:
        raise FileNotFoundError(
            f"Ambiguous scope name '{scope_name}'. Candidates:\n"
            + "\n".join(f"  {c.relative_to(scopes_product)}" for c in candidates)
        )

    raise FileNotFoundError(
        f"Scope not found: {scope_name}. Run: scopes scopes"
    )


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Output Formatting
# ─────────────────────────────────────────────────────────────────────────

def _json_out(data: dict | list) -> str:
    """Format data as JSON."""
    return json.dumps(data, indent=2)


def _error(message: str, hint: str = "", scope: str = "", **kwargs) -> str:
    """Format an error as JSON."""
    err = {"error": message}
    if hint:
        err["hint"] = hint
    if scope:
        err["scope"] = scope
    err.update(kwargs)
    return _json_out(err)


def _run(cmd: list[str], cwd: str = ".") -> subprocess.CompletedProcess:
    """Run a command and return result."""
    try:
        return subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Command timed out: {' '.join(cmd)}") from e
    except Exception as e:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{e}") from e


# ─────────────────────────────────────────────────────────────────────────
# Commands: Phase 1 — General & Script Bridges
# ─────────────────────────────────────────────────────────────────────────

def cmd_help(ctx: CliContext, args) -> int:
    """scopes help [command] — Show help for all or specific command."""
    # For now, print built-in help
    if hasattr(args, 'command') and args.command:
        # Detailed help for specific command
        print(f"Help for: {args.command}")
        print("(Phase 1 stub)")
        return 0
    else:
        # List all commands grouped by category
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
    """scopes commands — Alias for help."""
    return cmd_help(ctx, args)


def cmd_version(ctx: CliContext, args) -> int:
    """scopes version — Show version, project path, scope count, last sync."""
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        count = len(all_scopes)

        # Try to get last sync timestamp from git
        last_sync = "unknown"
        try:
            result = _run(
                ["git", "log", "-1", "--format=%aI", str(ctx.scopes_root)],
                cwd=str(ctx.project_root),
            )
            if result.returncode == 0 and result.stdout.strip():
                last_sync = result.stdout.strip()[:19]  # YYYY-MM-DDTHH:MM:SS
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
        else:  # compact
            print(f"Scopes CLI v{VERSION}")
            print(f"Project: {ctx.project_root}")
            print(f"Scopes: {count} documented")
            print(f"Last sync: {last_sync}")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_scopes(ctx: CliContext, args) -> int:
    """scopes scopes — List all scopes with optional filters."""
    try:
        all_files = _all_scope_files(ctx.scopes_product)

        scopes_list = []
        for f in all_files:
            rel = f.relative_to(ctx.scopes_product)
            title = _extract_title(f) or rel.stem
            area = rel.parts[0] if rel.parts else "Root"

            # Filter by area if provided
            if hasattr(args, 'area') and args.area and args.area != area:
                continue

            scopes_list.append({
                "path": rel.as_posix(),
                "title": title,
                "area": area,
                "status": "pending",  # Phase 2: detect staleness
            })

        # Apply limit if provided
        if hasattr(args, 'limit') and args.limit:
            scopes_list = scopes_list[:args.limit]

        if ctx.format == "json":
            print(_json_out(scopes_list))
        else:  # compact
            for scope in scopes_list:
                print(f"{scope['path']:50} {scope['area']:20} {scope['title']}")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_map(ctx: CliContext, args) -> int:
    """scopes map — Matrix view of scopes (wraps scope_map.py)."""
    try:
        # Import and call scope_map.py
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from scope_map import main as scope_map_main  # type: ignore[import]

        # Build args for scope_map
        map_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'query') and args.query:
            map_args.extend(["--query", args.query])
        if hasattr(args, 'limit') and args.limit:
            map_args.extend(["--limit", str(args.limit)])
        if hasattr(args, 'area') and args.area:
            for area in (args.area if isinstance(args.area, list) else [args.area]):
                map_args.extend(["--area", area])
        if hasattr(args, 'depth') and args.depth:
            map_args.extend(["--depth", str(args.depth)])
        if hasattr(args, 'from_artifact') and args.from_artifact:
            map_args.extend(["--from-artifact", args.from_artifact])
        if hasattr(args, 'only') and args.only:
            map_args.extend(["--only", args.only])
        if hasattr(args, 'no_summary') and args.no_summary:
            map_args.append("--no-summary")
        if hasattr(args, 'no_evidence') and args.no_evidence:
            map_args.append("--no-evidence")
        if hasattr(args, 'scope') and args.scope:
            map_args.extend(["--scope", args.scope])

        sys.argv = ["scope_map.py"] + map_args
        return scope_map_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_drift(ctx: CliContext, args) -> int:
    """scopes drift — Find stale scope evidence (wraps drift_detector.py)."""
    try:
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from drift_detector import main as drift_detector_main  # type: ignore[import]

        drift_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            drift_args.extend(["--scope", args.scope])
        if hasattr(args, 'area') and args.area:
            drift_args.extend(["--area", args.area])
        if hasattr(args, 'all') and args.all:
            drift_args.append("--all")
        if hasattr(args, 'stale_only') and args.stale_only:
            drift_args.append("--stale-only")
        if hasattr(args, 'days') and args.days:
            drift_args.extend(["--days", str(args.days)])
        if hasattr(args, 'limit') and args.limit:
            drift_args.extend(["--limit", str(args.limit)])

        sys.argv = ["drift_detector.py"] + drift_args
        return drift_detector_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_validate(ctx: CliContext, args) -> int:
    """scopes validate — Validate scope evidence (wraps validate_scopes.py)."""
    try:
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from validate_scopes import main as validate_scopes_main  # type: ignore[import]

        validate_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            for scope in (args.scope if isinstance(args.scope, list) else [args.scope]):
                validate_args.extend(["--scope", scope])
        if hasattr(args, 'area') and args.area:
            validate_args.extend(["--area", args.area])
        if hasattr(args, 'all') and args.all:
            validate_args.append("--all")
        if hasattr(args, 'allow_stale') and args.allow_stale:
            validate_args.append("--allow-stale")

        sys.argv = ["validate_scopes.py"] + validate_args
        return validate_scopes_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_create(ctx: CliContext, args) -> int:
    """scopes create — Create scope skeleton (wraps scope_skeleton_generator.py)."""
    try:
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from scope_skeleton_generator import main as skeleton_main  # type: ignore[import]

        create_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        # The CLI accepts --scope or --area/--capability
        if hasattr(args, 'scope') and args.scope:
            # Parse scope format: "Area/Capability" or "Area: Capability"
            scope = args.scope.strip()
            if "/" in scope:
                area, capability = scope.split("/", 1)
                create_args.extend(["--area", area.strip()])
                create_args.extend(["--capability", capability.strip()])
            elif ":" in scope:
                area, capability = scope.split(":", 1)
                create_args.extend(["--area", area.strip()])
                create_args.extend(["--capability", capability.strip()])
            else:
                create_args.extend(["--area", scope])
        elif hasattr(args, 'area') and args.area:
            create_args.extend(["--area", args.area])
            if hasattr(args, 'capability') and args.capability:
                create_args.extend(["--capability", args.capability])

        if hasattr(args, 'item') and args.item:
            for item in (args.item if isinstance(args.item, list) else [args.item]):
                create_args.extend(["--item", item])
        if hasattr(args, 'items_file') and args.items_file:
            create_args.extend(["--items-file", args.items_file])
        if hasattr(args, 'items_json') and args.items_json:
            create_args.extend(["--items-json", args.items_json])
        if hasattr(args, 'micro') and args.micro:
            create_args.append("--micro")
        if hasattr(args, 'micro_scope') and args.micro_scope:
            for ms in (args.micro_scope if isinstance(args.micro_scope, list) else [args.micro_scope]):
                create_args.extend(["--micro-scope", ms])
        if hasattr(args, 'micro_limit') and args.micro_limit:
            create_args.extend(["--micro-limit", str(args.micro_limit)])
        if hasattr(args, 'force') and args.force:
            create_args.append("--force")
        if hasattr(args, 'dry_run') and args.dry_run:
            create_args.append("--dry-run")
        if hasattr(args, 'template') and args.template:
            create_args.extend(["--template", args.template])

        sys.argv = ["scope_skeleton_generator.py"] + create_args
        return skeleton_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_contract(ctx: CliContext, args) -> int:
    """scopes contract — Build slice contract (wraps slice_contract_builder.py)."""
    try:
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from slice_contract_builder import main as contract_main  # type: ignore[import]

        contract_args = [
            "--repo-root", str(ctx.project_root),
        ]

        if hasattr(args, 'from_drift') and args.from_drift:
            contract_args.extend(["--from-drift", args.from_drift])
        if hasattr(args, 'from_skeletons') and args.from_skeletons:
            contract_args.extend(["--from-skeletons", args.from_skeletons])
        if hasattr(args, 'infer') and args.infer:
            contract_args.append("--infer")
        if hasattr(args, 'scope') and args.scope:
            contract_args.extend(["--scope", args.scope])
        if hasattr(args, 'target') and args.target:
            contract_args.extend(["--target", args.target])
        if hasattr(args, 'limit') and args.limit:
            contract_args.extend(["--limit", str(args.limit)])

        sys.argv = ["slice_contract_builder.py"] + contract_args
        return contract_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_trace(ctx: CliContext, args) -> int:
    """scopes trace — Trace scope from entrypoints (wraps scope_trace_stub_from_entrypoints.py)."""
    try:
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from scope_trace_stub_from_entrypoints import main as trace_main  # type: ignore[import]

        trace_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            for scope in (args.scope if isinstance(args.scope, list) else [args.scope]):
                trace_args.append(scope)
        if hasattr(args, 'desc') and args.desc:
            trace_args.extend(["--desc", args.desc])
        if hasattr(args, 'allow_missing_lines') and args.allow_missing_lines:
            trace_args.append("--allow-missing-lines")
        if hasattr(args, 'apply') and args.apply:
            trace_args.append("--apply")

        sys.argv = ["scope_trace_stub_from_entrypoints.py"] + trace_args
        return trace_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_rename(ctx: CliContext, args) -> int:
    """scopes rename — Rename scope with link rewriting (wraps scope_rename_guard.py)."""
    try:
        scripts_syncing = ctx.scripts_dir / "skills" / "syncing-scopes" / "scripts"
        sys.path.insert(0, str(scripts_syncing))

        from scope_rename_guard import main as rename_main  # type: ignore[import]

        rename_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'scope') and args.scope:
            rename_args.extend(["--scope", args.scope])
        if hasattr(args, 'to') and args.to:
            rename_args.extend(["--to", args.to])
        if hasattr(args, 'map') and args.map:
            rename_args.extend(["--map", args.map])
        if hasattr(args, 'apply') and args.apply:
            rename_args.append("--apply")
        if hasattr(args, 'dry_run') and args.dry_run:
            rename_args.append("--dry-run")
        if hasattr(args, 'update_plain') and args.update_plain:
            rename_args.append("--update-plain")
        if hasattr(args, 'strict') and args.strict:
            rename_args.append("--strict")

        sys.argv = ["scope_rename_guard.py"] + rename_args
        return rename_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_move(ctx: CliContext, args) -> int:
    """scopes move — Move scope with link rewriting (wraps scope_rename_guard.py)."""
    # Move is just rename with directory change semantics
    return cmd_rename(ctx, args)


def cmd_hotspot(ctx: CliContext, args) -> int:
    """scopes hotspot — Find hot files (wraps hotspot_matrix.py)."""
    try:
        scripts_scanning = ctx.scripts_dir / "skills" / "scanning-refactor" / "scripts"
        sys.path.insert(0, str(scripts_scanning))

        from hotspot_matrix import main as hotspot_main  # type: ignore[import]

        hotspot_args = [
            "--repo-root", str(ctx.project_root),
            "--format", args.format or "json",
        ]

        if hasattr(args, 'top') and args.top:
            hotspot_args.extend(["--top", str(args.top)])
        if hasattr(args, 'since_days') and args.since_days:
            hotspot_args.extend(["--since-days", str(args.since_days)])
        if hasattr(args, 'ext') and args.ext:
            for ext in (args.ext if isinstance(args.ext, list) else [args.ext]):
                hotspot_args.extend(["--ext", ext])
        if hasattr(args, 'exclude_dir') and args.exclude_dir:
            for exc in (args.exclude_dir if isinstance(args.exclude_dir, list) else [args.exclude_dir]):
                hotspot_args.extend(["--exclude-dir", exc])

        sys.argv = ["hotspot_matrix.py"] + hotspot_args
        return hotspot_main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Content Extraction
# ─────────────────────────────────────────────────────────────────────────

def _extract_title(file_path: Path) -> str:
    """Extract first H1 heading from markdown file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1) if match else ""
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    """Main CLI entry point."""
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

    help_parser = subparsers.add_parser(
        "help", help="Show help (all commands or specific)"
    )
    help_parser.add_argument(
        "command", nargs="?", default=None, help="Specific command for details"
    )
    help_parser.set_defaults(func=cmd_help)

    subparsers.add_parser(
        "commands", help="Alias for help"
    ).set_defaults(func=cmd_commands)

    subparsers.add_parser(
        "version", help="Show version and project info"
    ).set_defaults(func=cmd_version)

    # ─────────────────────────────────────────────────────────────────────
    # Scope Operations (browse)
    # ─────────────────────────────────────────────────────────────────────

    scopes_parser = subparsers.add_parser(
        "scopes", help="List all scopes"
    )
    scopes_parser.add_argument("--area", default=None, help="Filter by area")
    scopes_parser.add_argument("--limit", type=int, default=0, help="Limit results")
    scopes_parser.set_defaults(func=cmd_scopes)

    map_parser = subparsers.add_parser(
        "map", help="Matrix view of scopes"
    )
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

    create_parser = subparsers.add_parser(
        "create", help="Create scope skeleton"
    )
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

    validate_parser = subparsers.add_parser(
        "validate", help="Validate scope evidence"
    )
    validate_parser.add_argument("--scope", action="append", help="Scope (repeatable)")
    validate_parser.add_argument("--area", default="", help="Filter by area")
    validate_parser.add_argument("--all", action="store_true", help="Validate all")
    validate_parser.add_argument("--allow-stale", action="store_true", help="Allow stale")
    validate_parser.set_defaults(func=cmd_validate)

    drift_parser = subparsers.add_parser(
        "drift", help="Find stale scope evidence"
    )
    drift_parser.add_argument("--scope", default="", help="Single scope")
    drift_parser.add_argument("--area", default="", help="Filter by area")
    drift_parser.add_argument("--all", action="store_true", help="All scopes")
    drift_parser.add_argument("--stale-only", action="store_true", help="Show only stale")
    drift_parser.add_argument("--days", type=int, default=0, help="Stale threshold (days)")
    drift_parser.add_argument("--limit", type=int, default=0, help="Limit results")
    drift_parser.set_defaults(func=cmd_drift)

    trace_parser = subparsers.add_parser(
        "trace", help="Trace scope from entrypoints"
    )
    trace_parser.add_argument("scope", nargs="*", help="Scope(s) to trace")
    trace_parser.add_argument("--desc", default="", help="Description")
    trace_parser.add_argument("--allow-missing-lines", action="store_true", help="Allow missing lines")
    trace_parser.add_argument("--apply", action="store_true", help="Apply changes")
    trace_parser.set_defaults(func=cmd_trace)

    # ─────────────────────────────────────────────────────────────────────
    # Refactoring
    # ─────────────────────────────────────────────────────────────────────

    rename_parser = subparsers.add_parser(
        "rename", help="Rename scope with link rewriting"
    )
    rename_parser.add_argument("--scope", default="", help="Scope to rename")
    rename_parser.add_argument("--to", default="", help="New name")
    rename_parser.add_argument("--map", default="", help="Bulk rename map file")
    rename_parser.add_argument("--apply", action="store_true", help="Apply changes")
    rename_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    rename_parser.add_argument("--update-plain", action="store_true", help="Update plain text")
    rename_parser.add_argument("--strict", action="store_true", help="Strict mode")
    rename_parser.set_defaults(func=cmd_rename)

    move_parser = subparsers.add_parser(
        "move", help="Move scope with link rewriting"
    )
    move_parser.add_argument("--scope", default="", help="Scope to move")
    move_parser.add_argument("--to", default="", help="New location")
    move_parser.add_argument("--map", default="", help="Bulk move map file")
    move_parser.add_argument("--apply", action="store_true", help="Apply changes")
    move_parser.add_argument("--dry-run", action="store_true", help="Dry run")
    move_parser.add_argument("--update-plain", action="store_true", help="Update plain text")
    move_parser.add_argument("--strict", action="store_true", help="Strict mode")
    move_parser.set_defaults(func=cmd_move)

    contract_parser = subparsers.add_parser(
        "contract", help="Build slice contract"
    )
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

    hotspot_parser = subparsers.add_parser(
        "hotspot", help="Find hot files in codebase"
    )
    hotspot_parser.add_argument("--top", type=int, default=10, help="Top N files")
    hotspot_parser.add_argument("--since-days", type=int, default=30, help="Days to look back")
    hotspot_parser.add_argument("--ext", action="append", help="File extensions (repeatable)")
    hotspot_parser.add_argument("--exclude-dir", action="append", help="Exclude dirs (repeatable)")
    hotspot_parser.set_defaults(func=cmd_hotspot)

    # ─────────────────────────────────────────────────────────────────────
    # Parse arguments and execute
    # ─────────────────────────────────────────────────────────────────────

    args = root_parser.parse_args()

    # Handle -H flag
    if args.format_compact:
        args.format = "compact"

    # Default to help if no command given
    if not hasattr(args, "func"):
        root_parser.print_help()
        return 0

    # Resolve project root
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
