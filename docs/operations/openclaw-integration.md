# OpenClaw Integration

This document explains how this repository integrates with OpenClaw runtime scheduling.

## Integration Surfaces

- Repository assets:
  - `cron/templates/intention-engine-orchestrator-v2.md`
  - `agents/cron/reconcile-intention-engine-jobs.sh`
  - `ops/ie_micro.sh`, `ops/ie_deep.sh`, `ops/ie_status.sh`
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
bash ops/ie_deep.sh
bash ops/ie_status.sh
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
- decide whether to run `bash ops/ie_micro.sh` based on workspace heartbeat policy (`HEARTBEAT.md`)
- if human activity is high, heartbeat can emit `HEARTBEAT_OK` without invoking engine work
- run `bash ops/ie_status.sh`
- escalate only if actionable

Note: current engine CLI does not implement human-activity gating internally; that policy lives in heartbeat orchestration.

## Required OpenClaw Settings for IE Cron Jobs

For deep and brief jobs:
- `sessionTarget`: `isolated`
- `wakeMode`: `next-heartbeat`
- `delivery.mode`: `announce` for visible operator summaries

## Validation Checklist

1. `~/.openclaw/cron/jobs.json` contains enabled IE deep/brief jobs.
2. payload messages reference canonical wrappers (`ops/ie_*`).
3. deep and brief jobs run in isolated sessions.
4. status command remains parseable JSON for orchestrator consumption.
