# Audit: Scopes Prompt System

This file defines how to audit that the prompt set (and outputs produced by it) remain consistent over time.

## 1) Audit the Prompts (`Scopes/Prompts/**`)

### Prompt checklist (must pass)
- **Paths**: Output locations must be under `Scopes/` and use the canonical layout from `Scopes/Prompts/sync-scopes.md`.
- **Required reads**: Must mention `Scopes/INDEX.md`, `Scopes/GRAPH.md`, and relevant `Scopes/Product/**` scopes.
- **Workflow clarity**: Must describe the steps (deconstruct/diagnose/develop/deliver or equivalent) with enough detail that an engineer can follow.
- **Diagram present**: Includes at least one Mermaid diagram of the workflow.
- **Audit checklist present**: Contains a short checklist to validate outputs.
- **Consistent spine (preferred)**: Required Reads → Output Location → Diagram → Method (Silent) + Output Contract (Visible) → Rules & Constraints → Output Artifacts → Audit Checklist.
- **Cross-linking (“outer scopes”)**: Must encourage linking outputs to:
  - Capability Scopes (`Scopes/Product/**`)
  - `Scopes/INDEX.md` and `Scopes/GRAPH.md`
  - ADRs (`Scopes/Decisions/ADRs/**`) where decisions exist
  - Releases (`Scopes/Releases/**`) when changes ship
  - Research (`Scopes/Research/**`) when investigation drove choices

### Naming consistency checklist
- Prompts should refer to `Scopes/Prompts/sync-scopes.md` (not ambiguous “sync-scopes” references).
- Examples should use `Scopes/Product/**` for capability docs.

## 2) Audit the Capability Scopes (`Scopes/Product/**`)

### Capability Scope checklist (must pass)
- **Evidence**: Every functional claim has at least one evidence link in the form `[path:Lx-Ly](path#Lx-Ly)`.
- **Diagrams**: Exactly **2** Mermaid diagrams per substantial capability scope.
- **Traces**: At least one complete end-to-end trace table per major path.
- **Use cases**: At least 3 concrete use cases for substantial scopes.
- **Cross-links**: Has meaningful links to “outer scopes” (parents/children/related, ADRs, research, releases, tasks).
- **Graph alignment**: Dependencies described in the scope match edges in `Scopes/GRAPH.md`.

## 3) Audit the Graph (`Scopes/GRAPH.md`)
- Every edge has:
  - A relationship description, and
  - At least one evidence link (or is explicitly marked as low confidence).

## 4) Audit Release/Onboarding/Research/Decisions
- **Research** (`Scopes/Research/**`): strict separation of internal truth vs external sources.
- **Releases** (`Scopes/Releases/**`): every bullet points to a capability scope under `Scopes/Product/**`.
- **Onboarding** (`Scopes/Onboarding/**`): includes trace-based exercises that force clicking evidence links.
- **ADRs** (`Scopes/Decisions/ADRs/**`): lists affected scopes and states consequences.

