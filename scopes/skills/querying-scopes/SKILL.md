---
name: querying-scopes
description: Answers “how/where/what depends on what/what’s broken” questions by routing through scope_map.py and verifying with code evidence. Use when you need understanding or diagnosis (not code changes). Do NOT use for implementation — use developing-*.
model: inherit
---

# Querying Scopes — Instant Route + Diagnostic Delegation

You answer questions about the codebase by navigating Scopes documentation and verifying claims with code evidence. You route instantly via `scope_map.py` (no manual INDEX.md crawling), and delegate "what's wrong?" questions to `bug-scanner`.

## When to use this skill
Use when the user asks questions about how the codebase works, what depends on what, what's broken, or what they should read.

## Example prompts
- "Where is X configured?"
- "How does login work end-to-end?"
- "Why is X broken? What should I check first?"

## Prerequisites
- `Scopes/` exists with at least `INDEX.md`.
- If Scopes are completely missing, recommend `/sync` first.

## Mission Start
Load `../_shared/SCOPES_PROTOCOL.md`.

---

## Workflow: Intake → Classify → Route → Answer

### Step -1: Upstream Artifact Intake

Before routing, check for upstream artifacts (see SCOPES_PROTOCOL.md § Upstream Artifact Intake):
1. If invoked from another skill (e.g., after `/scan` or `/plan`), read the incoming `## Links` section for pre-resolved anchor scopes, evidence bundles, and constraints.
2. If an upstream artifact exists and is < 7 days old, skip re-routing for the scopes it already covers — reuse its anchor list and evidence links directly.
3. If no upstream artifact, proceed normally to Step 0.

### Step 0: Instant Route (< 30 seconds)

Run **two parallel lanes** and merge results before Step 1:

**Lane A: Scope Routing**

These checks are independent. **Run them in parallel** and merge into one evidence bundle. Parallel execution is mandatory (see SCOPES_PROTOCOL).

```bash
scopes map \
  --query "<question keywords>" --limit 5 --format json
```

Result: ranked anchor scopes + code paths + evidence counts.

**IF zero results AND Scopes/ exists:**
Don't give up — fall back to codebase search:
```bash
rg -n "<keywords>" . -S \
  -g'*.ts' -g'*.tsx' -g'*.js' -g'*.jsx' -g'*.py' -g'*.go' -g'*.rs' -g'*.md' \
  -g'!node_modules/**' -g'!.venv/**' -g'!venv/**' | head -20
```

**IF zero results AND no Scopes/:**
Set `Verdict: Needs Sync`, recommend `/sync`.

Optional (fast): glance `Scopes/GRAPH.md` for dependency/blast-radius context on the anchor scope(s).

**Lane B: Freshness Pre-Check** (runs in parallel with Lane A)

```bash
# Scope files last commit dates (all anchor scopes from routing)
git log -1 --format="%ci" -- <scope_path_1> <scope_path_2> ...

# Code files last commit dates (evidence paths from scopes)
git log -1 --format="%ci" -- <code_path_1> <code_path_2> ...
```

Freshness data is ready before answer composition — no separate freshness step needed later.

---

### Step 1: Classify Question Type

| Question Pattern | Type | Action |
|---|---|---|
| "How does X work?" | **Explainer** | Read scope + follow evidence |
| "What depends on X?" | **Dependency** | Read GRAPH.md + scope network |
| "What's wrong with X?" / "Why is X broken?" | **Diagnostic** | Delegate to `bug-scanner` |
| "What changed in X?" | **Changelog** | `git log` + scope drift comparison |
| "What should I read first?" | **Navigator** | Return ordered scope tree |
| "Where is X configured?" | **Locator** | Follow evidence links in scope |

---

### Step 2: Answer (type-specific)

#### Fast-path: Locator questions ("Where is X?")
For simple "where is X configured / defined?" questions: a single `scope_map` call + evidence-link follow is sufficient. Skip multi-scope investigation — return the location with a freshness note and exit.

