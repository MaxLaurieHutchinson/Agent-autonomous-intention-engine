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

## Troubleshooting

### Validate failures
- run `validate --json` and fix listed errors first
- confirm config matches `config/runtime.schema.json`

### Replay mismatch
- if replay returns `error_code=ROUTE_MISMATCH_DETECTED`, treat as determinism regression
- inspect replay bundle (`inputs.json`, `scores.json`, `decisions.json`, `config-hash.txt`)
- compare routing thresholds and context sources used in that run

### Announce failures
- if `status --json` reports actionable announce errors, check `~/.openclaw/cron/jobs.json`
- inspect failed job state and fix delivery configuration

## Operational Checkpoints

1. `intention-engine --config config/runtime.json validate --json` returns `ok`.
2. `intention-engine --config config/runtime.json run --mode micro --dry-run` exits `0`.
3. `intention-engine --config config/runtime.json status --json` returns parseable JSON.
4. Replay works for the latest run ID.
