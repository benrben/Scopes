# Syncing Scopes: Reference Protocols

Load this file when you need detailed rules beyond `skills/syncing-scopes/SKILL.md`.

## Scopes Root Layout (Canonical)

- `Scopes/INDEX.md` (tree entrypoint)
- `Scopes/GRAPH.md` (relationships + edges)
- `Scopes/DEVELOPER_INFO.md` (how to run/test/build; commands + signals)
- `Scopes/Onboarding/TECH_STACK.md` (stack inventory with evidence)
- `Scopes/Work/Standards/WRITE_STYLE.md` (engineering standards)
- Capability overview scopes (router): `Scopes/Product/<Area>/<Capability>.md` (router + cross-links; diagrams as needed)
- Micro scopes (smaller slices): `Scopes/Product/<Area>/<Capability>/<MicroScope>.md` (leaf slices; diagrams as needed)
- Work artifacts: `Scopes/Work/Planning/**`, `Scopes/Work/Tasks/**`, `Scopes/Work/Bugs/**`, `Scopes/Work/Refactors/**`
- Research: `Scopes/Research/**`
- Decisions: `Scopes/Decisions/ADRs/**`

## Operating Modes

### Generation Mode (No usable `Scopes/`)
- Create initial structure + top-level capability scopes.
- Bootstrap `INDEX.md`, `GRAPH.md`, `DEVELOPER_INFO.md`, `TECH_STACK.md`, and `WRITE_STYLE.md`.

### Update Mode (Scopes exist)
- Assume drift: treat existing prose as stale until proven by evidence.
- Prefer updating existing files/paths over churn.
- Validate after edits: broken links + drift.

## Evidence Protocol

Evidence link format: `[path:Lx-Ly](path#Lx-Ly)`

Evidence strength (strongest -> weakest):
1. Tests
2. Config/wiring (routes, DI, flags)
3. Schema/contracts (DB, OpenAPI, types)
4. Implementation (controllers/services)
5. Comments (hints only)

If you cannot find evidence, write `[Unknown]` and stop.

## Developer Info Protocol

Update `Scopes/DEVELOPER_INFO.md` when you discover:
- run/test/build commands
- required env vars or setup
- verification ladders per area

Prefer the format: `Command -> Signal` and link to the source of truth (config files).

## Template Fidelity

Capability scope templates live in `skills/syncing-scopes/references/TEMPLATES.md`.
Follow them exactly, including:
- include all diagram blocks that apply; delete the ones that don’t (never leave placeholders unchanged)
- at least 1 end-to-end trace per major path

## Post-Write Validation (Default)

After writing/updating scopes:
- `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all`
