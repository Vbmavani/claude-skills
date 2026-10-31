#!/usr/bin/env bash
# Start a new research run from the starter template (or the latest run with --from-latest).
# Usage: scripts/new_run.sh [YYYY-MM-DD] [--from-latest]
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATE="${1:-$(TZ=Asia/Kolkata date +%F)}"
DEST="$SKILL_DIR/runs/$DATE"
if [ -e "$DEST" ]; then echo "Refusing to overwrite $DEST (versions are never overwritten)"; exit 1; fi
SRC="$SKILL_DIR/templates/starter"
if [ "${2:-}" = "--from-latest" ]; then
  SRC="$(ls -d "$SKILL_DIR"/runs/20*/ 2>/dev/null | sort | tail -1)"; [ -n "$SRC" ] || { echo "No previous run in runs/"; exit 1; }
fi
mkdir -p "$DEST"
cp "$SRC"/tier_*.json "$SRC"/code_check.json "$SRC"/meta.json "$DEST"/
echo "New run at $DEST (copied from $SRC)"
echo "Next: fill the tier files (3 parallel agents), code-check gaps, then:"
echo "  python3 -I $SKILL_DIR/scripts/build_table.py --inputs $DEST/tier_*.json --status $DEST/code_check.json --meta $DEST/meta.json --out $DEST/${DATE}_competitor-intel_v1.html"
