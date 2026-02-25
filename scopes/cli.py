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

VERSION = "0.5.0"  # Phase 1-5 complete, Phase 6 in progress
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
# Phase 2: Core Brain Commands Helpers
# ─────────────────────────────────────────────────────────────────────────

def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown, return dict."""
    lines = content.split('\n')
    if not lines[0].startswith('---'):
        return {}
    
    end_idx = 1
    for i in range(1, len(lines)):
        if lines[i].startswith('---'):
            end_idx = i
            break
    
    fm = {}
    for line in lines[1:end_idx]:
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"\'')
    return fm


def _extract_section(content: str, section_name: str) -> str:
    """Extract markdown section by heading name."""
    pattern = rf"^##\s+{re.escape(section_name)}\s*\n(.*?)(?=^##|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _read_lines(file_path: Path, start: int = 1, end: int = None) -> str:
    """Read specific line range from a file."""
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if end is None:
            end = len(lines)
        return '\n'.join(lines[max(0, start-1):end])
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────
# Phase 2: Scope Reading Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_read(ctx: CliContext, args) -> int:
    """scopes read scope="X" — Read scope document content."""
    try:
        scope_name = getattr(args, 'scope', '')
        if not scope_name:
            print(_error("scope= parameter required"), file=sys.stderr)
            return 1
        
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")
        
        if hasattr(args, 'section') and args.section:
            content = _extract_section(content, args.section)
        
        if ctx.format == "json":
            sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
            print(_json_out({
                "scope": scope_name,
                "path": str(scope_file.relative_to(ctx.scopes_root)),
                "content": content,
                "sections": sections,
            }))
        else:
            print(content)
        
        return 0
    except FileNotFoundError as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_read_evidence(ctx: CliContext, args) -> int:
    """scopes read:evidence scope="X" — Extract evidence links."""
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")
        
        if hasattr(args, 'section') and args.section:
            content = _extract_section(content, args.section)
        
        # Parse evidence links: [text](path#L10-L20)
        evidence_re = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
        links = []
        for match in evidence_re.finditer(content):
            text, target, start_line, end_line = match.groups()
            if not target.endswith('.md'):
                links.append({
                    "target": target,
                    "start_line": int(start_line) if start_line else None,
                    "end_line": int(end_line) if end_line else None,
                    "display": text,
                })
        
        print(_json_out(links) if ctx.format == "json" else
              '\n'.join(f"{l['target']}:{l['start_line']}-{l['end_line']}" for l in links))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_read_code(ctx: CliContext, args) -> int:
    """scopes read:code scope="X" — Follow evidence links, return code snippets."""
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")
        
        if hasattr(args, 'section') and args.section:
            content = _extract_section(content, args.section)
        
        evidence_re = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
        code_blocks = []
        
        for match in evidence_re.finditer(content):
            text, target, start_line, end_line = match.groups()
            if target.endswith('.md'):
                continue
            
            target_path = ctx.project_root / target
            if not target_path.exists():
                code_blocks.append({
                    "file": target,
                    "status": "missing",
                    "code": None,
                })
                continue
            
            try:
                start = int(start_line) if start_line else 1
                end = int(end_line) if end_line else None
                code = _read_lines(target_path, start, end)
                code_blocks.append({
                    "file": target,
                    "lines": (start, end or len(target_path.read_text().splitlines())),
                    "code": code,
                    "status": "ok",
                })
            except Exception:
                code_blocks.append({
                    "file": target,
                    "status": "error",
                })
        
        print(_json_out(code_blocks))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 2: Search Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_search(ctx: CliContext, args) -> int:
    """scopes search --query "term" — Full-text search across scopes."""
    try:
        query = getattr(args, 'query', '')
        limit = getattr(args, 'limit', 0)
        if not query:
            print(_error("--query parameter required"), file=sys.stderr)
            return 1
        
        all_files = _all_scope_files(ctx.scopes_product)
        results = []
        
        for scope_file in all_files:
            content = scope_file.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(content.splitlines(), 1):
                if query.lower() in line.lower():
                    results.append({
                        "scope": str(scope_file.relative_to(ctx.scopes_product)),
                        "line": line_no,
                        "text": line.strip(),
                    })
        
        if limit:
            results = results[:limit]
        
        print(_json_out(results))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_locate(ctx: CliContext, args) -> int:
    """scopes locate --intent "..." — Intent-based scope routing."""
    try:
        intent = getattr(args, 'intent', '')
        if not intent:
            print(_error("--intent parameter required"), file=sys.stderr)
            return 1
        
        # Simple tokenization and matching
        terms = set(t.lower() for t in re.findall(r'\w+', intent) if len(t) > 2)
        all_files = _all_scope_files(ctx.scopes_product)
        
        scored = []
        for scope_file in all_files:
            try:
                content = scope_file.read_text(encoding="utf-8", errors="ignore").lower()
                title = _extract_title(scope_file).lower()
                score = sum(2 if t in title else (1 if t in content else 0) for t in terms)
                if score > 0:
                    scored.append({
                        "scope": str(scope_file.relative_to(ctx.scopes_product)),
                        "title": _extract_title(scope_file),
                        "score": score,
                    })
            except Exception:
                pass
        
        scored.sort(key=lambda x: x['score'], reverse=True)
        limit = getattr(args, 'limit', 5)
        print(_json_out(scored[:limit]))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 2: Evidence & Links Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_evidence(ctx: CliContext, args) -> int:
    """scopes evidence scope="X" — Full evidence report for a scope."""
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")
        
        evidence_re = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
        links = []
        
        for match in evidence_re.finditer(content):
            text, target, start_line, end_line = match.groups()
            if target.endswith('.md'):
                continue
            
            target_path = ctx.project_root / target
            exists = target_path.exists()
            stale = False
            
            if exists and start_line:
                try:
                    lines = target_path.read_text().splitlines()
                    in_range = int(start_line) <= len(lines)
                except Exception:
                    in_range = False
            else:
                in_range = True
            
            links.append({
                "target": target,
                "lines": (int(start_line) if start_line else None, int(end_line) if end_line else None),
                "exists": exists,
                "in_range": in_range,
                "display": text,
            })
        
        print(_json_out(links))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_backlinks(ctx: CliContext, args) -> int:
    """scopes backlinks scope="X" — Find scopes that reference this one."""
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        scope_rel = str(scope_file.relative_to(ctx.scopes_product)).replace('.md', '').replace('\\', '/')
        
        all_files = _all_scope_files(ctx.scopes_product)
        backlinks = []
        
        for other_file in all_files:
            if other_file == scope_file:
                continue
            try:
                content = other_file.read_text(encoding="utf-8", errors="ignore")
                if scope_rel in content or scope_name in content:
                    backlinks.append({
                        "scope": str(other_file.relative_to(ctx.scopes_product)),
                        "title": _extract_title(other_file),
                    })
            except Exception:
                pass
        
        print(_json_out(backlinks))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 3: Session Management Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_session_start(ctx: CliContext, args) -> int:
    """scopes session:start --scope "X" --goal "..." — Create session log."""
    try:
        scope_name = getattr(args, 'scope', '')
        goal = getattr(args, 'goal', '')
        
        # Create session in Scopes/Work/Notes/
        notes_dir = ctx.scopes_root / "Work" / "Notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import date as Date
        today = Date.today().isoformat()
        topic = scope_name.replace('/', '-').lower() or 'session'
        session_file = notes_dir / f"session-{today}-{topic}.md"
        
        content = dedent(f"""---
