#!/usr/bin/env bash
set -euo pipefail

say() { printf '%s\n' "$*" || true; }
say_err() { printf '%s\n' "$*" >&2 || true; }

usage() {
  cat <<'USAGE'
update-skills.sh

Update Scopes skills (and shared support files).

Usage:
  # Run from whatever skills folder you installed into (Cursor/Claude/Antigravity):
  bash <skills-root>/updating-skills/scripts/update-skills.sh

  # Override the target skills directory explicitly (rare):
  bash <skills-root>/updating-skills/scripts/update-skills.sh --target-dir <skills-root>

Options:
  --repo <git-url>            (default: https://github.com/benrben/Scopes.git)
  --ref <branch-or-tag>       (default: main)
  --target-dir <path>         (default: auto-detected skills root)
  --backup-dir <path>         (default: <target>/.scopes-backups/<timestamp>/)
  --no-backup                 (disable backups before overwriting)
  --include-evaluations       (also sync skills/_evaluations/)
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
BACKUP=1
BACKUP_DIR=""
INCLUDE_EVALUATIONS=0

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
    --backup-dir)
      require_value "$1" "${2:-}"
      BACKUP_DIR="$2"
      BACKUP=1
      shift 2
      ;;
    --no-backup)
      BACKUP=0; shift
      ;;
    --include-evaluations)
      INCLUDE_EVALUATIONS=1; shift
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

if [[ $BACKUP -eq 1 && -z "$BACKUP_DIR" ]]; then
  ts="$(date +"%Y%m%d-%H%M%S")"
  BACKUP_DIR="$TARGET_DIR/.scopes-backups/$ts"
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

backup_dir() {
  local src_dir="$1"
  if [[ $BACKUP -ne 1 || $DRY_RUN -eq 1 ]]; then
    return 0
  fi
  if [[ ! -d "$src_dir" ]]; then
    return 0
  fi

  mkdir -p "$BACKUP_DIR"
  cp -R "$src_dir" "$BACKUP_DIR/"
}

sync_dir() {
  local src_dir="$1"
  local dest_dir="$2"

  if [[ $DRY_RUN -eq 1 ]]; then
    if [[ -d "$dest_dir" ]]; then
      if [[ $BACKUP -eq 1 ]]; then
        say "Would backup: $dest_dir/ -> $BACKUP_DIR/"
      fi

      if [[ $VERBOSE -eq 1 ]]; then
        # diff exits 1 when differences exist, 0 when identical, 2 on error
        diff_out="$(diff -qr "$dest_dir" "$src_dir" 2>/dev/null || true)"
        if [[ -n "$diff_out" ]]; then
          diff_lines="$(printf '%s\n' "$diff_out" | wc -l | tr -d ' ')"
          say "Would update: $dest_dir/ (diff: ~$diff_lines item(s))"
        else
          say "Would update: $dest_dir/ (diff: none detected)"
        fi
      else
        say "Would update: $dest_dir/"
      fi
      UPDATED=$((UPDATED + 1))
    else
      say "Would add: $dest_dir/"
      ADDED=$((ADDED + 1))
    fi
    return 0
  fi

  if [[ -d "$dest_dir" ]]; then
    backup_dir "$dest_dir"
    UPDATED=$((UPDATED + 1))
  else
    ADDED=$((ADDED + 1))
  fi

  tmp_dir="$TARGET_DIR/.scopes-tmp-$(basename "$dest_dir")-$$"
  rm -rf "$tmp_dir"
  cp -R "$src_dir" "$tmp_dir"
  rm -rf "$dest_dir"
  mv "$tmp_dir" "$dest_dir"
  say "Synced: $dest_dir/"
}

# Always sync shared protocol/templates; skills depend on these.
if [[ -d "$SKILLS_ROOT/_shared" ]]; then
  FOUND=1
  sync_dir "$SKILLS_ROOT/_shared" "$TARGET_DIR/_shared"
fi

if [[ $INCLUDE_EVALUATIONS -eq 1 && -d "$SKILLS_ROOT/_evaluations" ]]; then
  FOUND=1
  sync_dir "$SKILLS_ROOT/_evaluations" "$TARGET_DIR/_evaluations"
fi

shopt -s nullglob
for skill_dir in "$SKILLS_ROOT"/*; do
  [[ -d "$skill_dir" ]] || continue
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  FOUND=1

  skill_name="$(basename "$skill_dir")"
  dest_dir="$TARGET_DIR/$skill_name"
  sync_dir "$skill_dir" "$dest_dir"
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
