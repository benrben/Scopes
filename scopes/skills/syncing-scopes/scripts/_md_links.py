#!/usr/bin/env python3
"""Shared markdown-link parsing and path resolution helpers."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable


SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def parse_link_destination(dest: str) -> tuple[str, str, str]:
    """Return (path_part, fragment, rest_after_path) from a markdown destination."""
    raw = dest.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()

    path_part = raw
    rest = ""
    if " " in raw or "\t" in raw:
        parts = raw.split()
        path_part = parts[0]
        rest = " " + " ".join(parts[1:])

    fragment = ""
    if "#" in path_part:
        path_part, fragment = path_part.split("#", 1)
        fragment = "#" + fragment
    return path_part, fragment, rest


def resolve_repo_relative_path(
    repo_root: Path,
    src_file: Path,
    link_path: str,
    *,
    normalize_bare: Callable[[str], str] | None = None,
) -> str | None:
    """Resolve a markdown link path to a repo-relative posix path (best-effort)."""
    p = link_path.strip().replace("\\", "/")
    if not p:
        return None
    if p.startswith(("http://", "https://")):
        return None
    if SCHEME_RE.match(p):  # mailto:, vscode:, etc
        return None

    if p.startswith("/"):
        p = p[1:]
        resolved = (repo_root / p).resolve()
    elif p.startswith("./") or p.startswith("../"):
        resolved = (src_file.parent / p).resolve()
    else:
        if normalize_bare:
            p = normalize_bare(p)
        resolved = (repo_root / p).resolve()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except Exception:
        return None
