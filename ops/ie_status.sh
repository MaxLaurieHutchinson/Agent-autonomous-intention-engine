#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_PATH="${INTENTION_ENGINE_CONFIG:-$ROOT_DIR/config/runtime.json}"
export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

exec python3 -m intention_engine_core.cli --config "$CONFIG_PATH" status --json "$@"
