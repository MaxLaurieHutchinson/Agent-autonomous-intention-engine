#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
JOBS_PATH="${OPENCLAW_CRON_JOBS_PATH:-$HOME/.openclaw/cron/jobs.json}"

if [[ ! -f "$JOBS_PATH" ]]; then
  echo "ERROR: jobs file not found: $JOBS_PATH" >&2
  exit 1
fi

BACKUP_PATH="${JOBS_PATH}.bak.$(date +%Y%m%dT%H%M%S)"
cp "$JOBS_PATH" "$BACKUP_PATH"

UPDATED_COUNT=$(python3 - "$JOBS_PATH" "$ROOT_DIR" <<'PY'
import json
import sys
from pathlib import Path

jobs_path = Path(sys.argv[1])
root_dir = Path(sys.argv[2]).resolve()

data = json.loads(jobs_path.read_text(encoding="utf-8"))
jobs = data.get("jobs", [])

updated = 0

for job in jobs:
    if not isinstance(job, dict):
        continue
    payload = job.get("payload")
    if not isinstance(payload, dict):
        continue

    name = str(job.get("name", ""))

    if name == "IE Deep Run (Orchestrated)":
        payload["message"] = (
            f"Run the Intention Engine deep loop from workspace root using canonical wrappers. "
            f"Execute `bash {root_dir}/ops/ie_deep.sh`. If it fails, retry once after 30 seconds. "
            f"Then run `bash {root_dir}/ops/ie_status.sh` and announce a concise summary including proposals_created, route breakdown, remaining budget, and any health issues."
        )
        updated += 1

    if name == "IE Brief Generation (Orchestrated)":
        payload["message"] = (
            f"Generate the IE morning brief from live runtime state. Execute `bash {root_dir}/ops/ie_status.sh` and parse the JSON. "
            f"Review `{root_dir}/memory/INTENT.md` and `{root_dir}/memory/proposals/inbox/` for active work. "
            f"Summarize budget, queue counts, last run, health issues, and items needing attention."
        )
        updated += 1

jobs_path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
print(updated)
PY
)

echo "Reconciled jobs file: $JOBS_PATH"
echo "Backup: $BACKUP_PATH"
echo "Intention Engine jobs updated: $UPDATED_COUNT"
