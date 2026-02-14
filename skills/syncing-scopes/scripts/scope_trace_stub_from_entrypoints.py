#!/usr/bin/env python3
"""scope_trace_stub_from_entrypoints.py — Generate a trace-table stub from entrypoints.

Reads a Capability Scope's "## Where to Start in Code" section, extracts
evidence links, and generates a "Usage & Flow Traces" table skeleton:

| Step | Layer | Evidence Link | Description |

Design goals:
- Deterministic: only uses evidence links already present in the scope.
- No speculation: does not invent missing steps (validation/output/etc).
- Low friction: can print the stub or update the scope file in-place.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from _md_links import parse_link_destination, resolve_repo_relative_path


H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
BULLET_LABEL_RE = re.compile(r"^\s*-\s*\*\*(.+?)\*\*", re.IGNORECASE)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
LINE_ANCHOR_RE = re.compile(r"#L\d+(?:-L\d+)?\b")


@dataclass(frozen=True)
class TraceRow:
    step: int
    layer: str
    evidence: str
    description: str


def _extract_h2_section(text: str, title: str) -> str | None:
    needle = re.compile(rf"^##\s+{re.escape(title)}\s*$", re.MULTILINE)
    m = needle.search(text)
    if not m:
        return None
    start = m.end()
    if start < len(text) and text[start] == "\n":
        start += 1
    n = H2_RE.search(text, pos=start)
    end = n.start() if n else len(text)
    return text[start:end].strip("\n")


def _layer_from_label(label: str) -> str:
    low = label.lower()
    if "primary" in low and ("entry" in low or "entrypoint" in low):
        return "Entry"
    if "orchestrator" in low or "service" in low:
        return "Logic"
    if "data" in low or "schema" in low or "db" in low:
        return "Data"
    if "ui" in low or "surface" in low or "page" in low or "component" in low:
        return "UI"
    return "Unspecified"

def _entrypoint_links(
    repo_root: Path,
    scope_file: Path,
    where_to_start: str,
    *,
    require_line_anchors: bool,
) -> list[tuple[str, str]]:
    """Return [(layer, markdown_link)] from the 'Where to Start in Code' section."""
    current_label = ""
    seen: set[str] = set()
    out: list[tuple[str, str]] = []

    for line in where_to_start.splitlines():
        lm = BULLET_LABEL_RE.match(line)
        if lm:
            current_label = lm.group(1).strip()

        for text, dest in MD_LINK_RE.findall(line):
            path_part, fragment, rest = parse_link_destination(dest)
            if require_line_anchors and not LINE_ANCHOR_RE.search(fragment):
                continue

            resolved = resolve_repo_relative_path(repo_root, scope_file, path_part)
            if resolved and resolved.startswith("Scopes/") and resolved.endswith(".md"):
                continue

            full_link = f"[{text}]({path_part}{fragment}{rest})"
            key = f"{resolved or path_part}{fragment}"
            if key in seen:
                continue
            seen.add(key)

            out.append((_layer_from_label(current_label), full_link))
    return out


def _render_table(rows: list[TraceRow]) -> str:
    lines = [
        "| Step | Layer | Evidence Link | Description |",
        "|------|-------|---------------|-------------|",
    ]
    for r in rows:
        lines.append(f"| {r.step} | {r.layer} | {r.evidence} | {r.description} |")
    return "\n".join(lines) + "\n"


def _update_usage_traces(text: str, new_table: str) -> tuple[str, bool, bool]:
    """Replace or insert the trace table under '## Usage & Flow Traces'.

    Returns: (updated_text, found_section, changed)
    """
    title = "Usage & Flow Traces"
    needle = re.compile(rf"^##\s+{re.escape(title)}\s*$", re.MULTILINE)
    m = needle.search(text)
    if not m:
        return text, False, False

    # Identify section body (after heading line, until next H2 or EOF)
    section_body_start = m.end()
    if section_body_start < len(text) and text[section_body_start] == "\n":
        section_body_start += 1
    n = H2_RE.search(text, pos=section_body_start)
    section_body_end = n.start() if n else len(text)
    section_body = text[section_body_start:section_body_end]

    table_re = re.compile(
        r"(?ms)^\\|\\s*Step\\s*\\|\\s*Layer\\s*\\|\\s*Evidence Link\\s*\\|\\s*Description\\s*\\|\\s*\\n"
        r"^\\|\\s*[-:]+\\s*\\|\\s*[-:]+\\s*\\|\\s*[-:]+\\s*\\|\\s*[-:]+\\s*\\|\\s*\\n"
        r"(?:^\\|.*\\|\\s*\\n)*"
    )

    if table_re.search(section_body):
        new_section_body = table_re.sub(new_table, section_body, count=1)
    else:
        prefix = "" if section_body.endswith("\n") or not section_body else "\n"
        new_section_body = section_body + prefix + new_table

    updated = text[:section_body_start] + new_section_body + text[section_body_end:]
    return updated, True, updated != text


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate a Usage & Flow Traces table stub from 'Where to Start in Code' evidence links.",
        epilog=(
            "Examples:\n"
            "  scope_trace_stub_from_entrypoints.py --scope Scopes/Product/Auth/Login.md\n"
            "  scope_trace_stub_from_entrypoints.py --scope Scopes/Product/Auth/Login.md --apply\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Scope file path (relative to repo root). Repeatable.",
    )
    ap.add_argument(
        "--desc",
        default="TODO",
        help="Description placeholder for each row (default: TODO).",
    )
    ap.add_argument(
        "--allow-missing-lines",
        action="store_true",
        help="Include links even if they lack #Lx anchors (default: require #L..).",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Update scope file(s) in-place (default: print table(s)).",
    )
    ap.add_argument("--format", choices=["compact", "json"], default="compact")
    args = ap.parse_args()

    if not args.scope:
        print("error: provide --scope (repeatable)", file=sys.stderr)
        return 2

    repo_root = Path(args.repo_root).resolve()

    results: list[dict] = []
    any_errors = False

    for scope_rel in args.scope:
        scope_path = (repo_root / scope_rel).resolve()
        if not scope_path.exists():
            any_errors = True
            results.append({"scope": scope_rel, "error": "not_found"})
            continue

        try:
            text = scope_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            any_errors = True
            results.append({"scope": scope_rel, "error": "unreadable"})
            continue

        where = _extract_h2_section(text, "Where to Start in Code") or ""
        if not where.strip():
            any_errors = True
            results.append({"scope": scope_rel, "error": "missing_where_to_start"})
            continue

        links = _entrypoint_links(
            repo_root,
            scope_path,
            where,
            require_line_anchors=not args.allow_missing_lines,
        )
        if not links:
            any_errors = True
            results.append({"scope": scope_rel, "error": "no_entrypoint_evidence_links"})
            continue

        rows = [
            TraceRow(step=i + 1, layer=layer, evidence=link, description=args.desc)
            for i, (layer, link) in enumerate(links)
        ]
        table = _render_table(rows)

        changed = False
        if args.apply:
            updated, found, changed = _update_usage_traces(text, table)
            if not found:
                any_errors = True
                results.append({"scope": scope_rel, "error": "missing_usage_traces_section"})
                continue
            if changed:
                scope_path.write_text(updated, encoding="utf-8")

        results.append(
            {
                "scope": scope_rel,
                "rows": [asdict(r) for r in rows],
                "table": table if not args.apply else "",
                "updated": bool(args.apply and changed),
            }
        )

    if args.format == "json":
        json.dump({"results": results, "summary": {"count": len(results), "errors": any_errors}}, sys.stdout, indent=2)
        print()
        return 1 if any_errors else 0

    for r in results:
        if "error" in r:
            print(f"{r['scope']}: error={r['error']}", file=sys.stderr)
            continue
        if args.apply:
            state = "updated" if r.get("updated") else "no-op"
            print(f"{r['scope']}: {state} trace table rows={len(r['rows'])}")
        else:
            print(f"\n# {r['scope']}\n")
            print(r["table"], end="")

    return 1 if any_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
