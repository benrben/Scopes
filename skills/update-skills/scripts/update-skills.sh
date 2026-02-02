#!/usr/bin/env bash
set -euo pipefail

say_err() { printf '%s\n' "$*" >&2 || true; }

usage() {
  cat <<'EOF'
update-skills.sh

Update Scopes Skills only (not commands).

This is a thin wrapper that invokes the project's updater:
  ./update-skill (preferred) or ./update-skill.sh

Usage:
  # Run from whatever skills folder you installed into:
  bash <skills-root>/update-skills/scripts/update-skills.sh

  # Override the target skills directory explicitly:
  bash <skills-root>/update-skills/scripts/update-skills.sh --target-dir .cursor/skills
  bash <skills-root>/update-skills/scripts/update-skills.sh --target-dir .claude/skills
  bash <skills-root>/update-skills/scripts/update-skills.sh --target-dir .agent/skills

Pass-through options (forwarded to update-skill.sh):
  --repo <git-url>            (default: https://github.com/benrben/Scopes.git)
  --ref <branch-or-tag>       (default: main)
  --source-subdir <path>      (default: commands)
  --dry-run
  -v, --verbose
EOF
}

TARGET_DIR=""

ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target-dir)
      TARGET_DIR="${2:-}"; shift 2
      ;;
    -h|--help)
      usage; exit 0
      ;;
    *)
      ARGS+=("$1"); shift
      ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

if [[ -z "$TARGET_DIR" ]]; then
  # Default: update the skills folder this script is installed under:
  #   <skills-root>/update-skills/scripts/update-skills.sh
  scripts_dir="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
  TARGET_DIR="$(CDPATH='' cd -- "$scripts_dir/../.." && pwd)"
fi

if [[ -x "./update-skill" ]]; then
  ./update-skill --target-dir "$TARGET_DIR" "${ARGS[@]:-}"
  exit 0
fi

if [[ -f "./update-skill.sh" ]]; then
  bash ./update-skill.sh --target-dir "$TARGET_DIR" "${ARGS[@]:-}"
  exit 0
fi

say_err "Error: update-skill updater not found in project root."
say_err "Expected one of:"
say_err "  - ./update-skill"
say_err "  - ./update-skill.sh"
say_err ""
say_err "Fix:"
say_err "  - Run ./install-scopes.sh and choose Skills (or Both), then retry."
exit 1

