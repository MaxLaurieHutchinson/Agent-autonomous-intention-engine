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
| `context_sources` | array | no | deterministic cognitive context inputs for scoring |
| `sources` | array | yes | discovery source definitions |
| `routing` | object | yes | risk and route thresholds |

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

## `context_sources`

Each entry:
- `name` (string, required)
- `path` (string, required; accepts file path or glob)
- `weight` (number > 0, optional, default `1.0`)

Behavior:
- loaded in list order
- glob expansion order is deterministic (sorted)
- weighted token contribution influences keyword extraction used by scoring
- context details are persisted into replay artifacts (`inputs.json` and `scores.json`)

Recommended baseline:
- `memory/INTENT.md`
- `memory/PHILOSOPHY.md`
- `memory/knowledge/frameworks/*.md`
- `memory/knowledge/patterns/*.md`
- `memory/knowledge/insights/*.md`

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

## Validation Command

```bash
intention-engine --config config/runtime.json validate --json
```

Validation checks:
- required config structure and fields
- schema file availability
- key path existence warnings (`intent_path`, philosophy, proposals dir)
- `context_sources` match counts and unmatched-source warnings
