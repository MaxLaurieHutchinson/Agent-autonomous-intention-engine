# State and Artifacts

Intention Engine is file-first. This document describes what files exist, who writes them, and why.

## State Categories

| Category | Path | Purpose |
|---|---|---|
| Intent | `memory/INTENT.md` | active focus and priorities used in keyword extraction |
| Reflection | `memory/REFLECT.md` | run-level reflection log appended by runtime |
| Philosophy | `memory/PHILOSOPHY.md` or `philosophy/PHILOSOPHY.md` | constitutional guidance used in scoring context |
| Proposal Queues | `memory/proposals/*` | routed decision artifacts |
| Daily Metrics | `memory/metrics/intention-engine-YYYY-MM-DD.json` | run summaries and rollups |
| Budget | `data/intention-engine-budget.json` | daily budget state and run ledger |
| Replay | `data/intention-engine-runs/<run-id>/` | deterministic replay artifacts |
| Logs | `logs/engine.jsonl` | structured operational events |
| Lock | configured `lock_path` | single-writer safety for concurrent run protection |

## Runtime-Owned Writes

On non-dry run:
- proposal markdown files in route destination queue
- budget ledger update
- daily metrics file update
- reflection append entry
- replay bundle files
- engine log events

On dry run:
- replay bundle and logs still written
- no budget/proposal/metrics/reflect mutations

## Proposal Queue Layout

- `memory/proposals/approved/`
- `memory/proposals/inbox/`
- `memory/proposals/deferred/`
- `memory/proposals/rejected/`

Runtime uses deterministic IDs:
`P-YYYY-MM-DD-NNN-<slug>.md`

## Metrics File Shape

Daily file contains:
- `date`
- `runs[]` (full run summaries)
- `total_runs`
- `total_proposals`

Run summary fields include:
- `timestamp`, `run_id`, `mode`, `status`
- `candidates_discovered`, `proposals_created`
- `approved`, `deferred`, `awaiting_human_gate`
- `network_errors`, `run_cost_gbp`, `budget_remaining_gbp`
- `replay_bundle`

## Replay Bundle Shape

For each run:
- `inputs.json`: source candidate inputs, mode profile, discovery errors
- `scores.json`: keyword set and full scored candidate list
- `decisions.json`: route decisions and routing config used
- `config-hash.txt`: SHA-256 hash of config payload

## Logging Contract

`logs/engine.jsonl` events include:
- `run_complete`
- `discovery_error`
- `announce_delivery_failure`
- `unhandled_exception`

Each log line is JSON with:
- `timestamp`, `level`, `event`, `message`
- optional `extra` payload

## Path Resolution Rules

All runtime paths are config-driven and resolved as:
- absolute paths: used as-is
- paths with `~`: expanded to home
- relative paths: anchored to workspace root

## Operational Implications

- Artifacts are diff-friendly and inspectable without special tooling.
- Replay artifacts allow deterministic validation of routing outcomes.
- Queue directories are the primary integration points for downstream agents.
