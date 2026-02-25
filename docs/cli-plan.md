# Scopes CLI — Master Plan

> **Goal**: Build a single `scopes` CLI (one Python file, zero external dependencies)
> that makes the Scopes layer the **cell brain** of an AI assistant for any project.
>
> Inspired by [Obsidian CLI](https://help.obsidian.md/cli) — but instead of talking to
> a note-taking app, this CLI talks to the evidence/navigation layer over a real codebase.

---

## Table of Contents

1. [Architecture](#1-architecture)
2. [Entry Point & Conventions](#2-entry-point--conventions)
3. [Command Reference (Full)](#3-command-reference-full)
4. [Phase 1 — Wire Existing Scripts](#4-phase-1--wire-existing-scripts)
5. [Phase 2 — Core Brain Commands](#5-phase-2--core-brain-commands)
6. [Phase 3 — Session & Agent Management](#6-phase-3--session--agent-management)
7. [Phase 4 — Sync Engine](#7-phase-4--sync-engine)
8. [Phase 5 — Profiles, Templates & Config](#8-phase-5--profiles-templates--config)
9. [Phase 6 — The `scopes-cli` Skill](#9-phase-6--the-scopes-cli-skill)
10. [Existing Script Integration Map](#10-existing-script-integration-map)
11. [Output Contracts](#11-output-contracts)
12. [Testing Strategy](#12-testing-strategy)
13. [Risks & Mitigations](#13-risks--mitigations)
14. [Missing Commands Audit (Obsidian Parity)](#14-missing-commands-audit-obsidian-parity)
15. [Refactoring Plan — Perfect Integration](#15-refactoring-plan--perfect-integration)
16. [`.scopes/` State Directory](#16-scopes-state-directory)
17. [`scopes/SKILL.md` Router Update](#17-scopesskillmd-router-update)
18. [Makefile Update](#18-makefile-update)
19. [`.claude-plugin/plugin.json` Update](#19-claude-pluginpluginjson-update)
20. [CHANGELOG Entry](#20-changelog-entry)

---

## 1. Architecture

### Single file: `scopes/cli.py`

One Python file, no external dependencies. Uses only the standard library:
`argparse`, `json`, `pathlib`, `subprocess`, `re`, `os`, `sys`, `datetime`,
`dataclasses`, `textwrap`, `glob`, `hashlib`.

```text
scopes/cli.py          ← THE file (~2000-3000 lines when complete)
├── main()             ← entry point, argparse root + subparsers
├── Commands           ← one function per command (cmd_read, cmd_search, etc.)
├── Core helpers       ← shared logic (scope resolution, evidence parsing, output)
└── Script bridges     ← thin wrappers that import/invoke existing scripts
```

### Why a single file

- **Zero install friction**: copy one file, done.
- **No import path headaches**: agents don't need to resolve SKILLS_ROOT.
- **Grep-friendly**: one file to search, one file to understand.
- **Matches the project philosophy**: pure Python, no external deps, minimal footprint.

### How it wraps existing scripts

The CLI does NOT rewrite existing scripts. It imports their `main()` or key
functions and wraps them with a unified interface. The existing scripts stay
where they are and continue to work standalone.

```python
# Example: scopes map → calls scope_map.py
def cmd_map(args):
    sys.path.insert(0, str(_scripts_dir() / "syncing-scopes" / "scripts"))
    from scope_map import main as scope_map_main
    return scope_map_main(...)  # pass translated args
```

For new commands (Phase 2+), logic lives directly in `cli.py`.

---

## 2. Entry Point & Conventions

### Invocation

```bash
# From any directory inside a project with Scopes/
scopes <command> [subcommand] [args...]

# Or explicitly target a project
scopes --project /path/to/repo <command> [args...]
```

### Project resolution (auto-detect)

Walk up from `cwd` looking for a `Scopes/` directory or `Scopes/INDEX.md`.
Fail with a clear error if not found (unless `--project` is set).

### Output modes

Every command supports `--format`:

| Flag | Output | When to use |
|---|---|---|
| `--format json` | Machine-readable JSON (default) | Agent consumption |
| `--format compact` | Human-readable compact text | Terminal / human use |
| `-H` | Alias for `--format compact` | Quick human mode |

Default is `json` because the primary consumer is an AI agent.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Error (with JSON error on stderr) |
| `2` | Partial result (e.g., drift found but non-blocking) |

### Error output

Errors always go to stderr as JSON:
```json
{"error": "Scope not found", "scope": "Auth/Nonexistent", "hint": "Run: scopes scopes"}
```

### Scope resolution (wikilink-style)

Like Obsidian's `file=` parameter, `scope=` resolves by name, not path:

```bash
scopes read scope="Login"          # resolves to Scopes/Product/Auth/Login_Flow.md
scopes read scope="Auth/Login"     # resolves to Scopes/Product/Auth/Login_Flow.md
scopes read path="Scopes/Product/Auth/Login_Flow.md"  # exact path
```

Resolution order:
1. Exact match in `Scopes/Product/**/`
2. Slug match (case-insensitive, underscores/hyphens normalized)
3. Substring match (unique prefix)
4. Ambiguous → error with candidates list

---

## 3. Command Reference (Full)

### 3.1 General

| Command | Description | Phase |
|---|---|---|
| `scopes help` | List all commands grouped by category | 1 |
| `scopes help <command>` | Detailed help for a specific command | 1 |
| `scopes version` | Version + last sync timestamp + scope count | 1 |
| `scopes status` | Dashboard: scope count, stale %, recent sessions, pending tasks | 2 |
| `scopes init` | Initialize Scopes/ for a new project (create INDEX, GRAPH, Product/) | 3 |

### 3.2 Scope Operations (Files & Folders equivalent)

| Command | Description | Phase |
|---|---|---|
| `scopes read scope="X"` | Read a scope doc | 2 |
| `scopes read scope="X" --section "Entry Points"` | Read one section only | 2 |
| `scopes read:evidence scope="X"` | Extract just evidence links | 2 |
| `scopes read:code scope="X"` | Follow evidence links → return actual code snippets | 2 |
| `scopes read:code scope="X" --section "Entry Points"` | Code from one section's evidence | 2 |
| `scopes scope name="X"` | Info about a scope: path, status, evidence count, staleness | 2 |
| `scopes scopes` | List all scopes | 1 |
| `scopes scopes --status stale` | Filter by status | 2 |
| `scopes scopes --area "Auth"` | Filter by area | 1 |
| `scopes area name="Auth"` | Info about a scope area | 2 |
| `scopes areas` | List all scope areas | 2 |
| `scopes create scope="Auth/MFA"` | Create scope skeleton | 1 |
| `scopes create scope="Auth/MFA" --template capability` | With specific template | 1 |
| `scopes create scope="Auth/MFA" --micro` | Create overview + micro-scopes | 1 |
| `scopes create:note name="summary-auth" --type summary` | Create a work note | 3 |
| `scopes create:task scope="Auth/Login" --title "Add rate limiting"` | Create a task file | 3 |
| `scopes create:adr --title "Session storage choice"` | Create an ADR skeleton | 3 |
| `scopes append scope="X" --section "Evidence" --content "..."` | Append to section | 2 |
| `scopes prepend scope="X" --section "Constraints" --content "..."` | Prepend to section | 2 |
| `scopes move scope="Auth/Login" --to "Authentication/Login"` | Move with link rewriting | 1 |
| `scopes rename scope="Auth/Login" --to "Auth/SignIn"` | Rename with link rewriting | 1 |
| `scopes delete scope="Auth/OldFlow"` | Delete (with orphan warning) | 2 |
| `scopes fill scope="Auth/Login"` | Populate skeleton with evidence guidance | 2 |
| `scopes open scope="Auth/Login"` | Print path (for editor integration) | 2 |

### 3.3 Search & Query

| Command | Description | Phase |
|---|---|---|
| `scopes search --query "auth" --limit 10` | Full-text search across scope docs | 2 |
| `scopes search:context --query "JWT" --lines 3` | Search with surrounding context | 2 |
| `scopes search:code --query "validateToken"` | Search evidence-linked code only | 2 |
| `scopes search:evidence --pattern "*.test.ts"` | Find evidence links by file pattern | 2 |
| `scopes locate --intent "add caching to API"` | Intent → scope routing | 2 |
| `scopes map --query "auth" --limit 3` | Scope matrix view | 1 |
| `scopes map --from-artifact "Scopes/Work/Tasks/x.md"` | Route from artifact | 1 |
| `scopes map --depth 3 --area "Auth"` | Deep area view | 1 |
| `scopes query "What depends on Auth?"` | Structured query against INDEX+GRAPH | 2 |

### 3.4 Links & Evidence

| Command | Description | Phase |
|---|---|---|
| `scopes backlinks scope="Auth/Login"` | Scopes referencing this one | 2 |
| `scopes links scope="Auth/Login"` | All outgoing references | 2 |
| `scopes links:scopes scope="Auth/Login"` | Only scope-to-scope refs | 2 |
| `scopes links:evidence scope="Auth/Login"` | Only evidence links (to code) | 2 |
| `scopes evidence scope="Auth/Login"` | Full evidence report with staleness | 2 |
| `scopes evidence:verify scope="Auth/Login"` | Actively verify links resolve | 2 |
| `scopes evidence:add scope="X" --section "Entry Points" --link "src/a.ts:L15-L30"` | Add evidence | 2 |
| `scopes evidence:remove scope="X" --link "src/old.ts:L5-L10"` | Remove evidence | 2 |
| `scopes graph scope="Auth/Login"` | Dependency neighbors from GRAPH.md | 2 |
| `scopes graph:path --from "Auth/Login" --to "DB/Users"` | Dependency chain | 2 |
| `scopes graph:impact scope="DB/Users"` | "What's affected if I change this?" | 2 |
| `scopes orphans` | Scopes with no incoming references | 2 |
| `scopes deadends` | Scopes with no outgoing evidence | 2 |
| `scopes unresolved` | Broken evidence links | 2 |
| `scopes drift --stale-only --limit 10` | Stale evidence detection | 1 |
| `scopes drift --scope "Auth/Login"` | Per-scope drift | 1 |
| `scopes drift --area "Auth"` | Per-area drift | 1 |

### 3.5 Properties & Metadata

| Command | Description | Phase |
|---|---|---|
| `scopes properties` | List all properties used across scopes | 2 |
| `scopes property:read scope="X" --name "status"` | Read a property | 2 |
| `scopes property:set scope="X" --name "status" --value "active"` | Set a property | 2 |
| `scopes property:remove scope="X" --name "deprecated"` | Remove a property | 2 |
| `scopes property:list scope="X"` | All properties for a scope | 2 |
| `scopes aliases scope="X"` | List aliases for a scope | 3 |

### 3.6 Tasks & Contracts

| Command | Description | Phase |
|---|---|---|
| `scopes tasks` | List all task files | 3 |
| `scopes tasks --scope "Auth/Login"` | Tasks for a specific scope | 3 |
| `scopes tasks --status pending` | Filter by status | 3 |
| `scopes task --id "task-rate-limit"` | Get a specific task | 3 |
| `scopes task:create --scope "Auth/Login" --title "Add rate limiting"` | Create task | 3 |
| `scopes task:status --id "task-rate-limit" --value "in-progress"` | Update status | 3 |
| `scopes task:close --id "task-rate-limit"` | Mark complete | 3 |
| `scopes contract --scope "Auth/Login" --target "Add rate limiting"` | Build Slice Contract | 1 |
| `scopes contract --from-drift "drift.json"` | Contract from drift output | 1 |
| `scopes contract --infer` | Infer contracts from repo | 1 |
| `scopes contract:validate --path "task-rate-limit.md"` | Validate contract fields | 3 |
| `scopes receipt --path "receipt.json"` | Parse/validate a JSON receipt | 3 |
| `scopes receipt:list --scope "Auth/Login"` | Recent receipts for a scope | 3 |

### 3.7 Session Log (Daily Notes equivalent)

| Command | Description | Phase |
|---|---|---|
| `scopes session` | Show current session log info | 3 |
| `scopes session:path` | Return path to current session log | 3 |
| `scopes session:read` | Read current session log | 3 |
| `scopes session:read --date "2026-02-24"` | Read specific session log | 3 |
| `scopes session:start --scope "Auth/Login" --goal "Fix token refresh"` | Start new session | 3 |
| `scopes session:append --content "- Found: auth uses JWT"` | Append to session | 3 |
| `scopes session:prepend --content "## Priority Change"` | Prepend to session | 3 |
| `scopes session:list --limit 5` | List recent sessions | 3 |
| `scopes session:summarize` | Trigger context-summarizer on session | 3 |

### 3.8 History (git-powered)

| Command | Description | Phase |
|---|---|---|
| `scopes diff scope="Auth/Login"` | Changes since last commit | 3 |
| `scopes diff scope="Auth/Login" --since "7d"` | Changes in time window | 3 |
| `scopes history scope="Auth/Login"` | Git history for a scope doc | 3 |
| `scopes history:list scope="Auth/Login" --limit 10` | List commits touching scope | 3 |
| `scopes history:read scope="Auth/Login" --commit "abc123"` | Read scope at point in time | 3 |
| `scopes history:restore scope="Auth/Login" --commit "abc123"` | Restore scope version | 3 |
| `scopes history:evidence scope="Auth/Login"` | How evidence evolved over time | 4 |
| `scopes history:blame scope="Auth/Login" --line 15` | Who last changed a scope line | 3 |

### 3.9 Sync (Truth Engine)

| Command | Description | Phase |
|---|---|---|
| `scopes sync` | Full Scopes sync (placeholder: prints guidance) | 4 |
| `scopes sync:dry` | Preview what sync would change | 4 |
| `scopes sync:scope scope="Auth/Login"` | Sync just one scope | 4 |
| `scopes sync:status` | Last sync time, stale %, drift summary | 4 |
| `scopes sync:history --limit 10` | Recent sync runs | 4 |
| `scopes sync:diff scope="Auth/Login"` | What changed since last sync | 4 |
| `scopes sync:restore scope="Auth/Login" --version "2026-02-24"` | Restore synced version | 4 |
| `scopes sync:removed` | Scopes/evidence removed in last sync | 4 |

### 3.10 Agents & Skills (Plugin Development equivalent)

| Command | Description | Phase |
|---|---|---|
| `scopes agents` | List all available agents with descriptions | 3 |
| `scopes agent --id "slice-developer"` | Get agent details (tools, model, constraints) | 3 |
| `scopes agent:describe --id "bug-scanner"` | Full agent capability description | 3 |
| `scopes agent:history --id "slice-developer" --limit 5` | Recent invocations | 4 |
| `scopes skills` | List all available skills | 3 |
| `scopes skill --id "syncing-scopes"` | Get skill details | 3 |
| `scopes skill:describe --id "syncing-scopes"` | Full skill description | 3 |
| `scopes validate` | Validate Scopes/ structure | 1 |
| `scopes validate --scope "Auth/Login"` | Validate one scope | 1 |
| `scopes validate --area "Auth"` | Validate an area | 1 |
| `scopes validate:contracts` | Validate all Slice Contracts | 3 |
| `scopes log --level error` | Recent agent logs/receipts | 4 |
| `scopes eval --code "..."` | Run Python in Scopes context | 4 |

### 3.11 Profiles & Config (Themes equivalent)

| Command | Description | Phase |
|---|---|---|
| `scopes profiles` | List available project profiles | 5 |
| `scopes profile` | Show current profile | 5 |
| `scopes profile:set --name "python-api"` | Switch profile | 5 |
| `scopes profile:install --repo "scopes-community/python-api-profile"` | Install profile | 5 |
| `scopes profile:uninstall --name "python-api"` | Remove profile | 5 |
| `scopes configs` | List config overrides | 5 |
| `scopes configs:enabled` | Active config overrides | 5 |
| `scopes config:enable --name "ignore-tests"` | Enable a config | 5 |
| `scopes config:disable --name "ignore-tests"` | Disable a config | 5 |

### 3.12 Templates

| Command | Description | Phase |
|---|---|---|
| `scopes templates` | List all templates | 5 |
| `scopes templates --type scope` | Filter by type | 5 |
| `scopes template:read --name "capability"` | Read a template | 5 |
| `scopes template:insert --name "capability" --target "Scopes/Product/Auth/MFA.md"` | Apply template | 5 |
| `scopes template:create --name "my-scope" --base "capability"` | Create custom template | 5 |
| `scopes template:variables --name "capability"` | List template placeholders | 5 |

### 3.13 Index & Graph (direct access)

| Command | Description | Phase |
|---|---|---|
| `scopes index` | Dump INDEX.md as structured JSON | 2 |
| `scopes index:update` | Regenerate INDEX.md from Product/ | 4 |
| `scopes graph` | Dump GRAPH.md as structured JSON | 2 |
| `scopes graph:update` | Regenerate GRAPH.md from evidence | 4 |

### 3.14 Hotspot Analysis

| Command | Description | Phase |
|---|---|---|
| `scopes hotspot` | Refactor hotspot matrix | 1 |
| `scopes hotspot --top 20 --since-days 90` | Custom window | 1 |
| `scopes hotspot --ext .py .ts` | Filter by extension | 1 |

### 3.15 Trace Stubs

| Command | Description | Phase |
|---|---|---|
| `scopes trace scope="Auth/Login"` | Generate trace table stub | 1 |
| `scopes trace scope="Auth/Login" --apply` | Apply trace table to scope file | 1 |

**Total: ~104 commands across 15 categories**

---

## 4. Phase 1 — Wire Existing Scripts

> **Effort**: ~400-500 lines of new code in `cli.py`
> **Value**: Immediate — replaces SCRIPT_DISCOVERY.md, unifies 9 scripts

### What gets built

The `cli.py` file with:
- `main()` with argparse root parser + subparsers
- `help` command (auto-generated from subparser descriptions)
- `version` command
- Bridges to all 9 existing scripts:

| CLI Command | Wraps Script | Script Lines |
|---|---|---|
| `scopes map` | `scope_map.py` | 399 |
| `scopes drift` | `drift_detector.py` | 193 |
| `scopes validate` | `validate_scopes.py` | 306 |
| `scopes create` | `scope_skeleton_generator.py` | 971 |
| `scopes contract` | `slice_contract_builder.py` | 435 |
| `scopes trace` | `scope_trace_stub_from_entrypoints.py` | 267 |
| `scopes rename` | `scope_rename_guard.py` | 297 |
| `scopes hotspot` | `hotspot_matrix.py` | 244 |
| `scopes scopes` | `scope_map.py` (--only tree) | (reuse) |

### Implementation pattern for each bridge

```python
def cmd_map(args):
    """Compact scope matrix view."""
    script = _resolve_script("syncing-scopes", "scope_map.py")
    cmd = [sys.executable, str(script), "--repo-root", str(args.project)]
    if args.query:
        cmd += ["--query", args.query]
    if args.limit:
        cmd += ["--limit", str(args.limit)]
    if args.area:
        for a in args.area:
            cmd += ["--area", a]
    if args.depth:
        cmd += ["--depth", str(args.depth)]
    if args.from_artifact:
        cmd += ["--from-artifact", args.from_artifact]
    cmd += ["--format", args.format]
    return _run(cmd)
```

### Scaffolding built in Phase 1

```python
# --- Project resolution ---
def _find_project_root(start: Path) -> Path:
    """Walk up from cwd looking for Scopes/INDEX.md."""

# --- Script resolution ---
def _resolve_script(skill: str, script: str) -> Path:
    """Find a helper script. Checks multiple locations."""

# --- Output helpers ---
def _run(cmd: list) -> int:
    """Run subprocess, forward stdout/stderr, return exit code."""

def _json_out(data: dict | list) -> None:
    """Print JSON to stdout."""

def _error(msg: str, **ctx) -> None:
    """Print JSON error to stderr, exit 1."""

# --- Scope resolution ---
def _resolve_scope(name: str, project_root: Path) -> Path:
    """Wikilink-style scope name → file path resolution."""

def _all_scope_files(project_root: Path) -> list[Path]:
    """Glob all .md files under Scopes/Product/."""
```

### Phase 1 deliverables

- [ ] `scopes/cli.py` — single file with argparse + 9 command bridges
- [ ] `scopes help` works — lists all commands with descriptions
- [ ] `scopes version` works — prints version + project info
- [ ] All 9 existing scripts callable via `scopes <command>`
- [ ] `--project` flag and auto-detection working
- [ ] `--format json|compact` respected (passed through to scripts)
- [ ] Exit codes: 0/1/2
- [ ] Entry point: `python3 scopes/cli.py <command>` (or symlinked to `scopes`)

---

## 5. Phase 2 — Core Brain Commands

> **Effort**: ~800-1000 lines of new code
> **Value**: This is what makes Scopes a "brain" — reading, searching, evidence, graph

### 5.1 Scope reading (`read`, `read:evidence`, `read:code`)

```python
def cmd_read(args):
    """Read a scope doc, optionally a specific section."""
    scope_path = _resolve_scope(args.scope, args.project)
    content = scope_path.read_text()
    if args.section:
        content = _extract_section(content, args.section)
    # json mode: {"scope": "Auth/Login", "path": "...", "content": "..."}
    # compact mode: just print content
```

```python
def cmd_read_evidence(args):
    """Extract only evidence links from a scope."""
    content = _read_scope(args)
    links = _parse_evidence_links(content, section=args.section)
    # Returns: [{"target": "src/auth.ts", "lines": "L15-L30", "section": "Entry Points"}]
```

```python
def cmd_read_code(args):
    """Follow evidence links and return actual code snippets."""
    links = _parse_evidence_links(...)
    snippets = []
    for link in links:
        code = _read_lines(project / link.target, link.start, link.end)
        snippets.append({"file": link.target, "lines": f"L{link.start}-L{link.end}", "code": code})
    # Returns the actual code the scope talks about
```

### 5.2 Evidence link parsing (core helper)

```python
@dataclass
class EvidenceLink:
    target: str       # "src/auth/login.ts"
    start_line: int   # 15
    end_line: int      # 30
    section: str       # "Entry Points"
    display: str       # "[src/auth/login.ts:L15-L30](...)"

def _parse_evidence_links(content: str, section: str | None = None) -> list[EvidenceLink]:
    """Parse [path:Lx-Ly](path#Lx-Ly) links from scope content."""
    # Uses regex: r'\[([^\]]+):L(\d+)-L(\d+)\]\(([^)]+)\)'
    # Also handles: [path](path#Lx-Ly) format
```

### 5.3 Search commands

```python
def cmd_search(args):
    """Full-text search across scope docs."""
    results = []
    for scope_path in _all_scope_files(args.project):
        content = scope_path.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if args.query.lower() in line.lower():
                results.append({
                    "scope": _scope_name(scope_path),
                    "line": i,
                    "text": line.strip()
                })
    # Sort by relevance, apply limit

def cmd_search_code(args):
    """Search within evidence-linked code files only."""
    # 1. Collect all evidence links across all scopes
    # 2. rg (or python grep) only within those files
    # Much more targeted than a full codebase search

def cmd_locate(args):
    """Intent → scope routing. The killer brain command."""
    # 1. Tokenize the intent
    # 2. Score each scope against the intent (reuse scope_map.py scoring)
    # 3. Return top matches with evidence links
    # This replaces the need for SCRIPT_DISCOVERY + manual navigation
```

### 5.4 Links & evidence commands

```python
def cmd_backlinks(args):
    """Find all scopes that reference the given scope."""
    target = _resolve_scope(args.scope, args.project)
    target_name = _scope_name(target)
    results = []
    for scope_path in _all_scope_files(args.project):
        if scope_path == target:
            continue
        content = scope_path.read_text()
        if target_name in content or str(target.relative_to(args.project)) in content:
            results.append({"scope": _scope_name(scope_path), "path": str(scope_path)})

def cmd_evidence(args):
    """Full evidence report: links + staleness per link."""
    links = _parse_evidence_links(_read_scope(args))
    for link in links:
        link_path = args.project / link.target
        link.exists = link_path.exists()
        link.stale = _is_stale(link_path, scope_path)  # reuse drift logic

def cmd_graph(args):
    """Parse GRAPH.md and return neighbors."""
    graph_path = args.project / "Scopes" / "GRAPH.md"
    edges = _parse_graph(graph_path)
    # Filter to neighbors of args.scope

def cmd_graph_path(args):
    """BFS/DFS to find dependency path between two scopes."""
    edges = _parse_graph(...)
    path = _bfs(edges, args.from_scope, args.to_scope)
```

### 5.5 Scope info & listing

```python
def cmd_scope_info(args):
    """Composite info about a scope."""
    scope_path = _resolve_scope(args.scope, args.project)
    content = scope_path.read_text()
    frontmatter = _parse_frontmatter(content)
    evidence_links = _parse_evidence_links(content)
    stale_count = sum(1 for l in evidence_links if _is_stale(l, scope_path))
    return {
        "name": _scope_name(scope_path),
        "path": str(scope_path),
        "properties": frontmatter,
        "evidence_count": len(evidence_links),
        "stale_count": stale_count,
        "sections": _list_h2_sections(content),
        "last_modified": _git_date(scope_path),
    }

def cmd_status(args):
    """Project dashboard."""
    scopes = _all_scope_files(args.project)
    total = len(scopes)
    stale = sum(1 for s in scopes if _has_stale_evidence(s))
    return {
        "project": str(args.project),
        "scope_count": total,
        "stale_count": stale,
        "stale_pct": round(stale / total * 100, 1) if total else 0,
        "areas": _list_areas(args.project),
        "last_sync": _last_sync_time(args.project),
    }
```

### 5.6 Index & Graph direct access

```python
def cmd_index(args):
    """Parse INDEX.md into structured JSON."""
    index_path = args.project / "Scopes" / "INDEX.md"
    content = index_path.read_text()
    # Parse the markdown structure into:
    # {"areas": [{"name": "Auth", "scopes": ["Login", "Registration", ...]}]}

def cmd_graph_dump(args):
    """Parse GRAPH.md into structured JSON."""
    # {"edges": [{"from": "Auth/Login", "to": "DB/Users", "type": "depends_on"}]}
```

### Phase 2 deliverables

- [ ] `scopes read` / `read:evidence` / `read:code` — scope reading with evidence follow
- [ ] `scopes search` / `search:code` / `search:evidence` — multi-layer search
- [ ] `scopes locate` — intent-to-scope routing (brain command)
- [ ] `scopes backlinks` / `links` / `links:scopes` / `links:evidence` — link traversal
- [ ] `scopes evidence` / `evidence:verify` / `evidence:add` / `evidence:remove`
- [ ] `scopes graph` / `graph:path` / `graph:impact` — dependency reasoning
- [ ] `scopes orphans` / `deadends` / `unresolved` — health checks
- [ ] `scopes scope` / `scopes areas` — scope metadata
- [ ] `scopes status` — project dashboard
- [ ] `scopes index` / `scopes graph` (dump) — structured JSON access
- [ ] `scopes properties` / `property:read` / `property:set` / `property:remove`
- [ ] `scopes append` / `prepend` — section-aware editing
- [ ] `scopes delete` / `scopes open` / `scopes fill`
- [ ] Evidence link parser as shared helper
- [ ] Scope resolution (wikilink-style) as shared helper

---

## 6. Phase 3 — Session & Agent Management

> **Effort**: ~500-700 lines
> **Value**: Cross-session continuity, agent discoverability, task management

### 6.1 Session log commands

Session logs live in `Scopes/Work/Notes/session-<YYYY-MM-DD>-<topic>.md`.

```python
def cmd_session_start(args):
    """Create a new session log."""
    date = datetime.date.today().isoformat()
    slug = _slugify(args.goal or "session")
    path = args.project / "Scopes" / "Work" / "Notes" / f"session-{date}-{slug}.md"
    content = SESSION_TEMPLATE.format(
        date=date, goal=args.goal, scope=args.scope
    )
    path.write_text(content)
    _set_current_session(args.project, path)  # track in .scopes/current_session

def cmd_session_append(args):
    """Append to the current session log."""
    path = _current_session(args.project)
    with open(path, "a") as f:
        f.write(f"\n{args.content}\n")
```

### 6.2 Agent & skill commands

Agents live in `agents/*.md`. Skills live in `scopes/skills/*/SKILL.md`.

```python
def cmd_agents(args):
    """List all agents with name, description, tools, readonly."""
    agents_dir = _find_agents_dir(args.project)
    results = []
    for agent_file in sorted(agents_dir.glob("*.md")):
        if agent_file.name == "WORKFLOW.md":
            continue
        fm = _parse_frontmatter(agent_file.read_text())
        results.append({
            "id": fm.get("name", agent_file.stem),
            "description": fm.get("description", ""),
            "tools": fm.get("tools", ""),
            "model": fm.get("model", "inherit"),
            "readonly": fm.get("readonly", False),
        })

def cmd_agent_describe(args):
    """Full agent description — everything the agent can do."""
    # Parse the full .md, extract sections, return structured
```

### 6.3 Task management

Tasks live in `Scopes/Work/Tasks/**`.

```python
def cmd_tasks(args):
    """List task files."""
    tasks_dir = args.project / "Scopes" / "Work" / "Tasks"
    results = []
    for task_file in tasks_dir.rglob("*.md"):
        fm = _parse_frontmatter(task_file.read_text())
        results.append({
            "id": task_file.stem,
            "title": fm.get("title", task_file.stem),
            "scope": fm.get("scope", ""),
            "status": fm.get("status", "pending"),
            "path": str(task_file),
        })
    # Filter by --scope, --status if provided
```

### 6.4 Init command

```python
def cmd_init(args):
    """Initialize Scopes/ structure for a new project."""
    scopes_dir = args.project / "Scopes"
    (scopes_dir / "Product").mkdir(parents=True, exist_ok=True)
    (scopes_dir / "Work" / "Tasks").mkdir(parents=True, exist_ok=True)
    (scopes_dir / "Work" / "Notes").mkdir(parents=True, exist_ok=True)
    (scopes_dir / "Work" / "Bugs").mkdir(parents=True, exist_ok=True)
    (scopes_dir / "Work" / "Planning").mkdir(parents=True, exist_ok=True)
    (scopes_dir / "Onboarding").mkdir(parents=True, exist_ok=True)
    # Write starter INDEX.md, GRAPH.md, DEVELOPER_INFO.md
```

### Phase 3 deliverables

- [ ] `scopes session:*` commands — start, read, append, prepend, list, summarize
- [ ] `scopes agents` / `agent` / `agent:describe` — agent discovery
- [ ] `scopes skills` / `skill` / `skill:describe` — skill discovery
- [ ] `scopes tasks` / `task` / `task:create` / `task:status` / `task:close`
- [ ] `scopes contract:validate` / `receipt` / `receipt:list`
- [ ] `scopes create:note` / `create:task` / `create:adr`
- [ ] `scopes init`
- [ ] `scopes aliases`
- [ ] Current session tracking (`.scopes/` state directory)

---

## 7. Phase 4 — Sync Engine

> **Effort**: ~300-500 lines
> **Value**: The CLI becomes the interface for keeping the brain truthful

### 7.1 Sync commands

Most sync logic is orchestrated by the `syncing-scopes` skill (which uses agents).
The CLI provides the entry points and status tracking.

```python
def cmd_sync(args):
    """Full Scopes sync — prints instructions for the skill or runs drift+validate."""
    # Option A: If syncing-scopes skill is accessible, invoke it
    # Option B: Run drift_detector + validate_scopes as a lightweight sync check
    # Option C: Print guidance for how to trigger a full sync via the skill

def cmd_sync_status(args):
    """Sync dashboard: when was last sync, what's stale, overall health."""
    drift_output = _run_drift_all(args.project)
    validate_output = _run_validate_all(args.project)
    return {
        "last_sync": _last_sync_time(args.project),
        "total_scopes": total,
        "stale_scopes": len(stale),
        "validation_errors": len(errors),
        "health": "healthy" if not stale and not errors else "needs_sync",
    }

def cmd_sync_removed(args):
    """Show evidence pointing to files that no longer exist."""
    # Walk all evidence links, check file existence
```

### 7.2 History commands (git-powered)

```python
def cmd_diff(args):
    """Git diff for a scope file."""
    scope_path = _resolve_scope(args.scope, args.project)
    rel = scope_path.relative_to(args.project)
    since = args.since or "HEAD"
    result = subprocess.run(
        ["git", "diff", since, "--", str(rel)],
        capture_output=True, text=True, cwd=args.project
    )

def cmd_history(args):
    """Git log for a scope file."""
    result = subprocess.run(
        ["git", "log", "--oneline", f"-{args.limit}", "--", str(rel)],
        ...
    )

def cmd_history_read(args):
    """Read a scope at a specific commit."""
    result = subprocess.run(
        ["git", "show", f"{args.commit}:{rel}"],
        ...
    )
```

### Phase 4 deliverables

- [ ] `scopes sync` / `sync:dry` / `sync:scope` — sync triggers
- [ ] `scopes sync:status` / `sync:history` / `sync:diff` — sync monitoring
- [ ] `scopes sync:restore` / `sync:removed` — sync recovery
- [ ] `scopes diff` / `history` / `history:list` / `history:read` / `history:restore`
- [ ] `scopes history:blame` / `history:evidence`
- [ ] `scopes index:update` / `graph:update`
- [ ] `scopes eval` / `scopes log`
- [ ] `scopes agent:history`
- [ ] Sync timestamp tracking (`.scopes/last_sync`)

---

## 8. Phase 5 — Profiles, Templates & Config

> **Effort**: ~300-400 lines
> **Value**: Customization layer — different project types get different defaults

### 8.1 Profiles

A profile is a JSON file that defines default scope sections, templates,
evidence patterns, and ignore rules for a project type.

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

Profiles stored in `scopes/profiles/` or `~/.scopes/profiles/`.

### 8.2 Templates

Templates stored in `scopes/templates/` with variables:

```markdown
---
name: {{scope_name}}
area: {{area_name}}
status: new
---
# {{scope_name}}

## Where to Start in Code
<!-- Evidence links go here -->

## Usage & Flow Traces
<!-- Generated by scopes trace -->

## Tests
<!-- Test evidence -->

## Constraints
<!-- Discovered constraints -->
```

### Phase 5 deliverables

- [ ] `scopes profiles` / `profile` / `profile:set` / `profile:install` / `profile:uninstall`
- [ ] `scopes configs` / `configs:enabled` / `config:enable` / `config:disable`
- [ ] `scopes templates` / `template:read` / `template:insert` / `template:create` / `template:variables`
- [ ] Profile JSON format and storage
- [ ] Template variable substitution engine

---

## 9. Phase 6 — The `scopes-cli` Skill

> The final piece: teach agents how to use the CLI they've been given.

Create `scopes/skills/scopes-cli/SKILL.md` following the same pattern as
Obsidian's `obsidian-cli` skill:

```markdown
---
name: scopes-cli
description: >
  Interact with the Scopes evidence layer via the CLI. Use when the agent
  needs to navigate scopes, read evidence, search code, check drift,
  manage tasks, or understand project structure without reading raw files.
---

# Scopes CLI

Use the `scopes` CLI to interact with a project's Scopes layer.

## Command reference

Run `scopes help` to see all available commands.

## Syntax

Parameters use `--name value`. Scope names resolve like wikilinks:

    scopes read scope="Auth/Login"
    scopes search --query "authentication" --limit 5

## Common patterns

    scopes read scope="Login"
    scopes read:code scope="Login" --section "Entry Points"
    scopes locate --intent "add caching to API responses"
    scopes drift --stale-only --limit 10
    scopes evidence:verify scope="Login"
    scopes graph:impact scope="DB/Users"
    scopes tasks --status pending
    scopes session:append --content "- Found: uses JWT tokens"

Use `--format json` (default) for machine-readable output.
Use `-H` for human-readable compact output.
```

### Phase 6 deliverables

- [ ] `scopes/skills/scopes-cli/SKILL.md` — the agent-teaching skill
- [ ] Update `scopes/SKILL.md` router to include `scopes-cli` as a sub-skill
- [ ] Update `README.md` to document the CLI
- [ ] Update `docs/automations.md` to reference CLI commands instead of raw scripts

---

## 10. Existing Script Integration Map

How each existing script maps to CLI commands:

| Script (lines) | CLI Command(s) | Integration | Notes |
|---|---|---|---|
| `scope_map.py` (399) | `map`, `scopes`, `locate` | subprocess | Core navigation, reused heavily |
| `drift_detector.py` (193) | `drift`, `sync:status` | subprocess | Staleness detection |
| `validate_scopes.py` (306) | `validate` | subprocess | Structure validation |
| `scope_skeleton_generator.py` (971) | `create` | subprocess | Scope creation |
| `slice_contract_builder.py` (435) | `contract` | subprocess | Contract building |
| `scope_trace_stub_from_entrypoints.py` (267) | `trace` | subprocess | Trace table generation |
| `scope_rename_guard.py` (297) | `rename`, `move` | subprocess | Safe renames |
| `hotspot_matrix.py` (244) | `hotspot` | subprocess | Refactor scanning |
| `_md_links.py` (62) | (internal) | import | Link parsing reused by read/evidence commands |

Scripts stay standalone. The CLI calls them via subprocess (Phase 1) or imports
key functions directly (Phase 2+ for performance-critical paths like evidence parsing).

---

## 11. Output Contracts

### JSON output structure

Every command returns a consistent envelope:

```json
{
  "command": "scopes read",
  "scope": "Auth/Login",
  "project": "/path/to/repo",
  "data": { ... },
  "meta": {
    "duration_ms": 45,
    "timestamp": "2026-02-25T10:30:00Z"
  }
}
```

For list commands, `data` is an array. For info commands, `data` is an object.
For errors, the envelope is on stderr with an `error` field instead of `data`.

### Compact output structure

Human-readable output is free-form but follows patterns:
- Lists: one item per line, `scope: description`
- Info: key-value pairs
- Search results: `scope:line: text`
- Evidence: `[OK|STALE|MISSING] path:Lx-Ly`

---

## 12. Testing Strategy

### Unit tests (per phase)

```bash
# Phase 1: script bridges work
python3 scopes/cli.py help
python3 scopes/cli.py version
python3 scopes/cli.py map --query "test" --format json

# Phase 2: brain commands work
python3 scopes/cli.py read scope="SomeScope"
python3 scopes/cli.py search --query "test"
python3 scopes/cli.py evidence scope="SomeScope"
```

### Integration test: full workflow

```bash
# Init → create → fill → validate → drift → search → session
scopes init --project /tmp/test-repo
scopes create scope="Auth/Login" --template capability
scopes validate --all
scopes drift --all
scopes search --query "Auth"
scopes session:start --goal "Test the CLI"
scopes session:append --content "- CLI works end to end"
scopes status
```

### Self-test command (optional)

```bash
scopes selftest  # runs basic health checks on the Scopes installation
```

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Single file gets too large | Hard to maintain | Clear section headers + foldable structure. Split into sections within the file. Cap at ~3000 lines. |
| Subprocess overhead for script bridges | Slow for batch operations | Phase 2+ imports key functions directly for hot paths |
| Scope resolution ambiguity | Wrong scope targeted | Clear error messages with candidate list. Require disambiguation. |
| Git dependency for history/diff | Fails in non-git repos | Graceful fallback: skip git commands, warn user |
| Profile/template system complexity | Scope creep | Phase 5 is optional/deferred. Core value is in Phases 1-3. |
| Breaking existing script interfaces | Scripts diverge from CLI | Scripts remain standalone, CLI is an additive layer |

---

## Summary: Implementation Order

```
Phase 1 (Wire existing)     ~400-500 lines   → 9 scripts unified under one CLI
Phase 2 (Brain commands)     ~800-1000 lines  → read:code, locate, evidence, graph
Phase 3 (Sessions & agents)  ~500-700 lines   → sessions, tasks, agent/skill discovery
Phase 4 (Sync engine)        ~300-500 lines   → sync, history, git-powered commands
Phase 5 (Profiles/templates) ~300-400 lines   → customization layer
Phase 6 (CLI skill)          ~skill file only  → teach agents to use the CLI
                             ─────────────────
Total                        ~2300-3100 lines   single Python file
```

Each phase is independently valuable. Phase 1 alone eliminates SCRIPT_DISCOVERY.md
and unifies 9 scripts. Phase 2 makes Scopes an active brain. Phase 3+ adds
depth and polish.

---

## 14. Missing Commands Audit (Obsidian Parity)

Commands from Obsidian's full CLI that were NOT mapped in the original plan:

| Obsidian Command | Scopes Equivalent | Description | Phase |
|---|---|---|---|
| `outline` | `scopes outline scope="X"` | Show heading structure of a scope doc (## sections list) | 2 |
| `random` | `scopes random` | Pick a random scope (useful for audit sampling) | 2 |
| `random:read` | `scopes random:read` | Read a random scope's content | 2 |
| `wordcount` | `scopes stats scope="X"` | Word count, evidence count, section count for a scope | 2 |
| `recents` | `scopes recents --limit 10` | Recently modified scopes (by git date) | 2 |
| `bookmarks` | `scopes bookmarks` | List bookmarked/pinned scopes | 3 |
| `bookmark` | `scopes bookmark scope="X"` | Bookmark a scope for quick access | 3 |
| `commands` | `scopes commands` | List all CLI commands (alias for `help`) | 1 |
| `command` | — | Not applicable (CLI commands aren't "runnable" like Obsidian palette) | — |
| `hotkeys` | — | Not applicable | — |
| `workspace:save` | `scopes workspace:save --name "refactor-auth"` | Save current working context (open scopes, session, tasks) | 5 |
| `workspace:load` | `scopes workspace:load --name "refactor-auth"` | Restore working context | 5 |
| `workspaces` | `scopes workspaces` | List saved workspaces | 5 |
| `tabs` | — | Not applicable (no UI) | — |
| `publish:*` | — | Not applicable (Scopes doesn't publish) | — |
| `web` | — | Not applicable | — |
| `unique` | `scopes create:unique --prefix "ZK"` | Create unique-ID note (Zettelkasten) | 3 |
| `devtools` | — | Not applicable (no UI) | — |

**Updated total: ~115 commands across 16 categories**

---

## 15. Refactoring Plan — Perfect Integration

> **This is the critical section.** The CLI is useless if agents/skills still
> call raw `python3 "$SKILLS_ROOT/..."` commands. Every reference to
> `SCRIPT_DISCOVERY.md`, `SKILLS_ROOT`, and direct script invocations must
> be replaced with `scopes <command>` calls.

### 15.1 Files Inventory (25 files to update)

**Agents (7 files):**

| File | Script References | CLI Replacement |
|---|---|---|
| `agents/bug-scanner.md` | `scope_map.py`, `drift_detector.py`, `SCRIPT_DISCOVERY` | `scopes map`, `scopes drift` |
| `agents/code-reviewer.md` | `drift_detector.py`, `SCRIPT_DISCOVERY` | `scopes drift` |
| `agents/code-simplifier.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |
| `agents/context-summarizer.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |
| `agents/evidence-verifier.md` | `drift_detector.py`, `SCRIPT_DISCOVERY` | `scopes drift` |
| `agents/refactor-scanner.md` | `scope_map.py`, `hotspot_matrix.py`, `SCRIPT_DISCOVERY` | `scopes map`, `scopes hotspot` |
| `agents/scope-filler.md` | `scope_trace_stub_from_entrypoints.py`, `scope_map.py`, `validate_scopes.py`, `SCRIPT_DISCOVERY` | `scopes trace`, `scopes map`, `scopes validate` |

**Skills (10 files):**

| File | Script References | CLI Replacement |
|---|---|---|
| `scopes/skills/brainstorming-project/SKILL.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |
| `scopes/skills/developing-tdd/SKILL.md` | `scope_map.py`, `validate_scopes.py`, `SCRIPT_DISCOVERY` | `scopes map`, `scopes validate` |
| `scopes/skills/developing-verified/SKILL.md` | `scope_map.py`, `validate_scopes.py`, `SCRIPT_DISCOVERY` | `scopes map`, `scopes validate` |
| `scopes/skills/planning-idea/SKILL.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |
| `scopes/skills/planning-refactor/SKILL.md` | `scope_rename_guard.py`, `SCRIPT_DISCOVERY` | `scopes rename` |
| `scopes/skills/querying-scopes/SKILL.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |
| `scopes/skills/researching-decisions/SKILL.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |
| `scopes/skills/scanning-refactor/SKILL.md` | `scope_map.py`, `hotspot_matrix.py`, `scope_rename_guard.py`, `SCRIPT_DISCOVERY` | `scopes map`, `scopes hotspot`, `scopes rename` |
| `scopes/skills/syncing-scopes/SKILL.md` | ALL 7 scripts, `SCRIPT_DISCOVERY` | ALL commands |
| `scopes/skills/writing-tasks/SKILL.md` | `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes map` |

**Shared Protocols (3 files):**

| File | Script References | CLI Replacement |
|---|---|---|
| `scopes/skills/_shared/SCOPES_PROTOCOL.md` | `scope_map.py` | `scopes map` |
| `scopes/skills/_shared/DEVELOPING_PROTOCOL.md` | `validate_scopes.py` | `scopes validate` |
| `scopes/skills/_shared/SCRIPT_DISCOVERY.md` | Entire file is the SKILLS_ROOT resolver | **DEPRECATED** — replaced by CLI |

**Docs & Meta (5 files):**

| File | Script References | CLI Replacement |
|---|---|---|
| `docs/automations.md` | `drift_detector.py`, `scope_map.py`, `SCRIPT_DISCOVERY` | `scopes drift`, `scopes map` |
| `docs/context-engineering.md` | `scope_map.py` reference | `scopes map` |
| `docs/settings.md` | `SCRIPT_DISCOVERY` reference | CLI reference |
| `README.md` | Lists all scripts, shows invocations | CLI commands |
| `agents/WORKFLOW.md` | `scope_map.py`, `drift_detector.py`, `slice_contract_builder.py` | CLI commands |

### 15.2 Refactoring Pattern (Before → After)

Every file follows the same transformation pattern:

**BEFORE** (current — 3 steps, fragile):
```markdown
Resolve `SKILLS_ROOT` using the shared snippet:
- `../_shared/SCRIPT_DISCOVERY.md`

\```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<keywords>" --limit 5 --format json
\```
```

**AFTER** (with CLI — 1 step, robust):
```markdown
\```bash
scopes map --query "<keywords>" --limit 5
\```
```

What gets removed:
1. The `SCRIPT_DISCOVERY` resolution step
2. The `SKILLS_ROOT` environment variable
3. The `python3 "$SKILLS_ROOT/..."` invocation pattern
4. Fallback instructions for when scripts are not found

### 15.3 Per-File Refactoring Details

#### 15.3.1 `agents/bug-scanner.md`

**Lines affected**: ~72-131 (Steps 2-3)

Replace SCRIPT_DISCOVERY block + scope_map.py call:
```markdown
# BEFORE (lines 72-112)
Resolve `SKILLS_ROOT` using:
- `scopes/skills/_shared/SCRIPT_DISCOVERY.md`
...
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --depth 2
If `scope_map.py` is not available, fall back to:
find Scopes/Product -name "*.md" -maxdepth 3 | head -15

# AFTER
scopes map --depth 2
```

Replace drift_detector.py call:
```markdown
# BEFORE (lines 118-125)
python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
  --area <area> --stale-only
If `drift_detector.py` is not available, compare file timestamps:
git log -1 --format="%ai" -- <scope-file>

# AFTER
scopes drift --area "<area>" --stale-only
```

Replace GRAPH.md grep with CLI:
```markdown
# BEFORE (line 130)
grep -A5 "<component>" Scopes/GRAPH.md

# AFTER
scopes graph scope="<component>"
```

**Bonus**: Remove all "If `X` is not available" fallback blocks — CLI is always available.

#### 15.3.2 `agents/code-reviewer.md`

**Lines affected**: ~37-41

```markdown
# BEFORE
python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
  --scope <anchor_scope> --stale-only --format json 2>/dev/null || true
Resolve `SKILLS_ROOT` using `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.

# AFTER
scopes drift --scope "<anchor_scope>" --stale-only
```

#### 15.3.3 `agents/code-simplifier.md`

**Lines affected**: ~66-79

```markdown
# BEFORE
Resolve `SKILLS_ROOT` (see `scopes/skills/_shared/SCRIPT_DISCOVERY.md`), then:
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --depth 2 2>/dev/null || true
cat Scopes/INDEX.md 2>/dev/null || true
cat Scopes/GRAPH.md 2>/dev/null || true
cat CLAUDE.md 2>/dev/null || true
rg -n "<changed-file-path>" Scopes/Product Scopes/GRAPH.md 2>/dev/null || true

# AFTER
scopes map --depth 2
scopes index
scopes backlinks scope="<changed-file-area>"
```

#### 15.3.4 `agents/context-summarizer.md`

**Lines affected**: ~37-41

```markdown
# BEFORE
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<topic keywords>" --limit 3 --format json
Resolve `SKILLS_ROOT` using `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.

# AFTER
scopes map --query "<topic keywords>" --limit 3
```

Or even better with the brain command:
```markdown
scopes locate --intent "<topic keywords>"
```

#### 15.3.5 `agents/evidence-verifier.md`

**Lines affected**: ~32-44

```markdown
# BEFORE
python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
  --scope <scope-path> --stale-only --format json
Resolve `SKILLS_ROOT` using `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.

# AFTER
scopes drift --scope "<scope-path>" --stale-only
```

Also replace the manual evidence verification steps with:
```markdown
scopes evidence:verify scope="<scope>"
```

#### 15.3.6 `agents/refactor-scanner.md`

**Lines affected**: ~46-71

```markdown
# BEFORE
Resolve `SKILLS_ROOT` using:
- `scopes/skills/_shared/SCRIPT_DISCOVERY.md`

python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<target keywords>" --limit 5 --format json

python3 "$SKILLS_ROOT/scanning-refactor/scripts/hotspot_matrix.py" \
  --repo-root . --since-days 90 --top 20 --format json

# AFTER
scopes map --query "<target keywords>" --limit 5
scopes hotspot --since-days 90 --top 20
```

#### 15.3.7 `agents/scope-filler.md`

**Lines affected**: ~55-82 (heaviest user of scripts)

```markdown
# BEFORE
- python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_trace_stub_from_entrypoints.py" --scope <scope.md> --apply
- python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" --depth 3 --format json
Resolve `SKILLS_ROOT` using:
- `scopes/skills/_shared/SCRIPT_DISCOVERY.md`
...
python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" \
  --scope "<scope-file-path>" 2>/dev/null || true

# AFTER
scopes trace scope="<scope>" --apply
scopes map --depth 3
scopes validate --scope "<scope>"
```

#### 15.3.8 `scopes/skills/syncing-scopes/SKILL.md` (the big one)

**Lines affected**: ~36-42, 99-101, 118-120, 166-168, 183-185, 191-193, 199-201, 213-215, 229-260, 285

This is the heaviest file — references ALL scripts. Full rewrite of script sections:

```markdown
# BEFORE (Mission Start)
- Resolve `SKILLS_ROOT` using `../_shared/SCRIPT_DISCOVERY.md`.
  ls "$SKILLS_ROOT/syncing-scopes/scripts/"*.py
If SKILLS_ROOT cannot be resolved or scripts are missing, STOP.

# AFTER (Mission Start)
Verify the CLI is available:
  scopes version
If the CLI is not available, STOP and tell the user.
```

Replace ALL script invocations in the wave model:

| Section | Before | After |
|---|---|---|
| Step 1 (Skeletons) | `python3 "$SKILLS_ROOT/.../scope_skeleton_generator.py" --item ...` | `scopes create scope="Area/Name"` |
| Step 2 (Contracts) | `python3 "$SKILLS_ROOT/.../slice_contract_builder.py" --from-skeletons ...` | `scopes contract --from-skeletons ...` |
| Validate gate | `python3 "$SKILLS_ROOT/.../validate_scopes.py" --all` | `scopes validate --all` |
| Drift check | `python3 "$SKILLS_ROOT/.../drift_detector.py" --all --format json` | `scopes drift --all` |
| Repair cycle contracts | `python3 "$SKILLS_ROOT/.../slice_contract_builder.py" --from-drift ...` | `scopes contract --from-drift ...` |
| Repair skeletons | `python3 "$SKILLS_ROOT/.../scope_skeleton_generator.py" ...` | `scopes create ...` |
| Final validate | `python3 "$SKILLS_ROOT/.../validate_scopes.py" --all` | `scopes validate --all` |

Replace the "Script Quick Reference" table:

```markdown
# BEFORE
| `scope_skeleton_generator.py` | Create overview + micro scope skeletons | `--item`, ... |
| `drift_detector.py` | Detect stale evidence links | `--all`, ... |
...

# AFTER
| `scopes create` | Create overview + micro scope skeletons | `scope="Area/Name"`, `--micro`, ... |
| `scopes drift` | Detect stale evidence links | `--all`, `--stale-only`, ... |
| `scopes validate` | Full structural gate | `--all`, `--scope`, `--area` |
| `scopes map` | Query scopes by keyword | `--query`, `--depth` |
| `scopes trace` | Generate trace table stubs | `scope="X"`, `--apply` |
| `scopes rename` | Fix evidence links after moves | `scope="X" --to "Y"` |
| `scopes contract` | Build Slice Contracts | `--from-drift`, `--from-skeletons`, `--infer` |
| `scopes hotspot` | Hotspot analysis for refactors | `--top`, `--since-days` |
```

Replace the blocked runbook:
```markdown
# BEFORE
- Scripts not found (`$SKILLS_ROOT` unresolvable): set `Verdict: Blocked`

# AFTER
- CLI not found (`scopes version` fails): set `Verdict: Blocked`
```

#### 15.3.9 All other skills (8 files — same pattern)

Every skill follows the same transformation. Here's the universal pattern:

**Remove from every skill:**
```markdown
Resolve `SKILLS_ROOT` using the shared snippet:
- `../_shared/SCRIPT_DISCOVERY.md`
```

**Replace in every skill:**

| Skill | Before | After |
|---|---|---|
| `brainstorming-project` | `python3 "$SKILLS_ROOT/.../scope_map.py" --query ...` | `scopes map --query ...` |
| `developing-tdd` | `scope_map.py` + `validate_scopes.py` calls | `scopes map` + `scopes validate` |
| `developing-verified` | `scope_map.py` + `validate_scopes.py` calls | `scopes map` + `scopes validate` |
| `planning-idea` | `scope_map.py --query ...` | `scopes map --query ...` or `scopes locate --intent ...` |
| `planning-refactor` | `scope_rename_guard.py --map ...` | `scopes rename --map ...` |
| `querying-scopes` | `scope_map.py --query ...` | `scopes map --query ...` or `scopes locate --intent ...` |
| `researching-decisions` | `scope_map.py --query ...` | `scopes map --query ...` |
| `writing-tasks` | `scope_map.py --query ...` | `scopes map --query ...` |

**Upgrade opportunities** — skills can now use richer CLI commands:

| Skill | Old Capability | New CLI Enhancement |
|---|---|---|
| `querying-scopes` | Read scope + manually follow evidence | `scopes read:code scope="X"` (follows evidence automatically) |
| `planning-idea` | Manual INDEX.md reading | `scopes index` (structured JSON) |
| `planning-refactor` | Manual GRAPH.md grep | `scopes graph:impact scope="X"` |
| `bug-scanner` | Manual grep for patterns | `scopes search:code --query "eval("` |
| `evidence-verifier` | Manual line-by-line checking | `scopes evidence:verify scope="X"` |
| `scanning-refactor` | Separate hotspot + scope map calls | `scopes hotspot` + `scopes map` (same interface) |

#### 15.3.10 `scopes/skills/_shared/SCOPES_PROTOCOL.md`

**Lines affected**: ~13-16 (Mission Start mandatory read)

This is read by EVERY skill. The scope_map.py call here is the most
impactful single change in the project.

```markdown
# BEFORE (Scopes-First Navigation)
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<keywords from user request>" --limit 5 --format json

# AFTER
scopes map --query "<keywords from user request>" --limit 5
```

Also update the "Before running scope_map.py" upstream artifact intake text:
```markdown
# BEFORE
Before running `scope_map.py` or reading `INDEX.md`, check if you were
invoked with a reference to an upstream artifact...

# AFTER
Before running `scopes map` or reading `INDEX.md`, check if you were
invoked with a reference to an upstream artifact...
```

#### 15.3.11 `scopes/skills/_shared/DEVELOPING_PROTOCOL.md`

**Lines affected**: ~61, 66

```markdown
# BEFORE
- IF output is non-empty: update affected scopes + run `validate_scopes.py` as the gate
- `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all`

# AFTER
- IF output is non-empty: update affected scopes + run `scopes validate` as the gate
- `scopes validate --all`
```

#### 15.3.12 `scopes/skills/_shared/SCRIPT_DISCOVERY.md`

**Status**: **DEPRECATED**

This entire file becomes obsolete. Replace its content with a deprecation notice:

```markdown
# Script Discovery (DEPRECATED)

> **This file is deprecated.** Use the `scopes` CLI instead.
>
> All scripts previously accessed via `$SKILLS_ROOT` are now available
> as `scopes <command>` subcommands. Run `scopes help` to see all commands.
>
> Migration: replace `python3 "$SKILLS_ROOT/..."` with `scopes <command>`.
```

#### 15.3.13 `agents/WORKFLOW.md`

**Lines affected**: ~119, 128, 164, 277-280, 307, 328, 394

Replace all script references in workflow diagrams and text:

```markdown
# BEFORE
3. **Slice Contracts**: every teammate gets a pre-built contract
   (from `slice_contract_builder.py` or manually)
...
- `TaskCompleted`: run `drift_detector.py --scope {target}` → if stale, prevent completion
...
│    Build Slice Contracts: slice_contract_builder.py    │
│    drift_detector.py --all --format json               │
│    Lane A: scope_map.py → anchor scopes (subagent)     │

# AFTER
3. **Slice Contracts**: every teammate gets a pre-built contract
   (from `scopes contract` or manually)
...
- `TaskCompleted`: run `scopes drift --scope "<target>"` → if stale, prevent completion
...
│    Build Slice Contracts: scopes contract               │
│    scopes drift --all                                   │
│    Lane A: scopes map → anchor scopes (subagent)        │
```

Also update the upstream intake reference:
```markdown
# BEFORE
...before running `scope_map.py` or reading `INDEX.md`.

# AFTER
...before running `scopes map` or reading `INDEX.md`.
```

#### 15.3.14 `docs/automations.md`

Full rewrite — the automation snippets become much cleaner:

```markdown
# BEFORE
Before running any helper scripts, resolve `SKILLS_ROOT`
(see `scopes/skills/_shared/SCRIPT_DISCOVERY.md`).

## 1) Drift Audit (Weekly)
python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
  --all --stale-only --limit 50

## 2) Artifact Router
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --from-artifact Scopes/Work/Tasks/<file>.md --depth 3 --only tree

## 3) Pre-Merge Quality Gate (CI)
python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" \
  --all --stale-only --limit 20

# AFTER
## 1) Drift Audit (Weekly)
scopes drift --all --stale-only --limit 50

## 2) Artifact Router
scopes map --from-artifact "Scopes/Work/Tasks/<file>.md" --depth 3

## 3) Pre-Merge Quality Gate (CI)
scopes drift --all --stale-only --limit 20
```

Remove the entire `SCRIPT_DISCOVERY` preamble.

#### 15.3.15 `docs/context-engineering.md`

**Line affected**: ~68

```markdown
# BEFORE
Before any skill runs `scope_map.py` or reads `INDEX.md`...

# AFTER
Before any skill runs `scopes map` or reads `INDEX.md`...
```

#### 15.3.16 `docs/settings.md`

**Line affected**: ~39

```markdown
# BEFORE
- `scopes/skills/_shared/SCRIPT_DISCOVERY.md`

# AFTER
- The `scopes` CLI (see `scopes help` for all commands)
```

#### 15.3.17 `README.md`

**Lines affected**: ~94-99, 129, 262, 302

Replace the helper scripts section:
```markdown
# BEFORE
Helper scripts included under `scopes/skills/syncing-scopes/scripts/`:
- `scope_map.py` — compact scope matrix view...
- `drift_detector.py` — stale evidence detection...
...

# AFTER
All helper functionality is available via the `scopes` CLI:
- `scopes map` — compact scope matrix view with JSON output
- `scopes drift` — stale evidence detection via git timestamps
- `scopes create` — generate fill-ready capability scope skeletons
- `scopes contract` — build Slice Contracts from drift, skeletons, or repo inference
- `scopes trace` — generate trace-table stubs from evidence links
- `scopes rename` — rewrite scope links after renames/moves
- `scopes hotspot` — refactor hotspot matrix (size, churn, TODOs)
- `scopes validate` — structural validation gate

Run `scopes help` for the full command list.
```

Replace the pre-merge section:
```markdown
# BEFORE
python3 scopes/skills/syncing-scopes/scripts/drift_detector.py --all --stale-only --limit 20

# AFTER
scopes drift --all --stale-only --limit 20
```

Replace the `scope_map.py --query` tip:
```markdown
# BEFORE
Use `scope_map.py --query "<keywords>"` if you need a fast route to related scopes.

# AFTER
Use `scopes map --query "<keywords>"` (or `scopes locate --intent "<intent>"`)
if you need a fast route to related scopes.
```

Update the shared infrastructure list:
```markdown
# BEFORE
- `scopes/skills/_shared/SCRIPT_DISCOVERY.md` — SKILLS_ROOT resolution snippet

# AFTER
- `scopes/cli.py` — unified CLI for all Scopes operations (`scopes help`)
```

#### 15.3.18 `scopes/skills/syncing-scopes/references/PROTOCOLS.md`

**Line affected**: ~61

```markdown
# BEFORE
- `python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all`

# AFTER
- `scopes validate --all`
```

#### 15.3.19 `scopes/skills/_evaluations/README.md`

**Line affected**: ~44

```markdown
# BEFORE
{"id": "runs-validators", "weight": 3, "desc": "Runs drift_detector.py (or records blockers)"}

# AFTER
{"id": "runs-validators", "weight": 3, "desc": "Runs scopes drift (or records blockers)"}
```

### 15.4 Integration Upgrade Opportunities

Beyond mechanical replacement, some agents/skills can be significantly
improved by using CLI commands that didn't exist before:

#### `agents/evidence-verifier.md` — Use `scopes evidence:verify`

Currently this agent manually reads each evidence link, resolves the file,
reads the line range, and compares. The CLI's `evidence:verify` does all
of this in one call:

```markdown
# BEFORE (manual multi-step process)
### Step 1: Pre-Filter with drift_detector.py
### Step 2: Walk Evidence Links
### Step 3: For each link, read source file...

# AFTER (one command handles pre-filter + verify)
scopes evidence:verify scope="<scope>"
# Returns: [{"link": "...", "status": "ok|stale|missing|content_mismatch", ...}]
```

#### `agents/bug-scanner.md` — Use `scopes graph:impact`

Currently uses manual grep on GRAPH.md. The CLI provides structured
dependency traversal:

```markdown
# BEFORE
grep -A5 "<component>" Scopes/GRAPH.md

# AFTER
scopes graph:impact scope="<component>"
# Returns: {"direct_dependents": [...], "transitive_dependents": [...]}
```

#### `scopes/skills/querying-scopes/SKILL.md` — Use `scopes read:code`

Currently the skill reads a scope, then manually follows evidence links to
read the actual code. The CLI does this in one step:

```markdown
# BEFORE (multi-step)
1. Read scope doc
2. Extract evidence links
3. Read each linked file at the right lines

# AFTER (one step)
scopes read:code scope="<scope>" --section "Entry Points"
# Returns: [{"file": "src/auth.ts", "lines": "L15-L30", "code": "..."}]
```

#### `scopes/skills/planning-refactor/SKILL.md` — Use `scopes graph:impact` + `scopes graph:path`

Currently the skill manually traces dependencies. The CLI provides
graph reasoning:

```markdown
# Enhanced refactor impact analysis
scopes graph:impact scope="<refactor-target>"
scopes graph:path --from "<target>" --to "<dependent>"
```

#### `agents/context-summarizer.md` — Use `scopes locate` instead of `scopes map`

The locate command is specifically designed for intent-based routing:

```markdown
# BEFORE
scopes map --query "<topic keywords>" --limit 3

# AFTER (more semantic)
scopes locate --intent "<topic being summarized>"
```

#### All skills — Use `scopes status` in Mission Start

Add a health check to the shared SCOPES_PROTOCOL Mission Start:

```markdown
# Check brain health before starting
scopes status
# If stale_pct > 50%: warn user, consider running scopes sync first
```

### 15.5 Refactoring Execution Order

The refactoring must happen in sync with CLI implementation phases:

**After Phase 1 (script bridges ready):**

1. Update `scopes/skills/_shared/SCOPES_PROTOCOL.md` — this cascades to all skills
2. Update `scopes/skills/_shared/DEVELOPING_PROTOCOL.md`
3. Deprecate `scopes/skills/_shared/SCRIPT_DISCOVERY.md`
4. Update all 10 skill SKILL.md files (mechanical replacement)
5. Update all 7 agent .md files (mechanical replacement)
6. Update `agents/WORKFLOW.md`
7. Update `docs/automations.md`
8. Update `docs/context-engineering.md`
9. Update `docs/settings.md`
10. Update `README.md`

**After Phase 2 (brain commands ready):**

11. Upgrade `agents/evidence-verifier.md` to use `scopes evidence:verify`
12. Upgrade `agents/bug-scanner.md` to use `scopes graph:impact`
13. Upgrade `scopes/skills/querying-scopes/SKILL.md` to use `scopes read:code`
14. Upgrade `scopes/skills/planning-refactor/SKILL.md` to use `scopes graph:*`
15. Upgrade `agents/context-summarizer.md` to use `scopes locate`
16. Add `scopes status` health check to SCOPES_PROTOCOL Mission Start

**After Phase 3 (sessions ready):**

17. Upgrade `agents/context-summarizer.md` to use `scopes session:*`
18. Add session tracking to skill workflows
19. Update `scopes/skills/_shared/SESSION_LOG_TEMPLATES.md` with CLI commands

### 15.6 Validation: How to Verify Perfect Integration

After all refactoring is done, run these checks:

```bash
# 1. No remaining SKILLS_ROOT references (except SCRIPT_DISCOVERY deprecation notice)
rg "SKILLS_ROOT" agents/ scopes/skills/ docs/ README.md \
  --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'
# Expected: 0 matches

# 2. No remaining python3 script invocations
rg 'python3.*scripts/' agents/ scopes/skills/ docs/ README.md \
  --glob '!*cli-plan*'
# Expected: 0 matches

# 3. No remaining SCRIPT_DISCOVERY references (except deprecation notice)
rg "SCRIPT_DISCOVERY" agents/ scopes/skills/ docs/ README.md \
  --glob '!*SCRIPT_DISCOVERY*' --glob '!*cli-plan*'
# Expected: 0 matches

# 4. All CLI commands referenced in skills/agents actually exist
scopes help | grep -c "^  scopes"
# Expected: matches the command count in this plan

# 5. Makefile still passes
make lint
```

---

## 16. `.scopes/` State Directory

The CLI needs a place to track runtime state (current session, last sync time,
bookmarks, etc.). This lives at `.scopes/` in the project root:

```text
<project-root>/
├── Scopes/            # The knowledge layer (committed to git)
└── .scopes/           # CLI runtime state (gitignored)
    ├── current_session    # path to active session log
    ├── last_sync          # timestamp of last full sync
    ├── bookmarks.json     # bookmarked scopes
    ├── workspaces/        # saved workspace contexts
    └── cache/             # optional cached index/graph parses
```

Add `.scopes/` to the project's `.gitignore`.

---

## 17. `scopes/SKILL.md` Router Update

The umbrella router needs a new entry for CLI-related intents:

```markdown
# Add to routing table:
| "Run a CLI command / use the scopes tool" | `./skills/scopes-cli/SKILL.md` |
| "Check status / health / drift" | `./skills/scopes-cli/SKILL.md` |
```

---

## 18. Makefile Update

Update `make lint` to also compile the CLI:

```makefile
.PHONY: lint

lint:
	python3 -m compileall -q scopes/skills/*/scripts
	python3 -m compileall -q scopes/cli.py
	python3 scopes/cli.py help > /dev/null
```

---

## 19. `.claude-plugin/plugin.json` Update

Add CLI info to the plugin manifest:

```json
{
  "name": "scopes",
  "description": "...",
  "version": "1.1.0",
  "cli": {
    "entry": "scopes/cli.py",
    "commands_prefix": "scopes"
  }
}
```

---

## 20. CHANGELOG Entry

```markdown
## 1.1.0 — CLI

- Add `scopes/cli.py` — unified CLI for all Scopes operations.
- Replace all `SKILLS_ROOT` / `SCRIPT_DISCOVERY` references with `scopes <command>` calls.
- Deprecate `scopes/skills/_shared/SCRIPT_DISCOVERY.md`.
- Add `scopes-cli` skill for teaching agents the CLI.
- Add `.scopes/` state directory for session tracking and runtime state.
- Update all 10 skills, 7 agents, 3 shared protocols, and 5 docs files for CLI integration.
```

---

## Summary: Complete Scope of Work

```
CLI Implementation:
  Phase 1 (Wire existing)      ~400-500 lines    → 9 scripts unified
  Phase 2 (Brain commands)      ~800-1000 lines   → read:code, locate, evidence, graph
  Phase 3 (Sessions & agents)   ~500-700 lines    → sessions, tasks, agent discovery
  Phase 4 (Sync engine)         ~300-500 lines    → sync, history, git-powered
  Phase 5 (Profiles/templates)  ~300-400 lines    → customization layer
  Phase 6 (CLI skill)           ~skill file only   → teach agents the CLI
                                ─────────────────
  CLI subtotal                  ~2300-3100 lines    single Python file

Refactoring (perfect integration):
  7 agent files                 mechanical + upgrade replacements
  10 skill files                mechanical + upgrade replacements
  3 shared protocol files       mechanical replacements
  5 docs/meta files             mechanical replacements
  1 file deprecated             SCRIPT_DISCOVERY.md
  3 config files updated        Makefile, plugin.json, CHANGELOG
                                ─────────────────
  Refactoring subtotal          25 files touched

  Verification:                 0 remaining SKILLS_ROOT refs
                                0 remaining python3 script calls
                                0 remaining SCRIPT_DISCOVERY refs
                                ~115 CLI commands available
```
