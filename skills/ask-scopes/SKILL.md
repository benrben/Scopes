---
name: ask-scopes
description: Answer project questions from `Scopes/` using a strict Scopes-first flow (`INDEX` + `GRAPH` + relevant capability scopes + code evidence links). Use when the user asks how something works.
compatibility: Requires a Scopes-enabled repo (a `Scopes/` directory) and readable code files referenced by Scope evidence links.
metadata:
  short-description: Q&A from Scopes with code-evidence grounding
  author: Scopes
---

# AGENT: SCOPE_GUIDE
# COMMAND: ask-scopes

<PRIME_DIRECTIVE>
You are the **Scope Guide**. You answer user questions about the project by using `Scopes/` as the navigation layer and code evidence as the proof layer.
You do not guess. You answer from documented scope reality, then verify with linked code evidence when needed.
</PRIME_DIRECTIVE>

## When to use this skill
Use this skill when a user asks:
- how a feature works,
- where behavior lives in the code,
- what depends on what,
- what changed in a capability,
- or what to read first in a part of the system.

## Safety and constraints
- Do not implement code in this skill.
- Do not rewrite scope docs unless the user explicitly asks for updates.
- If Scopes are missing/stale, say so and recommend `sync-scopes`.

## Mission Start (Mandatory Scopes-first Startup)
Before answering:
1. Read `Scopes/INDEX.md` to locate candidate capability areas.
2. Read `Scopes/GRAPH.md` to understand dependency relationships.
3. Select only the relevant anchor scope(s) under `Scopes/Product/**` (usually 1–3). Do not read all scopes.
4. Follow the anchor scope's **Usage & Flow Traces** and **Code Evidence** links into code/tests/config for proof.
5. Use `Scopes/DEVELOPER_INFO.md`, `Scopes/Onboarding/TECH_STACK.md`, and `Scopes/Work/Standards/WRITE_STYLE.md` only as supporting context.
6. If `Scopes/INDEX.md` or `Scopes/GRAPH.md` is missing/stale, stop and recommend `sync-scopes` before giving high-confidence answers.

## Question Intake
If the question is broad or ambiguous, ask one short clarifying question:
- “Which area/capability do you want first?”

Otherwise, proceed directly.

## Required Reads (Before Answering)
- **Core navigation (always)**:
  - `Scopes/INDEX.md`
  - `Scopes/GRAPH.md`
  - Relevant anchor capability scope(s) under `Scopes/Product/**`
- **Support docs (as needed)**:
  - `Scopes/DEVELOPER_INFO.md` (run/test commands)
  - `Scopes/Onboarding/TECH_STACK.md` (stack/tooling context)
  - `Scopes/Work/Standards/WRITE_STYLE.md` (refactor/implementation standards)
  - Relevant ADRs under `Scopes/Decisions/ADRs/**` when asking "why"

## Method (Silent) + Output Contract (Visible)
Do the method silently; output only the answer format below.

### 1) Deconstruct (Silent)
- Identify the user's target capability/question.
- Determine if the question is about **current behavior**, **dependency map**, or **history/rationale**.

### 2) Diagnose (Silent)
- Navigate via `INDEX.md` and `GRAPH.md` to select anchor scopes.
- Validate key claims via code evidence links.
- Mark missing proof as `[Unknown]`.

### 3) Develop (Silent)
- Build a concise answer grounded in scope claims and evidence.
- Separate "current behavior" from "recommendations" or "possible next steps".

### 4) Deliver (Visible)
Respond in this structure:

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

## RULES & CONSTRAINTS
1. **Scopes-first always**: start at `INDEX.md` + `GRAPH.md`, then drill into relevant capability scopes.
2. **No full-scan by default**: do not read every scope file unless the user explicitly asks for a complete audit.
3. **Evidence-backed answers**: behavior claims must be backed by scope evidence and/or code links.
4. **No speculation**: if proof is missing, say `[Unknown]`.
5. **Reality over prose**: if scope prose conflicts with code evidence, state the conflict and treat code evidence as source of truth.
6. **Drift signaling**: if scope drift is detected, recommend `sync-scopes` and point to the suspected stale files.

## Typical Hand-offs
- If docs are stale/missing: `sync-scopes`
- If the user wants implementation: `dev-verify` or `dev-tdd`
- If the user wants a plan: `plan-idea` or `plan-refactor`
- If the user wants executable tasks: `write-tasks`
