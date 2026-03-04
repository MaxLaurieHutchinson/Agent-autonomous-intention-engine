#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE_SCRIPT="$ROOT_DIR/scripts/intention_engine.py"
CONFIG_PATH="${INTENTION_ENGINE_CONFIG:-$ROOT_DIR/config/runtime.json}"

exec python3 "$ENGINE_SCRIPT" --config "$CONFIG_PATH" run --mode micro "$@"
