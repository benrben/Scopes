#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LintError:
    path: Path
    message: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return text[4:end + 1]


def _fm_key_value(frontmatter: str, key: str) -> str | None:
    m = re.search(rf"(?m)^{re.escape(key)}\s*:\s*(.+)\s*$", frontmatter)
    if not m:
        return None
    return m.group(1).strip()


def _iter_markdown_links(text: str) -> list[str]:
    # Collect relative (non-http) link targets.
    targets: list[str] = []
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        raw = m.group(1).strip()
        if "://" in raw or raw.startswith("#") or raw.startswith("mailto:"):
            continue
        raw = raw.split("#", 1)[0].strip()
        if not raw:
            continue
        # This repo contains many templates with placeholder link targets.
        # Only validate links that look like they intend to point to a Markdown file.
        if not raw.endswith(".md"):
            continue
        if "<" in raw or ">" in raw:
            continue
        targets.append(raw)
    return targets


def lint_skills_name_matches_folder() -> list[LintError]:
    errors: list[LintError] = []
    for skill_dir in sorted((REPO_ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith("_"):
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            errors.append(LintError(skill_dir, "missing SKILL.md"))
            continue
        text = _read_text(skill_file)
        fm = _extract_frontmatter(text)
        if fm is None:
            errors.append(LintError(skill_file, "missing YAML frontmatter"))
            continue
        name = _fm_key_value(fm, "name")
        if name is None:
            errors.append(LintError(skill_file, "frontmatter missing 'name'"))
            continue
        if name != skill_dir.name:
            errors.append(LintError(skill_file, f"frontmatter name {name!r} must match folder {skill_dir.name!r}"))
    return errors


def lint_commands_reference_existing_skills() -> list[LintError]:
    errors: list[LintError] = []
    commands_dir = REPO_ROOT / "commands"
    for cmd_file in sorted(commands_dir.glob("*.md")):
        text = _read_text(cmd_file)
        for m in re.finditer(r"`(skills/[^`]+/SKILL\.md)`", text):
            rel = m.group(1)
            target = REPO_ROOT / rel
            if not target.exists():
                errors.append(LintError(cmd_file, f"references missing skill file: {rel}"))
    return errors


def lint_readme_lists_match() -> list[LintError]:
    errors: list[LintError] = []
    readme = REPO_ROOT / "README.md"
    text = _read_text(readme)

    skill_dirs = sorted(d.name for d in (REPO_ROOT / "skills").iterdir() if d.is_dir() and not d.name.startswith("_"))
    agent_files = sorted(p.stem for p in (REPO_ROOT / "agents").glob("*.md") if p.name != "WORKFLOW.md")

    skills_in_readme = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`\s+—", text))
    agents_in_readme = set(re.findall(r"`([a-z0-9][a-z0-9-]+)`\s+—", text))

    # README contains both Skills and Agents using the same backtick pattern; disambiguate by actual sets.
    missing_skills = sorted(set(skill_dirs) - skills_in_readme)
    extra_skills = sorted(skills_in_readme - set(skill_dirs) - set(agent_files))

    missing_agents = sorted(set(agent_files) - agents_in_readme)
    extra_agents = sorted(agents_in_readme - set(agent_files) - set(skill_dirs))

    if missing_skills:
        errors.append(LintError(readme, f"README missing skills: {', '.join(missing_skills)}"))
    if extra_skills:
        errors.append(LintError(readme, f"README lists unknown skills: {', '.join(extra_skills)}"))
    if missing_agents:
        errors.append(LintError(readme, f"README missing agents: {', '.join(missing_agents)}"))
    if extra_agents:
        errors.append(LintError(readme, f"README lists unknown agents: {', '.join(extra_agents)}"))

    return errors


def lint_internal_links_exist() -> list[LintError]:
    errors: list[LintError] = []
    # Validate links only in the "package" surfaces, not in Scopes templates.
    md_files: list[Path] = []
    md_files.append(REPO_ROOT / "README.md")
    md_files.extend((REPO_ROOT / "docs").rglob("*.md"))
    md_files.extend((REPO_ROOT / "commands").rglob("*.md"))
    md_files.extend((REPO_ROOT / "agents").glob("*.md"))
    md_files.extend((REPO_ROOT / "skills").glob("*/SKILL.md"))
    md_files.extend((REPO_ROOT / "skills" / "_shared").glob("*.md"))

    for path in md_files:
        if not path.exists():
            continue
        if "references" in path.parts:
            continue
        if path.name == "SESSION_LOG_TEMPLATES.md":
            continue
        text = _read_text(path)
        for target in _iter_markdown_links(text):
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(REPO_ROOT)
            except ValueError:
                # Link points outside repo; ignore (not useful to validate here).
                continue
            if not resolved.exists():
                errors.append(LintError(path, f"broken internal link: {target}"))
    return errors


def main() -> int:
    errors: list[LintError] = []
    errors.extend(lint_skills_name_matches_folder())
    errors.extend(lint_commands_reference_existing_skills())
    errors.extend(lint_readme_lists_match())
    errors.extend(lint_internal_links_exist())

    if errors:
        for e in errors:
            rel = e.path.relative_to(REPO_ROOT)
            print(f"[FAIL] {rel}: {e.message}")
        print(f"\n{len(errors)} error(s)")
        return 1

    print("OK: package consistency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
