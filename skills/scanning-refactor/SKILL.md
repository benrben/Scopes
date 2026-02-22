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
- Read `skills/_shared/SCOPES_PROTOCOL.md`.

## Mission Start
Load and follow:
- `skills/_shared/SCOPES_PROTOCOL.md`
- `skills/_shared/SLICE_CONTRACT.md` (if delegating to agents)
Design patterns (Full GoF catalog; use only when it helps communicate a recommendation):
- `skills/_shared/GOF_PATTERNS.md`

Resolve `SKILLS_ROOT` using:
- `skills/_shared/SCRIPT_DISCOVERY.md`

---

## Workflow: Route → Hotspots → Refactor Opportunities → Report

### Step 0: Route to anchor scope(s) (< 60s)

If the user provided a scope path, use it as the anchor.
Otherwise, route mechanically:

```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<refactor goal keywords>" --limit 5 --format json
```

Pick 1–3 anchor scopes max (avoid full-scan).

Parallelism note: routing and hotspot generation are independent. **Run Step 0 (route) and Step 1 (hotspot_matrix) in parallel** and merge results. Parallel execution is mandatory (see SCOPES_PROTOCOL).

### Step 1: Build a mechanical hotspot list (< 3 min)

Generate candidate refactor hotspots (size/churn/TODO density):

```bash
python3 "$SKILLS_ROOT/scanning-refactor/scripts/hotspot_matrix.py" \
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
If a recommendation corresponds to a GoF pattern, name it (e.g., Strategy/Adapter/Decorator) for clarity — but keep it evidence-backed and avoid adding abstraction for its own sake. Use `skills/_shared/GOF_PATTERNS.md` for consistent naming.

For every recommendation, include:
- **What** you would change (concrete, name the new module/function boundaries)
- **Why** it helps (simplicity, reuse, tests, fewer deps)
- **Proof links**: `[path:Lx-Ly](path#Lx-Ly)` for the code smell/duplication you’re addressing
- **Risk**: blast radius from `Scopes/GRAPH.md` + whether tests exist
- **Safe migration steps** (green-to-green). If files move/rename, include rename guard:
  ```bash
  python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_rename_guard.py" \
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
```

### Gate: Output Caps (mandatory)

Enforce deterministic caps in the final artifact:
- Top 5 hotspot targets max
- <= 12 total opportunities across targets
- Every opportunity includes proof link(s) and a verify command

### Step 4: Optional follow-up tasks (max 3)

If you find high-value refactors that should be scheduled, write up to 3 task files:
- `Scopes/Work/Tasks/$(date +%F)-refactor-<slug>.md`

Each task must:
- Link 1–3 anchor scopes
- Name the exact target files/modules
- Include a verification command
- Be small enough to do green-to-green

After the refactor is implemented and verified, delete the refactor task file. If the scan report is now stale, delete it and replace with a short completion note linking to the changes.

---

## Agent Orchestration (Optional, “Use agents right”)

If the scan spans multiple anchor scopes or is broad, delegate **per-scope** scanning for context isolation:

- Spawn 1 `refactor-scanner` subagent per anchor scope (max 3 in parallel).
- Each subagent gets a Slice Contract:
  - `context.anchor_scope` = that scope file
  - `context.likely_entrypoints` = evidence-linked code entrypoints from the scope
  - `acceptance.artifact_required` = `Scopes/Work/Refactors/refactor-scan-<date>-<scope-slug>.md`

Wait for all receipts, then (optionally) write a 1-page rollup report linking the per-scope reports.

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

### JSON Receipt (mandatory)
```json
{
  "slice_target": "<area scanned>",
  "status": "complete | partial | blocked",
  "hotspots_count": 0,
  "opportunities_count": 0,
  "verdict": "Proceed | Blocked | Needs Sync | Needs Narrowing",
  "artifact": "Scopes/Work/Refactors/refactor-scan-<date>-<area>.md",
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
