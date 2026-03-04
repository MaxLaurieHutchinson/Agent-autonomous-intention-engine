# Changelog

## v2.1.0 - 2026-03-03
- Reworked runtime CLI to subcommands with compatibility shim:
  - `run`, `status`, `validate`, `replay`
  - legacy `--mode` invocation still supported
- Added config-driven mode registry:
  - `micro` enabled
  - `deep` enabled
  - `research_deep` present and disabled
- Added `config/runtime.schema.json` and stricter config validation checks.
- Removed hardcoded machine paths from runtime core; path resolution now uses config + `~`/relative normalization.
- Hardened routing/guardrails:
  - `allow_policy_guarded_auto=false` default
  - human-gate keyword path enforced
- Added deterministic replay bundles per run:
  - `inputs.json`, `scores.json`, `decisions.json`, `config-hash.txt`
- Added structured runtime logging to `logs/engine.jsonl`.
- Added canonical wrappers:
  - `ops/ie_micro.sh`, `ops/ie_deep.sh`, `ops/ie_status.sh`
- Added cron alignment assets:
  - `cron/templates/intention-engine-orchestrator-v2.md`
  - `agents/cron/reconcile-intention-engine-jobs.sh`
- Added test suite for path resolution, routing, CLI contract, replay determinism, and wrapper execution.
- Added CI workflow for compile + tests + smoke commands.

## v1.0.0 - 2026-02-22
- Exported standalone, shareable repository package.
- Added portable runtime path resolution via environment variables.
- Added initial ops scripts and standalone docs pack.
- Sanitized workspace-specific absolute paths in active docs.
- Added MIT license and baseline `.gitignore`.
