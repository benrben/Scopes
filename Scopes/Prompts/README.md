# Scopes Prompts (Agents)

This folder contains the “command prompts” (agents) that generate and maintain everything under `Scopes/`.

## The Root Rule
All generated artifacts MUST live under `Scopes/` (never outside it). The canonical layout is defined in `Scopes/Prompts/sync-scopes.md` under **Scopes Root Layout**.

## Start Here
- `sync-scopes.md`: The **gold standard** for Capability Scopes (templates, diagrams, traces, evidence, cross-links, audit protocol).

## Commands (By Category)

### Work (planning + execution)
- `dev-loop.md`: TDD driver (RED → GREEN → REFACTOR → SCOPE maintenance)
- `write-tasks.md`: engineer-ready task file generator
- `plan-board.md`: derive a kanban/board blueprint from `Scopes/INDEX.md` + `Scopes/GRAPH.md`
- `plan-idea.md`: turn an idea into a sequenced implementation plan
- `plan-refactor.md`: safe refactor planning with verification gates
- `ideate.md`: generate scope-anchored ideas ready for planning
- `bug-hunt.md`: find bugs/anti-patterns with evidence, then produce a bug report (and optional tasks)

### Research / Releases / Onboarding / Decisions
- `research-loop.md`: internal + external research, with strict truth separation
- `write-release.md`: release notes that are scope-linked and auditable
- `write-onboarding.md`: onboarding tours driven by Capability Scope traces
- `write-adr.md`: ADR creation with explicit “Affected Scopes” linkage

## Prompt Quality Bar (Audit)
Every prompt in this folder should:
- Define **required reads** (`Scopes/INDEX.md`, `Scopes/GRAPH.md`, relevant `Scopes/Product/**` scopes).
- Define **output paths** under the correct `Scopes/` subfolder.
- Include at least one **diagram** (Mermaid) explaining the workflow.
- Include an **audit checklist** so outputs are consistent and verifiable.
- Prefer a consistent spine: **Required Reads → Output Location → Diagram → Method (Silent) + Output Contract (Visible) → Rules & Constraints → Output Artifacts → Audit Checklist**.

