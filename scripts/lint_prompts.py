#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ALLOWED_VERDICTS = ["Proceed", "Blocked", "Needs Sync", "Needs Narrowing"]


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


def _fm_has_key(frontmatter: str, key: str) -> bool:
    return re.search(rf"(?m)^{re.escape(key)}\s*:\s*\S+", frontmatter) is not None


def _fm_key_value(frontmatter: str, key: str) -> str | None:
    m = re.search(rf"(?m)^{re.escape(key)}\s*:\s*(.+)\s*$", frontmatter)
    if not m:
        return None
    return m.group(1).strip()


def _has_heading(text: str, heading_prefix: str) -> bool:
    # heading_prefix examples: "## Mission Start"
    return re.search(rf"(?m)^{re.escape(heading_prefix)}\b", text) is not None


def _find_output_contract_block(text: str) -> str | None:
    # Find the "## Output Contract" section and take until the next "## " heading,
    # but ignore headings inside fenced code blocks.
    m = re.search(r"(?m)^## Output Contract\b", text)
    if not m:
        return None

    start = m.start()
    lines = text[start:].splitlines(keepends=True)
    in_fence = False
    out: list[str] = []

    for i, line in enumerate(lines):
        out.append(line)
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if i == 0:
            continue
        if not in_fence and re.match(r"^##\s+", line):
            out.pop()  # boundary heading belongs to next section
            break

    return "".join(out)


def _contains_line_limit(text: str) -> bool:
    return re.search(r"(?mi)\breturn\b.*(<=|≤)\s*\d+\s*lines", text) is not None


def lint_skill(path: Path) -> list[LintError]:
    errors: list[LintError] = []
    text = _read_text(path)
    frontmatter = _extract_frontmatter(text)
    if frontmatter is None:
        errors.append(LintError(path, "missing YAML frontmatter"))
        return errors

    for key in ["name", "description"]:
        if not _fm_has_key(frontmatter, key):
            errors.append(LintError(path, f"frontmatter missing required key: {key!r}"))

    if "skills/_shared/SCOPES_PROTOCOL.md" not in text:
        errors.append(LintError(path, "missing canonical protocol reference: `skills/_shared/SCOPES_PROTOCOL.md`"))

    for heading in ["## Mission Start", "## When to Stop", "## Blocked Runbook", "## Output Contract"]:
        if not _has_heading(text, heading):
            errors.append(LintError(path, f"missing required heading: {heading}"))

    oc = _find_output_contract_block(text)
    if oc is None:
        return errors

    if not _contains_line_limit(oc):
        errors.append(LintError(path, "Output Contract missing explicit line limit (e.g. 'Return <= N lines')"))

    verdict_line = next((ln for ln in oc.splitlines() if "Verdict:" in ln), None)
    if verdict_line is None:
        errors.append(LintError(path, "Output Contract missing `Verdict:` line"))
    else:
        for v in ALLOWED_VERDICTS:
            if v not in verdict_line:
                errors.append(LintError(path, f"Verdict line must include allowed verdict: {v!r}"))
                break

    return errors


def lint_agent(path: Path) -> list[LintError]:
    errors: list[LintError] = []
    text = _read_text(path)
    frontmatter = _extract_frontmatter(text)
    if frontmatter is None:
        errors.append(LintError(path, "missing YAML frontmatter"))
        return errors

    for key in ["name", "description", "tools", "model", "readonly"]:
        if not re.search(rf"(?m)^{re.escape(key)}\s*:", frontmatter):
            errors.append(LintError(path, f"frontmatter missing required key: {key!r}"))

    readonly_value = _fm_key_value(frontmatter, "readonly")
    if readonly_value is not None and readonly_value.lower() in {"false", "no", "0"}:
        if not re.search(r"(?m)^allowed_output_roots\s*:", frontmatter):
            errors.append(LintError(path, "readonly: false requires frontmatter key: allowed_output_roots"))

    for heading in ["## Output Contract", "## When to Stop"]:
        if not _has_heading(text, heading):
            errors.append(LintError(path, f"missing required heading: {heading}"))

    oc = _find_output_contract_block(text)
    if oc is None:
        return errors

    if not _contains_line_limit(oc):
        errors.append(LintError(path, "Output Contract missing explicit line limit (e.g. 'Return <= N lines')"))

    required_fields = ["Verdict:", "Decision:", "Evidence:", "Next:", "Artifact:"]
    for field in required_fields:
        if field not in oc:
            errors.append(LintError(path, f"Output Contract missing required field: {field!r}"))

    # Unknowns is required only when blocked/partial, but the schema must define it.
    if "Unknowns:" not in oc:
        errors.append(LintError(path, "Output Contract missing schema field: 'Unknowns:'"))

    verdict_line = next((ln for ln in oc.splitlines() if "Verdict:" in ln), None)
    if verdict_line is None:
        errors.append(LintError(path, "Output Contract missing `Verdict:` line"))
    else:
        for v in ALLOWED_VERDICTS:
            if v not in verdict_line:
                errors.append(LintError(path, f"Verdict line must include allowed verdict: {v!r}"))
                break

    # Artifact path sanity checks (best-effort).
    if re.search(r"Scopes/Work/Bugs", text) and re.search(r"Scopes/Work/Bug[^s/]", text):
        errors.append(LintError(path, "suspicious bug artifact root: use `Scopes/Work/Bugs/**`"))

    return errors


def main() -> int:
    errors: list[LintError] = []

    skill_files = sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))
    for p in skill_files:
        if p.parent.name.startswith("_"):
            continue
        errors.extend(lint_skill(p))

    agent_dir = REPO_ROOT / "agents"
    agent_files = sorted(agent_dir.glob("*.md"))
    for p in agent_files:
        if p.name == "WORKFLOW.md":
            continue
        errors.extend(lint_agent(p))

    if errors:
        for e in errors:
            rel = e.path.relative_to(REPO_ROOT)
            print(f"[FAIL] {rel}: {e.message}")
        print(f"\n{len(errors)} error(s)")
        return 1

    print("OK: prompt contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
