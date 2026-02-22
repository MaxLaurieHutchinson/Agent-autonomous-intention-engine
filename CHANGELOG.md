# Changelog

## v1.0.0 - 2026-02-22
- Exported standalone, shareable repository package.
- Added portable runtime path resolution via environment variables:
  - `INTENTION_ENGINE_WORKSPACE`
  - `INTENTION_ENGINE_CONFIG`
  - `INTENTION_ENGINE_PHILOSOPHY_SOURCE`
- Added portable ops scripts under `ops/` (`init`, `micro`, `deep`, `brief`, `install-cron`).
- Sanitized workspace-specific absolute paths in active docs.
- Added MIT license and `.gitignore` for runtime state.

## Historical Notes
This repository is derived from an internal evolution sequence (`v0.x`) consolidated into this standalone release.
