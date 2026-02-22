# Ash Time v3 Normalization Spec

Source analyzed:
- `<WORKSPACE>/ash/prompts/ash-time-system-v3.md`

## What To Preserve
- Event-driven OODA lifecycle:
  - Sense
  - Orient
  - Decide
  - Act
  - Reflect
- Opportunity scoring:
  - `(Value x Urgency) / (Effort x Risk)`
- Dynamic execution strategy:
  - serial vs parallel decisioning
  - max parallel workers = 3
- Budget-aware autonomous behavior:
  - main budget + reserve
  - reallocation triggers
- Reflection gates and validation logic.
- Adaptive output format by session signal.

## What To Fix
- Remove duplicated prompt blocks (file currently embeds multiple overlapping versions).
- Resolve budget contradictions:
  - eliminate `0.05/session` model in canonical runtime
  - keep `2.00/day` + `0.20 reserve`
- Replace generic `boss` language with stable actor naming (`human`).
- Replace ambiguous `/workspace/...` references with workspace-accurate paths.
- Keep one canonical deliverable set:
  - morning brief
  - pending approvals
  - session log

## Canonical Runtime Constants
```yaml
runtime:
  timezone: Europe/London
  daily_budget_gbp: 2.00
  reserve_budget_gbp: 0.20
  allocatable_budget_gbp: 1.80
  max_parallel_workers: 3
  reflection_interval_minutes: 20
  reflection_budget_step_gbp: 0.05
```

## Canonical Trigger Rules
- Spawn parallel workers only when:
  - topics >= 3
  - independence > 0.7
  - remaining allocatable budget > 0.30
- Otherwise run serial.

## Canonical Output Selection
- `full_brief`: high-signal sessions (`cost > 0.50` or `novel_discoveries > 2`)
- `scannable`: routine checks
- `hybrid`: mixed urgency

## Acceptance Checklist
- [ ] Prompt has one architecture block only.
- [ ] No conflicting budget values remain.
- [ ] All paths are valid in current workspace.
- [ ] Output rules align with Intention Engine proposal pipeline.
- [ ] Safety boundaries map to autonomy classes in `03-AUTONOMY-OPERATING-MODEL.md`.
