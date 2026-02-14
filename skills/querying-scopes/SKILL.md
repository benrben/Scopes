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
Load `skills/_shared/SCOPES_PROTOCOL.md`.

Resolve `SKILLS_ROOT` using the shared snippet:
- `skills/_shared/SCRIPT_DISCOVERY.md`

---

## Workflow: Classify → Route → Answer

### Step 0: Instant Route (< 30 seconds)

```bash
python3 "$SKILLS_ROOT/syncing-scopes/scripts/scope_map.py" \
  --query "<question keywords>" --limit 5 --format json
```

Result: ranked anchor scopes + code paths + evidence counts.

**IF zero results AND Scopes/ exists:**
Don't give up — fall back to codebase search:
```bash
grep -rn "<keywords>" --include="*.ts" --include="*.py" --include="*.go" \
  --include="*.js" --include="*.md" . | head -20
```

**IF zero results AND no Scopes/:**
Set `Verdict: Needs Sync`, recommend `/sync`.

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

#### For Explainer / Dependency / Locator / Navigator:
1. Read the top 1-3 anchor scopes from Step 0
2. Follow evidence links into code for verification:
   - Open the linked file:line ranges
   - Confirm the claim in the scope still matches the code
3. Compose answer with evidence links

#### For Diagnostic ("what's wrong?"):
Spawn `bug-scanner` as a subagent:
> **SLICE CONTRACT**
> - **Target**: Scan `{area}` for bug-prone patterns, security hotspots, and documentation drift
> - **Ownership**: Read-only (no edits)
> - **Context**: Anchor scope at `{scope_path}`, files to scan: `{entrypoints from scope}`
> - **Acceptance**: Return findings with severity ratings
> - **Artifact**: Write findings to `Scopes/Work/Bugs/scan-<area>-<date>.md`

Merge `bug-scanner` findings into your answer.

#### For Changelog:
```bash
git log --oneline --since="2 weeks ago" -- <files from scope evidence> | head -20
```
Compare against scope's last-modified date to show drift.

---

### Step 3: Freshness Note (mandatory on every scope-backed answer)

Every answer that cites a scope MUST include a freshness note:

```markdown
> **Freshness**: Scope last updated <scope_date>. Code last changed <code_date>.
> <IF drift > 14 days: "⚠ This scope may be outdated. Consider running /sync.">
> <IF drift ≤ 14 days: "✓ Scope appears current.">
```

To get the dates:
```bash
# Scope file last commit
git log -1 --format="%ci" -- <scope_path>

# Code files last commit (from scope evidence paths)
git log -1 --format="%ci" -- <code_path>
```

---

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

## Confidence Levels

| Level | Criteria |
|---|---|
| **High** | Scope evidence links verified in code, dates < 14 days drift |
| **Medium** | Scope exists but some evidence is `[Unknown]` or dates > 14 days |
| **Low** | No scope covers this area, or scope is very stale (> 30 days) |

---

## Artifacts (conditional)

**IF the question required > 5 minutes of tracing** (complex investigation):
- Invoke `context-summarizer` to write a research note to `Scopes/Work/Notes/`
- This prevents re-investigation of the same question in future sessions

**IF diagnostic question** (bug-scanner was invoked):
- The bug-scanner's findings file IS the artifact

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
