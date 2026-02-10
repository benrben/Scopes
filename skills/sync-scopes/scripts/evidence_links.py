#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Match:
    path: str
    start_line: int
    end_line: int
    line: int
    excerpt: str


def _relpath(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _find_matches(
    text: str,
    *,
    pattern: str,
    regex: bool,
    ignore_case: bool,
) -> list[re.Match[str]]:
    flags = re.MULTILINE
    if ignore_case:
        flags |= re.IGNORECASE
    compiled = re.compile(pattern if regex else re.escape(pattern), flags=flags)
    return list(compiled.finditer(text))


def _line_of_offset(text: str, offset: int) -> int:
    # 1-based line number
    return text.count("\n", 0, offset) + 1


def _excerpt_for_line(lines: list[str], line_no: int, start_line: int, end_line: int) -> str:
    # Keep excerpt compact: show the matched line plus optional context around it.
    if line_no < 1 or line_no > len(lines):
        return ""
    ctx_start = max(1, start_line)
    ctx_end = min(len(lines), end_line)
    snippet = lines[ctx_start - 1 : ctx_end]
    # Prefix with line numbers relative to file for readability
    out = []
    width = len(str(ctx_end))
    for i, s in enumerate(snippet, start=ctx_start):
        out.append(f"{i:>{width}}| {s.rstrip()}")
    return "\n".join(out)


def _resolve_files(file_arg: str, batch_arg: str, repo_root: Path) -> list[Path]:
    """Resolve --file or --batch into a list of files to search."""
    if batch_arg:
        import glob as _glob
        pattern = batch_arg
        if not Path(pattern).is_absolute():
            pattern = str(repo_root / pattern)
        paths = sorted(Path(p) for p in _glob.glob(pattern, recursive=True) if Path(p).is_file())
        return paths
    fp = Path(file_arg)
    if not fp.is_absolute():
        fp = (repo_root / fp).resolve()
    return [fp] if fp.exists() and fp.is_file() else []


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate evidence-backed Scopes links like `[path:Lx-Ly](path#Lx-Ly)` by searching for a pattern."
    )
    ap.add_argument("--repo-root", default=".", help="Repository root used to compute relative paths (default: .).")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--file", default="", help="Single file to search.")
    grp.add_argument("--batch", default="", help="Glob pattern for multiple files (e.g. 'src/**/*.ts').")
    ap.add_argument("--pattern", required=True, help="Pattern to search for (literal by default).")
    ap.add_argument("--regex", action="store_true", help="Interpret --pattern as a regex (default: literal).")
    ap.add_argument("--ignore-case", action="store_true", help="Case-insensitive search.")
    ap.add_argument("--before", type=int, default=0, help="Context lines before the match.")
    ap.add_argument("--after", type=int, default=0, help="Context lines after the match.")
    ap.add_argument("--all", action="store_true", help="Output all matches (default: first match per file).")
    ap.add_argument("--max-matches", type=int, default=20, help="Cap total matches (default: 20).")
    ap.add_argument("--link-only", action="store_true", help="Output only the link, no excerpt (saves tokens).")
    ap.add_argument("--format", choices=["md", "json"], default="md", help="Output format (default: md).")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if not args.pattern:
        print("error: --pattern cannot be empty", file=sys.stderr)
        return 2
    if args.before < 0 or args.after < 0:
        print("error: --before/--after must be >= 0", file=sys.stderr)
        return 2

    file_paths = _resolve_files(args.file, args.batch, repo_root)
    if not file_paths:
        print(f"error: no files found", file=sys.stderr)
        return 2

    out: list[Match] = []
    for file_path in file_paths:
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        try:
            matches = _find_matches(text, pattern=args.pattern, regex=args.regex, ignore_case=args.ignore_case)
        except re.error as exc:
            print(f"error: invalid regex pattern: {exc}", file=sys.stderr)
            return 2
        if not matches:
            continue
        rel = _relpath(file_path, repo_root)
        cap = args.max_matches - len(out) if args.all else 1
        for m in matches[:cap]:
            line_no = _line_of_offset(text, m.start())
            start_line = max(1, line_no - args.before)
            end_line = min(len(lines), line_no + args.after)
            excerpt = "" if args.link_only else _excerpt_for_line(lines, line_no, start_line, end_line)
            out.append(Match(path=rel, start_line=start_line, end_line=end_line, line=line_no, excerpt=excerpt))
        if len(out) >= args.max_matches:
            break

    if not out:
        print("error: pattern not found", file=sys.stderr)
        return 1

    if args.format == "json":
        print(
            json.dumps(
                [
                    {
                        "path": m.path,
                        "start_line": m.start_line,
                        "end_line": m.end_line,
                        "match_line": m.line,
                        "link_md": f"[{m.path}:L{m.start_line}-L{m.end_line}]({m.path}#L{m.start_line}-L{m.end_line})",
                        "excerpt": m.excerpt,
                    }
                    for m in out
                ],
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    # md
    for i, m in enumerate(out):
        if i and not args.link_only:
            print()
        link = f"[{m.path}:L{m.start_line}-L{m.end_line}]({m.path}#L{m.start_line}-L{m.end_line})"
        print(link)
        if m.excerpt and not args.link_only:
            print("```")
            print(m.excerpt)
            print("```")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
