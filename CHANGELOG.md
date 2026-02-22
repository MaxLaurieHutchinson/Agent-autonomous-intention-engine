# Changelog

## v1.0.1 - 2026-02-22
- Hardened non-blocking micro gating:
  - default fail-closed behavior when `data/last-human-activity.json` is missing
  - override available via `micro_missing_activity_signal: run`
- Added runtime timezone enforcement for day-boundary behavior (budget rollover, proposal IDs, metrics date, briefing date).
- Improved proposal recency semantics:
  - added `discovered_at` and `source_created_at` frontmatter fields
  - briefing recency filtering now prioritizes discovery timestamp
- Improved cron portability:
  - quotes executable paths
  - writes `PATH` and `CRON_TZ` in managed cron block
- Added CI smoke workflow for syntax and runtime command checks.

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
