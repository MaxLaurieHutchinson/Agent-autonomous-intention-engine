# Operations Runbook

## Prerequisites

1. Install package locally:

```bash
python3 -m pip install -e .
```

2. Bootstrap workspace state:

```bash
bash ops/bootstrap-workspace.sh
```

## Validation

```bash
intention-engine --config config/runtime.json validate --json
```

Expected:
- `status: ok`
- warnings allowed for intentionally missing optional context files

## Manual Runtime Commands

### Micro dry-run smoke

```bash
intention-engine --config config/runtime.json run --mode micro --dry-run
```

### Deep run

```bash
intention-engine --config config/runtime.json run --mode deep
```

### Status snapshot

```bash
intention-engine --config config/runtime.json status --json
```

### Replay verification

```bash
intention-engine --config config/runtime.json replay --run-id <run-id>
```

## Source Diagnostics

For a recent run, inspect:
- `data/intention-engine-runs/<run-id>/inputs.json`
- `data/intention-engine-runs/<run-id>/scores.json`

Check fields:
- `source_stats`
- `dedupe_stats`
- `discovery_errors`

Use these to tune `sources[].filters` and remove low-signal feeds.

## Troubleshooting

### Validate failures
- run `validate --json` and fix listed errors first
- confirm config matches `config/runtime.schema.json`

### Replay mismatch
- if replay returns `error_code=ROUTE_MISMATCH_DETECTED`, treat as determinism regression
- inspect replay bundle (`inputs.json`, `scores.json`, `decisions.json`, `config-hash.txt`)
- compare routing thresholds, source stats, and context sources used in that run

### Source errors in health
- if `status --json` reports `DISCOVERY_SOURCE_ERRORS_PRESENT`, inspect:
  - `health.source_health.last_run_source_stats`
  - recent `discovery_error` events in `logs/engine.jsonl`
- reduce scope temporarily by disabling noisy source entries

### Announce failures
- if `status --json` reports actionable announce errors, check `~/.openclaw/cron/jobs.json`
- inspect failed job state and fix delivery configuration

## Operational Checkpoints

1. `intention-engine --config config/runtime.json validate --json` returns `ok`.
2. `intention-engine --config config/runtime.json run --mode micro --dry-run` exits `0`.
3. `intention-engine --config config/runtime.json status --json` returns parseable JSON.
4. Replay works for the latest run ID.
5. Last run has expected `source_stats` and no unexplained source error spikes.
