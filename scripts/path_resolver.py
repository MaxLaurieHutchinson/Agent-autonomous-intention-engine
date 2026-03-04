#!/usr/bin/env python3
"""Compatibility shim for legacy path_resolver imports.

Preferred import:
  from intention_engine_core.path_resolver import ...
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from intention_engine_core.path_resolver import *  # noqa: F401,F403
