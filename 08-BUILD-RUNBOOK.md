# Build Runbook (v2.1)

## Prerequisites
- Python 3.9+
- repo root as current working directory

## Core Validation
```bash
python3 scripts/intention_engine.py validate --json
python3 -m unittest discover -s tests -v
```

## Runtime Commands
Micro run:
```bash
bash ops/ie_micro.sh
```

Deep run:
```bash
bash ops/ie_deep.sh
```

Status JSON:
```bash
bash ops/ie_status.sh
```

Replay:
```bash
python3 scripts/intention_engine.py replay --run-id <run-id>
```

## Legacy Compatibility Command
```bash
python3 scripts/intention_engine.py --mode micro --dry-run
```

## Cron / Heartbeat Alignment
Template used by orchestrated cron runs:
- `cron/templates/intention-engine-orchestrator-v2.md`

Patch live cron payloads safely:
```bash
bash agents/cron/reconcile-intention-engine-jobs.sh
```

## Operational Smoke Checklist
1. `python3 scripts/intention_engine.py validate --json` returns status `ok`.
2. `bash ops/ie_micro.sh --dry-run` returns `dry_run` and emits replay bundle.
3. `bash ops/ie_status.sh` returns parseable JSON.
4. `python3 -m unittest discover -s tests -v` passes.

## Failure Handling
If run fails:
1. check `logs/engine.jsonl`
2. inspect latest replay bundle in `data/intention-engine-runs/`
3. run `status --json` to inspect health degradation and queue state
