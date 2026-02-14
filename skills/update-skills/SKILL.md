---
name: update-skills
description: Refreshes local Scopes skills from upstream repository. Includes pre-update snapshots, change visibility, and post-update integrity validation to catch broken references.
model: inherit
---

# Update Skills — Self-Healing Updates

You update the local skills, agents, and scripts from the upstream repository. After updating, you automatically validate that all references are intact.

## When to use this skill
Use when skills, agents, or scripts need to be refreshed from upstream. This could be triggered by the user or detected when a referenced file is missing.

## Prerequisites
- Git installed.
- Network access to clone the upstream repo.
- Existing skills directory structure.

## Safety and confirmations
- Always check for local modifications before overwriting.
- Ask before overwriting files with local changes.

---

## Workflow: Snapshot → Update → Validate

### Step 1: Pre-Update Snapshot

Capture current state to enable rollback:

```bash
# Snapshot current skill versions
git log -1 --format="%H %s" -- skills/ agents/ commands/ scripts/

# Check for local modifications
git status --porcelain skills/ agents/ commands/ scripts/
```

**IF local modifications exist:**
- List the modified files
- Ask user: "These files have local changes. Overwrite or skip?"
- Record the decision

---

### Step 2: Update (Manual Sync)

```bash
# Clone upstream to temp directory
git clone --depth 1 <upstream_repo_url> /tmp/scopes-upstream

# Sync with change visibility
rsync -avh --itemize-changes /tmp/scopes-upstream/skills/ ./skills/
rsync -avh --itemize-changes /tmp/scopes-upstream/agents/ ./agents/
rsync -avh --itemize-changes /tmp/scopes-upstream/commands/ ./commands/
rsync -avh --itemize-changes /tmp/scopes-upstream/scripts/ ./scripts/ 2>/dev/null || true

# Clean up
rm -rf /tmp/scopes-upstream
```

The `--itemize-changes` flag shows exactly which files were added, changed, or deleted.

---

### Step 3: Post-Update Integrity Validation

For each updated `SKILL.md`, verify all references are intact:

```bash
# Check that all referenced scripts exist
for skill_file in skills/*/SKILL.md; do
  # Extract script references (paths ending in .py)
  grep -oP '[\w/.-]+\.py' "$skill_file" | while read script; do
    if [ ! -f "$script" ] && [ ! -f "skills/$script" ]; then
      echo "BROKEN: $skill_file references $script (not found)"
    fi
  done
done

# Check that all referenced agents exist
for skill_file in skills/*/SKILL.md; do
  grep -oP 'agents/[\w-]+\.md' "$skill_file" | while read agent; do
    if [ ! -f "$agent" ]; then
      echo "BROKEN: $skill_file references $agent (not found)"
    fi
  done
done

# Check that all shared protocols exist
for skill_file in skills/*/SKILL.md; do
  grep -oP 'skills/_shared/[\w_]+\.md' "$skill_file" | while read proto; do
    if [ ! -f "$proto" ]; then
      echo "BROKEN: $skill_file references $proto (not found)"
    fi
  done
done
```

**Smoke test:**
```bash
# Run drift detector as a basic sanity check
python3 skills/syncing-scopes/scripts/drift_detector.py --all --stale-only --limit 5
```

---

### Step 4: Report

```markdown
## UPDATE
Files Changed: <list from rsync --itemize-changes>
Files Added: <list>
Files Deleted: <list>
Integrity Check: PASS | FAIL (<broken references>)
Local Mods Preserved: <list of skipped files, if any>
```

---

## Scopes-First Policy Check

After updating, verify the updated skills still follow Scopes-first policy:
- Each SKILL.md should reference `skills/_shared/SCOPES_PROTOCOL.md`
- Each skill should have a Mission Start section
- Agent orchestration should use `skills/_shared/SLICE_CONTRACT.md`

If any policy violations are found, report them but don't auto-fix (the upstream may have intentional changes).

---

## Blocked Runbook
- No network access: set `Verdict: Blocked`.
- Local modifications and user declines overwrite: set `Verdict: Blocked`, list files.
- Broken references after update: report each one, set `Verdict: Proceed (with warnings)`.

## Output Contract

```markdown
## SKILL UPDATE
Verdict: Proceed | Blocked
Updated: <count> files
Added: <count> files
Integrity: PASS | FAIL
Next: <any follow-up needed>
```
