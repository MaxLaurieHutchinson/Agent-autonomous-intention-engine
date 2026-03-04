# Intention Engine

Intention Engine is a deterministic, file-first autonomous decision loop for discovering work, routing risk, and producing auditable outputs.

It is designed for two realities at once:
- operator-first use in an OpenClaw workspace
- clean packaging and documentation for public reuse

## Core Contract

Canonical runtime entrypoint:

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json run --mode <micro|deep|research_deep> [--dry-run]
```

Other commands:

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json status --json
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json validate --json
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json replay --run-id <run-id>
```

Wrapper commands:

```bash
bash ops/ie_micro.sh
bash ops/ie_deep.sh
bash ops/ie_status.sh
```

## How It Works

One run follows this sequence:

1. Observe: pull candidates from configured sources.
2. Orient: extract keywords from `memory/INTENT.md` plus philosophy text and score candidates.
3. Decide: classify risk (`auto_safe`, `policy_guarded`, `human_gate`) and route (`approved`, `inbox`, `deferred`).
4. Act: persist proposals and update budget state (unless `--dry-run`).
5. Reflect: write replay bundle, metrics rollup, and a reflection entry.

## Runtime Artifacts

- proposals: `memory/proposals/{approved,inbox,deferred,rejected}`
- budget state: `data/intention-engine-budget.json`
- replay bundles: `data/intention-engine-runs/<run-id>/`
- metrics: `memory/metrics/intention-engine-YYYY-MM-DD.json`
- logs: `logs/engine.jsonl`
- reflections: `memory/REFLECT.md`

## Philosophy and Safety

`philosophy/PHILOSOPHY.md` (or configured `memory/PHILOSOPHY.md`) is actively used in scoring through keyword extraction.

Safe defaults in `config/runtime.json`:
- `allow_policy_guarded_auto = false`
- `research_deep.enabled = false`

## OpenClaw Scheduling Model

- Heartbeat (workspace-level) should trigger micro checks and interruption-aware behavior.
- Cron (isolated runs) should own fixed-time deep run and morning brief orchestration.
- `cron/` contains prompt/templates.
- `agents/cron/` contains executable job reconciliation scripts.

## Documentation

Read the full handbook at [docs/INDEX.md](docs/INDEX.md).

## Stability Status

Implemented now:
- deterministic OODA-style run loop
- risk-aware routing and guardrails
- replayability and operational health surfaces

Planned (not implemented as first-class runtime modules yet):
- explicit BDI state model
- Rubber Duck multi-agent reasoning loops
