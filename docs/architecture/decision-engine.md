# Decision Engine

This document defines the scoring, risk, and routing behavior implemented in `runtime.py`.

## Inputs

For each run, the engine ingests:
- candidates from configured discovery sources
- keywords extracted from `INTENT` and `PHILOSOPHY`
- routing thresholds and keyword lists from config
- mode profile constraints (`max_items`, `max_run_cost`, `enabled`)

## Candidate Scoring

Scoring output fields:
- `value`
- `urgency`
- `effort`
- `risk`
- `relevance`
- final `score` (0.0 to 2.0)

### Relevance
Computed from token overlap between candidate title and extracted keyword set.

### Value
Weighted mix of:
- relevance
- AI signal terms in title
- normalized engagement
- low-signal penalties

### Urgency
Time-decay over candidate age (hours), clamped to a floor.

### Effort
Defaults to `0.75`, raised for terms indicating deeper work (`framework`, `migration`, `deep`, etc.).

### Risk and Autonomy Class
`classify_risk()` returns one of:
- `human_gate` (highest risk)
- `policy_guarded`
- `auto_safe`

Based on keyword matches in title+URL against config lists.

## Routing Logic

`route_from_values(score, relevance, autonomy_class, routing)` applies:

1. If relevance below `min_relevance_threshold` -> `deferred`
2. If score below `defer_threshold` -> `deferred`
3. If class is `human_gate` -> `inbox`
4. If class is `auto_safe` and score >= `auto_safe_threshold` -> `approved`
5. If class is `policy_guarded` and score >= `policy_guarded_threshold`:
   - `approved` only if `allow_policy_guarded_auto = true`
   - otherwise `inbox`
6. Else -> `inbox`

## Queue Semantics

- `approved`: autonomous execution candidate queue
- `inbox`: human review queue
- `deferred`: low relevance/priority queue
- `rejected`: explicit negative disposition queue

The runtime currently writes new proposals into `approved`, `inbox`, or `deferred`.

## Budget Gate

Before persistence (except `--dry-run`):
- load daily budget state
- reject run with `budget_blocked` if `remaining_gbp < mode.max_run_cost`
- on success, consume cost and append run metadata

## Deterministic Replay

Per-run bundle includes:
- raw inputs (`inputs.json`)
- computed scores (`scores.json`)
- chosen decisions and routing config (`decisions.json`)
- config hash (`config-hash.txt`)

`replay` recomputes route per decision and reports mismatches.

## Failure Surfaces

- Discovery errors are captured in run summary and logged (`discovery_error`).
- Unhandled runtime exceptions are logged (`unhandled_exception`) and returned as error JSON.
- Status degrades when config errors, announce failures, or recent error logs are present.
