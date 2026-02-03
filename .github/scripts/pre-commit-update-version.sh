#!/usr/bin/env bash
set -euo pipefail

# Pre-commit hook script to refresh Products/zms/version.txt
# Format: <latest-tag>-<shortsha7>

REPO_ROOT=$(git rev-parse --show-toplevel)
VERSION_FILE="$REPO_ROOT/Products/zms/version.txt"

mkdir -p "$(dirname "$VERSION_FILE")"

if TAG=$(git describe --tags --abbrev=0 2>/dev/null); then
  :
else
  TAG="0.0.0"
fi

if SHORT_SHA=$(git rev-parse --short=7 HEAD 2>/dev/null); then
  :
else
  SHORT_SHA="0000000"
fi

# Convert tag to version string
# - If TAG is in form YYYY-MM, convert to YYYY.M.1 and append +<shortsha>
# - Otherwise, keep original tag and append +<shortsha> for PEP 440 compliance
if [[ "$TAG" =~ ^([0-9]{4})-([0-9]{2})$ ]]; then
  YEAR="${BASH_REMATCH[1]}"
  MONTH="${BASH_REMATCH[2]}"
  # strip leading zero from month (e.g., 09 -> 9)
  MONTH_NO_LEAD="${MONTH#0}"
  VERSION_CORE="${YEAR}.${MONTH_NO_LEAD}.1"
else
  VERSION_CORE="$TAG"
fi

NEW_VERSION="${VERSION_CORE}+${SHORT_SHA}"

# Allow manual run with --force to bypass staged-file check
FORCE=${1:-}
STAGED_NON_VERSION=$(git diff --cached --name-only | grep -v '^Products/zms/version.txt$' || true)
if [[ -z "$STAGED_NON_VERSION" && "$FORCE" != "--force" ]]; then
  exit 0
fi

CURRENT_CONTENT=""
if [[ -f "$VERSION_FILE" ]]; then
  CURRENT_CONTENT=$(cat "$VERSION_FILE" || true)
fi

if [[ "$CURRENT_CONTENT" != "$NEW_VERSION" ]]; then
  echo "$NEW_VERSION" > "$VERSION_FILE"
  git add "$VERSION_FILE"
  echo "pre-commit: updated Products/zms/version.txt to $NEW_VERSION"
fi

exit 0
