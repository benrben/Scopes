---
name: scanning-refactor
description: Scans Scopes + code to find simplification/refactor opportunities (separate logic, reuse shared code, reduce duplication, clarify boundaries) and suggests safe, incremental steps and optional project-structure changes with evidence links. Produces a durable refactor-scan report (and optional hygiene tasks). Use when you want refactor recommendations or a maintainability audit. Do NOT use for implementation — use planning-refactor (plan) or developing-* (execute).
model: inherit
---

# Scanning Refactor — Scope-Aware Simplification Suggestions

You scan the codebase through **Scopes** (intent → evidence → code) and produce **evidence-backed refactor recommendations** that make the code simpler, more modular, and easier to reuse — without changing behavior.

## When to use this skill
Use when the user asks for:
- “How can we simplify this code?”
- “What should we refactor next?”
- “We need better separation of concerns / reuse”
- “Suggest project structure improvements”

## Example prompts
- "Scan the auth scopes and suggest refactors to simplify the code."
- "Find duplication and propose extraction points with a safe migration plan."
- "Suggest a folder/module restructure for this area, with incremental steps."

## Prerequisites
- `Scopes/` exists with at least `INDEX.md` and `GRAPH.md`.
- If Scopes are missing or obviously stale, recommend `syncing-scopes` first and set `Verdict: Needs Sync`.
- Read `../_shared/SCOPES_PROTOCOL.md`.

## Mission Start
Load and follow:
- `../_shared/SCOPES_PROTOCOL.md`
- `../_shared/SLICE_CONTRACT.md` (if delegating to agents)
Design patterns (Full GoF catalog; use only when it helps communicate a recommendation):
- `../_shared/GOF_PATTERNS.md`

---

## Workflow: Intake → Route → Hotspots → Refactor Opportunities → Report

### Step -1: Upstream Artifact Intake

Before routing, check for upstream artifacts (see SCOPES_PROTOCOL.md § Upstream Artifact Intake):
1. If invoked from another skill (e.g., after `/query` or `/plan`), read the incoming `## Links` section for pre-resolved anchor scopes, evidence bundles, and constraints.
2. **Reuse prior scan reports**: If a `Scopes/Work/Refactors/refactor-scan-*-<area>.md` exists and is **< 7 days old**, reuse its hotspot data and scope routing. Skip re-scanning for the scopes it already covers — focus new effort on uncovered areas only.
3. If no upstream artifact, proceed normally to Step 0.

### Step 0: Route to anchor scope(s) (< 60s)

**Fast-path for single-scope scans**: If the user specified a single scope path, use it directly as the anchor. Skip `scope_map.py` routing. Proceed immediately to Step 1 with that anchor.

Otherwise, route mechanically:

For multi-scope routing:

```bash
scopes map \
  --query "<refactor goal keywords>" --limit 5 --format json
```

Pick 1–3 anchor scopes max (avoid full-scan).

Parallelism note: routing and hotspot generation are independent. **Run Step 0 (route) and Step 1 (hotspot_matrix) in parallel** and merge results. Parallel execution is mandatory (see SCOPES_PROTOCOL).

### Step 1: Build a mechanical hotspot list (< 3 min)

Generate candidate refactor hotspots (size/churn/TODO density):

```bash
scopes hotspot \
  --repo-root . --since-days 90 --top 20 --format json
```

Then narrow to what matters for the anchor scope(s):
- Prefer files referenced by **Code Evidence** links in the anchor scope(s).
- If needed, map code → scopes:
  ```bash
  rg -n "<path/to/file>" Scopes/Product Scopes/GRAPH.md 2>/dev/null || true
  ```

### Step 1.5: Delegate Per-Scope Scans (preferred for multi-scope)

If you have 2-3 anchor scopes, run **one `refactor-scanner` per anchor scope in parallel** for context isolation:
- Each subagent receives a Slice Contract anchored to its scope + likely entrypoints.
- Each subagent writes a per-scope scan report under `Scopes/Work/Refactors/`.
- The lead merges receipts and produces one rollup report (or selects the best per-scope report as the primary artifact).

### Step 2: For each hotspot, identify refactor opportunities (top 5 targets)

For each target file/module, find **1–3 opportunities** only (avoid a giant wishlist):

