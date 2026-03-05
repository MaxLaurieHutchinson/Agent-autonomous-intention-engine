# Operations Runbook

This runbook is for operating the current `dev` runtime safely.

## Prerequisites

- Python 3.9+
- repo root as working directory
- `config/runtime.json` present

## Baseline Validation

Bootstrap workspace files and directories first:

```bash
bash ops/bootstrap-workspace.sh
```

Then run:

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli validate --json
python3 -m unittest discover -s tests -v
```

Expected:
- tests pass
- validate returns `status: ok` (warnings are acceptable and should be reviewed)

## Core Commands

Micro run:

```bash
bash ops/ie_micro.sh
```

Deep run:

```bash
bash ops/ie_deep.sh
```

Status:

```bash
bash ops/ie_status.sh
```

Replay:

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli replay --run-id <run-id>
```

## Dry-Run Safety Mode

```bash
bash ops/ie_micro.sh --dry-run
```

Dry run does not mutate budget/proposals/metrics/reflect, but still exercises discovery, scoring, routing, and replay artifact writes.

## Troubleshooting

### `status: degraded`
Check in order:
1. `health.validation_errors`
2. `health.announce_failures`
3. `health.recent_log_errors_24h`

### Discovery failures
- Inspect latest `discovery_error` events in `logs/engine.jsonl`.
- Network/API failures are expected to degrade source coverage but not crash full run by default.

### Budget blocked
- Runtime returns `status: budget_blocked` with `remaining_gbp` and `required_gbp`.
- Wait for daily rollover or adjust `mode_profiles` / budget config.

### Replay mismatch
- If replay returns mismatches, treat as determinism regression and investigate routing/config drift.

## Cron Installer (OS cron)

For local cron block installation:

```bash
bash ops/install-cron.sh
```

This manages a marker block and schedules canonical wrappers only.

## Operational Smoke Checklist

1. `validate --json` is `ok`.
2. `ie_micro.sh --dry-run` exits 0.
3. `ie_status.sh` returns parseable JSON.
4. one non-dry micro run updates budget and metrics.
