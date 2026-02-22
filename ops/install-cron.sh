#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_PATH="$REPO_ROOT/config/runtime.json"

BLOCK_START="# >>> intention-engine-autoschedule >>>"
BLOCK_END="# <<< intention-engine-autoschedule <<<"

TZ_NAME="$(python3 - "$CONFIG_PATH" <<'PY'
import json
import pathlib
import sys

cfg_path = pathlib.Path(sys.argv[1])
try:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    tz = str(cfg.get("timezone", "UTC")).strip() or "UTC"
except Exception:
    tz = "UTC"
print(tz)
PY
)"

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
PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
CRON_TZ=$TZ_NAME
*/30 * * * * "$REPO_ROOT/ops/micro.sh" >> /tmp/intention-engine-micro.log 2>&1
30 23 * * * "$REPO_ROOT/ops/deep.sh" >> /tmp/intention-engine-deep.log 2>&1
55 6 * * * "$REPO_ROOT/ops/brief.sh" >> /tmp/intention-engine-brief.log 2>&1
$BLOCK_END
CRON

crontab "${TMP}.clean"
rm -f "$TMP" "${TMP}.clean"

echo "Installed Intention Engine cron schedule for $REPO_ROOT"
