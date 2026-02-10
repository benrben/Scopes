# Scopes — Skills & Agents for Agentic IDEs

> **Scopes: Because "What does this code even do?" shouldn't be a full-time job.**
>
> Evidence-backed docs + implementation workflows, packaged as copy-paste skills and agents.

![Scopes skills](https://img.shields.io/badge/Scopes-skills-111827)
![Evidence-backed docs](https://img.shields.io/badge/docs-evidence--backed-0ea5e9)
![Scopes-first](https://img.shields.io/badge/workflow-scopes--first-22c55e)
![License](https://img.shields.io/badge/license-MIT-blue)

<p align="center">
  <img src="docs/assets/scopes.jpg" alt="Scopes diagram showing how Scopes transforms a codebase into evidence-backed documentation" width="700" />
</p>

## TL;DR

Scopes are **behavior docs with receipts** (links into code/tests/config). This repo ships skills and agents so teams can:

- Create and maintain `Scopes/` as a reliable system map.
- Convert ideas/research/findings into executable plans and tasks.
- Implement safely while keeping documentation synchronized.

Core artifacts in target repos:
- `Scopes/INDEX.md`
- `Scopes/GRAPH.md`
- `Scopes/Product/**`

## Install

Copy the folders into your project's IDE config directory:

### Cursor

```bash
# From your project root:
cp -r /path/to/Scopes/skills/ .cursor/skills/
cp -r /path/to/Scopes/agents/ .cursor/agents/
```

### Claude Code

```bash
cp -r /path/to/Scopes/skills/ .claude/skills/
cp -r /path/to/Scopes/agents/ .claude/agents/
```

### Antigravity

```bash
cp -r /path/to/Scopes/skills/ .agent/skills/
cp -r /path/to/Scopes/agents/ .agent/agents/
```

### Update installed skills

Once installed, the `update-skills` skill can refresh itself from upstream:

```bash
bash .cursor/skills/update-skills/scripts/update-skills.sh
```

## Skill Catalog

| Skill | Purpose |
|---|---|
| `sync-scopes` | Generate/update Scopes truth from code/config with git baseline + diff tracking |
| `ask-scopes` | Answer project questions by navigating Scopes first, then code evidence |
| `dev-tdd` | Strict TDD implementation loop with scope maintenance |
| `dev-verify` | Verify-as-you-go implementation loop with scope maintenance |
| `bug-hunt` | Evidence-backed bug and foot-gun discovery |
| `write-tasks` | Turn intent/research/findings into engineer-ready tasks |
| `plan-idea` | Convert ideas into sequenced implementation plans |
| `plan-refactor` | Safe phased refactor planning |
| `research-loop` | Internal-vs-external truth separated research reports |
| `write-adr` | Architecture decision records linked to Scopes |
| `update-skills` | Refresh installed skills from upstream |

## Agent Catalog

Agents are sub-agents that run in their own context window, keeping verbose output out of your main conversation.

| Agent | Purpose |
|---|---|
| `scope-auditor` | Validates evidence freshness and link integrity |
| `scope-navigator` | Maps requests to relevant scope files and dependencies |
| `scope-writer` | Creates/updates scope documentation with evidence links |
| `tdd-runner` | Runs Red→Green→Refactor TDD cycles in isolated context |
| `bug-scanner` | Static analysis with scope-aware blast radius context |
| `plan-researcher` | Background research across code, git history, and ADRs |

## Recommended Workflows

- Understand current behavior quickly: `ask-scopes` → `dev-verify` or `dev-tdd`
- Fix a bug: `bug-hunt` → `write-tasks` → `dev-tdd`
- Ship a feature: `plan-idea` → `write-tasks` → `dev-tdd` or `dev-verify`
- Make a decision: `research-loop` → `write-adr` → `write-tasks`
- Plan a structural change: `plan-refactor` → `write-tasks` → `dev-tdd`

## Docs

- Background and methodology: [`docs/why-scopes.md`](docs/why-scopes.md)

## Contributing

- Keep skill packages under `skills/<name>/`.
- Keep agent definitions under `agents/<name>.md`.
- Keep each skill self-contained (`SKILL.md`, optional `scripts/`, `references/`, `assets/`).
- Update this README when adding or renaming skills/agents.

## License

This project is licensed under the MIT License — see the `LICENSE` file for details.