**Opportunity types (use evidence, not vibes):**
- **Separate concerns**: split I/O (HTTP/db/fs) from pure logic; isolate orchestration from computation.
- **Extract reuse**: repeated validation/transform/error mapping becomes a shared helper/module.
- **Reduce duplication**: unify parallel code paths behind one function/type.
- **Clarify boundaries**: define stable public API surface; push details behind it.
- **Simplify control flow**: early returns, smaller functions, fewer flags.
- **Project structure change (only if justified)**: reorganize modules by capability/layer when current layout causes repeated cross-imports or “god” directories.
If a recommendation corresponds to a GoF pattern, name it (e.g., Strategy/Adapter/Decorator) for clarity — but keep it evidence-backed and avoid adding abstraction for its own sake. Use `../_shared/GOF_PATTERNS.md` for consistent naming.

For every recommendation, include:
- **What** you would change (concrete, name the new module/function boundaries)
- **Why** it helps (simplicity, reuse, tests, fewer deps)
- **Proof links**: `[path:Lx-Ly](path#Lx-Ly)` for the code smell/duplication you’re addressing
- **Risk**: blast radius from `Scopes/GRAPH.md` + whether tests exist
- **Migration Safety Rating**: LOW / MED / HIGH per opportunity (consistent with upgraded `refactor-scanner` agent):
  - **LOW**: single file, no downstream dependents, has test coverage
  - **MED**: 2-3 files, 1-2 downstream dependents, partial coverage
  - **HIGH**: 4+ files, 3+ downstream dependents, or no coverage
- **Safe migration steps** (green-to-green). If files move/rename, include rename guard:
  ```bash
  scopes rename \
    --map '{"Scopes/Product/Old.md":"Scopes/Product/New.md"}' --apply --repo-root .
  ```

### Step 3: Persist the scan report (mandatory artifact)

Write the report to:
- `Scopes/Work/Refactors/refactor-scan-$(date +%F)-<area>.md`

Minimum required sections:

