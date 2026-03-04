#!/usr/bin/env python3
"""Compatibility shim for legacy script entrypoints.

Preferred entrypoint:
  python3 -m intention_engine_core.cli
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from intention_engine_core.runtime import *  # noqa: F401,F403


if __name__ == "__main__":
    raise SystemExit(main())