#### For Explainer / Dependency (2+ anchor scopes):
When the question touches **2 or more anchor scopes**, spawn one `scope-investigator` per anchor scope (see `agents/scope-investigator.md`, max 3 in parallel). Each subagent:
- Reads its assigned scope and traces execution paths
- Follows evidence links into code and verifies claims
- Checks freshness (scope date vs code date)
- Maps architecture layers touched by the scope
- Returns a JSON receipt per `scope-investigator` output contract

> **SLICE CONTRACT — Per-Scope Investigator**
> - **Target**: Investigate `{scope_name}` for question `{question}`
> - **Ownership**: Exclusive — this investigator owns `{scope_path}` and its evidence files only
> - **Context**: Anchor scope at `{scope_path}`, question: `{question}`
> - **investigation_type**: `explainer` or `dependency`
> - **Acceptance**: Return receipt with findings, evidence bundle, freshness data, and verified evidence count
> - **WIP Limit**: Max 3 investigators in parallel

The lead merges receipts from all investigators into a unified answer.

#### For single-scope Explainer / Navigator:
1. Read the anchor scope from Step 0
2. Follow evidence links into code for verification:
   - Open the linked file:line ranges
   - Confirm the claim in the scope still matches the code
3. Compose answer with evidence links

#### For Diagnostic ("what's wrong?"):
Spawn **three subagents in parallel**:

