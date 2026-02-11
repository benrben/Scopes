#!/usr/bin/env python3
"""drift_detector.py — Detect stale scope evidence via git timestamps.

Compares each scope file's last-modified date against the code files it
references.  When code changed AFTER the scope was last updated, that
evidence is flagged as stale.

Design: output is compact by default.  Use --stale-only to suppress
healthy links.  Use --limit and --scope/--area filters to keep output
small.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

EVIDENCE_RE = re.compile(
    r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)"
)


@dataclass(frozen=True)
class DriftItem:
    scope: str
    target: str
    scope_date: str   # YYYY-MM-DD or "untracked"
    code_date: str    # YYYY-MM-DD or "missing"
    status: str       # ok | stale | missing | untracked


def _git_date(repo_root: Path, rel: str) -> str:
    """Last commit date for *rel* (YYYY-MM-DD), or a status tag."""
    if not (repo_root / rel).exists():
        return "missing"
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", rel],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        )
        d = r.stdout.strip()
        return d[:10] if d else "untracked"
    except Exception:
        return "unknown"


def _evidence_targets(text: str) -> list[str]:
    """Unique non-.md evidence paths from scope content."""
    seen: set[str] = set()
    out: list[str] = []
    for _, tgt, _, _ in EVIDENCE_RE.findall(text):
        if tgt.endswith(".md") or tgt.startswith("http"):
            continue
        base = tgt.split(":")[0].split("#")[0]
        if base and base not in seen:
            seen.add(base)
            out.append(base)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Detect stale scope evidence by comparing git timestamps.",
        epilog=(
            "Examples:\n"
            "  drift_detector.py --scope Scopes/Product/Auth/Login.md\n"
            "  drift_detector.py --area Auth --stale-only\n"
            "  drift_detector.py --all --stale-only --limit 10\n"
            "  drift_detector.py --all --days 14\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument("--scope", default="", help="Check single scope file.")
    ap.add_argument("--area", default="", help="Check all scopes in area (e.g. Auth).")
    ap.add_argument("--all", action="store_true", help="Check all scopes.")
    ap.add_argument("--stale-only", action="store_true", help="Show only stale/missing items.")
    ap.add_argument(
        "--days", type=int, default=0,
        help="Flag stale only if code changed ≥N days after scope (default: any).",
    )
    ap.add_argument("--limit", type=int, default=0, help="Max items (0=all).")
    ap.add_argument("--format", choices=["compact", "json"], default="compact")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scopes_dir = repo_root / "Scopes" / "Product"
    if not scopes_dir.exists():
        print("error: Scopes/Product/ not found", file=sys.stderr)
        return 2

    # Resolve scope file list
    files: list[Path] = []
    if args.scope:
        p = repo_root / args.scope
        if not p.exists():
            print(f"error: {args.scope} not found", file=sys.stderr)
            return 2
        files = [p]
    elif args.area:
        ad = scopes_dir / args.area
        if ad.is_dir():
            files = sorted(ad.rglob("*.md"))
        else:
            files = sorted(
                p for p in scopes_dir.rglob("*.md")
                if args.area.lower() in str(p.relative_to(scopes_dir)).lower()
            )
    elif args.all:
        files = sorted(scopes_dir.rglob("*.md"))
    else:
        print("error: specify --scope, --area, or --all", file=sys.stderr)
        return 2

    if not files:
        print("No scope files found.", file=sys.stderr)
        return 1

    items: list[DriftItem] = []
    for sf in files:
        srel = sf.relative_to(repo_root).as_posix()
        sdate = _git_date(repo_root, srel)
        try:
            text = sf.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for tgt in _evidence_targets(text):
            cdate = _git_date(repo_root, tgt)
            if cdate == "missing":
                status = "missing"
            elif cdate in ("untracked", "unknown") or sdate in ("untracked", "unknown"):
                status = "untracked"
            elif cdate > sdate:
                status = "stale"
                if args.days > 0:
                    try:
                        from datetime import date as D
                        if (D.fromisoformat(cdate) - D.fromisoformat(sdate)).days < args.days:
                            status = "ok"
                    except Exception:
                        pass
            else:
                status = "ok"
            items.append(DriftItem(scope=srel, target=tgt, scope_date=sdate, code_date=cdate, status=status))

    if args.stale_only:
        items = [i for i in items if i.status in ("stale", "missing")]
    if args.limit > 0:
        items = items[: args.limit]

    n_stale = sum(1 for i in items if i.status == "stale")
    n_miss = sum(1 for i in items if i.status == "missing")
    n_ok = sum(1 for i in items if i.status == "ok")

    if args.format == "json":
        json.dump(
            {"items": [asdict(i) for i in items], "summary": {"stale": n_stale, "missing": n_miss, "ok": n_ok}},
            sys.stdout, indent=2,
        )
        print()
        return 0

    # Compact
    icons = {"ok": "✓", "stale": "⚠", "missing": "✗", "untracked": "?"}
    print(f"Drift: {n_stale} stale, {n_miss} missing, {n_ok} ok")
    cur = ""
    for i in items:
        if i.scope != cur:
            cur = i.scope
            print(f"\n{cur} ({i.scope_date})")
        print(f"  {icons.get(i.status,'?')} {i.target} ({i.code_date})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
