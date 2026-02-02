#!/usr/bin/env bash
set -euo pipefail

say_err() { printf '%s\n' "$*" >&2 || true; }

usage() {
  cat <<'EOF'
update-skills.sh

Update Scopes Skills only (not commands).

Usage:
  # Run from whatever skills folder you installed into (Cursor/Claude/Antigravity):
  bash <skills-root>/update-skills/scripts/update-skills.sh

  # Override the target skills directory explicitly (rare):
  bash <skills-root>/update-skills/scripts/update-skills.sh --target-dir <skills-root>

Options:
  --repo <git-url>            (default: https://github.com/benrben/ScopesCommands.git)
  --ref <branch-or-tag>       (default: main)
  --source-subdir <path>      (default: commands)
  --dry-run
  -v, --verbose
EOF
}

TARGET_DIR=""
REPO_URL="${SCOPES_COMMANDS_REPO:-https://github.com/benrben/ScopesCommands.git}"
REF="${SCOPES_COMMANDS_REF:-main}"
SOURCE_SUBDIR="${SCOPES_COMMANDS_SOURCE_SUBDIR:-commands}"
DRY_RUN=0
VERBOSE=0

ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-dir)
      TARGET_DIR="${2:-}"; shift 2
      ;;
    --repo)
      REPO_URL="${2:-}"; shift 2
      ;;
    --ref)
      REF="${2:-}"; shift 2
      ;;
    --source-subdir)
      SOURCE_SUBDIR="${2:-}"; shift 2
      ;;
    --dry-run)
      DRY_RUN=1; shift
      ;;
    -v|--verbose)
      VERBOSE=1; shift
      ;;
    -h|--help)
      usage; exit 0
      ;;
    *)
      ARGS+=("$1"); shift
      ;;
  esac
done

if [[ -z "$TARGET_DIR" ]]; then
  # Default: update the skills folder this script is installed under:
  #   <skills-root>/update-skills/scripts/update-skills.sh
  scripts_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
  TARGET_DIR="$(CDPATH='' cd -- "$scripts_dir/../.." && pwd)"
fi

if [[ ${#ARGS[@]} -gt 0 ]]; then
  say_err "Unknown argument(s): ${ARGS[*]}"
  say_err "Run with --help for usage."
  exit 2
fi

if [[ -z "$REPO_URL" || -z "$REF" || -z "$TARGET_DIR" || -z "$SOURCE_SUBDIR" ]]; then
  say_err "Error: missing required configuration (repo/ref/target/source)."
  say_err "Run with --help for usage."
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  say_err "Error: git is required but was not found on PATH."
  exit 1
fi

say() { printf '%s\n' "$*" || true; }

yaml_quote() {
  # YAML single-quote escaping: ' -> ''
  printf "%s" "$1" | sed "s/'/''/g"
}

description_for() {
  case "$1" in
    ask-scopes) echo "Answers questions about the project using Scopes as primary truth; repairs scope drift only when required." ;;
    bug-hunt) echo "Finds proven bugs/foot-guns with evidence and outputs a bug report (optionally tasks)." ;;
    dev-loop) echo "Implements a feature/bug via strict TDD and updates Scopes as you go." ;;
    develop) echo "Implements a feature/bug via verify-as-you-go (no strict TDD) and updates Scopes as you go." ;;
    ideate) echo "Generates scope-anchored product ideas that are ready to plan." ;;
    plan-board) echo "Maps Scopes into an execution-ready board blueprint (epics/stories/tasks)." ;;
    plan-idea) echo "Turns an idea into a sequenced implementation blueprint (and creates/reuses research if needed)." ;;
    plan-refactor) echo "Plans a safe refactor with verification gates and required scope maintenance." ;;
    research-loop) echo "Researches a question with strict internal-vs-external truth separation; outputs decision-enabling artifacts." ;;
    sync-scopes) echo "Generates/updates Scopes (truth) from code/tests/config and maintains INDEX/GRAPH/DEV_INFO." ;;
    write-adr) echo "Writes an ADR linked to affected Scopes and graph implications." ;;
    write-onboarding) echo "Creates a role-based onboarding path driven by scope traces and code tours." ;;
    write-release) echo "Writes release notes from scope delta (facts-only, scope-linked)." ;;
    write-tasks) echo "Turns intent/plans/research/bugs into 1–4 hour engineer-ready tasks with verification + scope maintenance." ;;
    *) echo "Scopes workflow skill: $1." ;;
  esac
}

mkdir -p "$TARGET_DIR"

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

if [[ $VERBOSE -eq 1 ]]; then
  say_err "Cloning $REPO_URL (ref: $REF)..."
