# Changelog

## v2.3.0 - 2026-03-05 (dev)
- Refactored discovery into pluggable source adapters under `src/intention_engine_core/sources/`.
- Added non-auth source types:
  - `rss`
  - `arxiv`
- Kept existing adapters:
  - `reddit`
  - `hackernews`
  - `github`
  - `fixture`
- Expanded source config contract with typed entries and common fields:
  - `id`, `name`, `type`, `enabled`, `limit`, `timeout_s`, `filters`
- Added per-source deterministic filters:
  - `min_engagement`, `max_age_hours`, `include_keywords`, `exclude_keywords`, `domain_allowlist`, `domain_blocklist`
- Added deterministic canonical URL + title-fingerprint dedupe in discovery pipeline.
- Added source provenance into replay artifacts:
  - `source_stats`, `dedupe_stats`, candidate canonical metadata
- Expanded status health with source error surfaces (`DISCOVERY_SOURCE_ERRORS_PRESENT`).
- Added curated RSS seed set:
  - `config/sources/rss_seed_curated.json`
- Added new docs:
  - `docs/architecture/source-adapters.md`
  - `docs/operations/source-onboarding.md`
- Added source-focused tests and CI compile coverage for the new adapter package.

## v2.2.0 - 2026-03-05 (dev)
- Locked canonical runtime contract to installable CLI only:
  - added `project.scripts` entrypoint `intention-engine`
  - removed operational wrappers `ops/ie_micro.sh`, `ops/ie_deep.sh`, `ops/ie_status.sh`
- Updated active docs/cron/tests/CI to canonical CLI commands only.
- Added CI enforcement for no wrapper references in active contract surfaces.
- Config/runtime hygiene:
  - removed deprecated fields from default config (`idle_threshold_minutes`, `intake`, `external_action_keywords`)
  - runtime validation now rejects deprecated fields explicitly
  - added `context_sources` config with weighted deterministic context ingestion
- Cognitive integration:
  - `extract_keywords` now consumes ordered/weighted context sources with deterministic glob expansion
  - replay artifacts persist context source metadata
- Operability hardening:
  - status now emits failure taxonomy and actionable errors
  - replay now emits explicit error codes and mismatch actionability
- Added governance docs:
  - `docs/governance/engineering-governance.md`
  - `docs/governance/experiment-protocol.md`

## v2.1.4 - 2026-03-05 (dev)
- Hardened CI for release-readiness:
  - added `ops/bootstrap-workspace.sh` execution in CI to initialize expected runtime files and directories
  - added editable package install smoke (`pip install -e .` + import check)
- Kept runtime behavior unchanged; this update only strengthens build validation gates.

## v2.1.3 - 2026-03-05 (dev)
- Added `ops/bootstrap-workspace.sh` to initialize required workspace state for fresh clones:
  - creates configured intent/reflect files when missing
  - creates proposal queue directories and runtime artifact directories
  - seeds `memory/PHILOSOPHY.md` from fallback philosophy file when absent
- Updated setup documentation to run bootstrap before validation:
  - `README.md`
  - `docs/operations/runbook.md`
  - `docs/reference/faq.md`

## v2.1.2 - 2026-03-04 (dev)
- Replaced the prior numbered docs pack as the primary contract with a new topic-based handbook under `docs/`.
- Rewrote root `README.md` as a product and operations entrypoint.
- Added deep architecture/runtime/config/operations/reference/roadmap docs:
  - `docs/INDEX.md`
  - `docs/architecture/*`
  - `docs/runtime/*`
  - `docs/config/*`
  - `docs/operations/*`
  - `docs/reference/*`
  - `docs/roadmap/*`
- Archived previous numbered docs into `docs/archive/v2.1-notes/` with an archive index.
- Clarified framework status boundaries:
  - OODA implemented
  - BDI planned
  - Rubber Duck planned
- Clarified OpenClaw scheduling boundaries:
  - heartbeat behavior at workspace level
  - fixed-time deep/brief orchestration in cron isolated jobs

## v2.1.1 - 2026-03-04 (dev)
- Removed backward-compatibility command surfaces from `dev`:
  - deleted `scripts/intention_engine.py` and `scripts/path_resolver.py`
  - deleted `ops/init.sh`, `ops/brief.sh`, `ops/micro.sh`, `ops/deep.sh`
- Enforced strict subcommand CLI parsing (`run`, `status`, `validate`, `replay`) with no legacy top-level `--mode` shim.
- Updated cron installer to canonical wrappers only:
  - `ops/ie_micro.sh`, `ops/ie_deep.sh`, `ops/ie_status.sh`
- Updated tests and CI to use `python -m intention_engine_core.cli` and `ops/ie_*` wrappers only.
- Updated docs to reflect the clean `src` + `docs` runtime contract.

## v2.1.0 - 2026-03-03
- Reworked runtime CLI to subcommands:
  - `run`, `status`, `validate`, `replay`
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
