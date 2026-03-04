# Implementation Status (v2.1)

## Delivered in DEV

### Runtime Engine
- `scripts/intention_engine.py`
  - `run --mode micro|deep|research_deep [--dry-run]`
  - `status [--json]`
  - `validate [--json]`
  - `replay --run-id <id>`
  - legacy `--mode` shim retained

### Config and Path Contract
- `config/runtime.json`
  - mode profiles + safe routing defaults
  - config-driven paths (no hardcoded machine path)
- `config/runtime.schema.json`
  - schema-backed config checks

### Determinism and Operability
- replay bundles per run in `data/intention-engine-runs/<run-id>/`
- structured logs in `logs/engine.jsonl`
- status health includes announce-delivery failures

### Operational Surfaces
- wrappers:
  - `ops/ie_micro.sh`
  - `ops/ie_deep.sh`
  - `ops/ie_status.sh`
- cron alignment:
  - `cron/templates/intention-engine-orchestrator-v2.md`
  - `agents/cron/reconcile-intention-engine-jobs.sh`

### Quality Gates
- tests:
  - `tests/test_path_resolution.py`
  - `tests/test_routing_and_guardrails.py`
  - `tests/test_cli_integration.py`
- CI workflow in `.github/workflows/ci.yml`

## Open / Deferred
- `research_deep` orchestration remains intentionally deferred (`enabled=false`).
- multi-agent academic long-loop execution not implemented in this phase.

## Exit Criteria for Merge
- all tests pass locally and in CI
- `validate --json` status `ok`
- wrappers execute from repo root
- no generated runtime artifacts committed
