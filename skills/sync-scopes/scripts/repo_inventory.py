#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "target",
    ".venv",
    "venv",
    ".tox",
    ".idea",
    ".cursor",
    ".claude",
    ".agent",
}


def _walk_files(repo_root: Path) -> list[Path]:
    out: list[Path] = []
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            out.append(Path(root) / f)
    return out


def _detect_tooling(repo_root: Path) -> dict:
    def exists(rel: str) -> bool:
        return (repo_root / rel).exists()

    tooling = {
        "node": {
            "package_json": exists("package.json"),
            "pnpm_lock": exists("pnpm-lock.yaml"),
            "yarn_lock": exists("yarn.lock"),
            "npm_lock": exists("package-lock.json"),
        },
        "python": {
            "pyproject_toml": exists("pyproject.toml"),
            "requirements_txt": exists("requirements.txt"),
            "poetry_lock": exists("poetry.lock"),
            "pipfile": exists("Pipfile"),
        },
        "go": {"go_mod": exists("go.mod")},
        "rust": {"cargo_toml": exists("Cargo.toml")},
        "ruby": {"gemfile": exists("Gemfile")},
        "dotnet": {
            "sln": any(p.suffix == ".sln" for p in repo_root.glob("*.sln")),
            "csproj": any(repo_root.rglob("*.csproj")),
        },
    }
    return tooling


def _read_package_json(repo_root: Path) -> dict:
    package_json = repo_root / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return {}


def _package_contains(package: dict, token: str) -> bool:
    lowered = token.lower()
    for field in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        deps = package.get(field)
        if isinstance(deps, dict):
            for name in deps.keys():
                if lowered in str(name).lower():
                    return True
    scripts = package.get("scripts")
    if isinstance(scripts, dict):
        for value in scripts.values():
            if lowered in str(value).lower():
                return True
    return False


def _detect_tests(repo_root: Path) -> dict:
    # Lightweight but not overly broad signals.
    pyproject = (repo_root / "pyproject.toml")
    pyproject_text = ""
    if pyproject.exists():
        pyproject_text = pyproject.read_text(encoding="utf-8", errors="replace").lower()

    requirements = (repo_root / "requirements.txt")
    requirements_text = ""
    if requirements.exists():
        requirements_text = requirements.read_text(encoding="utf-8", errors="replace").lower()

    package = _read_package_json(repo_root)

    signals = {
        "pytest": (repo_root / "pytest.ini").exists()
        or "pytest" in pyproject_text
        or "pytest" in requirements_text,
        "jest": any(repo_root.glob("jest.config.*")) or _package_contains(package, "jest"),
        "vitest": any(repo_root.glob("vitest.config.*")) or _package_contains(package, "vitest"),
        "go_test": (repo_root / "go.mod").exists(),
        "cargo_test": (repo_root / "Cargo.toml").exists(),
    }
    return signals


def _top_extensions(files: list[Path], repo_root: Path, limit: int = 20) -> list[dict]:
    counts: dict[str, int] = {}
    for p in files:
        try:
            rel = p.relative_to(repo_root)
        except Exception:
            rel = p
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        ext = p.suffix.lower()
        if not ext:
            continue
        counts[ext] = counts.get(ext, 0) + 1
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"ext": k, "count": v} for k, v in top]


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Inventory repo languages/tooling/test signals to support Scopes TECH_STACK and DEVELOPER_INFO updates."
    )
    ap.add_argument("--repo-root", default=".", help="Repo root (default: .).")
    ap.add_argument("--format", choices=["json"], default="json", help="Output format (default: json).")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    files = _walk_files(repo_root)

    payload = {
        "repo_root": repo_root.as_posix(),
        "tooling": _detect_tooling(repo_root),
        "test_signals": _detect_tests(repo_root),
        "top_extensions": _top_extensions(files, repo_root),
        "counts": {
            "files_total": len(files),
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
