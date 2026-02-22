# Build Runbook (Full Auto)

## Runtime Commands

Initialize runtime state:
```bash
./ops/init.sh
```

Run micro autonomous loop (idle-gated, non-blocking):
```bash
./ops/micro.sh
```

Run deep autonomous loop:
```bash
./ops/deep.sh
```

Generate daily brief:
```bash
./ops/brief.sh
```

Install/update full-auto cron schedule (idempotent):
```bash
./ops/install-cron.sh
```

Check status and queues:
```bash
python3 ./scripts/intention_engine.py status
```

## What Gets Created/Updated

- `memory/PHILOSOPHY.md`
- `memory/REFLECT.md`
- `memory/proposals/inbox/*.md`
- `memory/proposals/approved/*.md`
- `memory/proposals/deferred/*.md`
- `memory/metrics/intention-engine-YYYY-MM-DD.json`
- `memory/briefings/YYYY-MM-DD-intention-brief.md`
- `memory/INTENT.md` (auto-intake insertions)
- `data/intention-engine-budget.json`

## Full-Auto Schedule (suggested)

Use your scheduler of choice with these cadences:
- every 30 minutes: micro loop
- 23:30 daily: deep loop
- 06:55 daily: briefing

### Example crontab entries
```cron
*/30 * * * * /path/to/Agent-autonomous-intention-engine/ops/micro.sh >> /tmp/intention-engine-micro.log 2>&1
30 23 * * * /path/to/Agent-autonomous-intention-engine/ops/deep.sh >> /tmp/intention-engine-deep.log 2>&1
55 6 * * * /path/to/Agent-autonomous-intention-engine/ops/brief.sh >> /tmp/intention-engine-brief.log 2>&1
```

`intention-engine-install-cron.sh` manages this block automatically.

## Non-Blocking Guarantee

- Micro loop is idle-gated by `data/last-human-activity.json`.
- Without `--force`, micro runs skip when human activity is recent.
- All writes are lock-protected (`memory/metrics/intention-engine.lock`).
- Runs are short and checkpointed by design.

## Safety/Routing Summary

Proposal routing:
- `auto_safe` + high score -> auto-approve
- `policy_guarded` + threshold -> auto-approve (if policy allows)
- `human_gate` -> remains in inbox for decision
- low score -> deferred

No external actions are executed by this runtime. It only creates/updates local state files.
