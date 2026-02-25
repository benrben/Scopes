#!/usr/bin/env python3
"""hotspot_matrix.py

Produce a small, deterministic "hotspot matrix" for refactor scanning:
- Biggest files by line count
- Most changed files by git churn (optional)
- Highest TODO/FIXME density

Intended to be used by the scanning-refactor skill as a mechanical input.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional


DEFAULT_CODE_EXTS = [
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".swift",
    ".scala",
    ".sh",
]

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "out",
    "target",
    ".next",
    ".turbo",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
}

TODO_RX = re.compile(r"\b(?:TODO|FIXME|HACK|XXX)\b")


@dataclass(frozen=True)
class FileMetrics:
    path: str
    lines: int
    todos: int
    churn: Optional[int]


def _iter_files(repo_root: Path, exts: set[str], exclude_dirs: set[str]) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Prune excluded dirs in-place for os.walk
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() not in exts:
                continue
            yield p


def _count_lines(path: Path) -> int:
    # Count '\n' in chunks; treat final line without newline as a line.
    lines = 0
    last_byte = b""
    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                lines += chunk.count(b"\n")
                last_byte = chunk[-1:]
    except OSError:
        return 0
    if lines == 0 and path.stat().st_size > 0:
        return 1
    if last_byte and last_byte != b"\n":
        return lines + 1
    return lines


def _count_todos(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0
    return len(TODO_RX.findall(text))


def _git_churn(repo_root: Path, since_days: int) -> Optional[dict[str, int]]:
    if since_days <= 0:
        return None

    since_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).date().isoformat()
    cmd = [
        "git",
        "-C",
        str(repo_root),
        "log",
        f"--since={since_date}",
        "--name-only",
        "--pretty=format:",
    ]
    try:
        proc = subprocess.run(cmd, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError:
        return None
    if proc.returncode != 0:
        return None

    churn: dict[str, int] = {}
    for line in proc.stdout.splitlines():
        fp = line.strip()
        if not fp:
            continue
        churn[fp] = churn.get(fp, 0) + 1
    return churn


def _top(items: list[FileMetrics], key, n: int) -> list[FileMetrics]:
    return sorted(items, key=key, reverse=True)[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute a simple refactor hotspot matrix (size/churn/todos).")
    ap.add_argument("--repo-root", default=".", help="Repo root to scan (default: .)")
    ap.add_argument("--top", type=int, default=20, help="Top N to report per metric (default: 20)")
    ap.add_argument("--since-days", type=int, default=90, help="Git churn window in days (default: 90). Use 0 to disable.")
    ap.add_argument(
        "--ext",
        action="append",
        default=[],
        help="File extension to include (repeatable). Defaults to common code extensions.",
    )
    ap.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory name to exclude (repeatable). Defaults to common dependency/build dirs.",
    )
    ap.add_argument("--format", choices=["json", "compact"], default="json")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    if not repo_root.exists():
        print(f"repo_root does not exist: {repo_root}", file=sys.stderr)
        return 2

    exts = {e if e.startswith(".") else f".{e}" for e in (args.ext or [])}
    if not exts:
        exts = {e.lower() for e in DEFAULT_CODE_EXTS}

    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS)
    exclude_dirs.update(args.exclude_dir or [])

    churn_map = _git_churn(repo_root, args.since_days)

    metrics: list[FileMetrics] = []
    for p in _iter_files(repo_root, exts, exclude_dirs):
        rel = str(p.relative_to(repo_root))
        churn = churn_map.get(rel, 0) if churn_map is not None else None
        metrics.append(
            FileMetrics(
                path=rel,
                lines=_count_lines(p),
                todos=_count_todos(p),
                churn=churn,
            )
        )

    top_n = max(1, args.top)
    top_by_lines = _top(metrics, key=lambda m: m.lines, n=top_n)
    top_by_todos = _top(metrics, key=lambda m: m.todos, n=top_n)
    top_by_churn = _top(metrics, key=lambda m: (m.churn or 0), n=top_n) if churn_map is not None else []

    payload = {
        "status": "ok",
        "repo_root": str(repo_root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan": {
            "extensions": sorted(exts),
            "excluded_dirs": sorted(exclude_dirs),
            "since_days": args.since_days,
            "files_scanned": len(metrics),
            "git_churn_available": churn_map is not None,
        },
        "top_by_lines": [asdict(m) for m in top_by_lines],
        "top_by_todos": [asdict(m) for m in top_by_todos],
        "top_by_churn": [asdict(m) for m in top_by_churn],
    }

    if args.format == "compact":
        print(f"files_scanned={payload['scan']['files_scanned']} git_churn={payload['scan']['git_churn_available']}")
        print("top_by_lines:")
        for m in top_by_lines[:10]:
            print(f"- {m.lines:>6}  {m.path}")
        print("top_by_todos:")
        for m in top_by_todos[:10]:
            print(f"- {m.todos:>6}  {m.path}")
        if churn_map is not None:
            print("top_by_churn:")
            for m in top_by_churn[:10]:
                print(f"- {(m.churn or 0):>6}  {m.path}")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
