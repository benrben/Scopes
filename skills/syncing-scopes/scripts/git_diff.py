#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Change:
    status: str
    path: str
    old_path: Optional[str] = None


def _run_git(repo_root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git command failed")
    return proc.stdout


def _parse_name_status(raw: str) -> list[Change]:
    out: list[Change] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status_token = parts[0]
        status = status_token[:1] if status_token else "?"

        if status in {"R", "C"} and len(parts) >= 3:
            out.append(Change(status=status, old_path=parts[1], path=parts[2]))
            continue

        if len(parts) >= 2:
            out.append(Change(status=status, path=parts[1]))
            continue

        # Fallback for unexpected formatting.
        out.append(Change(status=status, path=""))

    return out


def _norm(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Summarize git diff for Scopes/** from a baseline ref."
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .)")
    ap.add_argument(
        "--base-ref",
        required=True,
        help="Baseline git ref/commit (required), e.g. HEAD or a commit sha.",
    )
    ap.add_argument(
        "--scopes-dir", default="Scopes", help="Scopes dir to inspect (default: Scopes)"
    )
    ap.add_argument(
        "--list-untouched",
        action="store_true",
        help="Include untouched markdown files under Scopes.",
    )
    ap.add_argument(
        "--max-untouched",
        type=int,
        default=100,
        help="Cap untouched list length in text output (default: 100).",
    )
    ap.add_argument("--changed-only", action="store_true", help="Suppress untouched listing (faster, fewer tokens).")
    ap.add_argument("--limit", type=int, default=0, help="Max changed files to show (0=all).")
    ap.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scopes_dir = args.scopes_dir

    try:
        _run_git(repo_root, ["rev-parse", "--is-inside-work-tree"])
    except RuntimeError as exc:
        print(f"error: not a git worktree: {exc}", file=sys.stderr)
        return 2

    try:
        resolved_base = _run_git(repo_root, ["rev-parse", "--verify", args.base_ref]).strip()
    except RuntimeError as exc:
        print(f"error: invalid --base-ref '{args.base_ref}': {exc}", file=sys.stderr)
        return 2

    try:
        raw_diff = _run_git(
            repo_root,
            ["diff", "--name-status", "--find-renames", resolved_base, "--", scopes_dir],
        )
    except RuntimeError as exc:
        print(f"error: failed to diff scopes: {exc}", file=sys.stderr)
        return 2

    changes = _parse_name_status(raw_diff)

    # Include untracked Scopes files so working tree reality is visible.
    try:
        raw_untracked = _run_git(
            repo_root,
            ["ls-files", "--others", "--exclude-standard", "--", scopes_dir],
        )
    except RuntimeError:
        raw_untracked = ""

    for line in raw_untracked.splitlines():
        p = line.strip()
        if p:
            changes.append(Change(status="?", path=p))

    # Deduplicate while keeping order.
    seen = set()
    deduped: list[Change] = []
    for ch in changes:
        key = (ch.status, ch.old_path or "", ch.path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(ch)

    summary = Counter(ch.status for ch in deduped)

    untouched: list[str] = []
    if args.list_untouched:
        scopes_root = repo_root / scopes_dir
        if scopes_root.exists():
            all_md = sorted(
                _norm(p, repo_root) for p in scopes_root.rglob("*.md") if p.is_file()
            )
            changed_paths = {c.path for c in deduped if c.status != "D" and c.path}
            untouched = [p for p in all_md if p not in changed_paths]

    payload = {
        "repo_root": repo_root.as_posix(),
        "base_ref": args.base_ref,
        "base_ref_resolved": resolved_base,
        "scopes_dir": scopes_dir,
        "summary": dict(sorted(summary.items())),
        "changed_total": len(deduped),
        "changes": [asdict(c) for c in deduped],
        "untouched_markdown_total": len(untouched),
        "untouched_markdown": untouched,
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"Scopes diff: {payload['changed_total']} changed (base: {args.base_ref[:8]})")
    if payload["summary"]:
        print(" ".join(f"{s}={c}" for s, c in payload["summary"].items()))

    show_changes = deduped
    if args.limit > 0:
        show_changes = deduped[: args.limit]

    if show_changes:
        for c in show_changes:
            if c.status in {"R", "C"} and c.old_path:
                print(f"  {c.status} {c.old_path} -> {c.path}")
            else:
                print(f"  {c.status} {c.path}")
        if args.limit > 0 and len(deduped) > args.limit:
            print(f"  ... +{len(deduped) - args.limit} more")
    else:
        print("  (none)")

    if args.list_untouched and not args.changed_only:
        print(f"\nUntouched: {len(untouched)}")
        for p in untouched[: max(0, args.max_untouched)]:
            print(f"  {p}")
        if len(untouched) > max(0, args.max_untouched):
            print(f"  ... +{len(untouched) - max(0, args.max_untouched)} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
