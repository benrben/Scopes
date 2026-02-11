#!/usr/bin/env bash
set -euo pipefail

say() { printf '%s\n' "$*" || true; }
say_err() { printf '%s\n' "$*" >&2 || true; }

usage() {
  cat <<'USAGE'
update-skills.sh

Update Scopes Skills only.

Usage:
  # Run from whatever skills folder you installed into (Cursor/Claude/Antigravity):
  bash <skills-root>/updating-skills/scripts/update-skills.sh

  # Override the target skills directory explicitly (rare):
  bash <skills-root>/updating-skills/scripts/update-skills.sh --target-dir <skills-root>

Options:
  --repo <git-url>            (default: https://github.com/benrben/Scopes.git)
  --ref <branch-or-tag>       (default: main)
  --target-dir <path>         (default: auto-detected skills root)
  --dry-run
  -v, --verbose

Environment overrides:
  SCOPES_SKILLS_REPO
  SCOPES_SKILLS_REF
  (legacy fallback: SCOPES_COMMANDS_REPO / SCOPES_COMMANDS_REF)
USAGE
}

TARGET_DIR=""
REPO_URL="${SCOPES_SKILLS_REPO:-${SCOPES_COMMANDS_REPO:-https://github.com/benrben/Scopes.git}}"
REF="${SCOPES_SKILLS_REF:-${SCOPES_COMMANDS_REF:-main}}"
DRY_RUN=0
VERBOSE=0

require_value() {
  local flag="$1"
  local value="${2:-}"
  if [[ -z "$value" || "$value" == --* ]]; then
    say_err "Error: $flag requires a value."
    say_err "Run with --help for usage."
    exit 2
  fi
}

ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-dir)
      require_value "$1" "${2:-}"
      TARGET_DIR="$2"; shift 2
      ;;
    --repo)
      require_value "$1" "${2:-}"
      REPO_URL="$2"; shift 2
      ;;
    --ref)
      require_value "$1" "${2:-}"
      REF="$2"; shift 2
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
  scripts_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
  TARGET_DIR="$(CDPATH='' cd -- "$scripts_dir/../.." && pwd)"
fi

if [[ ${#ARGS[@]} -gt 0 ]]; then
  say_err "Unknown argument(s): ${ARGS[*]}"
  say_err "Run with --help for usage."
  exit 2
fi

if [[ -z "$REPO_URL" || -z "$REF" || -z "$TARGET_DIR" ]]; then
  say_err "Error: missing required configuration (repo/ref/target)."
  say_err "Run with --help for usage."
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  say_err "Error: git is required but was not found on PATH."
  exit 1
fi

mkdir -p "$TARGET_DIR"

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

if [[ $VERBOSE -eq 1 ]]; then
  say_err "Cloning $REPO_URL (ref: $REF)..."
fi

if ! git ls-remote --exit-code "$REPO_URL" >/dev/null 2>&1; then
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

SKILLS_ROOT="$TMP_DIR/repo/skills"
if [[ ! -d "$SKILLS_ROOT" ]]; then
  say_err "Error: repo does not contain skills/"
  say_err "  repo: $REPO_URL"
  say_err "  ref:  $REF"
  exit 1
fi

ADDED=0
UPDATED=0
FOUND=0

shopt -s nullglob
for skill_dir in "$SKILLS_ROOT"/*; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  FOUND=1

  skill_name="$(basename "$skill_dir")"
  dest_dir="$TARGET_DIR/$skill_name"
  tmp_skill_dir="$TARGET_DIR/.scopes-tmp-${skill_name}-$$"

  if [[ $DRY_RUN -eq 1 ]]; then
    if [[ -d "$dest_dir" ]]; then
      say "Would update: $dest_dir/"
      UPDATED=$((UPDATED + 1))
    else
      say "Would add: $dest_dir/"
      ADDED=$((ADDED + 1))
    fi
    continue
  fi

  if [[ -d "$dest_dir" ]]; then
    UPDATED=$((UPDATED + 1))
  else
    ADDED=$((ADDED + 1))
  fi

  rm -rf "$tmp_skill_dir"
  cp -R "$skill_dir" "$tmp_skill_dir"
  rm -rf "$dest_dir"
  mv "$tmp_skill_dir" "$dest_dir"
  say "Synced: $dest_dir/"
done
shopt -u nullglob

if [[ $FOUND -eq 0 ]]; then
  say_err "Error: no skill packages with SKILL.md were found under skills/"
  exit 1
fi

if [[ $DRY_RUN -eq 1 ]]; then
  say "Done. Would add $ADDED skill(s), would update $UPDATED skill(s)."
else
  say "Done. Added $ADDED skill(s), updated $UPDATED skill(s)."
fi
