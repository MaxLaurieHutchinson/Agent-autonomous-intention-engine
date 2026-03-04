# CLI Reference

Primary entrypoint:

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli
```

Global option:
- `--config <path>`: path to runtime config JSON

## Commands

### `run`

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json run --mode <micro|deep|research_deep> [--dry-run]
```

Behavior:
- validates mode profile exists and is enabled
- enforces budget gate unless `--dry-run`
- discovers/scores/routes candidates
- writes replay bundle always
- writes budget/proposals/metrics/reflect only on non-dry runs

Common statuses:
- `ok`
- `dry_run`
- `mode_disabled`
- `invalid_mode`
- `budget_blocked`

### `status`

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json status --json
```

Returns:
- `status` (`ok` or `degraded`)
- `budget`
- `queues`
- `last_run`
- `health` (`validation_*`, `announce_failures`, `recent_log_errors_24h`)

### `validate`

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json validate --json
```

Checks:
- config structural requirements
- key path existence warnings
- schema presence

### `replay`

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli --config config/runtime.json replay --run-id <run-id>
```

Verifies deterministic route reproduction from replay artifacts.

## Exit Codes

- `0`: success
- `1`: runtime/config/replay failure
- `2`: parser/usage error

## Wrapper Commands

For operators, preferred wrappers are:

```bash
bash ops/ie_micro.sh
bash ops/ie_deep.sh
bash ops/ie_status.sh
```

They inject `PYTHONPATH` and default config path for repo-root execution.
