# Cron vs Heartbeat

Use both, but for different responsibilities.

## Responsibility Split

| Mechanism | Purpose | Cadence | Session Type |
|---|---|---|---|
| Heartbeat | frequent, interruption-aware micro control loop | high-frequency (e.g., every 30 min) | main session system event |
| Cron | deterministic fixed-time jobs (deep run, morning brief) | fixed schedule | isolated session |

## What Goes in Heartbeat

- micro run attempts
- quick status checks
- low-cost safety/attention routing
- immediate skip behavior when human is active

Do not place long, deep, or expensive pipelines directly in heartbeat.

## What Goes in Cron

- deep scouting/exploration runs
- briefing generation
- maintenance jobs that can run isolated

Cron is the right place for predictable wall-clock operations.

## `cron/` vs `agents/cron/`

| Path | Role |
|---|---|
| `cron/` | declarative templates/prompts for orchestrated jobs |
| `agents/cron/` | executable scripts that mutate/repair live cron payloads |

Best practice:
- keep prompts in `cron/templates/`
- keep JSON mutation/reconciliation scripts in `agents/cron/`
- do not mix these concerns

## Failure and Visibility Model

- heartbeat should stay minimal and avoid noisy logs unless actionable
- cron deep/brief jobs should announce concise outcomes
- status health should surface announce delivery failures and recent runtime errors