fi

if ! git ls-remote --exit-code "$REPO_URL" >/dev/null 2>&1; then
  # Back-compat: older scripts used ScopesCommands.git (doesn't exist).
  if [[ "$REPO_URL" == "https://github.com/benrben/ScopesCommands.git" ]]; then
    REPO_URL="https://github.com/benrben/Scopes.git"
  fi

  if ! git ls-remote --exit-code "$REPO_URL" >/dev/null 2>&1; then
    say_err "Error: cannot access repo (bad URL, no network, or auth required)."
    say_err "  repo: $REPO_URL"
    exit 1
  fi
fi

if ! git ls-remote --exit-code --heads --tags "$REPO_URL" "$REF" >/dev/null 2>&1; then
  say_err "Error: ref not found in repo (branch/tag)."
  say_err "  repo: $REPO_URL"
  say_err "  ref:  $REF"
  exit 1
fi

if [[ $VERBOSE -eq 1 ]]; then
  git -c advice.detachedHead=false clone --depth 1 --branch "$REF" -- "$REPO_URL" "$TMP_DIR/repo"
else
  if ! git -c advice.detachedHead=false clone --depth 1 --branch "$REF" -- "$REPO_URL" "$TMP_DIR/repo" >/dev/null 2>&1; then
    say_err "Error: failed to clone repo."
    say_err "  repo: $REPO_URL"
    say_err "  ref:  $REF"
    exit 1
  fi
fi

SRC_ROOT="$TMP_DIR/repo/$SOURCE_SUBDIR"
if [[ ! -d "$SRC_ROOT" ]]; then
  say_err "Error: source subdir not found in repo: $SOURCE_SUBDIR"
  exit 1
fi

ADDED=0
UPDATED=0

while IFS= read -r -d '' src_file; do
  base="$(basename "$src_file")"
  # Docs-only file (not a skill).
  if [[ "$base" == "README.md" ]]; then
    continue
  fi
  name="${base%.md}"

  dest_dir="$TARGET_DIR/$name"
  dest_file="$dest_dir/SKILL.md"

  desc="$(description_for "$name")"
  desc_q="$(yaml_quote "$desc")"

  tmp_dir="$TARGET_DIR/.scopes-tmp-${name}-$$"
  mkdir -p "$tmp_dir"

  {
    printf "%s\n" "---"
    printf "%s\n" "name: $name"
    printf "%s\n" "description: '$desc_q'"
    printf "%s\n" "disable-model-invocation: true"
    printf "%s\n" "---"
    printf "\n"
    cat "$src_file"
  } >"$tmp_dir/SKILL.md"

  if [[ -d "$dest_dir" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      say "Would update: $dest_dir/"
      rm -rf "$tmp_dir"
    else
      rm -rf "$dest_dir"
      mv "$tmp_dir" "$dest_dir"
      say "Updated: $dest_file"
    fi
    UPDATED=$((UPDATED + 1))
  else
    if [[ $DRY_RUN -eq 1 ]]; then
      say "Would add: $dest_dir/"
      rm -rf "$tmp_dir"
    else
      mv "$tmp_dir" "$dest_dir"
      say "Added: $dest_file"
    fi
    ADDED=$((ADDED + 1))
  fi
done < <(find "$SRC_ROOT" -type f -name '*.md' -print0)

# Also sync any bundled skill folders (optional).
EXTRA_SKILLS_ROOT="$TMP_DIR/repo/skills"
if [[ -d "$EXTRA_SKILLS_ROOT" ]]; then
  shopt -s nullglob
  for skill_dir in "$EXTRA_SKILLS_ROOT"/*; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"
    dest_dir="$TARGET_DIR/$skill_name"
    tmp_dir="$TARGET_DIR/.scopes-tmp-extra-${skill_name}-$$"

    if [[ $DRY_RUN -eq 1 ]]; then
      if [[ -d "$dest_dir" ]]; then
        say "Would update: $dest_dir/"
      else
        say "Would add: $dest_dir/"
      fi
      continue
    fi

    rm -rf "$tmp_dir"
    cp -R "$skill_dir" "$tmp_dir"
    rm -rf "$dest_dir"
    mv "$tmp_dir" "$dest_dir"
    say "Synced: $dest_dir/"
  done
  shopt -u nullglob
fi

if [[ $DRY_RUN -eq 1 ]]; then
  say "Done. Would add $ADDED skill(s), would update $UPDATED skill(s)."
else
  say "Done. Added $ADDED skill(s), updated $UPDATED skill(s)."
fi

