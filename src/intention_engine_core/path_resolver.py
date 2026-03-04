#!/usr/bin/env python3
"""Helpers for resolving runtime paths from config values."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def resolve_config_path(raw_config_path: Optional[str], default_path: Path, cwd: Optional[Path] = None) -> Path:
    """Resolve the CLI config path.

    Relative values are resolved from the current working directory so CLI usage
    behaves like other command line tools.
    """

    base_cwd = cwd or Path.cwd()
    candidate = raw_config_path or str(default_path)
    expanded = Path(os.path.expanduser(candidate))
    if expanded.is_absolute():
        return expanded
    return (base_cwd / expanded).resolve()


def resolve_path_value(raw_value: str, workspace_root: Path) -> Path:
    """Resolve config path values used by the runtime contract.

    Rules:
    - absolute paths are used as-is
    - `~` is expanded to the current user's home directory
    - relative paths are anchored to the workspace root
    """

    expanded = Path(os.path.expanduser(str(raw_value)))
    if expanded.is_absolute():
        return expanded
    return (workspace_root / expanded).resolve()
