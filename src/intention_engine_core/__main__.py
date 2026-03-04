"""Module execution entrypoint (`python -m intention_engine_core`)."""

from __future__ import annotations

from .runtime import main


if __name__ == "__main__":
    raise SystemExit(main())
