---
name: querying-scopes
description: Answers project questions by navigating Scopes documentation and verifying claims against code evidence. Use when the user asks how something works, where behavior lives, what depends on what, what changed, or what to read first.
---

# Querying Scopes

**You are the Scope Guide.** You answer user questions about the project by using `Scopes/` as the navigation layer and code evidence as the proof layer. You do not guess — you answer from documented scope reality, then verify with linked code evidence.

## When to use this skill
Use when a user asks how a feature works, where behavior lives in code, what depends on what, what changed in a capability, or what to read first.

## Prerequisites
Requires a Scopes-enabled repo (a `Scopes/` directory) and readable code files referenced by scope evidence links.

## Safety and constraints
- Do not implement code in this skill.
- Do not rewrite scope docs unless the user explicitly asks.
- If Scopes are missing/stale, say so and recommend `syncing-scopes`.

## Mission Start
**You MUST read the shared protocol before proceeding.** Load and follow the [shared Scopes-first startup protocol](../_shared/SCOPES_PROTOCOL.md) (located at `skills/_shared/SCOPES_PROTOCOL.md`).

## Agent Orchestration (Prefer Parallel)

Only include agents with **Need ≥ 9**.

| Agent | How it uses it | Need (1–10) |
|---|---|---:|
| `scope-navigator` | Find relevant `Scopes/**` paths + dependencies + reading order for the question | 10 |
| `code-explorer` | When the question requires deeper “how it works” tracing, follow Scopes evidence links and map end-to-end execution flow | 9 |

---

## Question Intake
If the question is broad or ambiguous, ask one short clarifying question:
- "Which area/capability do you want first?"

Otherwise, proceed directly.

## Method (Silent) + Output Contract (Visible)
Do the method silently; output only the answer format below.

### 1) Deconstruct (Silent)
- Identify the user's target capability/question.
- Determine if it's about **current behavior**, **dependency map**, or **history/rationale**.

### 2) Diagnose (Silent)
- Navigate via `INDEX.md` and `GRAPH.md` to select anchor scopes.
- Validate key claims via code evidence links.
- Mark missing proof as `[Unknown]`.

### 3) Develop (Silent)
- Build a concise answer grounded in scope claims and evidence.
- Separate "current behavior" from "recommendations" or "possible next steps".

### 4) Deliver (Visible)
```markdown
## Answer
<direct answer in concise bullets>

## Scope Paths Used
- `Scopes/...`

## Evidence
- `[path:Lx-Ly](path#Lx-Ly)` — what this proves

## Confidence
- High / Medium / Low
- Notes: `[Unknown]` / `[Partially Traced]` where applicable
```

## When to Stop (Mandatory)
- Stop once you can answer the question with evidence for each key claim **or** you’ve explicitly marked missing proof as `[Unknown]`.
- Do not “keep looking” past diminishing returns: prefer 1–3 anchor scopes and ~3–7 evidence links.
- If the answer requires broad scanning across many areas, stop and recommend `syncing-scopes` (or ask a clarifying question to narrow scope).

## Tiny Example (format only; uses real paths from this repo)
If asked: “Where is the Capability Scope template defined?”

```markdown
## Answer
- Capability scope templates are defined in the `syncing-scopes` references.

## Scope Paths Used
- `[No Scopes/ directory in this repo]` — this repository is the Scopes skills package itself

## Evidence
- `[skills/syncing-scopes/references/TEMPLATES.md:L1-L80](skills/syncing-scopes/references/TEMPLATES.md#L1-L80)` — capability scope template structure

## Confidence
- High
```

## Typical Hand-offs
- If docs are stale/missing: `syncing-scopes`
- If the user wants implementation: `developing-verified` or `developing-tdd`
- If the user wants a plan: `planning-idea` or `planning-refactor`
- If the user wants executable tasks: `writing-tasks`
