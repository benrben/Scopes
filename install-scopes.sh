#!/usr/bin/env bash
set -euo pipefail

say() { printf '%s\n' "$*" || true; }
say_err() { printf '%s\n' "$*" >&2 || true; }

usage() {
  cat <<'EOF'
install-scopes.sh

Interactive installer for Scopes workflows.

- Lets the user install Commands and/or Skills.
- Supports multiple IDE targets (multi-select).
- Copies only the commands updater under ./scripts/ for later refresh:
  - ./scripts/sync-scopes-commands.sh (refresh commands)
  - Skills refresh: use the bundled update-skills skill (e.g. .cursor/skills/update-skills/scripts/update-skills.sh)

Defaults:
  repo: https://github.com/benrben/ScopesCommands.git
  ref:  main

Usage:
  ./install-scopes.sh
  ./install-scopes.sh --repo <git-url> --ref <branch-or-tag>
  ./install-scopes.sh --dry-run

Environment overrides:
  SCOPES_COMMANDS_REPO
  SCOPES_COMMANDS_REF
EOF
}

REPO_URL="${SCOPES_COMMANDS_REPO:-https://github.com/benrben/ScopesCommands.git}"
REF="${SCOPES_COMMANDS_REF:-main}"

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

if [[ -z "$REPO_URL" || -z "$REF" ]]; then
  say_err "Error: missing required configuration (repo/ref)."
  say_err "Run with --help for usage."
  exit 2
fi

if ! command -v git >/dev/null 2>&1; then
  say_err "Error: git is required but was not found on PATH."
  exit 1
fi

prompt_one() {
  local prompt="$1"
  local default="${2:-}"
  local ans=""
  if [[ -n "$default" ]]; then
    printf "%s [%s]: " "$prompt" "$default" >&2
  else
    printf "%s: " "$prompt" >&2
  fi
  IFS= read -r ans || true
  if [[ -z "$ans" ]]; then
    ans="$default"
  fi
  printf "%s" "$ans"
}

choose_mode() {
  say_err ""
  say_err "Install what?"
  say_err "  1) Commands"
  say_err "  2) Skills"
  say_err "  3) Both"
  local ans
  ans="$(prompt_one "Choose 1/2/3" "3")"
  case "$ans" in
    1) echo "commands" ;;
    2) echo "skills" ;;
    3) echo "both" ;;
    *) say_err "Invalid choice: $ans"; exit 2 ;;
  esac
}

choose_targets() {
  local kind="$1"
  say_err ""
  if [[ "$kind" == "commands" ]]; then
    say_err "Install commands into which IDE folders? (space-separated numbers)"
    say_err "  1) Cursor: .cursor/commands"
    say_err "  2) Claude: .claude/commands"
    say_err "  3) All (Cursor + Claude)"
    local ans
    ans="$(prompt_one "Selection" "1")"
    printf "%s" "$ans"
    return
  fi

  say_err "Install skills into which IDE folders? (space-separated numbers)"
  say_err "  1) Cursor: .cursor/skills"
  say_err "  2) Claude: .claude/skills"
  say_err "  3) Antigravity: .agent/skills"
  say_err "  4) All (Cursor + Claude + Antigravity)"
  local ans
  ans="$(prompt_one "Selection" "1")"
  printf "%s" "$ans"
}

targets_to_paths() {
  local kind="$1"; shift
  local out=""
  for tok in "$@"; do
    case "$kind:$tok" in
      commands:1) out="$out .cursor/commands" ;;
      commands:2) out="$out .claude/commands" ;;
      commands:3) out="$out .cursor/commands .claude/commands" ;;
      skills:1) out="$out .cursor/skills" ;;
      skills:2) out="$out .claude/skills" ;;
      skills:3) out="$out .agent/skills" ;;
      skills:4) out="$out .cursor/skills .claude/skills .agent/skills" ;;
      *) ;;
    esac
  done
  printf "%s" "$out"
}

validate_tokens() {
  local kind="$1"; shift
  local tok
  for tok in "$@"; do
    case "$kind:$tok" in
      commands:1|commands:2|commands:3) ;;
      skills:1|skills:2|skills:3|skills:4) ;;
      *) say_err "Invalid selection for $kind: $tok"; return 1 ;;
    esac
  done
  return 0
}

