# Autonomy Operating Model

## Objective
Run fully autonomous, automated, and proactive operations while preserving safety through policy instead of constant manual approvals.

## Full-Autonomy by Policy

Autonomy classes:
- `auto_safe`: always execute
- `policy_guarded`: execute when explicit policy conditions pass
- `human_gate`: queue for human decision

This preserves autonomy for routine work and reserves interruptions for genuinely high-risk actions.

## Default Policy Profile (Recommended)

```yaml
autonomy:
  mode: FULL
  timezone: Europe/London
  daily_budget_gbp: 2.00
  max_parallel_workers: 3

permissions:
  local_filesystem: allow
  web_research: allow
  local_code_execution: allow
  send_updates_to_human: allow
  external_public_posts: queue
  purchases_or_paid_subscriptions: queue
  system_config_mutations: queue

routing:
  auto_safe_threshold: 0.75
  policy_guarded_threshold: 0.70
  human_gate_threshold: 0.00
```

## Canonical Budget Model
Adopt one budget model and remove ambiguity:
- `daily_budget_gbp: 2.00`
- `reserve_budget_gbp: 0.20`
- `allocatable_budget_gbp: 1.80`

Suggested dynamic allocation bands:
- High-value exploration: `0.40-0.60`
- Medium exploration: `0.20-0.30`
- Quick validation: `0.05-0.10`
- Sub-agent spawn: `0.05-0.15` per agent

## Proactive Triggers

Trigger events and actions:
- `idle > 5 min` -> run micro-scout (2-5 min)
- `new trend spike detected` -> create proposal and score
- `deadline < 72h in active saga` -> auto-generate execution plan
- `task stale > 3 days` -> auto-create unblock proposal
- `heartbeat with no alerts` -> consume backlog proactively
- `morning window` -> generate executive briefing automatically

## Main-Thread Non-Blocking Rules
Canonical triggers must never block live conversation:
- Triggered work runs in isolated background sessions, not the main chat session.
- On any inbound human message, background scout work is preempted (pause or stop at safe checkpoint).
- Main-thread lock priority is always `human conversation > autonomous background tasks`.
- Use short work slices (`2-5 min`) and frequent checkpoints so preemption latency stays low.
- Writes to shared state files (`INTENT.md`, proposal queues) must use lock discipline to avoid collisions.

## Automation Cadence

Suggested schedule (Europe/London):
- Every 30 minutes: heartbeat control loop and micro-scout eligibility check
- 23:30 daily: deep scout run (30-60 minutes)
- 06:55 daily: executive morning briefing
- 12:30 daily: midday replanning pass
- 18:00 daily: evidence/status reconciliation
- Sunday 21:00: weekly digest + archive + metric rollup

## Worker Roles
- `Scout`: observes trends and opportunities
- `Analyst`: performs orientation and scoring
- `Planner`: maps approved proposals into saga-linked intentions
- `Builder`: executes implementation tasks
- `Critic`: validates logic, risks, and evidence quality
- `Reflector`: writes outcomes to `REFLECT.md` and knowledge library

## Decision Heuristics (From Ash Time v3)

Opportunity scoring:
`score = (value * urgency) / (effort * risk)`

Recommended routing:
- `score >= 0.75`: execute now (`NOW`) if capacity exists
- `0.60 <= score < 0.75`: queue as `NEXT`
- `< 0.60`: capture as backlog or reject

Sub-agent spawning rule:
- Spawn parallel workers when:
  - topic count >= 3
  - independence score > 0.7
  - remaining allocatable budget > 0.30
  - active workers < 3
- Otherwise execute serially.

Reflection cadence:
- Perform micro-reflection every 20 minutes or every 0.05 budget consumed.
- At each checkpoint: continue, pivot, or cut-loss decision.

## Quality Gates

Before any proposal becomes active work:
- Alignment to philosophy >= threshold
- Clear relevance to active saga/chapter
- Evidence target defined
- Risk class assigned

Before marking an intention complete:
- Artifact exists (file/link/commit/report)
- Evidence meets expected tier
- Reflection entry written

## KPIs for Proactive Effectiveness
- Proposal-to-intention conversion rate
- Autonomous completion rate
- Mean time from discovery to execution
- Percentage of completed intentions with Tier 1 or Tier 2 evidence
- Number of stale tasks auto-unblocked per week

## Escalation Logic
- If budget consumption > 90% before midday: switch to `high_signal_only`
- If 3 consecutive low-value runs: reduce scout frequency by 50%
- If critical saga blocked: pause scouting and prioritize unblock tasks

## Output Mode Selection
Select output format by signal and novelty:
- `full_brief`: high signal (`total_cost > 0.50` or `novel_discoveries > 2`)
- `scannable`: routine maintenance
- `hybrid`: mixed urgency/importance