date: {today}
goal: {goal}
scope: {scope_name}
---

# Session: {goal or 'Work'} on {scope_name}

## Findings

## Decisions

## Next
""").strip()
        
        session_file.write_text(content)
        
        # Update current session pointer
        scopes_state = ctx.scopes_root.parent / ".scopes"
        scopes_state.mkdir(exist_ok=True)
        (scopes_state / "current_session").write_text(str(session_file))
        
        if ctx.format == "json":
            print(_json_out({
                "session": str(session_file.relative_to(ctx.scopes_root)),
                "status": "created",
            }))
        else:
            print(f"✓ Session created: {session_file}")
        
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_session_read(ctx: CliContext, args) -> int:
    """scopes session:read — Read current or specified session log."""
    try:
        scopes_state = ctx.scopes_root.parent / ".scopes"
        current_file = scopes_state / "current_session"
        
        if current_file.exists():
            session_path = Path(current_file.read_text().strip())
        else:
            # Find most recent session
            notes_dir = ctx.scopes_root / "Work" / "Notes"
            sessions = sorted(notes_dir.glob("session-*.md"), reverse=True) if notes_dir.exists() else []
            if not sessions:
                print(_error("No sessions found"), file=sys.stderr)
                return 1
            session_path = sessions[0]
        
        if not session_path.exists():
            print(_error(f"Session not found: {session_path}"), file=sys.stderr)
            return 1
        
        content = session_path.read_text(encoding="utf-8", errors="ignore")
        print(content)
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 3: Task Management Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_tasks(ctx: CliContext, args) -> int:
    """scopes tasks — List all task files."""
    try:
        tasks_dir = ctx.scopes_root / "Work" / "Tasks"
        if not tasks_dir.exists():
            print(_json_out([]))
            return 0
        
        status_filter = getattr(args, 'status', '')
        scope_filter = getattr(args, 'scope', '')
        
        tasks_list = []
        for task_file in sorted(tasks_dir.glob("**/*.md")):
            try:
                content = task_file.read_text(encoding="utf-8", errors="ignore")
                fm = _parse_frontmatter(content)
                
                if status_filter and fm.get('status') != status_filter:
                    continue
                if scope_filter and scope_filter not in fm.get('scope', ''):
                    continue
                
                tasks_list.append({
                    "id": task_file.stem,
                    "title": fm.get('title', task_file.stem),
                    "scope": fm.get('scope', ''),
                    "status": fm.get('status', 'pending'),
                    "path": str(task_file.relative_to(ctx.scopes_root)),
                })
            except Exception:
                pass
        
        print(_json_out(tasks_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_task_create(ctx: CliContext, args) -> int:
    """scopes task:create --scope "X" --title "..." — Create task file."""
    try:
        scope = getattr(args, 'scope', '')
        title = getattr(args, 'title', '')
        
        if not title:
            print(_error("--title required"), file=sys.stderr)
            return 1
        
        tasks_dir = ctx.scopes_root / "Work" / "Tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        
        from datetime import date as Date
        today = Date.today().isoformat()
        task_id = title.lower().replace(' ', '-')[:30]
        task_file = tasks_dir / f"{task_id}.md"
        
        content = dedent(f"""---
