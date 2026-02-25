"""scopes/scripts/cmd_work.py — Work commands: session:start/read, tasks, task:create, agents, skills."""
from __future__ import annotations

import sys
from datetime import date as Date
from pathlib import Path
from textwrap import dedent

from cli_helpers import (
    CliContext,
    _error,
    _json_out,
    _parse_frontmatter,
)


def cmd_session_start(ctx: CliContext, args) -> int:
    try:
        scope_name = getattr(args, 'scope', '')
        goal = getattr(args, 'goal', '')

        notes_dir = ctx.scopes_root / "Work" / "Notes"
        notes_dir.mkdir(parents=True, exist_ok=True)

        today = Date.today().isoformat()
        topic = scope_name.replace('/', '-').lower() or 'session'
        session_file = notes_dir / f"session-{today}-{topic}.md"

        content = dedent(f"""---
date: {today}
goal: {goal}
scope: {scope_name}
---

# Session: {goal or 'Work'} on {scope_name}

## Findings

## Decisions

## Next
""").strip()

        session_file.write_text(content)

        scopes_state = ctx.scopes_root.parent / ".scopes"
        scopes_state.mkdir(exist_ok=True)
        (scopes_state / "current_session").write_text(str(session_file))

        if ctx.format == "json":
            print(_json_out({
                "session": str(session_file.relative_to(ctx.scopes_root)),
                "status": "created",
            }))
        else:
            print(f"✓ Session created: {session_file}")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_session_read(ctx: CliContext, args) -> int:
    try:
        scopes_state = ctx.scopes_root.parent / ".scopes"
        current_file = scopes_state / "current_session"

        if current_file.exists():
            session_path = Path(current_file.read_text().strip())
        else:
            notes_dir = ctx.scopes_root / "Work" / "Notes"
            sessions = sorted(notes_dir.glob("session-*.md"), reverse=True) if notes_dir.exists() else []
            if not sessions:
                print(_error("No sessions found"), file=sys.stderr)
                return 1
            session_path = sessions[0]

        if not session_path.exists():
            print(_error(f"Session not found: {session_path}"), file=sys.stderr)
            return 1

        content = session_path.read_text(encoding="utf-8", errors="ignore")
        print(content)
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_tasks(ctx: CliContext, args) -> int:
    try:
        tasks_dir = ctx.scopes_root / "Work" / "Tasks"
        if not tasks_dir.exists():
            print(_json_out([]))
            return 0

        status_filter = getattr(args, 'status', '')
        scope_filter = getattr(args, 'scope', '')

        tasks_list = []
        for task_file in sorted(tasks_dir.glob("**/*.md")):
            try:
                content = task_file.read_text(encoding="utf-8", errors="ignore")
                fm = _parse_frontmatter(content)

                if status_filter and fm.get('status') != status_filter:
                    continue
                if scope_filter and scope_filter not in fm.get('scope', ''):
                    continue

                tasks_list.append({
                    "id": task_file.stem,
                    "title": fm.get('title', task_file.stem),
                    "scope": fm.get('scope', ''),
                    "status": fm.get('status', 'pending'),
                    "path": str(task_file.relative_to(ctx.scopes_root)),
                })
            except Exception:
                pass

        print(_json_out(tasks_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_task_create(ctx: CliContext, args) -> int:
    try:
        scope = getattr(args, 'scope', '')
        title = getattr(args, 'title', '')

        if not title:
            print(_error("--title required"), file=sys.stderr)
            return 1

        tasks_dir = ctx.scopes_root / "Work" / "Tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        today = Date.today().isoformat()
        task_id = title.lower().replace(' ', '-')[:30]
        task_file = tasks_dir / f"{task_id}.md"

        content = dedent(f"""---
title: {title}
scope: {scope}
status: pending
created: {today}
---

# Task: {title}

## Scope
{scope}

## Description

## Acceptance Criteria

## Notes
""").strip()

        task_file.write_text(content)

        if ctx.format == "json":
            print(_json_out({"id": task_id, "status": "created"}))
        else:
            print(f"✓ Task created: {task_file}")

        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_agents(ctx: CliContext, args) -> int:
    try:
        agents_dir = ctx.scopes_root.parent / "agents"
        if not agents_dir.exists():
            print(_json_out([]))
            return 0

        agents_list = []
        for agent_file in sorted(agents_dir.glob("*.md")):
            if agent_file.name == "WORKFLOW.md":
                continue
            try:
                content = agent_file.read_text(encoding="utf-8", errors="ignore")
                fm = _parse_frontmatter(content)
                agents_list.append({
                    "id": agent_file.stem,
                    "name": fm.get('name', agent_file.stem),
                    "description": fm.get('description', ''),
                })
            except Exception:
                pass

        print(_json_out(agents_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1


def cmd_skills(ctx: CliContext, args) -> int:
    try:
        skills_dir = ctx.scopes_root / "skills"
        if not skills_dir.exists():
            print(_json_out([]))
            return 0

        skills_list = []
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith('_'):
                continue

            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                try:
                    content = skill_file.read_text(encoding="utf-8", errors="ignore")
                    fm = _parse_frontmatter(content)
                    skills_list.append({
                        "id": skill_dir.name,
                        "name": fm.get('name', skill_dir.name),
                        "description": fm.get('description', ''),
                    })
                except Exception:
                    pass

        print(_json_out(skills_list))
        return 0
    except Exception as e:
        print(_error(str(e)), file=sys.stderr)
        return 1
