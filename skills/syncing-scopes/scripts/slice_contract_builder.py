#!/usr/bin/env python3
"""slice_contract_builder.py — Build Slice Contracts for scope-filler agents.

Produces a JSON array of Slice Contracts from:
  1. drift_detector.py output (update mode), OR
  2. repo structure inference (generation mode)

Each contract contains everything a scope-filler agent needs to work without
re-discovering the project: entrypoints, tech stack snippet, test command,
related scopes, and ownership boundaries.

This eliminates the #1 source of token waste in syncing-scopes: every
scope-filler re-navigating INDEX.md + GRAPH.md + the codebase from scratch.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SliceContract:
    target: str                              # scope file path
    ownership: list[str] = field(default_factory=list)   # files the filler may edit
    priority: str = "medium"                 # high | medium | low
    wip_slot: str = ""                       # "i of N" for parallel batching (informational)
    context: dict[str, Any] = field(default_factory=dict)
    acceptance: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _extract_tech_stack_summary(repo_root: Path) -> str:
    """Extract a 3-line tech stack summary from TECH_STACK.md or dependency files."""
    ts_path = repo_root / "Scopes" / "Onboarding" / "TECH_STACK.md"
    if ts_path.exists():
        content = _read_file_safe(ts_path)
        lines = [l.strip() for l in content.split("\n") if l.strip().startswith("- **")]
        return "\n".join(lines[:5]) if lines else "[Unknown — TECH_STACK.md exists but has no entries]"

    # Fallback: scan dependency files
    summaries = []
    for dep_file in ["package.json", "pyproject.toml", "go.mod", "Cargo.toml", "Gemfile", "pom.xml"]:
        if (repo_root / dep_file).exists():
            summaries.append(f"- {dep_file} detected")
    return "\n".join(summaries) if summaries else "[Unknown — no dependency files found]"


def _extract_test_command(repo_root: Path) -> str:
    """Extract the primary test command from DEVELOPER_INFO.md or package.json."""
    di_path = repo_root / "Scopes" / "DEVELOPER_INFO.md"
    if di_path.exists():
        content = _read_file_safe(di_path)
        # Look for test commands in the table or bullet lists
        for line in content.split("\n"):
            if "test" in line.lower() and "`" in line:
                match = re.search(r"`([^`]+)`", line)
                if match:
                    return match.group(1)

    # Fallback: check package.json
    pkg = repo_root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            scripts = data.get("scripts", {})
            if "test" in scripts:
                return f"npm test"
            if "test:unit" in scripts:
                return f"npm run test:unit"
        except Exception:
            pass

    # Fallback: check for common test runners
    for cmd in ["pytest", "go test ./...", "cargo test"]:
        tool = cmd.split()[0]
        if (repo_root / f"{tool}.ini").exists() or (repo_root / f"{tool}.cfg").exists():
            return cmd

    return "[Unknown — no test command detected]"


# Module-level cache for scope content (avoid re-reading for every contract)
_scope_content_cache: dict[str, str] = {}


def _find_related_scopes(scope_path: str, repo_root: Path) -> list[str]:
    """Find scopes that reference or are referenced by this scope."""
    global _scope_content_cache
    related = []
    scopes_dir = repo_root / "Scopes" / "Product"
    if not scopes_dir.exists():
        return related

    # Build cache once
    if not _scope_content_cache:
        for md_file in scopes_dir.rglob("*.md"):
            rel = str(md_file.relative_to(repo_root))
            _scope_content_cache[rel] = _read_file_safe(md_file)

    scope_name = Path(scope_path).stem
    for rel_path, content in _scope_content_cache.items():
        if rel_path == scope_path:
            continue
        if scope_name in content:
            related.append(rel_path)
    return related[:5]  # cap at 5


# Module-level cache for code file list (avoid repeated `find` calls)
_code_files_cache: list[str] | None = None


def _infer_entrypoints_for_area(area_name: str, repo_root: Path) -> list[str]:
    """Infer likely code entrypoints for a given area name."""
    global _code_files_cache
    area_lower = area_name.lower().replace(" ", "").replace("-", "").replace("_", "")

    # Build file list cache once with a single find call
    if _code_files_cache is None:
        try:
            result = subprocess.run(
                ["find", ".", "(",
                 "-name", "*.ts", "-o", "-name", "*.tsx", "-o",
                 "-name", "*.js", "-o", "-name", "*.jsx", "-o",
                 "-name", "*.py", "-o", "-name", "*.go", "-o",
                 "-name", "*.rs", ")",
                 "-not", "-path", "*/node_modules/*",
                 "-not", "-path", "*/.git/*",
                 "-not", "-path", "*/Scopes/*"],
                capture_output=True, text=True, cwd=str(repo_root), timeout=15
            )
            _code_files_cache = [l.lstrip("./") for l in result.stdout.strip().split("\n") if l]
        except Exception:
            _code_files_cache = []

    # Filter cached files by area name match
    candidates = []
    for f in _code_files_cache:
        file_lower = f.lower().replace("/", "").replace(".", "").replace("-", "").replace("_", "")
        if area_lower in file_lower:
            candidates.append(f)
            if len(candidates) >= 5:
                break

    return candidates


def build_from_drift(drift_json: dict, repo_root: Path) -> list[SliceContract]:
    """Build slice contracts from drift_detector.py JSON output."""
    contracts = []
    tech_stack = _extract_tech_stack_summary(repo_root)
    test_cmd = _extract_test_command(repo_root)

    if isinstance(drift_json, list):
        entries = drift_json
    else:
        entries = (
            drift_json.get("items")
            or drift_json.get("entries")
            or drift_json.get("results")
            or []
        )

    for entry in entries:
        scope_path = entry.get("scope", entry.get("scope_file", ""))
        if not scope_path:
            continue

        status = str(entry.get("status", "")).lower()
        is_problem = status in ("stale", "missing")
        stale = entry.get("stale", entry.get("is_stale", is_problem))
        priority = "high" if stale or is_problem else "medium"

        # Extract area name from path for entrypoint inference
        parts = Path(scope_path).parts
        area_name = parts[-2] if len(parts) >= 2 else parts[-1].replace(".md", "")

        contract = SliceContract(
            target=scope_path,
            ownership=[scope_path],
            priority=priority,
            context={
                "anchor_scope": scope_path,
                "tech_stack_summary": tech_stack,
                "test_command": test_cmd,
                "likely_entrypoints": _infer_entrypoints_for_area(area_name, repo_root),
                "related_scopes": _find_related_scopes(scope_path, repo_root),
            },
            acceptance={
                "done_when": "All sections filled with evidence or marked [Unknown]. Exactly 2 Mermaid diagrams. Trace table present.",
                "guard_command": f'python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --scope {scope_path}',
                "artifact_required": "JSON receipt with evidence_count, unknowns, graph_edges_found",
            },
        )
        contracts.append(contract)

    return contracts


def build_from_skeleton_output(skeleton_json: dict, repo_root: Path) -> list[SliceContract]:
    """Build slice contracts from scope_skeleton_generator.py JSON output."""
    contracts = []
    tech_stack = _extract_tech_stack_summary(repo_root)
    test_cmd = _extract_test_command(repo_root)

    created = skeleton_json.get("created", [])
    for entry in created:
        scope_path = entry.get("scope", "")
        if not scope_path:
            continue

        parts = Path(scope_path).parts
        area_name = parts[-2] if len(parts) >= 2 else parts[-1].replace(".md", "")

        contract = SliceContract(
            target=scope_path,
            ownership=[scope_path],
            priority="high",  # new scopes are always high priority
            context={
                "anchor_scope": scope_path,
                "tech_stack_summary": tech_stack,
                "test_command": test_cmd,
                "likely_entrypoints": _infer_entrypoints_for_area(area_name, repo_root),
                "related_scopes": _find_related_scopes(scope_path, repo_root),
            },
            acceptance={
                "done_when": "All sections filled with evidence or marked [Unknown]. Exactly 2 Mermaid diagrams. Trace table present.",
                "guard_command": f'python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --scope {scope_path}',
                "artifact_required": "JSON receipt with evidence_count, unknowns, graph_edges_found",
            },
        )
        contracts.append(contract)

    return contracts


def build_from_repo_inference(repo_root: Path) -> list[SliceContract]:
    """Infer capability areas from repo structure when Scopes/ is empty/missing."""
    contracts = []
    tech_stack = _extract_tech_stack_summary(repo_root)
    test_cmd = _extract_test_command(repo_root)

    # Look for top-level source directories
    src_dirs = []
    for candidate in ["src", "lib", "app", "pkg", "internal", "cmd", "components", "pages", "routes", "api"]:
        cand_path = repo_root / candidate
        if cand_path.is_dir():
            src_dirs.append(cand_path)

    if not src_dirs:
        # Fallback: look at any top-level directory that has code files
        for d in sorted(repo_root.iterdir()):
            if d.is_dir() and not d.name.startswith(".") and d.name not in (
                "node_modules", "vendor", "dist", "build", "__pycache__", "Scopes",
                "skills", "agents", "commands", "scripts", ".git"
            ):
                has_code = any(d.rglob("*.py")) or any(d.rglob("*.ts")) or any(d.rglob("*.go")) or any(d.rglob("*.js"))
                if has_code:
                    src_dirs.append(d)

    # Build one contract per top-level area
    for src_dir in src_dirs:
        subdirs = sorted([d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
        if not subdirs:
            # The src dir itself is a capability
            area_name = src_dir.name.replace("_", " ").replace("-", " ").title()
            scope_path = f"Scopes/Product/{area_name}/{area_name}.md"
            contract = SliceContract(
                target=scope_path,
                ownership=[scope_path],
                priority="high",
                context={
                    "anchor_scope": scope_path,
                    "tech_stack_summary": tech_stack,
                    "test_command": test_cmd,
                    "likely_entrypoints": [str(f.relative_to(repo_root)) for f in sorted(src_dir.glob("*.*"))[:3]],
                    "related_scopes": [],
                },
                acceptance={
                    "done_when": "All sections filled with evidence or marked [Unknown]. Exactly 2 Mermaid diagrams.",
                    "guard_command": 'python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --all --stale-only',
                    "artifact_required": "JSON receipt with evidence_count, unknowns, graph_edges_found",
                },
            )
            contracts.append(contract)
        else:
            for subdir in subdirs[:10]:  # cap at 10 areas
                area_name = subdir.name.replace("_", " ").replace("-", " ").title()
                scope_path = f"Scopes/Product/{src_dir.name.title()}/{area_name}.md"
                entrypoints = []
                for ext in ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.go", "*.rs"]:
                    entrypoints.extend(str(f.relative_to(repo_root)) for f in sorted(subdir.glob(ext))[:2])

                contract = SliceContract(
                    target=scope_path,
                    ownership=[scope_path],
                    priority="high",
                    context={
                        "anchor_scope": scope_path,
                        "tech_stack_summary": tech_stack,
                        "test_command": test_cmd,
                        "likely_entrypoints": entrypoints[:5],
                        "related_scopes": [],
                    },
                    acceptance={
                        "done_when": "All sections filled with evidence or marked [Unknown]. Exactly 2 Mermaid diagrams.",
                        "guard_command": 'python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --all --stale-only',
                        "artifact_required": "JSON receipt with evidence_count, unknowns, graph_edges_found",
                    },
                )
                contracts.append(contract)

    return contracts


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Build Slice Contracts for scope-filler agents/teammates.",
        epilog=(
            "Examples:\n"
            "  # From drift detector output:\n"
            "  scope_map_drift.json | python3 slice_contract_builder.py --from-drift -\n\n"
            "  # From skeleton generator output:\n"
            "  python3 slice_contract_builder.py --from-skeletons skeleton_output.json\n\n"
            "  # From repo inference (no existing Scopes/):\n"
            "  python3 slice_contract_builder.py --infer\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")

    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument("--from-drift", metavar="FILE",
                        help="Build contracts from drift_detector.py JSON output (use - for stdin)")
    source.add_argument("--from-skeletons", metavar="FILE",
                        help="Build contracts from scope_skeleton_generator.py JSON output")
    source.add_argument("--infer", action="store_true",
                        help="Infer capability areas from repo structure (for empty Scopes/)")

    ap.add_argument("--limit", type=int, default=0,
                    help="Max number of contracts to produce (0 = no limit)")

    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.from_drift:
        if args.from_drift == "-":
            data = json.load(sys.stdin)
        else:
            data = json.loads(Path(args.from_drift).read_text())
        contracts = build_from_drift(data, repo_root)
    elif args.from_skeletons:
        data = json.loads(Path(args.from_skeletons).read_text())
        contracts = build_from_skeleton_output(data, repo_root)
    elif args.infer:
        contracts = build_from_repo_inference(repo_root)
    else:
        ap.error("One of --from-drift, --from-skeletons, or --infer is required.")
        return 2

    # Sort by priority (high first)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    contracts.sort(key=lambda c: priority_order.get(c.priority, 1))

    if args.limit > 0:
        contracts = contracts[:args.limit]

    # Assign WIP slots for parallel batching (informational; orchestrator still chooses batch size)
    total = len(contracts)
    for idx, contract in enumerate(contracts):
        contract.wip_slot = f"{idx + 1} of {total}"

    output = {
        "contracts": [c.to_dict() for c in contracts],
        "total": len(contracts),
        "repo_root": str(repo_root),
    }

    json.dump(output, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
