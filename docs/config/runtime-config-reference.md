# Runtime Config Reference

Source file: `config/runtime.json`
Schema: `config/runtime.schema.json`

## Top-Level Fields

| Field | Type | Required | Purpose |
|---|---|---|---|
| `daily_budget_gbp` | number | yes | daily budget ceiling |
| `reserve_budget_gbp` | number | yes | reserved budget not allocatable |
| `mode_profiles` | object | yes | per-mode limits and enable flags |
| `paths` | object | yes | file and directory contracts |
| `sources` | array | yes | discovery source definitions |
| `routing` | object | yes | risk and route thresholds |
| `idle_threshold_minutes` | number | no | optional integration hint |
| `intake` | object | no | optional downstream intake defaults |
| `external_action_keywords` | array | no | optional policy signals |

## `mode_profiles`

Required keys: `micro`, `deep`, `research_deep`

Per mode:
- `enabled` (boolean)
- `max_items` (integer > 0)
- `max_run_cost` (number >= 0)
- `validation` (string)
- `delegation` (boolean)
- `checkpointing` (optional boolean)

Runtime behavior:
- missing/invalid profile -> `invalid_mode`
- disabled profile -> `mode_disabled`

## `paths`

Key paths:
- `intent_path`
- `reflect_path`
- `philosophy_path`
- `philosophy_fallback_path`
- `proposals_dir`
- `briefings_dir`
- `metrics_dir`
- `budget_state_path`
- `lock_path`
- `logs_path`
- `replay_dir`
- `cron_jobs_path`

Resolution rules:
- absolute path: unchanged
- `~`: home-expanded
- relative: resolved from workspace root

## `sources`

Supported source types in current runtime:
- `reddit`
- `hackernews`
- `github`
- `fixture`

Unknown type behavior:
- candidate fetch skipped
- discovery error captured

## `routing`

Required keys:
- `auto_safe_threshold`
- `policy_guarded_threshold`
- `defer_threshold`
- `min_relevance_threshold`
- `allow_policy_guarded_auto`
- `guarded_keywords`
- `always_human_gate_keywords`

Recommended defaults:
- keep `allow_policy_guarded_auto = false` for safe-by-default behavior
- keep human-gate keyword list strict for irreversible actions

## Optional Sections

### `intake`
Not consumed by core routing today; available for downstream intention insertion workflows.

### `external_action_keywords`
Not directly enforced in routing logic today; useful for policy and integration layers.

## Validation Commands

```bash
PYTHONPATH=./src python3 -m intention_engine_core.cli validate --json
```

Validation checks:
- required config structure and fields
- schema file availability
- key path existence warnings (`intent_path`, philosophy, proposals dir)
