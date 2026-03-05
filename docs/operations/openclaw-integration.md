# OpenClaw Integration

This document explains how this repository integrates with OpenClaw runtime scheduling.

## Integration Surfaces

- Repository assets:
  - `cron/templates/intention-engine-orchestrator-v2.md`
  - `agents/cron/reconcile-intention-engine-jobs.sh`
- OpenClaw scheduler state:
  - `~/.openclaw/cron/jobs.json`
- Workspace heartbeat policy:
  - `~/.openclaw/workspace/HEARTBEAT.md` (outside this repo)

## Current OpenClaw Job Model (Grounded)

Observed pattern in live jobs:
- `Heartbeat`
  - `payload.kind = systemEvent`
  - reads workspace `HEARTBEAT.md`
  - every 30 minutes
- `IE Deep Run (Orchestrated)`
  - cron at `23:30 Europe/London`
  - `sessionTarget = isolated`
  - `delivery.mode = announce`
- `IE Brief Generation (Orchestrated)`
  - cron at `06:55 Europe/London`
  - `sessionTarget = isolated`
  - `delivery.mode = announce`

## Recommended Wiring

### 1. Deep run template contract
Use `cron/templates/intention-engine-orchestrator-v2.md` and execute:

```bash
intention-engine --config config/runtime.json run --mode deep
intention-engine --config config/runtime.json status --json
```

### 2. Live jobs reconciliation
Apply repo-owned patching to matching job names:

```bash
bash agents/cron/reconcile-intention-engine-jobs.sh
```

This script:
- backs up jobs JSON
- rewrites message payloads for `IE Deep Run (Orchestrated)` and `IE Brief Generation (Orchestrated)`

### 3. Heartbeat contract
Heartbeat should do short, interruption-aware checks and micro opportunity handling.

Typical heartbeat behavior in workspace:
- decide whether to run `intention-engine --config config/runtime.json run --mode micro` based on workspace heartbeat policy
- if human activity is high, emit `HEARTBEAT_OK` without invoking engine work
- run `intention-engine --config config/runtime.json status --json`
- escalate only if actionable

Note: human-activity gating is owned by heartbeat/orchestrator policy, not by runtime engine internals.

## Required OpenClaw Settings for IE Cron Jobs

For deep and brief jobs:
- `sessionTarget`: `isolated`
- `wakeMode`: `next-heartbeat`
- `delivery.mode`: `announce` for visible operator summaries

## AshTime Experimentation Lane

- Keep `ash-time-v3-dynamic` disabled by default.
- Enable only for explicit experiment windows with defined budget and rollback.
- Do not couple AshTime experiments to canonical IE cron jobs by default.

## Validation Checklist

1. `~/.openclaw/cron/jobs.json` contains enabled IE deep/brief jobs.
2. payload messages reference canonical CLI commands.
3. deep and brief jobs run in isolated sessions.
4. status output remains parseable JSON for orchestrator consumption.
