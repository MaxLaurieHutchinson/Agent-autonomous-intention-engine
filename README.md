# Intention Engine Unified

Single deployable Intention Engine with deterministic runtime, safe guardrails, and operational wrappers for heartbeat/cron alignment.

## Mission
Build one autonomous system that:
- discovers useful work continuously
- routes decisions safely (`auto_safe`, `policy_guarded`, `human_gate`)
- keeps human-readable memory first (Markdown files)
- remains replayable and debuggable by design

## Constitutional Source
- `philosophy/PHILOSOPHY.md`

This philosophy file is the decision filter for discovery, routing, and execution.

## Canonical Runtime Name
- `Intention Engine` (canonical)

Legacy names (`DayDream`, `Ash Time`) remain historical references, not product names.

## v2.1 Runtime Contract
Preferred package entrypoint:
- `PYTHONPATH=./src python3 -m intention_engine_core.cli run --mode <micro|deep|research_deep> [--dry-run]`
- `PYTHONPATH=./src python3 -m intention_engine_core.cli status --json`
- `PYTHONPATH=./src python3 -m intention_engine_core.cli validate --json`
- `PYTHONPATH=./src python3 -m intention_engine_core.cli replay --run-id <id>`

Wrappers:
- `bash ops/ie_micro.sh`
- `bash ops/ie_deep.sh`
- `bash ops/ie_status.sh`

## What This Pack Contains
- `docs/01-PROJECT-AUDIT.md` - retained value + consolidation decisions
- `docs/02-UNIFIED-ARCHITECTURE.md` - end-to-end v2.1 architecture
- `docs/03-AUTONOMY-OPERATING-MODEL.md` - safety model + policy defaults
- `docs/04-MIGRATION-PLAN.md` - main -> dev migration plan
- `docs/05-IMPLEMENTATION-BACKLOG.md` - backlog by saga/chapter
- `docs/06-ASH-TIME-V3-NORMALIZATION.md` - what was retained/simplified
- `docs/07-CLAW-TIME-V04-IDEA-TRIAGE.md` - idea triage decisions
- `docs/08-BUILD-RUNBOOK.md` - build/run/reconcile operations
- `docs/09-IMPLEMENTATION-STATUS.md` - shipped scope and gaps
- `docs/10-ASH-OPERATOR-PROMPT.md` - operator prompt for autonomous runs

## Quick Start
1. Validate config:
   - `PYTHONPATH=./src python3 -m intention_engine_core.cli validate --json`
2. Dry-run micro loop:
   - `bash ops/ie_micro.sh --dry-run`
3. Status check:
   - `bash ops/ie_status.sh`
4. Run tests:
   - `python3 -m unittest discover -s tests -v`

## Runtime Artifacts
- replay bundles: `data/intention-engine-runs/<run-id>/`
- logs: `logs/engine.jsonl`
- budget state: `data/intention-engine-budget.json`
- proposal queues: `memory/proposals/{inbox,approved,deferred,rejected}`

## Safe Defaults
- `allow_policy_guarded_auto=false`
- `research_deep` profile present but disabled
- path contract fully config-driven (no machine-specific hardcoded paths)
