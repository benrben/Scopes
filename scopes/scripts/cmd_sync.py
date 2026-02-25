"""scopes/scripts/cmd_sync.py — Sync and history commands: sync:status, history."""
from __future__ import annotations

import sys

from cli_helpers import (
    CliContext,
    _all_scope_files,
    _error,
    _json_out,
    _resolve_scope,
    _run,
)


def cmd_sync_status(ctx: CliContext, args) -> int:
    try:
        scopes_state = ctx.scopes_root.parent / ".scopes"
        last_sync_file = scopes_state / "last_sync"
        last_sync = last_sync_file.read_text().strip() if last_sync_file.exists() else "never"

        all_scopes = _all_scope_files(ctx.scopes_product)
        stale_count = 0

        try:
            result = _run(
                ["git", "log", "-1", "--format=%aI", str(ctx.scopes_root)],
                cwd=str(ctx.project_root),
            )
            if result.returncode == 0 and result.stdout.strip():
                last_sync = result.stdout.strip()[:19]
        except Exception:
            pass

        status = {
            "last_sync": last_sync,
            "total_scopes": len(all_scopes),
            "stale_scopes": stale_count,
            "health": "good" if stale_count == 0 else "warning",
        }

        print(_json_out(status) if ctx.format == "json" else
              f"Last sync: {last_sync}\nTotal: {len(all_scopes)}\nHealth: {status['health']}")
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_history(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        scope_file = _resolve_scope(ctx.scopes_product, scope_name)
        limit = getattr(args, 'limit', 10)

        result = _run(
            ["git", "log", "--oneline", f"-{limit}", str(scope_file)],
            cwd=str(ctx.project_root),
        )

        if result.returncode == 0:
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    commits.append({
                        "hash": parts[0] if parts else "",
                        "message": parts[1] if len(parts) > 1 else "",
                    })
            print(_json_out(commits))
        else:
            print(_json_out([]))

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
