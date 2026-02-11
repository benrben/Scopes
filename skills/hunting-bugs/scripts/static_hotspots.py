#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "target",
    ".venv",
    "venv",
    ".tox",
    ".idea",
    ".cursor",
    ".claude",
    ".agent",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    text: str


RULES: list[tuple[str, str, str]] = [
    ("HIGH", "unsafe_eval", r"\beval\s*\("),
    ("HIGH", "unsafe_exec", r"\bexec\s*\("),
    # Keep SQL concat pattern narrow to reduce shell/operator false positives.
    ("HIGH", "sql_concat", r"\b(SELECT|INSERT|UPDATE|DELETE)\b.+\+\s*\w+"),
    ("MED", "todo_fixme", r"\b(TODO|FIXME)\b"),
    ("MED", "panic", r"\bpanic!\b|\bthrow\b|\braise\b"),
    ("MED", "broad_except", r"except\s+Exception\b|catch\s*\(\s*Exception\b"),
    ("LOW", "print_debug", r"\bprint\(|\bconsole\.log\("),
]


def _iter_files(repo_root: Path) -> list[Path]:
    out: list[Path] = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            out.append(Path(root) / f)
    return out


def _search_file(path: Path, rx: re.Pattern[str]) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f, start=1):
                if rx.search(line):
                    hits.append((idx, line.rstrip()))
    except Exception:
        return hits
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fast static 'hotspot' scan for bug magnets and foot-guns (outputs file/line evidence)."
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument("--path", default="", help="Limit scan to subdirectory (e.g. 'src/auth').")
    ap.add_argument("--severity", default="", choices=["", "HIGH", "MED", "LOW"], help="Filter by severity.")
    ap.add_argument("--skip-comments", action="store_true", help="Skip lines that look like comments.")
    ap.add_argument("--max-per-rule", type=int, default=20, help="Max hits per rule (default: 20).")
    ap.add_argument("--limit", type=int, default=0, help="Max total findings (0=all).")
    ap.add_argument("--format", choices=["md", "json", "compact"], default="compact", help="Output format (default: compact).")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scan_root = (repo_root / args.path) if args.path else repo_root
    if not scan_root.exists():
        print(f"error: path not found: {scan_root}", file=sys.stderr)
        return 2
    files = _iter_files(scan_root)

    comment_re = re.compile(r"^\s*(?:#|//|\*|/\*|<!--|%)") if args.skip_comments else None

    active_rules = RULES
    if args.severity:
        active_rules = [(s, r, p) for s, r, p in RULES if s == args.severity]
    findings: list[Finding] = []
    for severity, rule, pat in active_rules:
        rx = re.compile(pat, flags=re.IGNORECASE)
        count = 0
        for f in files:
            if f.name.endswith(".min.js") or f.suffix.lower() in {".map", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
                continue
            for line_no, text in _search_file(f, rx):
                if comment_re and comment_re.match(text):
                    continue
                rel = f.relative_to(repo_root).as_posix()
                findings.append(Finding(severity=severity, rule=rule, path=rel, line=line_no, text=text))
                count += 1
                if count >= args.max_per_rule:
                    break
            if count >= args.max_per_rule:
                break

    if args.limit > 0:
        findings = findings[: args.limit]

    if args.format == "json":
        print(json.dumps([asdict(f) for f in findings], indent=2, sort_keys=True))
        return 0

    if not findings:
        print("No hotspots.")
        return 0

    if args.format == "md":
        print("| Sev | Rule | Where | Evidence | Snippet |")
        print("|---|---|---|---|---|")
        for f in findings:
            where = f"`{f.path}:{f.line}`"
            evidence = f"[{f.path}:L{f.line}-L{f.line}]({f.path}#L{f.line}-L{f.line})"
            snippet = f.text.replace("|", "\\|")[:80]
            print(f"| {f.severity} | `{f.rule}` | {where} | {evidence} | `{snippet}` |")
    else:  # compact
        print(f"Hotspots: {len(findings)}")
        for f in findings:
            print(f"  {f.severity} {f.rule} {f.path}:{f.line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