title: {title}
scope: {scope}
status: pending
created: {today}
---

# Task: {title}

## Scope
{scope}

## Description

## Acceptance Criteria

## Notes
""").strip()
        
        task_file.write_text(content)
        
        if ctx.format == "json":
            print(_json_out({"id": task_id, "status": "created"}))
        else:
            print(f"✓ Task created: {task_file}")
        
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 3: Agent & Skill Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_agents(ctx: CliContext, args) -> int:
    """scopes agents — List all agents."""
    try:
        agents_dir = ctx.scopes_root.parent / "agents"
        if not agents_dir.exists():
            print(_json_out([]))
            return 0
        
        agents_list = []
        for agent_file in sorted(agents_dir.glob("*.md")):
            if agent_file.name == "WORKFLOW.md":
                continue
            try:
                content = agent_file.read_text(encoding="utf-8", errors="ignore")
                fm = _parse_frontmatter(content)
                agents_list.append({
                    "id": agent_file.stem,
                    "name": fm.get('name', agent_file.stem),
                    "description": fm.get('description', ''),
                })
            except Exception:
                pass
        
        print(_json_out(agents_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_skills(ctx: CliContext, args) -> int:
    """scopes skills — List all skills."""
    try:
        skills_dir = ctx.scopes_root / "skills"
        if not skills_dir.exists():
            print(_json_out([]))
            return 0
        
        skills_list = []
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                try:
                    content = skill_file.read_text(encoding="utf-8", errors="ignore")
                    fm = _parse_frontmatter(content)
                    skills_list.append({
                        "id": skill_dir.name,
                        "name": fm.get('name', skill_dir.name),
                        "description": fm.get('description', ''),
                    })
                except Exception:
                    pass
        
        print(_json_out(skills_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 3: Init Command
# ─────────────────────────────────────────────────────────────────────────

def cmd_init(ctx: CliContext, args) -> int:
    """scopes init — Initialize Scopes structure for a new project."""
    try:
        scopes_root = ctx.scopes_root
        
        # Create directories
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
        
        # Create INDEX.md template
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
        
        # Create GRAPH.md template
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
        
        # Create .gitignore entry
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


# ─────────────────────────────────────────────────────────────────────────
# Phase 4: Sync & History Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_sync_status(ctx: CliContext, args) -> int:
    """scopes sync:status — Sync dashboard."""
    try:
        scopes_state = ctx.scopes_root.parent / ".scopes"
        last_sync_file = scopes_state / "last_sync"
        last_sync = last_sync_file.read_text().strip() if last_sync_file.exists() else "never"
        
        all_scopes = _all_scope_files(ctx.scopes_product)
        
        # Count stale (simple check: modified long ago)
        stale_count = 0
        try:
            result = _run(["git", "log", "-1", "--format=%aI", str(ctx.scopes_root)],
                         cwd=str(ctx.project_root))
            if result.returncode == 0:
                last_sync = result.stdout.strip()[:19]
        except Exception:
            pass
        
        status = {
            "last_sync": last_sync,
            "total_scopes": len(all_scopes),
            "stale_scopes": stale_count,
            "health": "good" if stale_count == 0 else "warning",
        }
        
        print(_json_out(status) if ctx.format == "json" else 
              f"Last sync: {last_sync}\nTotal: {len(all_scopes)}\nHealth: {status['health']}")
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_history(ctx: CliContext, args) -> int:
    """scopes history scope="X" — Git log for a scope file."""
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        limit = getattr(args, 'limit', 10)
        
        result = _run(
            ["git", "log", f"--oneline", f"-{limit}", str(scope_file)],
            cwd=str(ctx.project_root)
        )
        
        if result.returncode == 0:
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    commits.append({
                        "hash": parts[0] if parts else "",
                        "message": parts[1] if len(parts) > 1 else "",
                    })
            print(_json_out(commits))
        else:
            print(_json_out([]))
        
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


# ─────────────────────────────────────────────────────────────────────────
# Phase 5: Profile & Template Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_profiles(ctx: CliContext, args) -> int:
    """scopes profiles — List available profiles."""
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
    """scopes templates — List available templates."""
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


# ─────────────────────────────────────────────────────────────────────────
# Phase 2: Status & Info Commands
# ─────────────────────────────────────────────────────────────────────────

def cmd_status(ctx: CliContext, args) -> int:
    """scopes status — Project dashboard."""
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        
        # Extract areas
        areas = {}
        for scope_file in all_scopes:
            area = scope_file.relative_to(ctx.scopes_product).parts[0] if scope_file.relative_to(ctx.scopes_product).parts else "Root"
            areas[area] = areas.get(area, 0) + 1
        
        status = {
            "project_root": str(ctx.project_root),
            "scope_count": len(all_scopes),
            "areas": areas,
            "stale_count": 0,
            "health": "good",
        }
        
        print(_json_out(status))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_areas(ctx: CliContext, args) -> int:
    """scopes areas — List all scope areas."""
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        
        areas_dict = {}
        for scope_file in all_scopes:
            rel = scope_file.relative_to(ctx.scopes_product)
            if rel.parts:
                area = rel.parts[0]
                if area not in areas_dict:
                    areas_dict[area] = 0
                areas_dict[area] += 1
        
        areas_list = [{"name": k, "scope_count": v} for k, v in sorted(areas_dict.items())]
        print(_json_out(areas_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_orphans(ctx: CliContext, args) -> int:
    """scopes orphans — Scopes with no incoming references."""
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        orphans = []
        
        for scope_file in all_scopes:
            scope_name = scope_file.relative_to(ctx.scopes_product).as_posix()
            
            # Check if any other scope references this one
            has_backlink = False
            for other_file in all_scopes:
                if other_file == scope_file:
                    continue
                try:
                    content = other_file.read_text(encoding="utf-8", errors="ignore")
                    if scope_name in content or scope_file.stem in content:
                        has_backlink = True
                        break
                except Exception:
                    pass
            
            if not has_backlink:
                orphans.append({
                    "scope": scope_name,
                    "title": _extract_title(scope_file),
                })
        
        print(_json_out(orphans))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_unresolved(ctx: CliContext, args) -> int:
    """scopes unresolved — Broken evidence links."""
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        unresolved = []
        
        evidence_re = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
        
        for scope_file in all_scopes:
            content = scope_file.read_text(encoding="utf-8", errors="ignore")
            for match in evidence_re.finditer(content):
                text, target, start_line, end_line = match.groups()
                if target.endswith('.md'):
                    continue
                
                target_path = ctx.project_root / target
                if not target_path.exists():
                    unresolved.append({
                        "scope": str(scope_file.relative_to(ctx.scopes_product)),
                        "target": target,
                        "status": "missing",
                    })
                elif start_line:
                    try:
                        lines = target_path.read_text().splitlines()
                        if int(start_line) > len(lines):
                            unresolved.append({
                                "scope": str(scope_file.relative_to(ctx.scopes_product)),
                                "target": target,
                                "status": "out_of_range",
                            })
                    except Exception:
                        pass
        
        print(_json_out(unresolved))
        return 0
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
    # Phase 2: Scope Reading
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
    # Phase 2: Search
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
    # Phase 2: Evidence & Links
    # ─────────────────────────────────────────────────────────────────────

    evidence_parser = subparsers.add_parser("evidence", help="Evidence report")
    evidence_parser.add_argument("--scope", required=True, help="Scope name")
    evidence_parser.set_defaults(func=cmd_evidence)

    backlinks_parser = subparsers.add_parser("backlinks", help="Find referencing scopes")
    backlinks_parser.add_argument("--scope", required=True, help="Scope name")
    backlinks_parser.set_defaults(func=cmd_backlinks)

    # ─────────────────────────────────────────────────────────────────────
    # Phase 2: Status & Info
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("status", help="Project dashboard").set_defaults(func=cmd_status)

    areas_parser = subparsers.add_parser("areas", help="List all areas")
    areas_parser.set_defaults(func=cmd_areas)

    orphans_parser = subparsers.add_parser("orphans", help="Scopes with no backlinks")
    orphans_parser.set_defaults(func=cmd_orphans)

    unresolved_parser = subparsers.add_parser("unresolved", help="Broken evidence links")
    unresolved_parser.set_defaults(func=cmd_unresolved)

    # ─────────────────────────────────────────────────────────────────────
    # Phase 3: Sessions
    # ─────────────────────────────────────────────────────────────────────

    session_start_parser = subparsers.add_parser("session:start", help="Create session log")
    session_start_parser.add_argument("--scope", default="", help="Scope anchor")
    session_start_parser.add_argument("--goal", required=True, help="Session goal")
    session_start_parser.set_defaults(func=cmd_session_start)

    subparsers.add_parser("session:read", help="Read current session").set_defaults(func=cmd_session_read)

    # ─────────────────────────────────────────────────────────────────────
    # Phase 3: Tasks
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
    # Phase 3: Agents & Skills
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("agents", help="List agents").set_defaults(func=cmd_agents)
    subparsers.add_parser("skills", help="List skills").set_defaults(func=cmd_skills)

    # ─────────────────────────────────────────────────────────────────────
    # Phase 3: Init
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("init", help="Initialize Scopes structure").set_defaults(func=cmd_init)

    # ─────────────────────────────────────────────────────────────────────
    # Phase 4: Sync & History
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("sync:status", help="Sync dashboard").set_defaults(func=cmd_sync_status)

    history_parser = subparsers.add_parser("history", help="Git history for scope")
    history_parser.add_argument("--scope", required=True, help="Scope name")
    history_parser.add_argument("--limit", type=int, default=10, help="Limit commits")
    history_parser.set_defaults(func=cmd_history)

    # ─────────────────────────────────────────────────────────────────────
    # Phase 5: Profiles & Templates
    # ─────────────────────────────────────────────────────────────────────

    subparsers.add_parser("profiles", help="List available profiles").set_defaults(func=cmd_profiles)

    templates_parser = subparsers.add_parser("templates", help="List available templates")
    templates_parser.add_argument("--type", default="", help="Filter by type")
    templates_parser.set_defaults(func=cmd_templates)

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
