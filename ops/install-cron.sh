#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BLOCK_START="# >>> intention-engine-autoschedule >>>"
BLOCK_END="# <<< intention-engine-autoschedule <<<"

TMP=$(mktemp)
(crontab -l 2>/dev/null || true) > "$TMP"

awk -v start="$BLOCK_START" -v end="$BLOCK_END" '
BEGIN {skip=0}
$0==start {skip=1; next}
$0==end {skip=0; next}
skip==0 {print}
' "$TMP" > "${TMP}.clean"

cat >> "${TMP}.clean" <<CRON
$BLOCK_START
*/30 * * * * cd "$REPO_ROOT" && intention-engine --config config/runtime.json run --mode micro >> /tmp/intention-engine-micro.log 2>&1
30 23 * * * cd "$REPO_ROOT" && intention-engine --config config/runtime.json run --mode deep >> /tmp/intention-engine-deep.log 2>&1
55 6 * * * cd "$REPO_ROOT" && intention-engine --config config/runtime.json status --json >> /tmp/intention-engine-status.log 2>&1
$BLOCK_END
CRON

crontab "${TMP}.clean"
rm -f "$TMP" "${TMP}.clean"

echo "Installed Intention Engine cron schedule for $REPO_ROOT"