**1. `bug-scanner`** (see `agents/bug-scanner.md`):
> **SLICE CONTRACT — Bug Scanner**
> - **Target**: Scan `{area}` for bug-prone patterns, security hotspots, and documentation drift
> - **Ownership**: Exclusive read-only on `{scope_path}` and its entrypoints
> - **Context**: Anchor scope at `{scope_path}`, files to scan: `{entrypoints from scope}`
> - **acceptance.create_tasks**: `false` (diagnostics don't auto-create tasks)
> - **Acceptance**: Return findings with confidence scores (>= 70 only) as JSON receipt
> - **Artifact**: Write findings to `Scopes/Work/Bugs/bug-scan-<date>-<area>.md`

**2. `evidence-verifier`** (see `agents/evidence-verifier.md`):
> **SLICE CONTRACT — Evidence Verifier**
> - **Target**: Verify all evidence links in `{scope_path}`
> - **Ownership**: Exclusive read-only on scope evidence links
> - **Context**: Scope path `{scope_path}`, evidence link list from scope
> - **Acceptance**: Return JSON receipt classifying links as ok/stale/shifted/broken/deleted

**3. `silent-failure-hunter`** (see `agents/silent-failure-hunter.md`):
> **SLICE CONTRACT — Silent Failure Hunter**
> - **Target**: Scan `{area}` for inadequate error handling
> - **Ownership**: Exclusive read-only on `{scope_path}` entrypoints
> - **Context**: Anchor scope at `{scope_path}`, critical paths from scope
> - **Acceptance**: Return findings with confidence scores as JSON receipt

Merge all three receipts into your answer. The `evidence-verifier` receipt replaces the old freshness-checker role with deeper semantic validation.

#### For Changelog:
```bash
git log --oneline --since="2 weeks ago" -- <files from scope evidence> | head -20
```
Compare against scope's last-modified date to show drift.

---

### Step 3: Freshness Note (mandatory on every scope-backed answer)

Every answer that cites a scope MUST include a freshness note. Use the dates already collected in Step 0 Lane B:

```markdown
> **Freshness**: Scope last updated <scope_date>. Code last changed <code_date>.
> <IF drift > 14 days: "⚠ This scope may be outdated. Consider running /sync.">
> <IF drift ≤ 14 days: "✓ Scope appears current.">
```

---

### Step 3.5: Gate (mandatory)

Do not finalize an answer unless it passes ALL checks:

**Manual checks:**
1. Evidence links into code (or clearly marked `[Unknown]` where evidence is missing)
2. A freshness note (scope date vs code date)
3. A clear handoff recommendation (next skill or next command)

**Automated checks (run mechanically, no judgment):**
4. **Evidence file existence**: For every cited evidence link `[path:Lx-Ly]`, verify the file exists:
   ```bash
   test -f "<path>" && echo "OK" || echo "BROKEN: <path>"
   ```
   If any link is broken, mark it `[BROKEN]` in the answer and recommend `/sync`.
5. **Automated confidence assignment**: Compute confidence mechanically from signals:
   - **High**: drift ≤ 14 days AND evidence_count ≥ 2 AND zero broken links
   - **Medium**: drift 15-30 days OR evidence_count == 1 OR any broken links
   - **Low**: drift > 30 days OR evidence_count == 0 OR no scope covers the area

### Step 4: Handoff Recommendations (automatic)

Based on what you found, recommend the appropriate next skill:

| Finding | Recommendation |
|---|---|
| Scope is stale/outdated | "Consider running `/sync` to update this area." |
| Evidence links are broken | "Run `/sync` — evidence links need repair." |
| User wants to change something | "Use `/plan` to create an implementation blueprint." |
| Bug found | "Use `/tdd` to write a regression test and fix." |
| User is onboarding | "Start with `Scopes/INDEX.md` → `DEVELOPER_INFO.md` → anchor scope." |
| Answer confidence is Low | "⚠ Low confidence. Consider running `/sync` to refresh documentation." |

---

## Confidence Levels (automated — see Gate Step 3.5)

| Level | Mechanical Signal |
|---|---|
| **High** | drift ≤ 14 days AND evidence_count ≥ 2 AND zero broken links |
| **Medium** | drift 15-30 days OR evidence_count == 1 OR any broken links |
| **Low** | drift > 30 days OR evidence_count == 0 OR no scope covers the area |

---

## Artifacts

### Research Notes (mandatory when triggered)

Write a research note to `Scopes/Work/Notes/query-<date>-<slug>.md` when ANY of these conditions are true:
- **(a)** Answer required reading **3+ files**
- **(b)** Question type is **Diagnostic**
- **(c)** Confidence is **Medium or Low**

Research note MUST include:
- Question asked and answer summary
- Evidence links cited
- Freshness data
- `## Links` section for downstream consumption:
  ```markdown
  ## Links
  - **Anchor Scopes**: [Scopes/Product/...](path)
  - **Evidence**: [path:Lx-Ly](path#Lx-Ly) — <what it proves>
  - **Related Notes**: [Scopes/Work/Notes/...](path)
  - **Next Skill**: <recommended skill>
  ```

Invoke `context-summarizer` to write the note. Trigger deterministically: **IF 5+ files read OR 3+ scopes traversed**.

### Diagnostic Artifacts
- The `bug-scanner`'s findings file IS the primary artifact.
- The `evidence-verifier`'s receipt is attached to the research note (replaces old freshness-checker).
- The `silent-failure-hunter`'s receipt highlights error-handling gaps not caught by `bug-scanner`.
- Any follow-up task files created from the diagnostic are ephemeral: once implemented, delete the task file and keep durable learnings in a Notes summary instead.

---

## Blocked Runbook
- No Scopes/ exists: set `Verdict: Needs Sync`.
- Scope exists but all evidence is `[Unknown]`: answer what you can from code, recommend `/sync`.
- Question is about something outside the repo: answer from general knowledge, clearly mark as non-evidence-based.

## Output Contract

Return a natural-language answer with evidence, followed by:

```markdown
## QUERY
Verdict: Answered | Partial | Needs Sync
Confidence: High | Medium | Low
Freshness: <scope_date> vs <code_date>
Evidence:
- [path:Lx-Ly](path#Lx-Ly) — <what it proves>
Handoff: <recommended next skill, if any>
Artifact: <path to research note, if created>
```
