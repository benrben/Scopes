#!/usr/bin/env python3
"""scope_map.py — Compact matrix view of the Scopes knowledge graph.

Parses Scopes/ in one pass and outputs a structured overview that any
skill can use for fast navigation without reading every scope file.

Design: output is token-efficient by default.  Use --depth and filters
to request exactly the slice you need.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Regexes
# ---------------------------------------------------------------------------
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

SUMMARY_RE = re.compile(
    r"^## Summary\s*\n(.+?)(?=\n##|\Z)", re.MULTILINE | re.DOTALL
)

EVIDENCE_RE = re.compile(
    r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)"
)

CONFIDENCE_RE = re.compile(r"\*\*Confidence\*\*:\s*(\w+)", re.IGNORECASE)

SCOPE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+\.md[^)]*)\)")

GRAPH_ROW_RE = re.compile(
    r"^\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", re.MULTILINE
)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

@dataclass
class ScopeEntry:
    path: str
    title: str
    area: str
    summary: str = ""
    evidence_count: int = 0
    code_paths: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    used_by: list[str] = field(default_factory=list)
    confidence: str = ""


@dataclass
class GraphEdge:
    src: str
    dst: str
    relation: str
    evidence: str


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_scope(
    path: Path, repo_root: Path, want_summary: bool, want_evidence: bool,
) -> ScopeEntry | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    rel = path.relative_to(repo_root).as_posix()
    parts = rel.replace("Scopes/Product/", "").split("/")
    area = parts[0] if len(parts) > 1 else "(root)"

    m = TITLE_RE.search(text)
    title = m.group(1).strip() if m else path.stem

    summary = ""
    if want_summary:
        sm = SUMMARY_RE.search(text)
        if sm:
            summary = sm.group(1).strip().split("\n")[0][:120]

    ev_links = EVIDENCE_RE.findall(text)
    ev_count = len(ev_links)

    code_paths: list[str] = []
    if want_evidence:
        seen: set[str] = set()
        for _, tgt, _, _ in ev_links:
            if tgt.endswith(".md") or tgt.startswith("http"):
                continue
            base = tgt.split(":")[0].split("#")[0]
            if base and base not in seen:
                seen.add(base)
                code_paths.append(base)

    # Cross-links (simple state machine over lines)
    depends_on: list[str] = []
    used_by: list[str] = []
    bucket: list[str] | None = None
    for line in text.splitlines():
        low = line.lower().strip()
        if "depends on" in low or "upstream" in low:
            bucket = depends_on
            continue
        elif "used by" in low or "downstream" in low:
            bucket = used_by
            continue
        elif low.startswith("##") or (low.startswith("- **") and bucket is not None and ":" in low):
            bucket = None
            continue
        if bucket is not None:
            for name, _ in SCOPE_LINK_RE.findall(line):
                bucket.append(name.strip())

    cm = CONFIDENCE_RE.search(text)
    return ScopeEntry(
        path=rel, title=title, area=area, summary=summary,
        evidence_count=ev_count, code_paths=code_paths[:8],
        depends_on=depends_on[:5], used_by=used_by[:5],
        confidence=cm.group(1) if cm else "",
    )


def _parse_graph(repo_root: Path) -> list[GraphEdge]:
    gf = repo_root / "Scopes" / "GRAPH.md"
    if not gf.exists():
        return []
    text = gf.read_text(encoding="utf-8", errors="replace")
    edges: list[GraphEdge] = []
    for m in GRAPH_ROW_RE.finditer(text):
        vals = [x.strip() for x in m.groups()]
        if vals[0].lower() in ("from", "---", ""):
            continue
        edges.append(GraphEdge(src=vals[0], dst=vals[1], relation=vals[2], evidence=vals[3]))
    return edges


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _compact(
    entries: list[ScopeEntry],
    areas: dict[str, list[ScopeEntry]],
    graph: list[GraphEdge],
    depth: int,
    only: str,
    total_ev: int,
    code_count: int,
    want_summary: bool,
    want_evidence: bool,
) -> None:
    header = f"Scopes: {len(entries)} | Areas: {len(areas)} | Evidence: {total_ev} | Code refs: {code_count}"

    if only == "stats":
        print(header)
        return

    # Depth 1: areas only (ultra-compact)
    if depth == 1 and only != "graph":
        print(header)
        for a in sorted(areas):
            ae = areas[a]
            names = ", ".join(e.title for e in ae[:4])
            if len(ae) > 4:
                names += f" +{len(ae)-4}"
            print(f"  {a}/ ({len(ae)}) [{names}]")

    # Depth 2+: scope detail
    elif depth >= 2 and only != "graph":
        print(header)
        for a in sorted(areas):
            print(f"\n{a}/")
            for e in areas[a]:
                deps = ",".join(e.depends_on[:3]) or "-"
                used = ",".join(e.used_by[:3]) or "-"
                parts = [f"  {e.title:<22}", f"ev={e.evidence_count:<3}"]
                parts.append(f"dep=[{deps}]")
                parts.append(f"by=[{used}]")
                if e.confidence:
                    parts.append(f"({e.confidence})")
                print(" ".join(parts))
                if want_summary and e.summary:
                    print(f"    » {e.summary}")
                if want_evidence and e.code_paths:
                    print(f"    code: {', '.join(e.code_paths[:5])}")

    # Graph
    if (not only or only == "graph") and graph:
        print(f"\nGraph ({len(graph)} edges)")
        for g in graph:
            print(f"  {g.src} -> {g.dst} ({g.relation})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compact Scopes matrix view for fast agent navigation.",
        epilog=(
            "Examples:\n"
            "  scope_map.py --depth 1                         # areas only (~5 lines)\n"
            "  scope_map.py --depth 2 --area Auth             # Auth scopes + links\n"
            "  scope_map.py --scope Scopes/Product/Auth/Login.md  # single scope\n"
            "  scope_map.py --only stats                      # 1-line counts\n"
            "  scope_map.py --depth 3 --area Auth --format json   # full JSON\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument(
        "--depth", type=int, default=2, choices=[1, 2, 3],
        help="1=areas only, 2=names+links (default), 3=+summaries+code.",
    )
    ap.add_argument("--area", action="append", default=[], help="Whitelist area(s). Repeatable.")
    ap.add_argument("--scope", default="", help="Single scope path (relative to repo).")
    ap.add_argument("--only", choices=["tree", "graph", "stats"], default="", help="One section only.")
    ap.add_argument("--format", choices=["compact", "json"], default="compact", help="Output format.")
    ap.add_argument("--no-summary", action="store_true", help="Omit summaries even at depth 3.")
    ap.add_argument("--no-evidence", action="store_true", help="Omit code paths even at depth 3.")
    ap.add_argument("--limit", type=int, default=0, help="Max scopes (0=all).")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scopes_dir = repo_root / "Scopes" / "Product"
    if not scopes_dir.exists():
        print("error: Scopes/Product/ not found", file=sys.stderr)
        return 2

    want_summary = not args.no_summary and args.depth >= 3
    want_evidence = not args.no_evidence and args.depth >= 3

    # Collect
    entries: list[ScopeEntry] = []
    for md in sorted(scopes_dir.rglob("*.md")):
        if md.name.startswith("."):
            continue
        e = _parse_scope(md, repo_root, want_summary, want_evidence)
        if not e:
            continue
        if args.area and e.area not in args.area:
            continue
        if args.scope and e.path != args.scope:
            continue
        entries.append(e)

    if args.limit > 0:
        entries = entries[: args.limit]

    graph = _parse_graph(repo_root) if not args.only or args.only == "graph" else []

    # Group by area
    areas: dict[str, list[ScopeEntry]] = {}
    total_ev = 0
    code_files: set[str] = set()
    for e in entries:
        areas.setdefault(e.area, []).append(e)
        total_ev += e.evidence_count
        code_files.update(e.code_paths)

    if args.format == "json":
        out: dict = {}
        if not args.only or args.only == "stats":
            out["stats"] = dict(
                scopes=len(entries), areas=len(areas),
                evidence=total_ev, code_files=len(code_files),
            )
        if not args.only or args.only == "tree":
            out["scopes"] = [asdict(e) for e in entries]
        if not args.only or args.only == "graph":
            out["graph"] = [asdict(g) for g in graph]
        json.dump(out, sys.stdout, indent=2, sort_keys=False)
        print()
        return 0

    _compact(
        entries, areas, graph, args.depth, args.only,
        total_ev, len(code_files), want_summary, want_evidence,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
