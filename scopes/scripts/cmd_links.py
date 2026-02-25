"""scopes/scripts/cmd_links.py — Link/graph commands: evidence, backlinks, status, areas, orphans, unresolved, graph:impact."""
from __future__ import annotations

import re
import sys

from cli_helpers import (
    CliContext,
    _all_scope_files,
    _error,
    _extract_title,
    _json_out,
    _resolve_scope,
)

_EVIDENCE_RE = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")


def cmd_evidence(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")

        links = []
        for match in _EVIDENCE_RE.finditer(content):
            text, target, start_line, end_line = match.groups()
            if target.endswith('.md'):
                continue

            target_path = ctx.project_root / target
            exists = target_path.exists()
            in_range = True

            if exists and start_line:
                try:
                    lines = target_path.read_text().splitlines()
                    in_range = int(start_line) <= len(lines)
                except Exception:
                    in_range = False

            links.append({
                "target": target,
                "lines": (int(start_line) if start_line else None, int(end_line) if end_line else None),
                "exists": exists,
                "in_range": in_range,
                "display": text,
            })

        print(_json_out(links))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_backlinks(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        scope_rel = str(scope_file.relative_to(ctx.scopes_product)).replace('.md', '').replace('\\', '/')

        all_files = _all_scope_files(ctx.scopes_product)
        backlinks = []

        for other_file in all_files:
            if other_file == scope_file:
                continue
            try:
                content = other_file.read_text(encoding="utf-8", errors="ignore")
                if scope_rel in content or scope_name in content:
                    backlinks.append({
                        "scope": str(other_file.relative_to(ctx.scopes_product)),
                        "title": _extract_title(other_file),
                    })
            except Exception:
                pass

        print(_json_out(backlinks))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_status(ctx: CliContext, args) -> int:
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)

        areas: dict[str, int] = {}
        for scope_file in all_scopes:
            rel = scope_file.relative_to(ctx.scopes_product)
            area = rel.parts[0] if rel.parts else "Root"
            areas[area] = areas.get(area, 0) + 1

        status = {
            "project_root": str(ctx.project_root),
            "scope_count": len(all_scopes),
            "areas": areas,
            "stale_count": 0,
            "health": "good",
        }

        print(_json_out(status))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_areas(ctx: CliContext, args) -> int:
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)

        areas_dict: dict[str, int] = {}
        for scope_file in all_scopes:
            rel = scope_file.relative_to(ctx.scopes_product)
            if rel.parts:
                area = rel.parts[0]
                areas_dict[area] = areas_dict.get(area, 0) + 1

        areas_list = [{"name": k, "scope_count": v} for k, v in sorted(areas_dict.items())]
        print(_json_out(areas_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_orphans(ctx: CliContext, args) -> int:
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        orphans = []

        for scope_file in all_scopes:
            scope_name = scope_file.relative_to(ctx.scopes_product).as_posix()

            has_backlink = False
            for other_file in all_scopes:
                if other_file == scope_file:
                    continue
                try:
                    content = other_file.read_text(encoding="utf-8", errors="ignore")
                    if scope_name in content or scope_file.stem in content:
                        has_backlink = True
                        break
                except Exception:
                    pass

            if not has_backlink:
                orphans.append({
                    "scope": scope_name,
                    "title": _extract_title(scope_file),
                })

        print(_json_out(orphans))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_unresolved(ctx: CliContext, args) -> int:
    try:
        all_scopes = _all_scope_files(ctx.scopes_product)
        unresolved = []

        for scope_file in all_scopes:
            content = scope_file.read_text(encoding="utf-8", errors="ignore")
            for match in _EVIDENCE_RE.finditer(content):
                text, target, start_line, end_line = match.groups()
                if target.endswith('.md'):
                    continue

                target_path = ctx.project_root / target
                if not target_path.exists():
                    unresolved.append({
                        "scope": str(scope_file.relative_to(ctx.scopes_product)),
                        "target": target,
                        "status": "missing",
                    })
                elif start_line:
                    try:
                        lines = target_path.read_text().splitlines()
                        if int(start_line) > len(lines):
                            unresolved.append({
                                "scope": str(scope_file.relative_to(ctx.scopes_product)),
                                "target": target,
                                "status": "out_of_range",
                            })
                    except Exception:
                        pass

        print(_json_out(unresolved))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_graph_impact(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        if not scope_name:
            print(_error("--scope required"), file=sys.stderr)
            return 1

        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        scope_rel = str(scope_file.relative_to(ctx.scopes_product)).replace('\\', '/')

        all_files = _all_scope_files(ctx.scopes_product)
        dependents = []

        for other_file in all_files:
            if other_file == scope_file:
                continue
            try:
                content = other_file.read_text(encoding="utf-8", errors="ignore")
                if scope_rel in content or scope_file.stem in content:
                    dependents.append({
                        "scope": str(other_file.relative_to(ctx.scopes_product)),
                        "title": _extract_title(other_file),
                        "type": "direct",
                    })
            except Exception:
                pass

        result = {
            "scope": scope_name,
            "path": scope_rel,
            "direct_dependents": [d for d in dependents if d["type"] == "direct"],
            "total": len(dependents),
        }

        print(_json_out(result) if ctx.format == "json" else
              f"Impact: {scope_name} — {len(dependents)} direct dependents\n" +
              "\n".join(f"  {d['scope']}" for d in dependents))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
