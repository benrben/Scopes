#!/usr/bin/env python3
"""scope_rename_guard.py — Update scope link targets after renames/moves.

Given a rename map (JSON), rewrites markdown link targets across Scopes/** so
references keep working after refactors or file moves.

Design goals:
- Deterministic: only rewrites links that resolve to mapped old paths.
- Safe by default: dry-run unless --apply.
- Correct relative links: updates relative links based on the source file.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class RewriteHit:
    file: str
    old: str
    new: str
    count: int


def _norm_path(p: str) -> str:
    s = p.strip().replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    if s.startswith("/"):
        s = s[1:]
    return s


def _load_rename_map(arg: str) -> dict[str, str]:
    maybe_file = Path(arg)
    raw = maybe_file.read_text(encoding="utf-8", errors="replace") if maybe_file.exists() else arg
    data = json.loads(raw)

    out: dict[str, str] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            out[_norm_path(str(k))] = _norm_path(str(v))
        return out
    if isinstance(data, list):
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"rename_map[{idx}] must be an object")
            old = item.get("from", item.get("old", item.get("src", "")))
            new = item.get("to", item.get("new", item.get("dst", "")))
            if not old or not new:
                raise ValueError(f"rename_map[{idx}] must include from/to")
            out[_norm_path(str(old))] = _norm_path(str(new))
        return out
    raise ValueError("rename map must be a JSON object or array")


def _parse_dest(dest: str) -> tuple[str, str, str]:
    raw = dest.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    path_part = raw
    rest = ""
    if " " in raw or "\t" in raw:
        parts = raw.split()
        path_part = parts[0]
        rest = " " + " ".join(parts[1:])
    fragment = ""
    if "#" in path_part:
        path_part, fragment = path_part.split("#", 1)
        fragment = "#" + fragment
    return path_part, fragment, rest


def _resolve_link(repo_root: Path, src_file: Path, link_path: str) -> str | None:
    raw = link_path.strip().replace("\\", "/")
    if not raw:
        return None
    p = raw
    if not p:
        return None
    if p.startswith(("http://", "https://")):
        return None
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", p):
        return None
    if p.startswith("/"):
        p = p[1:]
        resolved = (repo_root / p).resolve()
    elif p.startswith("./") or p.startswith("../"):
        resolved = (src_file.parent / p).resolve()
    else:
        resolved = (repo_root / _norm_path(p)).resolve()
    try:
        return resolved.relative_to(repo_root).as_posix()
    except Exception:
        return None


def _is_root_style(original_path: str) -> bool:
    s = original_path.strip()
    return s.startswith(("/Scopes/", "Scopes/", "./Scopes/"))


def _rewrite_links_in_text(
    repo_root: Path,
    src_file: Path,
    text: str,
    rename_map: dict[str, str],
) -> tuple[str, list[tuple[str, str]]]:
    """Return (updated_text, replacements[(old_rel, new_rel)])."""
    replacements: list[tuple[str, str]] = []

    out_parts: list[str] = []
    last = 0

    for m in MD_LINK_RE.finditer(text):
        out_parts.append(text[last : m.start()])
        label = m.group(1)
        dest = m.group(2)

        path_part, fragment, rest = _parse_dest(dest)
        resolved = _resolve_link(repo_root, src_file, path_part)

        if resolved and resolved in rename_map:
            new_repo_rel = rename_map[resolved]
            if _is_root_style(path_part) or path_part.strip().startswith("/"):
                prefix = ""
                stripped = path_part.strip()
                if stripped.startswith("/"):
                    prefix = "/"
                elif stripped.startswith("./Scopes/"):
                    prefix = "./"
                new_path_part = prefix + new_repo_rel
            else:
                new_abs = (repo_root / new_repo_rel).resolve()
                rel = os.path.relpath(str(new_abs), start=str(src_file.parent.resolve()))
                new_path_part = Path(rel).as_posix()
                if path_part.strip().startswith("./") and not new_path_part.startswith(".."):
                    if not new_path_part.startswith("./"):
                        new_path_part = "./" + new_path_part

            new_dest = f"{new_path_part}{fragment}{rest}"
            out_parts.append(f"[{label}]({new_dest})")
            replacements.append((resolved, new_repo_rel))
        else:
            out_parts.append(m.group(0))

        last = m.end()

    out_parts.append(text[last:])
    return "".join(out_parts), replacements


def _count_leftover_mapped_links(
    repo_root: Path,
    src_file: Path,
    text: str,
    mapped_old_paths: set[str],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for _label, dest in MD_LINK_RE.findall(text):
        path_part, _fragment, _rest = _parse_dest(dest)
        resolved = _resolve_link(repo_root, src_file, path_part)
        if resolved and resolved in mapped_old_paths:
            counts[resolved] = counts.get(resolved, 0) + 1
    return counts


def _plain_path_rewrite(text: str, rename_map: dict[str, str]) -> tuple[str, int]:
    """Best-effort plain string replacement for exact repo-relative paths."""
    count = 0
    updated = text
    for old, new in rename_map.items():
        if old in updated:
            updated = updated.replace(old, new)
            count += 1
        if f"./{old}" in updated:
            updated = updated.replace(f"./{old}", f"./{new}")
            count += 1
        if f"/{old}" in updated:
            updated = updated.replace(f"/{old}", f"/{new}")
            count += 1
    return updated, count


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Rewrite scope markdown links across Scopes/** using a rename map JSON.",
        epilog=(
            "Examples:\n"
            "  scope_rename_guard.py --map rename.json\n"
            "  scope_rename_guard.py --map rename.json --apply\n"
            "  scope_rename_guard.py --map '{\"Scopes/Product/Auth/Login.md\":\"Scopes/Product/Auth/Login-Flow.md\"}' --apply\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument(
        "--map",
        required=True,
        help="Rename map JSON (file path or inline JSON).",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to files (default: dry-run).",
    )
    ap.add_argument(
        "--update-plain",
        action="store_true",
        help="Also rewrite exact plain-text occurrences of mapped paths (best-effort).",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any mapped old path is still referenced after rewriting.",
    )
    ap.add_argument("--format", choices=["compact", "json"], default="compact")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    scopes_root = repo_root / "Scopes"
    if not scopes_root.exists():
        print("error: Scopes/ not found", file=sys.stderr)
        return 2

    try:
        rename_map = _load_rename_map(args.map)
    except Exception as exc:
        print(f"error: invalid rename map: {exc}", file=sys.stderr)
        return 2

    if not rename_map:
        print("error: empty rename map", file=sys.stderr)
        return 2

    files = sorted(p for p in scopes_root.rglob("*.md") if not p.name.startswith("."))

    hits: list[RewriteHit] = []
    total_files_changed = 0
    total_links_rewritten = 0
    strict_leftovers: dict[str, int] = {k: 0 for k in rename_map}

    for f in files:
        rel_file = f.relative_to(repo_root).as_posix()
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        updated, replacements = _rewrite_links_in_text(repo_root, f, text, rename_map)

        plain_count = 0
        if args.update_plain:
            updated, plain_count = _plain_path_rewrite(updated, rename_map)

        if updated != text:
            total_files_changed += 1
            total_links_rewritten += len(replacements)
            # Aggregate by mapping old->new for reporting
            counter: dict[tuple[str, str], int] = {}
            for old, new in replacements:
                counter[(old, new)] = counter.get((old, new), 0) + 1
            for (old, new), cnt in counter.items():
                hits.append(RewriteHit(file=rel_file, old=old, new=new, count=cnt))
            if args.apply:
                f.write_text(updated, encoding="utf-8")

        if args.strict:
            leftovers = _count_leftover_mapped_links(repo_root, f, updated, set(rename_map.keys()))
            for old, cnt in leftovers.items():
                strict_leftovers[old] += cnt

    strict_failed = args.strict and any(v > 0 for v in strict_leftovers.values())

    if args.format == "json":
        json.dump(
            {
                "summary": {
                    "files_scanned": len(files),
                    "files_changed": total_files_changed,
                    "links_rewritten": total_links_rewritten,
                    "dry_run": not args.apply,
                    "strict_failed": strict_failed,
                },
                "hits": [asdict(h) for h in hits],
                "leftovers": strict_leftovers if args.strict else {},
            },
            sys.stdout,
            indent=2,
        )
        print()
        return 1 if strict_failed else 0

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode}: scanned={len(files)} changed={total_files_changed} rewrites={total_links_rewritten}")
    for h in hits[:200]:
        print(f"- {h.file}: {h.old} -> {h.new} (x{h.count})")
    if len(hits) > 200:
        print(f"... ({len(hits) - 200} more)")

    if args.strict:
        leftovers = {k: v for k, v in strict_leftovers.items() if v > 0}
        if leftovers:
            print("\nSTRICT: leftover references found:")
            for k, v in leftovers.items():
                print(f"- {k}: {v}")
            return 1
        print("\nSTRICT: ok (no leftover references)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
