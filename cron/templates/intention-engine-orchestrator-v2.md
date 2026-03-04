# Intention Engine Orchestrator v2

Use this template for isolated cron runs that execute the Intention Engine in a deterministic and operable way.

## Execution Contract

1. Run the engine with canonical workspace wrappers only.
2. Capture JSON output and surface errors if command exit code is non-zero.
3. Verify status after run.
4. Announce only concise operational results.

## Commands

```bash
bash ops/ie_deep.sh
bash ops/ie_status.sh
```

## Error Handling

1. If `ops/ie_deep.sh` fails, retry once after 30 seconds.
2. If second attempt fails, report:
   - exit code
   - error summary
   - whether budget file exists (`data/intention-engine-budget.json`)
3. If `ops/ie_status.sh` shows announce failures in health, report as actionable.

## Output Rules

1. If proposals were created, report count plus route breakdown (`approved`, `inbox`, `deferred`).
2. If nothing new was created, report run status and remaining budget.
3. Keep output short and operational.
