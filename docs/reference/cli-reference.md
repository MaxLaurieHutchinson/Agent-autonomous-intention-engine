# CLI Reference

Canonical command:

```bash
intention-engine --config config/runtime.json
```

## Commands

### `run`

```bash
intention-engine --config config/runtime.json run --mode <micro|deep|research_deep> [--dry-run]
```

Behavior:
- enforces mode profile constraints and budget policy
- writes replay bundle always
- writes proposals/metrics/reflect only when not `--dry-run`

Common statuses:
- `ok`
- `dry_run`
- `budget_blocked`
- `mode_disabled`
- `invalid_mode`

### `status`

```bash
intention-engine --config config/runtime.json status --json
```

Returns:
- budget summary
- queue counts
- last run snapshot
- health checks (validation, announce failures, recent runtime errors)
- failure taxonomy and actionable errors

### `validate`

```bash
intention-engine --config config/runtime.json validate --json
```

Checks:
- config structure and required fields
- schema availability
- critical path existence
- context source match counts

Exit behavior:
- `0` when `status=ok`
- `1` when validation errors exist

### `replay`

```bash
intention-engine --config config/runtime.json replay --run-id <run-id>
```

Verifies deterministic route reproduction from replay artifacts.

Exit behavior:
- `0`: no mismatches
- `1`: runtime/config/replay failure or mismatch detected

## Exit Codes

- `0`: success
- `1`: domain/runtime validation error
- `2`: parser/argument error

## Notes

- There is no wrapper command contract in this phase.
- Use the canonical `intention-engine` executable for local, cron, and heartbeat integration.
