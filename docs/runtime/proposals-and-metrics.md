# Proposals and Metrics

This document explains the queue workflow and telemetry model.

## Proposal Lifecycle

1. Candidate is discovered and scored.
2. Candidate is classified by risk and routed.
3. Proposal markdown is created.
4. File is moved to destination queue (`approved`, `inbox`, `deferred`).

`rejected` exists as a queue but is currently populated by external/manual workflows.

## Proposal File Contract

Example generated frontmatter:

```yaml
id: P-2026-03-04-001
title: Example opportunity
source: hackernews
url: https://example.com/item
created_at: 2026-03-04T10:53:22Z
score: 0.812
relevance: 0.33
autonomy_class: auto_safe
routed_to: approved
```

Body includes `Source` and detailed scoring breakdown (`value`, `urgency`, `effort`, `risk`).

## Queue Semantics

- `approved`: can be executed downstream without human gate
- `inbox`: requires explicit human decision
- `deferred`: intentionally parked due to low relevance/score
- `rejected`: explicit no-go decisions

## Duplicate Control

Runtime prevents duplicate proposal creation per run by:
- checking existing slugs across all queues
- checking run-local slug set before writing

## Metrics Model

Daily metrics file name:
`memory/metrics/intention-engine-YYYY-MM-DD.json`

Rollup fields:
- `total_runs`
- `total_proposals`

Each run record contains operational facts only (no hidden reasoning state).

## What Metrics Are For

- trend visibility (proposal volume, route distribution)
- budget tracking by mode and day
- operational reliability checks over time

## What Metrics Are Not

- task completion ledger for downstream execution
- source of truth for philosophical alignment decisions
- substitute for replay bundle validation

## Recommended Operator Checks

1. Compare `proposals_created` vs queue deltas.
2. Track `network_errors` for source health degradation.
3. Watch `budget_remaining_gbp` before deep runs.
4. Use replay bundles when route outcomes are questioned.
