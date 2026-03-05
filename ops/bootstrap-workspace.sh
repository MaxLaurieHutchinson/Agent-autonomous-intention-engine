#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${INTENTION_ENGINE_CONFIG:-$ROOT_DIR/config/runtime.json}"
export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$ROOT_DIR" "$CONFIG_PATH" <<'PY'
import json
import os
import sys
from pathlib import Path

from intention_engine_core.path_resolver import resolve_path_value

root_dir = Path(sys.argv[1]).resolve()
config_path = Path(sys.argv[2]).expanduser().resolve()

if not config_path.exists():
    raise SystemExit(f"ERROR: config not found: {config_path}")

config = json.loads(config_path.read_text(encoding="utf-8"))
paths_cfg = config.get("paths", {})


def resolve_config_path(key: str, default: str) -> Path:
    raw = str(paths_cfg.get(key, default))
    return resolve_path_value(raw, root_dir)


intent_path = resolve_config_path("intent_path", "memory/INTENT.md")
reflect_path = resolve_config_path("reflect_path", "memory/REFLECT.md")
proposals_dir = resolve_config_path("proposals_dir", "memory/proposals")
metrics_dir = resolve_config_path("metrics_dir", "memory/metrics")
briefings_dir = resolve_config_path("briefings_dir", "memory/briefings")
lock_path = resolve_config_path("lock_path", "memory/metrics/intention-engine.lock")
budget_state_path = resolve_config_path("budget_state_path", "data/intention-engine-budget.json")
replay_dir = resolve_config_path("replay_dir", "data/intention-engine-runs")
logs_path = resolve_config_path("logs_path", "logs/engine.jsonl")
philosophy_path = resolve_config_path("philosophy_path", "memory/PHILOSOPHY.md")
philosophy_fallback = resolve_config_path("philosophy_fallback_path", "philosophy/PHILOSOPHY.md")

created_paths: list[Path] = []

for directory in (
    proposals_dir,
    proposals_dir / "inbox",
    proposals_dir / "approved",
    proposals_dir / "deferred",
    proposals_dir / "rejected",
    metrics_dir,
    briefings_dir,
    lock_path.parent,
    budget_state_path.parent,
    replay_dir,
    logs_path.parent,
):
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        created_paths.append(directory)

if not intent_path.exists():
    intent_path.parent.mkdir(parents=True, exist_ok=True)
    intent_path.write_text(
        "# INTENT\n\n"
        "## NOW\n"
        "- (fill in your current high-priority intentions)\n\n"
        "## NEXT\n"
        "- (fill in upcoming intentions)\n\n"
        "## LATER\n"
        "- (optional backlog)\n",
        encoding="utf-8",
    )
    created_paths.append(intent_path)

if not reflect_path.exists():
    reflect_path.parent.mkdir(parents=True, exist_ok=True)
    reflect_path.write_text("# REFLECT\n\n", encoding="utf-8")
    created_paths.append(reflect_path)

if not philosophy_path.exists() and philosophy_fallback.exists():
    philosophy_path.parent.mkdir(parents=True, exist_ok=True)
    philosophy_path.write_text(philosophy_fallback.read_text(encoding="utf-8"), encoding="utf-8")
    created_paths.append(philosophy_path)

if created_paths:
    print("Bootstrap complete. Created:")
    for path in created_paths:
        print(f"- {path}")
else:
    print("Bootstrap complete. No changes needed.")
PY
