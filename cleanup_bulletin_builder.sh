#!/usr/bin/env bash
set -euo pipefail

# --- CONFIG / DEFAULTS ---
APPLY=0
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

KEEP_SRC_DIR="src/bulletin_builder"
REQUIRED_MARKERS=(
  "$KEEP_SRC_DIR"
  "$KEEP_SRC_DIR/__init__.py"
  "$KEEP_SRC_DIR/app_core/__init__.py"
)

# Junk & cache you almost never want in repo
GLOBS_TO_REMOVE=(
  "build" "dist"
  ".pytest_cache" ".mypy_cache" ".ruff_cache" ".coverage"
  "**/__pycache__" "**/*.pyc" "**/*.pyo" ".DS_Store"
  ".venv" "venv" "env" ".env" ".idea" ".vscode"
)

# Potential legacy duplicates at repo root (kept only if not canonical)
CANDIDATE_DUP_DIRS=(
  "app_core"
  "ui"
  "bulletin_builder"   # top-level package accidentally duplicated
)

# --- ARGS ---
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
fi

echo "== Bulletin Builder Cleanup =="
echo "Repo root: $ROOT"
echo "Mode: $([[ $APPLY -eq 1 ]] && echo APPLY || echo DRY-RUN)"
echo

# --- SAFETY CHECKS ---
missing=0
for m in "${REQUIRED_MARKERS[@]}"; do
  if [[ ! -e "$ROOT/$m" ]]; then
    echo "!! Required path missing: $m"
    missing=1
  fi
done
if [[ $missing -eq 1 ]]; then
  echo
  echo "Aborting: expected src layout not found. Make sure you're at the repo root."
  exit 1
fi

# --- BUILD DELETION LIST ---
declare -a TO_DELETE

# 1) Standard junk
while IFS= read -r -d '' p; do
  TO_DELETE+=("$p")
done < <(
  # Expand each glob safely; use find for ** patterns
  for g in "${GLOBS_TO_REMOVE[@]}"; do
    if [[ "$g" == **"**"** ]]; then
      # handle recursive globs via find
      base="${g%%/**}"
      pattern="${g#*/}" # after the first /
      find "$ROOT" -type d -name "__pycache__" -print0 2>/dev/null
      find "$ROOT" -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -print0 2>/dev/null
    else
      # non-recursive: allow both files and dirs
      [[ -e "$ROOT/$g" ]] && printf "%s\0" "$ROOT/$g"
    fi
  done | awk 'BEGIN{RS="\0"; ORS="\0"} {print}' # normalize NUL delim
)

# 2) Root-level duplicate directories (only if canonical src exists)
for d in "${CANDIDATE_DUP_DIRS[@]}"; do
  if [[ -d "$ROOT/$d" ]]; then
    # If it's literally the src tree, skip
    [[ "$d" == "$KEEP_SRC_DIR" ]] && continue

    # Only delete if the canonical src/bulletin_builder exists
    if [[ -d "$ROOT/$KEEP_SRC_DIR" ]]; then
      # Extra safety: don't delete if it *is* the canonical package root
      if [[ "$d" == "bulletin_builder" && -d "$ROOT/src/bulletin_builder" ]]; then
        # If both exist, the top-level is almost certainly a stale duplicate
        TO_DELETE+=("$ROOT/$d")
      elif [[ "$d" != "bulletin_builder" ]]; then
        # app_core/ or ui/ at repo root are duplicates if we have src/bulletin_builder/app_core or /ui
        if [[ -d "$ROOT/src/bulletin_builder/$d" ]]; then
          TO_DELETE+=("$ROOT/$d")
        fi
      fi
    fi
  fi
done

# 3) De-dup & confirm paths
# remove non-existent, then unique
declare -A seen
declare -a FINAL
for p in "${TO_DELETE[@]:-}"; do
  [[ -e "$p" ]] || continue
  [[ -n "${seen[$p]:-}" ]] && continue
  seen[$p]=1
  FINAL+=("$p")
done

# --- REPORT ---
if [[ ${#FINAL[@]} -eq 0 ]]; then
  echo "Nothing to delete. Your tree looks tidy. 👍"
  exit 0
fi

echo "Will remove the following paths:"
for p in "${FINAL[@]}"; do
  echo "  - ${p#$ROOT/}"
done
echo

if [[ $APPLY -eq 0 ]]; then
  echo "(dry-run) Not deleting anything."
  echo "Run:  bash $(basename "$0") --apply   to actually delete."
  exit 0
fi

# --- APPLY ---
echo "Deleting..."
for p in "${FINAL[@]}"; do
  if [[ -d "$p" ]]; then
    rm -rf -- "$p"
  else
    rm -f -- "$p"
  fi
done
echo "✅ Done."
