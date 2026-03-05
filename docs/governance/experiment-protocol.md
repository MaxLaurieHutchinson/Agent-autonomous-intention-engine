# Experiment Protocol

Use this protocol for every runtime or orchestration experiment.

## Required Header

- id: `EXP-YYYYMMDD-<slug>`
- owner:
- status: `proposed|active|stopped|promoted|archived`
- scope:
- hypothesis:
- cost_cap_gbp:
- start_date:
- review_date:

## Required Sections

1. Hypothesis and expected impact.
2. Success metrics and failure metrics.
3. Safety constraints and rollback triggers.
4. Runtime surfaces affected (CLI/config/cron/heartbeat/docs).
5. Validation commands and evidence location.
6. Promotion decision with rationale.

## Hard Limits

- experiments must not bypass guardrails
- experiments must be reversible
- experiments must not change public contract silently
- experiments without evidence are archived, not promoted
