# Unified Architecture (v2.1)

## System Overview

```text
Sources -> Discover -> Score -> Classify Risk -> Route -> Persist Proposals
            |          |             |             |
            |          |             |             +--> approved/inbox/deferred/rejected
            |          |             +--> auto_safe/policy_guarded/human_gate
            |          +--> config thresholds + relevance
            +--> mode profile constraints (max_items, max_run_cost)

Run Artifacts -> replay bundle (inputs/scores/decisions/config-hash)
Status Layer  -> budget + queues + health + announce-failure visibility
```

## Core Runtime Files
- `scripts/intention_engine.py`
- `scripts/path_resolver.py`
- `config/runtime.json`
- `config/runtime.schema.json`

## Operational Contracts
- wrappers: `ops/ie_micro.sh`, `ops/ie_deep.sh`, `ops/ie_status.sh`
- cron orchestrator template: `cron/templates/intention-engine-orchestrator-v2.md`
- cron reconciliation helper: `agents/cron/reconcile-intention-engine-jobs.sh`

## Canonical State Files
- `memory/INTENT.md`
- `memory/REFLECT.md`
- `memory/PHILOSOPHY.md` (or fallback from `philosophy/PHILOSOPHY.md`)
- `memory/proposals/{inbox,approved,deferred,rejected}`
- `data/intention-engine-budget.json`
- `data/intention-engine-runs/<run-id>/`
- `logs/engine.jsonl`

## Determinism and Replay
Each run captures a single start timestamp and writes a replay bundle.
`replay --run-id` recomputes route outcomes from bundle data and asserts deterministic equivalence.

## Design Principles Enforced
- Radical simplicity (file-first, minimal moving parts)
- Determinism by design
- Operability first (status, logs, failure surfacing)
- Guardrails with explicit policy boundaries
