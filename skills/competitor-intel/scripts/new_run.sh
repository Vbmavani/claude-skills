#!/usr/bin/env bash
# Start a new research run from the starter template (or the latest run with --from-latest).
# Usage: scripts/new_run.sh [YYYY-MM-DD] [--from-latest]
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATE=""
FROM_LATEST=0
for arg in "$@"; do
  case "$arg" in
    --from-latest) FROM_LATEST=1 ;;
    *)
      if [[ ! "$arg" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then echo "Expected a YYYY-MM-DD date or --from-latest, got: $arg"; exit 1; fi
      DATE="$arg" ;;
  esac
done
DATE="${DATE:-$(date +%F)}"
DEST="$SKILL_DIR/runs/$DATE"
if [ -e "$DEST" ]; then echo "Refusing to overwrite $DEST (versions are never overwritten). Pass a different date or keep working in that run."; exit 1; fi
SRC="$SKILL_DIR/templates/starter"
if [ "$FROM_LATEST" = 1 ]; then
  SRC="$(ls -d "$SKILL_DIR"/runs/20*/ 2>/dev/null | sort | tail -1 || true)"
  [ -n "$SRC" ] || { echo "No previous run in runs/"; exit 1; }
fi
mkdir -p "$DEST"
cp "$SRC"/tier_*.json "$SRC"/code_check.json "$SRC"/meta.json "$DEST"/
echo "New run at $DEST (copied from $SRC)"
echo "Next: fill the tier files (3 parallel agents), run the gap check, then:"
echo "  python3 -I $SKILL_DIR/scripts/build_table.py --inputs $DEST/tier_*.json --status $DEST/code_check.json --meta $DEST/meta.json --out $DEST/${DATE}_competitor-intel_v1.html"
