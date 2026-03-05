# Source Onboarding

This runbook defines how to add or tune discovery sources safely.

## No-Secrets Policy (Current Phase)

This repository currently allows only non-auth source integrations.

Allowed now:
- `reddit`
- `hackernews`
- `github`
- `fixture`
- `rss`
- `arxiv`

Not in scope now:
- API-key or token-based sources

## Add a Source Entry

Edit `config/runtime.json` and add a `sources[]` entry with:
- `id` (unique)
- `name`
- `type`
- `enabled`
- `limit`
- `timeout_s`
- optional `filters`

Example:

```json
{
  "id": "rss-aifeed",
  "name": "AIFeed",
  "type": "rss",
  "feed_url": "https://aifeed.dev/feed.xml",
  "enabled": true,
  "limit": 25,
  "timeout_s": 10,
  "filters": {
    "max_age_hours": 168,
    "include_keywords": ["agent", "llm", "mcp"]
  }
}
```

## Filter Tuning

Use `filters` to reduce noise and cost:
- `min_engagement`
- `max_age_hours`
- `include_keywords`
- `exclude_keywords`
- `domain_allowlist`
- `domain_blocklist`

Start strict, then relax only if recall is too low.

## Validation Flow

1. Validate config:

```bash
intention-engine --config config/runtime.json validate --json
```

2. Dry-run micro:

```bash
intention-engine --config config/runtime.json run --mode micro --dry-run
```

3. Inspect replay inputs for source stats:
- `data/intention-engine-runs/<run-id>/inputs.json`
- confirm `source_stats` and `dedupe_stats`

4. Check health:

```bash
intention-engine --config config/runtime.json status --json
```

## Curated RSS Seeds

A starter seed set is maintained at:
- `config/sources/rss_seed_curated.json`

These entries are intentionally disabled by default. Enable selectively.

## Quality Gate Before Merge

For each source change PR:
1. unit tests for parser/adapter behavior
2. deterministic discovery test
3. docs update in config reference or architecture notes