ensure_updaters_present() {
  local need_commands="${1:-0}"
  local need_skills="${2:-0}"
  local repo_url="${3:-$REPO_URL}"
  local ref="${4:-$REF}"
  local skill_targets="${5:-}"
  # Subshell so cleanup trap doesn't leak into caller.
  (
    tmp_dir="$(mktemp -d)"
    trap 'rm -rf "$tmp_dir"' EXIT

    if [[ $VERBOSE -eq 1 ]]; then
      say_err "Fetching from $repo_url (ref: $ref)..."
      git -c advice.detachedHead=false clone --depth 1 --branch "$ref" -- "$repo_url" "$tmp_dir/repo"
    else
      git -c advice.detachedHead=false clone --depth 1 --branch "$ref" -- "$repo_url" "$tmp_dir/repo" >/dev/null 2>&1
    fi

    scripts_root="./scripts"

    if [[ $DRY_RUN -eq 1 ]]; then
      if [[ "$need_commands" == "1" ]]; then
        say "Would write: $scripts_root/sync-scopes-commands.sh"
      fi
      if [[ "$need_skills" == "1" && -n "$skill_targets" ]]; then
        for d in $skill_targets; do
          say "Would run: update-skill.sh from clone --target-dir $d"
        done
      fi
      exit 0
    fi

    mkdir -p "$scripts_root"

    if [[ "$need_commands" == "1" ]]; then
      src_sync="$tmp_dir/repo/scripts/sync-scopes-commands.sh"
      if [[ ! -f "$src_sync" ]]; then
        src_sync="$tmp_dir/repo/scripts/sync-cursor-commands.sh"
      fi
      if [[ ! -f "$src_sync" ]]; then
        src_sync="$tmp_dir/repo/sync-cursor-commands.sh"
      fi
      if [[ ! -f "$src_sync" ]]; then
        say_err ""
        say_err "Error: selected Commands, but the repo/ref you are installing from does not include sync-scopes-commands.sh."
        say_err "  repo: $repo_url"
        say_err "  ref:  $ref"
        say_err ""
        say_err "Expected one of: scripts/sync-scopes-commands.sh, scripts/sync-cursor-commands.sh, sync-cursor-commands.sh"
        exit 1
      fi

      cp "$src_sync" "$scripts_root/sync-scopes-commands.sh"
      chmod +x "$scripts_root/sync-scopes-commands.sh"
    fi

    if [[ "$need_skills" == "1" && -n "$skill_targets" ]]; then
      src_update_skill_sh="$tmp_dir/repo/scripts/update-skill.sh"
      if [[ ! -f "$src_update_skill_sh" ]]; then
        src_update_skill_sh="$tmp_dir/repo/update-skill.sh"
      fi
      if [[ ! -f "$src_update_skill_sh" ]]; then
        say_err ""
        say_err "Error: selected Skills, but the repo/ref you are installing from does not include update-skill.sh."
        say_err "  repo: $repo_url"
        say_err "  ref:  $ref"
        say_err ""
        say_err "Fix: Use a repo that has scripts/update-skill.sh (e.g. ScopesCommands)."
        say_err "  Example: ./install-scopes.sh --repo https://github.com/benrben/ScopesCommands.git --ref main"
        say_err "  Or local: ./install-scopes.sh --repo /path/to/ScopesCommands --ref main"
        exit 1
      fi
      for d in $skill_targets; do
        bash "$src_update_skill_sh" --repo "$repo_url" --ref "$ref" --target-dir "$d"
      done
    fi
  )
}

MODE="$(choose_mode)"

CMD_SELECTION=""
SKILL_SELECTION=""

case "$MODE" in
  commands)
    CMD_SELECTION="$(choose_targets commands)"
    ;;
  skills)
    SKILL_SELECTION="$(choose_targets skills)"
    ;;
  both)
    CMD_SELECTION="$(choose_targets commands)"
    SKILL_SELECTION="$(choose_targets skills)"
    ;;
esac

# Normalize selection tokens (split on spaces/commas).
CMD_TOKENS=()
if [[ -n "$CMD_SELECTION" ]]; then
  CMD_SELECTION="${CMD_SELECTION//,/ }"
  for t in $CMD_SELECTION; do CMD_TOKENS+=("$t"); done
fi

SKILL_TOKENS=()
if [[ -n "$SKILL_SELECTION" ]]; then
  SKILL_SELECTION="${SKILL_SELECTION//,/ }"
  for t in $SKILL_SELECTION; do SKILL_TOKENS+=("$t"); done
fi

if [[ ${#CMD_TOKENS[@]} -gt 0 ]]; then
  validate_tokens commands "${CMD_TOKENS[@]}" || exit 2
fi
if [[ ${#SKILL_TOKENS[@]} -gt 0 ]]; then
  validate_tokens skills "${SKILL_TOKENS[@]}" || exit 2
fi

CMD_TARGETS="$(targets_to_paths commands "${CMD_TOKENS[@]:-}")"
SKILL_TARGETS="$(targets_to_paths skills "${SKILL_TOKENS[@]:-}")"

say_err ""
say_err "Summary:"
say_err "  repo: $REPO_URL"
say_err "  ref:  $REF"
if [[ -n "$CMD_TARGETS" ]]; then
  say_err "  commands ->$CMD_TARGETS"
fi
if [[ -n "$SKILL_TARGETS" ]]; then
  say_err "  skills   ->$SKILL_TARGETS"
fi

NEED_COMMANDS=0
NEED_SKILLS=0
if [[ -n "$CMD_TARGETS" ]]; then NEED_COMMANDS=1; fi
if [[ -n "$SKILL_TARGETS" ]]; then NEED_SKILLS=1; fi

ensure_updaters_present "$NEED_COMMANDS" "$NEED_SKILLS" "$REPO_URL" "$REF" "$SKILL_TARGETS"

if [[ -n "$CMD_TARGETS" ]]; then
  for d in $CMD_TARGETS; do
    if [[ $DRY_RUN -eq 1 ]]; then
      say "Would run: bash ./scripts/sync-scopes-commands.sh --repo \"$REPO_URL\" --ref \"$REF\" --target-dir \"$d\""
    else
      bash ./scripts/sync-scopes-commands.sh --repo "$REPO_URL" --ref "$REF" --target-dir "$d"
    fi
  done
fi

say "Done."

