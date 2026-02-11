#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LinkIssue:
    md_file: str
    md_line: int
    target_path: str
    target_fragment: str
    issue: str


LINK_RE = re.compile(
    r"\[[^\]]+\]\((?P<path>[^)#\s]+)(?P<frag>#L(?P<s>\d+)(?:-L(?P<e>\d+))?)?\)"
)


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _file_line_count(path: Path) -> int:
    # Robust and fast enough for typical code files.
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate Scopes evidence links like `[path:Lx-Ly](path#Lx-Ly)` across markdown files."
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument(
        "--scopes-dir",
        default="Scopes",
        help="Scopes directory to scan (default: Scopes).",
    )
    ap.add_argument("--scope", default="", help="Check a single .md file (path relative to repo root).")
    ap.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    ap.add_argument("--broken-only", action="store_true", help="Only report broken links (suppress OK).")
    ap.add_argument("--summary", action="store_true", help="Print counts only (1 line).")
    ap.add_argument("--limit", type=int, default=0, help="Max issues to report (0=all).")
    ap.add_argument(
        "--fail-on-missing-scopes",
        action="store_true",
        help="Exit non-zero if --scopes-dir is missing (default: no issues).",
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scopes_dir = repo_root / args.scopes_dir
    if not scopes_dir.exists():
        if args.fail_on_missing_scopes:
            print(f"error: scopes dir not found: {scopes_dir}", file=sys.stderr)
            return 2
        return 0

    issues: list[LinkIssue] = []
    checked = 0
    if args.scope:
        scope_path = repo_root / args.scope
        md_files = [scope_path] if scope_path.exists() else []
    else:
        md_files = sorted(scopes_dir.rglob("*.md"))
    for md in md_files:
        checked += 1
        rel_md = _rel(md, repo_root)
        md_dir = md.parent
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        for idx, line in enumerate(lines, start=1):
            for m in LINK_RE.finditer(line):
                target_path = m.group("path")
                frag = m.group("frag") or ""
                start = m.group("s")
                end = m.group("e")

                # Skip absolute URLs / mailto.
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", target_path) or target_path.startswith("mailto:"):
                    continue

                target_fs = Path(target_path)
                if not target_fs.is_absolute():
                    # Markdown resolves relative links from the markdown file location.
                    target_candidate = (md_dir / target_fs).resolve()
                    if target_candidate.exists() and target_candidate.is_file():
                        target_fs = target_candidate
                    else:
                        # Back-compat for repos that store repo-root style link paths.
                        target_fs = (repo_root / target_fs).resolve()

                if not target_fs.exists() or not target_fs.is_file():
                    issues.append(
                        LinkIssue(
                            md_file=rel_md,
                            md_line=idx,
                            target_path=target_path,
                            target_fragment=frag,
                            issue="target file missing",
                        )
                    )
                    continue

                if not start:
                    # No line fragment -> consider valid (some links intentionally omit).
                    continue

                try:
                    s_i = int(start)
                    e_i = int(end) if end else s_i
                except ValueError:
                    issues.append(
                        LinkIssue(
                            md_file=rel_md,
                            md_line=idx,
                            target_path=target_path,
                            target_fragment=frag,
                            issue="invalid line numbers",
                        )
                    )
                    continue

                if s_i <= 0 or e_i <= 0 or e_i < s_i:
                    issues.append(
                        LinkIssue(
                            md_file=rel_md,
                            md_line=idx,
                            target_path=target_path,
                            target_fragment=frag,
                            issue="invalid line range",
                        )
                    )
                    continue

                max_lines = _file_line_count(target_fs)
                if s_i > max_lines or e_i > max_lines:
                    issues.append(
                        LinkIssue(
                            md_file=rel_md,
                            md_line=idx,
                            target_path=target_path,
                            target_fragment=frag,
                            issue=f"line out of range (file has {max_lines} lines)",
                        )
                    )

    if args.limit > 0:
        issues = issues[: args.limit]

    if args.summary:
        print(f"checked={checked} broken={len(issues)}")
        return 1 if issues else 0

    if args.format == "json":
        print(json.dumps([asdict(i) for i in issues], indent=2, sort_keys=True))
    else:
        if not issues:
            if not args.broken_only:
                print(f"OK ({checked} files, no broken links)")
        else:
            print(f"{len(issues)} broken link(s) in {checked} file(s):")
            for i in issues:
                print(
                    f"  {i.md_file}:{i.md_line} -> {i.target_path}{i.target_fragment}: {i.issue}"
                )

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
