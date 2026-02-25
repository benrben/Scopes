---
title: "Phase 2 — Core Brain Commands"
status: pending
phase: 2
effort: "~800-1000 lines"
created: 2026-02-25
depends_on: [01-phase1-wire-scripts]
blocks: []
source: docs/cli-plan.md#5-phase-2--core-brain-commands
---

# Phase 2 — Core Brain Commands

> This is what makes Scopes a "brain" — reading scopes with evidence follow,
> searching across layers, graph reasoning, and intent-based routing.

## Tasks

### 2.1 Core Helpers

- [ ] **Evidence link parser** (`_parse_evidence_links`)
  - Parse `[path:Lx-Ly](path#Lx-Ly)` links from scope content
  - Parse `[path](path#Lx-Ly)` variant
  - Return `EvidenceLink` dataclass: target, start_line, end_line, section, display
  - Optional section filter
- [ ] **Section extractor** (`_extract_section`)
  - Extract content under a specific `## Heading` from markdown
  - Return text between the heading and the next same-level heading (or EOF)
- [ ] **Frontmatter parser** (`_parse_frontmatter`)
  - Parse YAML frontmatter from markdown files
  - Return dict of key-value pairs
- [ ] **GRAPH.md parser** (`_parse_graph`)
  - Parse GRAPH.md into list of edges: `{from, to, type, label}`
  - Support BFS/DFS traversal helper
- [ ] **INDEX.md parser** (`_parse_index`)
  - Parse INDEX.md into structured `{areas: [{name, scopes: [...]}]}`
- [ ] **Staleness checker** (`_is_stale`)
  - Given an evidence link + scope path, check if code file was modified after scope
  - Reuse git timestamp logic from drift_detector.py
- [ ] **Line reader** (`_read_lines`)
  - Read specific line range from a file, return content

### 2.2 Scope Reading Commands

- [ ] **`scopes read scope="X"`** — read full scope doc content
  - `--section "Entry Points"` — read one section only
  - JSON: `{scope, path, content, sections: [...]}`
  - Compact: raw content
- [ ] **`scopes read:evidence scope="X"`** — extract evidence links only
  - `--section` optional filter
  - JSON: `[{target, lines, section, status}]`
- [ ] **`scopes read:code scope="X"`** — follow evidence → return code snippets
  - `--section` optional filter
  - JSON: `[{file, lines, code, section}]`
  - Compact: file paths + code blocks

### 2.3 Scope Info & Listing

- [ ] **`scopes scope name="X"`** — composite scope info
  - Return: name, path, properties, evidence_count, stale_count, sections, last_modified
- [ ] **`scopes scopes --status stale`** — filter scopes by staleness
- [ ] **`scopes area name="X"`** — area info (scope count, total evidence, staleness)
- [ ] **`scopes areas`** — list all scope areas
- [ ] **`scopes outline scope="X"`** — show heading structure (list of ## sections)
- [ ] **`scopes random`** — pick a random scope (for audit sampling)
- [ ] **`scopes random:read`** — read a random scope's content
- [ ] **`scopes stats scope="X"`** — word count, evidence count, section count
- [ ] **`scopes recents --limit 10`** — recently modified scopes (by git date)
- [ ] **`scopes status`** — project dashboard
  - scope_count, stale_count, stale_pct, areas, last_sync, pending_tasks

### 2.4 Search Commands

- [ ] **`scopes search --query "auth" --limit 10`** — full-text search across scope docs
  - Case-insensitive match
  - Return: scope, line number, matching text
  - Sort by relevance
- [ ] **`scopes search:context --query "JWT" --lines 3`** — search with surrounding context lines
- [ ] **`scopes search:code --query "validateToken"`** — search within evidence-linked code files only
  - Collect all evidence link targets across scopes
  - Search only within those files (much more targeted)
- [ ] **`scopes search:evidence --pattern "*.test.ts"`** — find evidence links matching a file pattern
- [ ] **`scopes locate --intent "add caching to API"`** — intent → scope routing
  - Tokenize intent
  - Score each scope (reuse scope_map.py scoring logic)
  - Return top matches with evidence links
  - This is THE "brain" command
- [ ] **`scopes query "What depends on Auth?"`** — structured query against INDEX + GRAPH

### 2.5 Links & Evidence Commands

- [ ] **`scopes backlinks scope="X"`** — scopes that reference this one
- [ ] **`scopes links scope="X"`** — all outgoing references (scopes + evidence)
- [ ] **`scopes links:scopes scope="X"`** — only scope-to-scope references
- [ ] **`scopes links:evidence scope="X"`** — only evidence links (to code)
- [ ] **`scopes evidence scope="X"`** — full evidence report with staleness per link
  - For each link: target, lines, exists, stale, section
- [ ] **`scopes evidence:verify scope="X"`** — actively verify links resolve
  - Check file exists, lines in range, optionally content matches
- [ ] **`scopes evidence:add scope="X" --section "Entry Points" --link "src/a.ts:L15-L30"`**
  - Append evidence link to specified section
- [ ] **`scopes evidence:remove scope="X" --link "src/old.ts:L5-L10"`**
  - Remove evidence link from scope doc
- [ ] **`scopes orphans`** — scopes with no incoming references from other scopes
- [ ] **`scopes deadends`** — scopes with no outgoing evidence links
- [ ] **`scopes unresolved`** — broken evidence links (file missing or lines out of range)

### 2.6 Graph Commands

- [ ] **`scopes graph scope="X"`** — dependency neighbors from GRAPH.md
- [ ] **`scopes graph:path --from "Auth/Login" --to "DB/Users"`** — BFS shortest dependency chain
- [ ] **`scopes graph:impact scope="X"`** — "What's affected if I change this?"
  - Direct dependents + transitive dependents

### 2.7 Index & Graph Direct Access

- [ ] **`scopes index`** — dump INDEX.md as structured JSON
- [ ] **`scopes graph`** (no scope arg) — dump full GRAPH.md as structured JSON

### 2.8 Properties Commands

- [ ] **`scopes properties`** — list all properties used across all scopes
- [ ] **`scopes property:read scope="X" --name "status"`** — read a property value
- [ ] **`scopes property:set scope="X" --name "status" --value "active"`** — set a property
- [ ] **`scopes property:remove scope="X" --name "deprecated"`** — remove a property
- [ ] **`scopes property:list scope="X"`** — list all properties for a scope

### 2.9 Scope Editing Commands

- [ ] **`scopes append scope="X" --section "Evidence" --content "..."`** — append to section
- [ ] **`scopes prepend scope="X" --section "Constraints" --content "..."`** — prepend to section
- [ ] **`scopes delete scope="X"`** — delete scope (with orphan check warning)
- [ ] **`scopes open scope="X"`** — print resolved path (for editor integration)
- [ ] **`scopes fill scope="X"`** — print fill guidance for a skeleton scope

## Acceptance Criteria

```bash
scopes read scope="SomeScope"
scopes read:code scope="SomeScope" --section "Entry Points"
scopes search --query "auth" --limit 5
scopes locate --intent "add caching"
scopes evidence scope="SomeScope"
scopes evidence:verify scope="SomeScope"
scopes graph scope="SomeScope"
scopes graph:impact scope="SomeScope"
scopes backlinks scope="SomeScope"
scopes status
scopes index
scopes orphans
scopes unresolved
```
