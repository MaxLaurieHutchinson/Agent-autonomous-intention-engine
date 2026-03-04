# Autonomy Operating Model (v2.1)

## Objective
Run proactive autonomous discovery with strong guardrails and clear human intervention paths.

## Autonomy Classes
- `auto_safe`: may route to approved when threshold is met.
- `policy_guarded`: threshold pass still routes to inbox unless explicitly allowed.
- `human_gate`: always inbox.

## Default Policy Profile
```yaml
autonomy:
  timezone: Europe/London
  daily_budget_gbp: 2.0
  reserve_budget_gbp: 0.2

modes:
  micro:
    enabled: true
    max_items: 2
    max_run_cost: 0.05
  deep:
    enabled: true
    max_items: 5
    max_run_cost: 0.20
  research_deep:
    enabled: false
    max_items: 8
    max_run_cost: 0.40

routing_defaults:
  allow_policy_guarded_auto: false
```

## Why This Model
- preserves autonomy for low-risk items
- forces human review for policy-sensitive and human-gate cases
- prevents silent escalation in higher-risk contexts

## Operability Expectations
- every run emits machine-readable summary
- every run writes replay artifacts
- status must include health degradations (including announce delivery failures)

## Explicit Non-Goals
- no hidden autonomous external sends
- no opaque chain-of-thought persistence
- no auto-enabling of `research_deep` in this phase
