---
name: syncing-scopes
description: Generates or updates Scopes docs from code/tests/config with evidence-backed claims (INDEX.md, GRAPH.md, DEVELOPER_INFO.md). Use when Scopes are missing, stale, or drifted from code reality. Do NOT use just to answer a question — use querying-scopes.
model: inherit
---

# Syncing Scopes

You generate/repair `Scopes/` from observable repo truth. No guessing: missing proof becomes `[Unknown]`.

## When to use this skill
Use when `Scopes/` is missing, stale, or you suspect scope drift (broken evidence links, outdated traces, missing capability coverage).

## Example prompts
- "My Scopes docs are stale; update them from the code."
- "Generate Scopes/ from scratch for this repo."
- "Fix broken evidence links and refresh INDEX/GRAPH."

## Prerequisites
- Read access to the repo code/tests/config.
- Permission to write under `Scopes/`.
- **Parallel subagents are MANDATORY** when filling 2+ scopes: spawn all in one batch (see `skills/_shared/SCOPES_PROTOCOL.md`). No sequential fallback.

## Safety and confirmations
- Prefer updating existing files over churn/renames.
- Ask before destructive operations (mass deletes, large rewrites, moving many files).

## Mission Start
Load and follow the shared Scopes-first startup protocol at `skills/_shared/SCOPES_PROTOCOL.md`.
For detailed rules, load `skills/syncing-scopes/references/PROTOCOLS.md` and `skills/syncing-scopes/references/TEMPLATES.md` as needed.
For delegation rules, load `skills/_shared/SLICE_CONTRACT.md`.

## Script Discovery (MANDATORY — do this FIRST)

Before doing ANY work:
- Resolve `SKILLS_ROOT` using `skills/_shared/SCRIPT_DISCOVERY.md`.
- Verify scripts exist:
  ```bash
  ls "$SKILLS_ROOT/syncing-scopes/scripts/"*.py
  ```

If SKILLS_ROOT cannot be resolved or scripts are missing, STOP and tell the user.

## Parallel Wave Model (Preferred)

Treat sync as a batch system with deterministic gates:
- **Wave 0 (Preflight)**: resolve scripts, decide mode, and gather drift/gen signals (parallel where possible).
- **Wave 1 (Fill)**: run multiple `scope-filler` workers in parallel (<= 6), one per scope file (exclusive ownership via Slice Contracts).
- **Wave 2 (Stitch/Validate)**: lead stitches `INDEX.md` + `GRAPH.md` from receipts, then gates on `validate_scopes.py`.
- Loop by batch until all scopes are valid.

Intermediate JSON outputs (drift JSON, skeleton JSON, contract JSON) are **temporary**. Delete them after stitching/validation unless the user explicitly asks to keep them.

---

## ⛔ CRITICAL RULES — READ BEFORE ACTING

1. **DO NOT fill scope content manually by writing it inline.** ALWAYS delegate scope filling to `scope-filler` subagents (or agent team teammates for 4+). The lead creates skeletons and META files; agents fill them.
2. **ALWAYS use scripts** for drift detection (`drift_detector.py`), skeleton generation (`scope_skeleton_generator.py`), and Slice Contract building (`slice_contract_builder.py`). Do not replicate their logic manually.
3. **ALWAYS delegate filling to `scope-filler`** — use subagents (Task tool) or Agent Teams. Each filler receives a Slice Contract with pre-gathered context.
4. The ONLY things the lead agent does manually are: META files (INDEX.md, GRAPH.md, DEVELOPER_INFO.md, TECH_STACK.md), skeleton generation via script, and final stitching.

---

## Kickoff (Automatic)
- Do **not** ask which area to focus on.
- Discover all capability areas from `Scopes/INDEX.md` and `Scopes/Product/**` (or from repo structure if Scopes are missing) and sync **all** areas.
- Only ask the user for destructive operations (see Safety) or when Scopes are missing and generation from scratch needs approval.

---

## Operating Modes

### Generation Mode (Scopes/ is empty or missing)

When `Scopes/` doesn't exist or has no scope files:

**Step 1: Discover** (lead only, < 5 min)
1. Scan the repo for project shape:
   - Read dependency files: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.
   - Identify top-level source directories: `src/`, `lib/`, `app/`, `components/`, `routes/`, etc.
   - Run: `find . -name "*.py" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" | head -200`
