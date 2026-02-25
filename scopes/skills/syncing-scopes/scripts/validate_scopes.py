#!/usr/bin/env python3
"""validate_scopes.py — Validate Scopes/ docs are usable + current.

This is the missing quality gate.

What it validates (deterministic, best-effort):
- Required META files exist (INDEX/GRAPH/DEVELOPER_INFO/TECH_STACK/WRITE_STYLE)
- Scopes/Product exists and contains at least 1 scope
- No obvious skeleton placeholders remain (path:Lx-Ly, TODO, "Fill with ...")
- Markdown links resolve and targets exist (scope links + evidence links)
- Evidence line anchors (#Lx or #Lx-Ly) are within target file bounds
- Router scopes link to micro scopes, and micro scopes link back to the parent router
- Drift gate: uses drift_detector.py to flag stale/missing evidence (fail by default)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from _md_links import parse_link_destination, resolve_repo_relative_path


MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
LINE_FRAG_RE = re.compile(r"^#L(\d+)(?:-L(\d+))?$")

PLACEHOLDER_RE = re.compile(
    r"(path:Lx-Ly|path#Lx-Ly|\bTODO\b|\bFill with\b|<(rule|failure|claim proven|claim|scope name|parent scope|child scope)>)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    kind: str
    file: str
    message: str
    target: str = ""


def _norm_path(p: str) -> str:
    s = p.strip().replace("\\", "/")
    while s.startswith("./"):
        s = s[2:]
    if s.startswith("/"):
        s = s[1:]
    return s


def _scope_files(repo_root: Path, scopes: list[str], area: str, want_all: bool) -> list[Path]:
    scopes_dir = repo_root / "Scopes" / "Product"
    if scopes:
        out: list[Path] = []
        for s in scopes:
            rel = _norm_path(s)
            p = (repo_root / rel).resolve()
            out.append(p)
        return out
    if area:
        ad = scopes_dir / area
        if ad.is_dir():
            return sorted(ad.rglob("*.md"))
        return sorted(
            p
            for p in scopes_dir.rglob("*.md")
            if area.lower() in str(p.relative_to(scopes_dir)).lower()
        )
    if want_all:
        return sorted(scopes_dir.rglob("*.md"))
    # default behavior: all
    return sorted(scopes_dir.rglob("*.md"))


def _resolve_link(repo_root: Path, src_file: Path, dest: str) -> tuple[str | None, str]:
    path_part, fragment, _rest = parse_link_destination(dest)
    rel = resolve_repo_relative_path(repo_root, src_file, path_part, normalize_bare=_norm_path)
    return rel, fragment


def _link_targets(text: str) -> list[tuple[str, str]]:
    # return list[(dest, label)]
    return [(dest, label) for (label, dest) in MD_LINK_RE.findall(text)]


def _validate_line_fragment(target_file: Path, fragment: str) -> str | None:
    m = LINE_FRAG_RE.match(fragment)
    if not m:
        return None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    if start <= 0 or end <= 0 or end < start:
        return f"invalid line fragment {fragment}"

    try:
        n_lines = sum(1 for _ in target_file.open("r", encoding="utf-8", errors="replace"))
    except Exception:
        return f"cannot read target to validate line fragment {fragment}"

    if start > n_lines or end > n_lines:
        return f"line fragment {fragment} exceeds file length (lines={n_lines})"
    return None


def _collect_resolved_scope_links(repo_root: Path, src: Path, text: str) -> set[str]:
    out: set[str] = set()
    for dest, _label in _link_targets(text):
        rel, _frag = _resolve_link(repo_root, src, dest)
        if not rel:
            continue
        if rel.endswith(".md") and rel.startswith("Scopes/Product/"):
            out.add(rel)
    return out


def _run_drift_detector(repo_root: Path) -> dict:
    drift_py = Path(__file__).resolve().parent / "drift_detector.py"
    # Importing drift_detector as a module would be cleaner, but it is a script today.
    import subprocess

    r = subprocess.run(
        [sys.executable, str(drift_py), "--repo-root", str(repo_root), "--all", "--stale-only", "--format", "json"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode not in (0, 1, 2):
        return {"items": [], "summary": {"stale": 0, "missing": 0, "ok": 0}, "error": r.stderr.strip()}
    try:
        return json.loads(r.stdout or "{}")
    except Exception:
        return {"items": [], "summary": {"stale": 0, "missing": 0, "ok": 0}, "error": "invalid drift json"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate Scopes/ docs and evidence links.")
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Scope file to validate (repeatable, repo-relative).",
    )
    ap.add_argument("--area", default="", help="Validate all scopes in area (e.g. Auth).")
    ap.add_argument("--all", action="store_true", help="Validate all Product scopes.")
    ap.add_argument(
        "--allow-stale",
        action="store_true",
        help="Do not fail on stale evidence (still reported).",
    )
    ap.add_argument("--format", choices=["compact", "json"], default="compact")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()

    required_meta = [
        "Scopes/INDEX.md",
        "Scopes/GRAPH.md",
        "Scopes/DEVELOPER_INFO.md",
        "Scopes/Onboarding/TECH_STACK.md",
        "Scopes/Work/Standards/WRITE_STYLE.md",
    ]

    findings: list[Finding] = []
    for rel in required_meta:
        if not (repo_root / rel).exists():
            findings.append(Finding(kind="missing_meta", file=rel, message="required meta file missing"))

    scopes_dir = repo_root / "Scopes" / "Product"
    if not scopes_dir.exists():
        findings.append(Finding(kind="missing_product_root", file="Scopes/Product/", message="Scopes/Product/ not found"))
        return _emit(findings, args.format, exit_code=2)

    scope_files = _scope_files(repo_root, args.scope, args.area, args.all)
    scope_files = [p for p in scope_files if p.exists()]

    if not scope_files:
        findings.append(Finding(kind="no_product_scopes", file="Scopes/Product/", message="no scope files found"))
        return _emit(findings, args.format, exit_code=1)

    # Pre-run drift detector (all scopes) and filter to scope set.
    drift = _run_drift_detector(repo_root)
    drift_items = drift.get("items", []) if isinstance(drift, dict) else []
    allowed_scopes: set[str] = set(
        (p.relative_to(repo_root).as_posix() for p in scope_files)
    )
    for item in drift_items:
        scope = str(item.get("scope", ""))
        if scope and scope in allowed_scopes:
            status = str(item.get("status", ""))
            tgt = str(item.get("target", ""))
            msg = f"{status}: code changed after scope ({item.get('scope_date')} < {item.get('code_date')})"
            findings.append(Finding(kind="drift", file=scope, message=msg, target=tgt))

    # Validate each scope file: placeholders + links + micro connectivity.
    for sf in scope_files:
        rel_sf = sf.relative_to(repo_root).as_posix()
        text = sf.read_text(encoding="utf-8", errors="replace")

        if PLACEHOLDER_RE.search(text):
            findings.append(Finding(kind="placeholder", file=rel_sf, message="skeleton placeholder(s) still present"))

        for dest, label in _link_targets(text):
            resolved, frag = _resolve_link(repo_root, sf, dest)
            if not resolved:
                continue
            target_path = repo_root / resolved
            if not target_path.exists():
                findings.append(
                    Finding(
                        kind="broken_link",
                        file=rel_sf,
                        message=f"link target missing (label={label})",
                        target=resolved,
                    )
                )
                continue
            if frag:
                err = _validate_line_fragment(target_path, frag)
                if err:
                    findings.append(
                        Finding(
                            kind="bad_line_anchor",
                            file=rel_sf,
                            message=err,
                            target=f"{resolved}{frag}",
                        )
                    )

        # Router <-> micro link checks for generated micro layouts.
        parts = rel_sf.split("/")
        is_router = rel_sf.startswith("Scopes/Product/") and len(parts) == 4  # Scopes/Product/<Area>/<Capability>.md
        if is_router and sf.suffix == ".md":
            micro_dir = sf.parent / sf.stem
            if micro_dir.exists() and micro_dir.is_dir():
                micro_files = sorted(micro_dir.glob("*.md"))
                if micro_files:
                    router_links = _collect_resolved_scope_links(repo_root, sf, text)
                    for mf in micro_files:
                        rel_mf = mf.relative_to(repo_root).as_posix()
                        if rel_mf not in router_links:
                            findings.append(
                                Finding(
                                    kind="micro_unlinked",
                                    file=rel_sf,
                                    message="router does not link to micro scope",
                                    target=rel_mf,
                                )
                            )

                        micro_text = mf.read_text(encoding="utf-8", errors="replace")
                        micro_links = _collect_resolved_scope_links(repo_root, mf, micro_text)
                        if rel_sf not in micro_links:
                            findings.append(
                                Finding(
                                    kind="micro_missing_parent",
                                    file=rel_mf,
                                    message="micro scope does not link back to router",
                                    target=rel_sf,
                                )
                            )

    # Decide exit code
    drift_findings = [f for f in findings if f.kind == "drift"]
    non_drift_findings = [f for f in findings if f.kind != "drift"]
    has_failures = bool(non_drift_findings) or (bool(drift_findings) and not args.allow_stale)

    exit_code = 1 if has_failures else 0
    return _emit(findings, args.format, exit_code=exit_code)


def _emit(findings: list[Finding], fmt: str, *, exit_code: int) -> int:
    if fmt == "json":
        payload = {
            "status": "pass" if exit_code == 0 else "fail",
            "findings_count": len(findings),
            "findings": [asdict(f) for f in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return exit_code

    counts: dict[str, int] = {}
    for f in findings:
        counts[f.kind] = counts.get(f.kind, 0) + 1

    if not findings:
        print("Scopes validation: PASS")
        return exit_code

    parts = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"Scopes validation: FAIL ({parts})")
    for f in findings[:80]:
        tgt = f" -> {f.target}" if f.target else ""
        print(f"- {f.kind}: {f.file}: {f.message}{tgt}")
    if len(findings) > 80:
        print(f"... ({len(findings) - 80} more)")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
