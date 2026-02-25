"""scopes/scripts/cmd_read.py — Read commands: read, read:evidence, read:code, search, locate."""
from __future__ import annotations

import re
import sys

from cli_helpers import (
    CliContext,
    _all_scope_files,
    _error,
    _extract_section,
    _extract_title,
    _json_out,
    _read_lines,
    _resolve_scope,
)


def cmd_read(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        if not scope_name:
            print(_error("scope= parameter required"), file=sys.stderr)
            return 1

        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")

        if hasattr(args, 'section') and args.section:
            content = _extract_section(content, args.section)

        if ctx.format == "json":
            sections = re.findall(r"^##\s+(.+)$", content, re.MULTILINE)
            print(_json_out({
                "scope": scope_name,
                "path": str(scope_file.relative_to(ctx.scopes_root)),
                "content": content,
                "sections": sections,
            }))
        else:
            print(content)

        return 0
    except FileNotFoundError as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_read_evidence(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")

        if hasattr(args, 'section') and args.section:
            content = _extract_section(content, args.section)

        evidence_re = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
        links = []
        for match in evidence_re.finditer(content):
            text, target, start_line, end_line = match.groups()
            if not target.endswith('.md'):
                links.append({
                    "target": target,
                    "start_line": int(start_line) if start_line else None,
                    "end_line": int(end_line) if end_line else None,
                    "display": text,
                })

        print(_json_out(links) if ctx.format == "json" else
              '\n'.join(f"{l['target']}:{l['start_line']}-{l['end_line']}" for l in links))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_read_code(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        content = scope_file.read_text(encoding="utf-8", errors="ignore")

        if hasattr(args, 'section') and args.section:
            content = _extract_section(content, args.section)

        evidence_re = re.compile(r"\[([^\]]+)\]\(([^)#\s]+)(?:#L(\d+)(?:-L(\d+))?)?\)")
        code_blocks = []

        for match in evidence_re.finditer(content):
            text, target, start_line, end_line = match.groups()
            if target.endswith('.md'):
                continue

            target_path = ctx.project_root / target
            if not target_path.exists():
                code_blocks.append({
                    "file": target,
                    "status": "missing",
                    "code": None,
                })
                continue

            try:
                start = int(start_line) if start_line else 1
                end = int(end_line) if end_line else None
                code = _read_lines(target_path, start, end)
                code_blocks.append({
                    "file": target,
                    "lines": (start, end or len(target_path.read_text().splitlines())),
                    "code": code,
                    "status": "ok",
                })
            except Exception:
                code_blocks.append({
                    "file": target,
                    "status": "error",
                })

        print(_json_out(code_blocks))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_search(ctx: CliContext, args) -> int:
    try:
        query = getattr(args, 'query', '')
        limit = getattr(args, 'limit', 0)
        if not query:
            print(_error("--query parameter required"), file=sys.stderr)
            return 1

        all_files = _all_scope_files(ctx.scopes_product)
        results = []

        for scope_file in all_files:
            content = scope_file.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(content.splitlines(), 1):
                if query.lower() in line.lower():
                    results.append({
                        "scope": str(scope_file.relative_to(ctx.scopes_product)),
                        "line": line_no,
                        "text": line.strip(),
                    })

        if limit:
            results = results[:limit]

        print(_json_out(results))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_locate(ctx: CliContext, args) -> int:
    try:
        intent = getattr(args, 'intent', '')
        if not intent:
            print(_error("--intent parameter required"), file=sys.stderr)
            return 1

        terms = set(t.lower() for t in re.findall(r'\w+', intent) if len(t) > 2)
        all_files = _all_scope_files(ctx.scopes_product)

        scored = []
        for scope_file in all_files:
            try:
                content = scope_file.read_text(encoding="utf-8", errors="ignore").lower()
                title = _extract_title(scope_file).lower()
                score = sum(2 if t in title else (1 if t in content else 0) for t in terms)
                if score > 0:
                    scored.append({
                        "scope": str(scope_file.relative_to(ctx.scopes_product)),
                        "title": _extract_title(scope_file),
                        "score": score,
                    })
            except Exception:
                pass

        scored.sort(key=lambda x: x['score'], reverse=True)
        limit = getattr(args, 'limit', 5)
        print(_json_out(scored[:limit]))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
