# Session Log Templates

Shared session log structure used by `developing-tdd` and `developing-verified`.

---

## Memory Model

Maintain two memory layers inside the Session Log:

### Short-Term Memory (operational; updated frequently)
- Current active scenario (one behavior only)
- Current verification method + exact command(s)
- Last observed signal: failing/passing snippet (1-3 lines)
- Current hypothesis (clearly labeled as hypothesis)
- Next micro-step (one tiny edit you will do next)

### Long-Term Memory (strategic; updated as it changes)
- Goal + Definition of Done checklist
- Scenario/Test list status (plan vs done)
- Scope constraints discovered (from `Scopes/Product/**`)
- Decisions made (naming/API/contract choices) + brief rationale
- Environment/setup blockers discovered during preflight
- Known drift items that must be documented

### Memory Hygiene Rules
- Keep memory concise: prefer bullets; avoid long narrative.
- Distinguish **Observed** vs **Hypothesis** explicitly.
- Do not record unverified claims as facts.

### Parking Lot (Required)
If you discover important follow-up work that violates "One Behavior per Cycle", record it in a Parking Lot section instead of doing it immediately.

---

## TDD Session Log Template

**File Path**: `Scopes/Work/STDD/<YYYY-MM-DD>-<session-slug>.md`

```markdown
# STDD Session: <Title>

## Context Snapshot
- **Goal**: <User Goal>
- **Relevant Scopes**: [Link]
- **Tech Stack**: [Scopes/Onboarding/TECH_STACK.md](link)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](link)
- **Risks**: ...

## Working Memory

### Short-Term (Now)
- **Active Scenario**: ...
- **Focused Command**: ...
- **Last Signal (Observed)**: ...
- **Hypothesis**: ...
- **Next Micro-step**: ...

### Long-Term (Track)
- **Definition of Done**:
  - [ ] ...
- **Constraints from Scopes**:
  - ...
- **Decisions**:
  - ...
- **Drift to Document**:
  - ...
- **Env/Setup Notes**:
  - ...

## Parking Lot
- [ ] ...

## Test List (The Plan)
- [x] Scenario 1: <Description>
- [ ] Scenario 2: <Description>
- [ ] Scenario 3: <Description>

## Execution Log

### Cycle 1: <Scenario Name>
- **RED**: <Test File Path>
  - *Outcome*: Failed as expected (Output snippet).
- **GREEN**: <Implementation File Path>
  - *Outcome*: Passed.
- **REFACTOR**: <Description of improvements>
- **SCOPE UPDATE**: Updated `Scopes/Product/Auth/Login.md` with new trace and diagram.
#### Micro-steps (Edit -> Rerun)
1) Edit: <file> — <1 sentence>
   - Rerun: <command> -> pass/fail (<signal>)
2) ...

### Cycle 2: ...
```

---

## Verify Session Log Template

**File Path**: `Scopes/Work/DEV/<YYYY-MM-DD>-<session-slug>.md`

```markdown
# DEV Session: <Title>

## Context Snapshot
- **Goal**: <User Goal>
- **Relevant Scopes**: [Link]
- **Tech Stack**: [Scopes/Onboarding/TECH_STACK.md](link)
- **Code Standards**: [Scopes/Work/Standards/WRITE_STYLE.md](link)
- **Risks**: ...

## Working Memory

### Short-Term (Now)
- **Active Scenario**: ...
- **Verification Method**: test/script/manual
- **Focused Command(s) / Steps**: ...
- **Last Signal (Observed)**: ...
- **Hypothesis**: ...
- **Next Micro-step**: ...

### Long-Term (Track)
- **Definition of Done**:
  - [ ] ...
- **Constraints from Scopes**:
  - ...
- **Decisions**:
  - ...
- **Drift to Document**:
  - ...
- **Env/Setup Notes**:
  - ...

## Parking Lot
- [ ] ...

## Scenario List (The Plan)
- [x] Scenario 1: <Description>
- [ ] Scenario 2: <Description>

## Execution Log

### Scenario 1: <Scenario Name>
- **Baseline Verification**:
  - Method: test/script/manual
  - Command(s)/Steps: ...
  - Observed: ...
- **Implementation**:
  - Files touched: `...`
- **Final Verification**:
  - Command(s)/Steps: ...
  - Observed: ...
- **Polish**: <what changed structurally>
- **SCOPE UPDATE**: Updated `Scopes/Product/...` with new trace and evidence.
#### Micro-steps (Edit -> Verify)
1) Edit: <file> — <1 sentence>
   - Verify: <command/steps> -> pass/fail (<signal>)
2) ...
```
