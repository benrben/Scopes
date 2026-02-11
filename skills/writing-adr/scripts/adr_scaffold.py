#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "decision"


TEMPLATE = """# ADR {num}: {title}

## Status
{status}

## Context
- **Problem**:
- **Constraints**:
- **Scope Context**:
  - {scope_links}

## Options
- **Option A**:
  - Pros:
  - Cons:
- **Option B**:
  - Pros:
  - Cons:

## Decision
(fill in)

## Consequences
### Positive
- (fill in)

### Negative
- (fill in)

## Affected Scopes
- (fill in impacted `Scopes/Product/**` files)
- (fill in `Scopes/GRAPH.md` changes if any)
"""


def _next_adr_number(adrs_dir: Path) -> str:
    rx = re.compile(r"^(?P<num>\d{4})-")
    max_n = 0
    for p in adrs_dir.glob("*.md"):
        m = rx.match(p.name)
        if not m:
            continue
        try:
            max_n = max(max_n, int(m.group("num")))
        except ValueError:
            continue
    return f"{max_n + 1:04d}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Create an ADR skeleton under Scopes/Decisions/ADRs/**.")
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument("--title", required=True, help="ADR title.")
    ap.add_argument("--slug", default="", help="Optional slug override for filename.")
    ap.add_argument("--out", default="", help="Explicit output path (overrides default).")
    ap.add_argument("--force", action="store_true", help="Overwrite if file exists.")
    ap.add_argument(
        "--scope-links",
        default="`Scopes/Product/...`",
        help="Initial scope link(s) to include in Context.",
    )
    ap.add_argument("--supersedes", default="", help="ADR number to supersede (e.g. '0003'). Auto-links both files.")
    ap.add_argument("--dry-run", action="store_true", help="Print path and status, don't write.")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    adrs_dir = repo_root / "Scopes" / "Decisions" / "ADRs"
    adrs_dir.mkdir(parents=True, exist_ok=True)
    num = _next_adr_number(adrs_dir)

    slug = args.slug.strip() or _slugify(args.title)
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
    else:
        out_path = adrs_dir / f"{num}-{slug}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not args.force:
        print(f"error: file exists: {out_path} (use --force to overwrite)", file=sys.stderr)
        return 2

    status_line = "Proposed"
    if args.supersedes:
        status_line = f"Proposed (Supersedes ADR-{args.supersedes})"

    if args.dry_run:
        print(f"Would create: {out_path.relative_to(repo_root).as_posix()}")
        if args.supersedes:
            print(f"Would mark ADR-{args.supersedes} as superseded")
        return 0

    out_path.write_text(
        TEMPLATE.format(
            num=num,
            title=args.title.strip(),
            scope_links=args.scope_links.strip(),
            status=status_line,
        ),
        encoding="utf-8",
    )

    # Auto-link superseded ADR
    if args.supersedes:
        old_pattern = f"{args.supersedes}-"
        for old_adr in adrs_dir.glob(f"{old_pattern}*.md"):
            old_text = old_adr.read_text(encoding="utf-8", errors="replace")
            if f"Superseded by ADR-{num}" not in old_text:
                marker = f"\n\n> **Superseded by ADR-{num}** (`{out_path.name}`)"
                old_text = old_text.replace("## Status\n", f"## Status\nSuperseded{marker}\n\n", 1)
                old_adr.write_text(old_text, encoding="utf-8")
                print(f"Marked superseded: {old_adr.relative_to(repo_root).as_posix()}")

    try:
        print(out_path.relative_to(repo_root).as_posix())
    except Exception:
        print(out_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