2. Build a capability area list from directory structure + entry files.
3. Create the META files **before** any scope files (lead does these manually — they're one-off):
   - `Scopes/INDEX.md` (skeleton with inferred area tree)
   - `Scopes/GRAPH.md` (empty template)
   - `Scopes/DEVELOPER_INFO.md` (from `package.json` scripts, `Makefile`, CI config, etc.)
   - `Scopes/Onboarding/TECH_STACK.md` (from dependency files)
   - `Scopes/Work/Standards/WRITE_STYLE.md` (from linter configs, existing patterns)

**Step 2: Generate Skeletons** (USE THE SCRIPT)

```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_skeleton_generator.py" \
  --item "Area1: Capability1" \
  --item "Area2: Capability2" \
  --item "Area3: Capability3" \
  --micro \
  --format json \
  --repo-root .
```

This creates empty skeleton scope files. With `--micro`, each item produces:
- 1 overview scope: `Scopes/Product/<Area>/<Capability>.md` (router)
- N micro scopes: `Scopes/Product/<Area>/<Capability>/*.md` (smaller slices, linked)
Capture the JSON output — it lists the created files. Treat this JSON as temporary (prefer a temp file under `/tmp` if you must write it to disk).

**Step 3: Build Slice Contracts** (USE THE SCRIPT)

```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/slice_contract_builder.py" \
  --from-skeletons <skeleton_output.json> --repo-root .
```

This generates one Slice Contract per skeleton, pre-packaged with entrypoints, tech stack, and related scopes.
Treat contract JSON outputs as temporary (delete after the batch validates).

**Step 4: Delegate Filling to scope-filler Agents**

**Strategy Selection:**

**Option A — Multiple Scopes (2+) → Agent Team (Preferred)**
> Create an agent team with N teammates (max 6).
> Each teammate gets ONE scope file and its Slice Contract.
> Wait for ALL teammates to complete (guaranteed parallel).
> Clean up the team.

**Option B — Single Scope (1) OR Agent Teams Disabled → Subagents**
> Spawn subagents.
> ⚠️ **CRITICAL:** If spawning >1 subagents, you MUST issue ALL tool calls in the **same turn**.
> Do NOT spawn one, wait, then spawn next. THIS IS A FAILURE.

**Batch limits:**
- Max **6 parallel workers** per batch. If you have 15 scopes, run 3 batches of 5.
- Each worker gets exclusive ownership of its scope file.

Each filler returns a JSON receipt with `evidence_count`, `unknowns`, `graph_edges_found`.


**Step 5: Stitch** (lead only, after all fillers complete)
1. Read the JSON receipts from all fillers.
2. Update `INDEX.md` with all new scope references.
3. Update `GRAPH.md` with dependency edges from `graph_edges_found` in receipts.
4. Final validation:
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all
```

**Cleanup (mandatory):**
- Delete intermediate JSON outputs (skeleton output, drift output, contract output) if written to disk.
- Keep only `Scopes/` docs plus (optionally) one durable sync summary note under `Scopes/Work/Notes/`.

---

### Update Mode (Scopes/ exists)

When `Scopes/` already has content, the agent detects drift and fixes it:

**Step 1: Detect Drift** (lead only — USE THE SCRIPTS)

Run drift detection FIRST — this IS the router, not an afterthought:
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/drift_detector.py" --all --format json
```

Sort results by severity: `missing` > `stale` > `ok`. This sorted list IS the work backlog.
Treat the drift JSON output as temporary (prefer a temp file under `/tmp` if you must write it to disk).

**Step 2: Build Slice Contracts from drift output**
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/slice_contract_builder.py" \
  --from-drift <drift_output.json> --repo-root .
```

**Step 3: Fix using scope-filler agents** (DELEGATE — do NOT fix scopes manually)

For scopes that need updating, generate new skeletons if needed:
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_skeleton_generator.py" \
  --items-json '<list of stale scopes>' --force --micro --format json --repo-root .
```

Then delegate filling to scope-filler subagents or agent team (same as Generation Mode Step 4).

**For broken evidence links only** (mechanical fix by lead — this IS acceptable to do manually):
- Find-and-replace dead links with updated file paths
- This is a simple text substitution, not scope filling

**Step 4: Stitch and Validate** (lead only)
1. Update `INDEX.md` + `GRAPH.md` from filler receipts.
2. Re-run drift detection as final gate:
```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/validate_scopes.py" --all
```
3. Fix any remaining issues inline.

**Cleanup (mandatory):**
- Delete intermediate JSON outputs (drift output, contract output, any regenerated skeleton output) if written to disk.
- Keep only updated `Scopes/` docs plus one durable sync summary note.

---

## What the Lead May Do Manually vs. What MUST Use Scripts/Agents

| Task | Who Does It |
|---|---|
| Create/update META files (INDEX, GRAPH, DEVELOPER_INFO, TECH_STACK) | **Lead** (manual) — these are one-off structural files |
| Create scope skeleton files | **Script** (`scope_skeleton_generator.py`) |
| Fill scope content (evidence, traces, diagrams) | **Agent** (`scope-filler` via subagent or agent team) |
| Fix broken evidence links (file path changes) | **Lead** (manual text substitution is acceptable) |
| Run drift detection | **Script** (`drift_detector.py`) |
| Build Slice Contracts | **Script** (`slice_contract_builder.py`) |
| Final stitching (INDEX + GRAPH updates) | **Lead** (manual) |

---

## Available Scripts Reference

| Script | Purpose | Key Flags |
|---|---|---|
| `scope_skeleton_generator.py` | Create overview + micro scope skeletons | `--item`, `--items-json`, `--micro`, `--micro-scope`, `--micro-limit`, `--format json`, `--force` |
| `drift_detector.py` | Detect stale evidence links | `--all`, `--stale-only`, `--format json` |
| `validate_scopes.py` | Full gate: META present + links resolve + no placeholders + drift not stale | `--all`, `--scope`, `--area`, `--allow-stale`, `--format json` |
| `scope_map.py` | Query scopes by keyword | `--query`, `--depth`, `--format json` |
| `scope_trace_stub_from_entrypoints.py` | Generate trace table stubs | `--scope`, `--apply` |
| `scope_rename_guard.py` | Fix evidence links after file moves | `--map`, `--dry-run` |
| `slice_contract_builder.py` | Build Slice Contracts from drift/skeletons | `--from-drift`, `--from-skeletons`, `--infer` |

---

## Available Agents Reference

| Agent | File | Purpose | Invoked By |
|---|---|---|---|
| `scope-filler` | `agents/scope-filler.md` | Fills one scope skeleton with evidence | Subagent (Task tool) or Agent Team teammate |

**Note:** There is NO `scope-auditor` or `scope-writer` agent. Filling goes through `scope-filler`; validation goes through `validate_scopes.py` (drift-only view is `drift_detector.py`).

---

## Git Tracking Protocol (Permissioned)
- Always record `BASE_REF` (branch/sha) in the session log or plan artifact.
- Create checkpoint commits only if explicitly approved by the user.
- Diff-only fallback: if commits are not allowed, use `git diff` summaries to show what changed.

## When to Stop (Mandatory)
- Stop once validators are clean for **all** areas OR you can precisely report what is blocked and why.
- No scope cap: sync all areas. Label gaps as `[Unknown]` where evidence is missing.
- If the repo is too large to sync in one run, split by capability areas and use agent teams per area; do not arbitrarily limit to 1-3 scopes.

## Maintenance / Hygiene (mandatory)

After a sync completes and validates:
- Delete any “sync tracking” task files created during the run that are now complete.
- Delete executed plan/refactor-plan artifacts created to manage the sync work.
- Keep: updated `Scopes/` docs + one durable sync summary note (and ADR/Notes as needed).

## Blocked Runbook (Mandatory)
- No `Scopes/` and generation from scratch is not approved: set `Verdict: Needs Narrowing` and ask for permission to generate (do not ask which area — generate all).
- Evidence links cannot be validated (missing files, permissions): record exact blocker; set `Verdict: Blocked`.
- Git history unavailable (no git metadata): use filesystem timestamps and direct evidence checks; record limitation.
- Scripts not found (`$SKILLS_ROOT` unresolvable): set `Verdict: Blocked` and tell user to check installation.

## Output Contract

Return <= 20 lines:

```markdown
## SYNC
Verdict: Proceed | Blocked | Needs Sync | Needs Narrowing
Decision: <one sentence summary of what was updated/generated>
Scripts Used: <list of scripts that were run>
Agents Spawned: <count of scope-filler agents>
Evidence:
- `Scopes/INDEX.md` | `Scopes/GRAPH.md` | `Scopes/Product/...` (as applicable)
Areas Synced: <count>
Evidence Links: <total count>
Unknowns: <count>
Next: <one action>
Artifact: Scopes/Work/Notes/summary-<date>-sync.md
```
