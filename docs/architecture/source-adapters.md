# Source Adapter Architecture

Source discovery is implemented through pluggable adapters under `src/intention_engine_core/sources/`.

## Why This Exists

- remove hardcoded source branching from runtime core
- make source onboarding predictable and testable
- keep deterministic behavior while expanding source coverage

## Runtime Contract

`runtime.py` calls `discover_candidates()` which now:
1. reads ordered `sources[]` config entries
2. dispatches by `type` using `sources/registry.py`
3. runs adapter fetch
4. applies config filters
5. applies canonical dedupe
6. emits structured source stats + errors

## Adapter Package

- `base.py`: `SourceAdapter`, `SourceCandidate`, `SourceFetchResult`
- `registry.py`: source-type registry and dispatch
- `common.py`: URL canonicalization, filtering, dedupe, and fetch utilities
- adapters:
  - `reddit.py`
  - `hackernews.py`
  - `github.py`
  - `fixture.py`
  - `rss.py`
  - `arxiv.py`

## Determinism Rules

- source execution order follows config list order
- each candidate tracks `source_index`
- URLs are normalized before dedupe
- dedupe key order:
  1. `canonical_url`
  2. `title_fingerprint`
- final candidate order is stable:
  - `source_index`
  - `created_at` (desc)
  - `canonical_url`
  - `title`

## Error Taxonomy

Adapter fetch failures are structured with:
- `source_timeout`
- `source_parse_error`
- `source_rate_limited`
- `source_unknown`

These are persisted in replay inputs and surfaced in status health.

## Replay Provenance

Replay bundles include:
- `source_stats`
- `dedupe_stats`
- per-candidate source metadata (`source_id`, `source_type`, `canonical_url`)

This allows route decisions to be audited against the exact source pipeline used in that run.