```markdown
# Refactor Scan: <Area>

## Links (Scopes + Proof)
- **Anchor Scopes**: [...]
- **GRAPH.md**: [Scopes/GRAPH.md](../../GRAPH.md) — <relevant edges>
- **DEVELOPER_INFO**: [commands](../../DEVELOPER_INFO.md)

## Hotspots (Mechanical)
<!-- summarize hotspot_matrix.py output; include top candidates -->

## Opportunities (Evidence-Backed)
### 1) <Title>
- **What**: ...
- **Why**: ...
- **Proof**:
  - `[path:Lx-Ly](path#Lx-Ly)` — <symptom>
- **Risk**: blast_radius=..., coverage=STRONG|WEAK|NONE, moves_files=T/F
- **Safe Steps**:
  1. ...
  2. ...
  3. ...
- **Verify**: `<command>`
- **Scopes to Update**: <scope files likely to need link/evidence updates>

## Links
- **Anchor Scopes**: [Scopes/Product/...](path)
- **GRAPH.md**: [Scopes/GRAPH.md](../../GRAPH.md)
- **Upstream Artifact**: <path to upstream scan/query, if any>
- **Handoff → planning-refactor**: Pre-resolved anchors, hotspots, and top opportunities for immediate plan generation
```

### Gate: Output Caps + Automated Validation (mandatory)

**Automated output-cap validation** (run mechanically before finalizing):
- Top 5 hotspot targets max — if more, truncate and note overflow count
- <= 12 total opportunities across targets — if more, rank and drop lowest
- Every opportunity includes proof link(s) and a verify command

**Automated proof-link file existence check**:
For every proof link `[path:Lx-Ly]` in the report, verify the file exists:
```bash
test -f "<path>" && echo "OK" || echo "BROKEN: <path>"
```
If any link is broken, mark it `[BROKEN]` in the report and add a note recommending `/sync`.

### Step 3.5: Pattern Conformance Check (optional, recommended)

If the scan found opportunities involving introducing new patterns or reorganizing existing ones, spawn `pattern-conformance-checker` (see `agents/pattern-conformance-checker.md`) in parallel with the report persistence to validate that recommendations don't violate the Pattern Conformance Rule from `SCOPES_PROTOCOL.md`. Include its findings in the report's `## Opportunities` section.

### Step 4: Follow-up tasks (opt-in, max 3)

Follow-up task creation is **opt-in** (consistent with the upgraded `refactor-scanner` agent):
- Tasks are only created when the Slice Contract sets `acceptance.create_tasks: true` or the user explicitly requests actionable task files.
- When tasks are NOT requested, list recommendations in the report only.

If creating tasks, write up to 3 task files:
- `Scopes/Work/Tasks/$(date +%F)-refactor-<slug>.md`

Each task must:
- Link 1–3 anchor scopes
- Name the exact target files/modules
- Include a verification command
- Be small enough to do green-to-green

After the refactor is implemented and verified, delete the refactor task file. If the scan report is now stale, delete it and replace with a short completion note linking to the changes.

---

## Agent Orchestration (Mandatory for 2+ anchor scopes)

When scanning **2 or more anchor scopes**, you MUST delegate per-scope scanning for context isolation. No sequential fallback.

When hotspots span **2+ modules**, spawn one subagent per module for per-module hotspot analysis.

- Spawn 1 `refactor-scanner` subagent per anchor scope (max 3 in parallel — WIP limit enforced).
- Each subagent gets a full Slice Contract with exclusive ownership:

> **SLICE CONTRACT — Per-Scope Scanner**
> - **Target**: Scan `{scope_name}` for refactor opportunities
> - **Ownership**: Exclusive — this scanner owns `{scope_path}` and its evidence files only. No other scanner may read or write to these paths.
> - **Context**: Anchor scope at `{scope_path}`, likely entrypoints: `{entrypoints from scope}`
> - **Acceptance**: Return JSON receipt (universal format) + write per-scope report to `Scopes/Work/Refactors/refactor-scan-<date>-<scope-slug>.md`
> - **WIP Limit**: Max 3 scanners in parallel

Wait for all JSON receipts, then write a 1-page rollup report linking the per-scope reports.

---

## Output Contract

Write the full report to `Scopes/Work/Refactors/refactor-scan-$(date +%F)-<area>.md` AND return BOTH:

### Summary (<= 14 lines)
```
## REFACTOR SCAN
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence>
Top Hotspots: <N> files (size/churn/todos)
Opportunities: <count> (top 3 listed below)
Evidence:
- `[path:Lx-Ly](path#Lx-Ly)` — <one-line recommendation>
Next: planning-refactor | writing-tasks | developing-verified
Artifact: `Scopes/Work/Refactors/refactor-scan-<date>-<area>.md`
Confidence: High | Medium | Low
```

### JSON Receipt (mandatory from lead AND every scanner)

Every scanner subagent MUST return a JSON receipt in this universal format. The lead collects all receipts and includes them in the final output.

**Per-scanner receipt** (universal base fields from upgraded `refactor-scanner`):
```json
{
  "slice_target": "<scope scanned>",
  "status": "complete | partial | blocked",
  "files_read": ["<scope files, GRAPH.md read for context>"],
  "files_changed": ["<report file>"],
  "key_findings": ["<top opportunities>"],
  "evidence_count": 0,
  "unknowns": 0,
  "hotspots_count": 0,
  "opportunities_count": 0,
  "migration_safety": {"low": 0, "med": 0, "high": 0},
  "proof_links_verified": 0,
  "proof_links_broken": 0,
  "tasks_created": false,
  "artifact": "Scopes/Work/Refactors/refactor-scan-<date>-<scope-slug>.md"
}
```

**Lead rollup receipt:**
```json
{
  "slice_target": "<area scanned>",
  "status": "complete | partial | blocked",
  "hotspots_count": 0,
  "opportunities_count": 0,
  "verdict": "Proceed | Blocked | Needs Sync | Needs Narrowing",
  "artifact": "Scopes/Work/Refactors/refactor-scan-<date>-<area>.md",
  "scanner_receipts": ["<per-scanner receipts>"],
  "follow_ups": ["<task file paths, or deferred items>"]
}
```

## Rules
- NEVER edit source code — scan + suggest only.
- Every recommendation MUST include at least one proof link, or be labeled `[Unknown]`.
- Do not recommend big-bang rewrites; always propose incremental, reversible steps.
- Do not propose project-structure changes unless you can point to concrete pain (duplication, cross-import churn, unclear ownership) with proof links.

## Lifecycle / Hygiene (mandatory rule)

Refactor-scan reports and generated tasks are not an archive. After the chosen refactors are implemented:
- Delete completed refactor task files under `Scopes/Work/Tasks/`.
- Delete the now-stale refactor-scan report under `Scopes/Work/Refactors/` (optional but recommended) and keep a short durable completion note instead.
