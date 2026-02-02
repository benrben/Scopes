#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
sync-cursor-commands.sh

Download Cursor command prompt files from a git repo and overwrite ONLY
the command files that already exist in your project's .cursor/commands/.

Defaults:
  repo:   https://github.com/benrben/Scopes.git
  ref:    main
  target: .cursor/commands
  source: commands

Usage:
  ./sync-cursor-commands.sh
  ./sync-cursor-commands.sh --repo <git-url> --ref <branch-or-tag>
  ./sync-cursor-commands.sh --target-dir <path> --source-subdir <path>
  ./sync-cursor-commands.sh --dry-run

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
      echo "Unknown argument: $1" >&2
      echo "Run with --help for usage." >&2
      exit 2
      ;;
  esac
done

if [[ -z "$REPO_URL" || -z "$REF" || -z "$TARGET_DIR" || -z "$SOURCE_SUBDIR" ]]; then
  echo "Error: missing required configuration (repo/ref/target/source)." >&2
  echo "Run with --help for usage." >&2
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required but was not found on PATH." >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: target directory does not exist: $TARGET_DIR" >&2
  echo "Nothing to update (this script only overwrites existing files)." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

if [[ $VERBOSE -eq 1 ]]; then
  echo "Cloning $REPO_URL (ref: $REF)..." >&2
fi

if [[ $VERBOSE -eq 1 ]]; then
  git -c advice.detachedHead=false clone --depth 1 --branch "$REF" -- "$REPO_URL" "$TMP_DIR/repo"
else
  if ! git -c advice.detachedHead=false clone --depth 1 --branch "$REF" -- "$REPO_URL" "$TMP_DIR/repo" >/dev/null 2>&1; then
    echo "Error: failed to clone repo." >&2
    echo "  repo: $REPO_URL" >&2
    echo "  ref:  $REF" >&2
    exit 1
  fi
fi

SRC_ROOT="$TMP_DIR/repo/$SOURCE_SUBDIR"
if [[ ! -d "$SRC_ROOT" ]]; then
  echo "Error: source subdir not found in repo: $SOURCE_SUBDIR" >&2
  exit 1
fi

UPDATED=0
SKIPPED_NO_UPSTREAM=0

while IFS= read -r -d '' target_file; do
  rel="${target_file#"$TARGET_DIR"/}"
  src_file="$SRC_ROOT/$rel"

  if [[ -f "$src_file" ]]; then
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "Would update: $TARGET_DIR/$rel"
    else
      cp "$src_file" "$target_file"
      echo "Updated: $TARGET_DIR/$rel"
    fi
    UPDATED=$((UPDATED + 1))
  else
    SKIPPED_NO_UPSTREAM=$((SKIPPED_NO_UPSTREAM + 1))
    if [[ $VERBOSE -eq 1 ]]; then
      echo "No upstream match; skipped: $TARGET_DIR/$rel" >&2
    fi
  fi
done < <(find "$TARGET_DIR" -type f -name '*.md' -print0)

if [[ $DRY_RUN -eq 1 ]]; then
  if [[ $UPDATED -eq 0 ]]; then
    echo "Done. No matching existing command files would be updated."
  else
    echo "Done. Would update $UPDATED file(s)."
  fi
else
  if [[ $UPDATED -eq 0 ]]; then
    echo "Done. No matching existing command files were updated."
  else
    echo "Done. Updated $UPDATED file(s)."
  fi
fi

if [[ $VERBOSE -eq 1 && $SKIPPED_NO_UPSTREAM -gt 0 ]]; then
  echo "Skipped $SKIPPED_NO_UPSTREAM file(s) with no upstream match." >&2
fi
