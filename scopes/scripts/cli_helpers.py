"""scopes/scripts/cli_helpers.py — Shared constants, types, and helpers for the Scopes CLI."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────

VERSION = "0.5.0"
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
        return self.scopes_root / "Product"


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Project Resolution
# ─────────────────────────────────────────────────────────────────────────

def _find_project_root(start_path: Path = None) -> Path:
    """Walk up from start_path looking for Scopes/INDEX.md or Scopes/."""
    start = Path(start_path or os.getcwd())
    current = start.resolve()

    for _ in range(50):
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
    scopes_root = project_root / SCOPES_DIR_NAME
    if not scopes_root.is_dir():
        raise FileNotFoundError(f"Scopes directory not found: {scopes_root}")
    return scopes_root


def _scripts_dir() -> Path:
    return Path(__file__).resolve().parent


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Scope Resolution
# ─────────────────────────────────────────────────────────────────────────

def _all_scope_files(scopes_product: Path) -> list[Path]:
    return sorted(scopes_product.glob("**/*.md"))


def _normalize_slug(s: str) -> str:
    return s.lower().replace("_", "-").replace(" ", "-")


def _resolve_scope(scopes_product: Path, scope_name: str) -> Path:
    """Resolve scope by name to file path.

    Resolution order:
    1. Exact match (case-insensitive) in Scopes/Product/**/
    2. Slug match (underscores/hyphens normalized)
    3. Substring match (unique prefix)
    4. Ambiguous → error with candidates
    """
    all_files = _all_scope_files(scopes_product)
    scope_name_lower = scope_name.lower()
    scope_slug = _normalize_slug(scope_name)

    for f in all_files:
        rel = f.relative_to(scopes_product).as_posix().lower()
        stem = rel.replace(".md", "")
        if stem == scope_name_lower or stem.endswith("/" + scope_name_lower):
            return f

    for f in all_files:
        rel = f.relative_to(scopes_product).as_posix().lower()
        stem = rel.replace(".md", "")
        stem_slug = _normalize_slug(stem)
        if stem_slug == scope_slug or stem_slug.endswith("/" + scope_slug):
            return f

    candidates = []
    for f in all_files:
        rel = f.relative_to(scopes_product).as_posix()
        if scope_name_lower in rel.lower():
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
    return json.dumps(data, indent=2)


def _error(message: str, hint: str = "", scope: str = "", **kwargs) -> str:
    err = {"error": message}
    if hint:
        err["hint"] = hint
    if scope:
        err["scope"] = scope
    err.update(kwargs)
    return _json_out(err)


def _run(cmd: list[str], cwd: str = ".") -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Command timed out: {' '.join(cmd)}") from e
    except Exception as e:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{e}") from e


# ─────────────────────────────────────────────────────────────────────────
# Helpers: Content Extraction
# ─────────────────────────────────────────────────────────────────────────

def _extract_title(file_path: Path) -> str:
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1) if match else ""
    except Exception:
        return ""


def _parse_frontmatter(content: str) -> dict:
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
    pattern = rf"^##\s+{re.escape(section_name)}\s*\n(.*?)(?=^##|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _read_lines(file_path: Path, start: int = 1, end: int = None) -> str:
    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if end is None:
            end = len(lines)
        return '\n'.join(lines[max(0, start - 1):end])
    except Exception:
        return ""
