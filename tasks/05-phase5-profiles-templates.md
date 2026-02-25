---
title: "Phase 5 — Profiles, Templates & Config"
status: pending
phase: 5
effort: "~300-400 lines"
created: 2026-02-25
depends_on: [04-phase4-sync-engine]
blocks: []
source: docs/cli-plan.md#8-phase-5--profiles-templates--config
---

# Phase 5 — Profiles, Templates & Config

> Customization layer — different project types get different scope structures,
> templates, and agent configurations.

## Tasks

### 5.1 Profile System

Profiles are JSON files defining defaults for a project type.
Stored in `scopes/profiles/` (bundled) or `~/.scopes/profiles/` (user).

- [ ] Define profile JSON schema:
  ```json
  {
    "name": "python-api",
    "description": "Python API project with routes, models, services",
    "default_areas": ["API", "Models", "Services", "Config", "Auth"],
    "scope_sections": ["Entry Points", "Tests", "Config", "Dependencies"],
    "evidence_patterns": ["*.py", "*.yaml", "*.toml"],
    "ignore_patterns": ["__pycache__", ".venv", "*.pyc"]
  }
  ```
- [ ] **`scopes profiles`** — list available profiles (bundled + user)
- [ ] **`scopes profile`** — show current active profile (from `.scopes/profile`)
- [ ] **`scopes profile:set --name "python-api"`** — switch profile
  - Write to `.scopes/profile`
- [ ] **`scopes profile:install --repo "scopes-community/python-api-profile"`**
  - Download profile JSON to `~/.scopes/profiles/`
- [ ] **`scopes profile:uninstall --name "python-api"`** — remove user profile

### 5.2 Template System

Templates stored in `scopes/templates/` with `{{variable}}` placeholders.

- [ ] Define template format:
  - `.md` files with `{{scope_name}}`, `{{area_name}}`, `{{date}}`, `{{status}}` variables
  - Types: `capability`, `task`, `adr`, `session-log`, `summary-note`, `refactor-plan`
- [ ] Implement variable substitution engine (`_render_template`)
- [ ] **`scopes templates`** — list all available templates
  - `--type scope` — filter by type
- [ ] **`scopes template:read --name "capability"`** — show template content
- [ ] **`scopes template:insert --name "capability" --target "Scopes/Product/Auth/MFA.md"`**
  - Render template with variables, write to target path
- [ ] **`scopes template:create --name "my-scope" --base "capability"`**
  - Copy existing template as starting point for customization
- [ ] **`scopes template:variables --name "capability"`**
  - List all `{{variable}}` placeholders in a template

### 5.3 Config Overrides

Config snippets are small JSON files that override default behaviors.

- [ ] **`scopes configs`** — list available config snippets
- [ ] **`scopes configs:enabled`** — list active config overrides
- [ ] **`scopes config:enable --name "ignore-tests"`** — enable a config snippet
- [ ] **`scopes config:disable --name "ignore-tests"`** — disable a config snippet

### 5.4 Workspace Management

Save/restore working context for complex multi-session work.

- [ ] Define workspace format (JSON in `.scopes/workspaces/`):
  ```json
  {
    "name": "refactor-auth",
    "scopes": ["Auth/Login", "Auth/Registration"],
    "session": "Scopes/Work/Notes/session-2026-02-25-auth.md",
    "tasks": ["task-rate-limit", "task-mfa"],
    "created": "2026-02-25"
  }
  ```
- [ ] **`scopes workspaces`** — list saved workspaces
- [ ] **`scopes workspace:save --name "refactor-auth"`** — save current context
- [ ] **`scopes workspace:load --name "refactor-auth"`** — restore context
- [ ] **`scopes workspace:delete --name "refactor-auth"`** — remove workspace

## Acceptance Criteria

```bash
scopes profiles
scopes profile
scopes profile:set --name "python-api"
scopes templates
scopes template:read --name "capability"
scopes template:variables --name "capability"
scopes configs
scopes workspaces
```
