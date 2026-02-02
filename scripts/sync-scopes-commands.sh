#!/usr/bin/env bash
set -euo pipefail

say() { printf '%s\n' "$*" || true; }
say_err() { printf '%s\n' "$*" >&2 || true; }

usage() {
  cat <<'EOF'
sync-scopes-commands.sh

Download Scopes command prompt files from a git repo and sync them into a target
commands directory (overwrite existing + add missing).

Defaults:
  repo:   https://github.com/benrben/Scopes.git
  ref:    main
  target: .cursor/commands
  source: commands

Usage:
  ./sync-scopes-commands.sh
  ./sync-scopes-commands.sh --repo <git-url> --ref <branch-or-tag>
  ./sync-scopes-commands.sh --target-dir <path> --source-subdir <path>
  ./sync-scopes-commands.sh --dry-run

Environment overrides:
  SCOPES_COMMANDS_REPO
  SCOPES_COMMANDS_REF
  SCOPES_COMMANDS_TARGET_DIR
  SCOPES_COMMANDS_SOURCE_SUBDIR
EOF
}

REPO_URL="${SCOPES_COMMANDS_REPO:-https://github.com/benrben/Scopes.git}"
REF="${SCOPES_COMMANDS_REF:-main}"
TARGET_DIR="${SCOPES_COMMANDS_TARGET_DIR:-.cursor/commands}"
SOURCE_SUBDIR="${SCOPES_COMMANDS_SOURCE_SUBDIR:-commands}"

DRY_RUN=0
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_URL="${2:-}"; shift 2
      ;;
    --ref)
      REF="${2:-}"; shift 2
      ;;
    --target-dir)
      TARGET_DIR="${2:-}"; shift 2
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
      say_err "Unknown argument: $1"
      say_err "Run with --help for usage."
      exit 2
      ;;
  esac
done

if [[ -z "$REPO_URL" || -z "$REF" || -z "$TARGET_DIR" || -z "$SOURCE_SUBDIR" ]]; then
  say_err "Error: missing required configuration (repo/ref/target/source)."
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
  # Back-compat: older script versions used ScopesCommands.git (doesn't exist).
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
  rel="${src_file#"$SRC_ROOT"/}"
  # Docs-only file (not a slash command).
  if [[ "$rel" == "README.md" ]]; then
    continue
  fi
  dest_file="$TARGET_DIR/$rel"

  mkdir -p "$(dirname "$dest_file")"

  if [[ -f "$dest_file" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      say "Would update: $dest_file"
    else
      cp "$src_file" "$dest_file"
      say "Updated: $dest_file"
    fi
    UPDATED=$((UPDATED + 1))
  else
    if [[ $DRY_RUN -eq 1 ]]; then
      say "Would add: $dest_file"
    else
      cp "$src_file" "$dest_file"
      say "Added: $dest_file"
    fi
    ADDED=$((ADDED + 1))
  fi
done < <(find "$SRC_ROOT" -type f -name '*.md' -print0)

if [[ $DRY_RUN -eq 1 ]]; then
  say "Done. Would add $ADDED file(s), would update $UPDATED file(s)."
else
  say "Done. Added $ADDED file(s), updated $UPDATED file(s)."
fi

