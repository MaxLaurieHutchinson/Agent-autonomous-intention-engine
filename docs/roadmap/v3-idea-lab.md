# V3 Idea Lab

Living planning note for v3 ideas, tradeoffs, and decision capture.

## Goal

Design a clearer, more operable v3 without losing:
- deterministic replayability
- file-first transparency
- safe default autonomy
- non-blocking operator workflow

## Current Baseline (v2.x)

- `micro` runs hourly in isolated cron (`IE Micro Run (Orchestrated)`)
- `deep` runs daily in isolated cron (`IE Deep Run (Orchestrated)`)
- heartbeat is non-blocking/no-op by default (`HEARTBEAT_OK`)
- markdown-first memory + proposal queues + replay bundles are active

## V3 Scope (Approved Now)

Keep these as the active v3 implementation set:
- V3-006 Source fallback chains + mirrors
- V3-008 Proposal lifecycle outcome tracking
- V3-004 Health taxonomy split
- V3-003 Proposal quality schema v2
- V3-013 Full sub-agent repertoire access (manual catalog model)

## Deferred (Keep on Sheet, Not in Current Build)

- V3-010 Saga-aware routing/weight profiles

## Maybe Pile (Optional Tidy Work)

- V3-012 Runtime path layout tidy (`data/` vs `logs/`)

## Removed for Now (Over-Engineering in This Phase)

- V3-001 Rename modes to `scan`/`synthesis`
- V3-002 Source circuit-breakers
- V3-005 Context-layer weighting model
- V3-007 Source health scoring + auto-weight adjust
- V3-009 Interactive `policy_guarded` decision prompt
- V3-011 Semantic relevance (embeddings)

## Backlog (Current)

| ID | Idea | Why | Cost/Risk | Status |
|---|---|---|---|---|
| V3-006 | Source fallback chains + mirrors | reduce hard source outages (e.g. reddit 403) | medium/medium | active |
| V3-008 | Proposal lifecycle outcome tracking | measure discovery -> action conversion | medium/low | active |
| V3-004 | Health taxonomy split | faster diagnosis and cleaner alerts | medium/low | active |
| V3-003 | Proposal quality schema v2 | better downstream actionability | medium/medium | active |
| V3-013 | Full sub-agent repertoire access | deterministic access to 51 specialist prompts | medium/low | active |
| V3-010 | Saga-aware routing/weight profiles | align scoring to active strategic mode | medium/high | deferred |
| V3-012 | Runtime path layout tidy (`runtime/data` + `runtime/logs`) | cleaner tree without mixing deterministic artifacts and operational logs | low/low | maybe |

## Priority Stack (Current)

1. V3-006 Source fallback chains + mirrors
2. V3-008 Proposal lifecycle outcome tracking
3. V3-004 Health taxonomy split
4. V3-003 Proposal quality schema v2
5. V3-013 Full sub-agent repertoire access
6. V3-010 Saga-aware routing/weight profiles (deferred)

## Prioritized Cards

### V3-006 Source Fallback Chains + Mirrors (P1)
- hypothesis: discovery reliability increases if adapters support deterministic fallback endpoints.
- change: add fallback resolver per source type (`primary -> secondary -> mirror`) with explicit timeout/retry rules.
- success metric: weekly source error rate reduced by >=50% without lower proposal quality.
- guardrail: preserve deterministic adapter ordering and log exact endpoint used.
- rollout: enable for reddit/rss adapters first.

### V3-008 Proposal Lifecycle Outcome Tracking (P1)
- hypothesis: explicit lifecycle states improve conversion and quality control.
- change: add `state` metadata (`created`, `reviewed`, `approved`, `acted`, `closed`) and optional `outcome` fields.
- success metric: visibility into end-to-end conversion per week; no orphan proposals older than N days.
- guardrail: additive file metadata only; no queue contract break.
- rollout: start with markdown frontmatter and one daily rollup report.

### V3-004 Health Taxonomy Split (P1)
- hypothesis: split health domains improve diagnosis speed and reduce noisy alerts.
- change: split health into `runtime`, `source`, and `delivery` with stable machine-readable status output.
- success metric: faster root-cause identification for failed runs and fewer non-actionable alerts.
- guardrail: no hidden status semantics; preserve backward-compatible JSON keys where possible.
- rollout: introduce in status first, then reflect in runbook/ops docs.

### V3-003 Proposal Quality Schema v2 (P1)
- hypothesis: minimal required fields improve downstream review quality.
- change: require `why_now`, `risk`, `effort`, and `evidence` on proposal artifacts.
- success metric: lower reviewer clarification churn and higher approval confidence.
- guardrail: additive changes only; do not break existing queue file flow.
- rollout: soft-validate first, then enforce after one review cycle.

### V3-013 Full Sub-Agent Repertoire Access (P1)
- hypothesis: a complete, pinned specialist catalog improves task quality and speed without runtime complexity.
- change: add pinned `agency-agents` submodule and indexed roster; manual selection only.
- success metric: deterministic availability of all 51 specialists and reduced specialist prompt search time.
- guardrail: explicit/manual invocation only; no runtime auto-spawn or hidden orchestration behavior.
- rollout: docs + validation now; orchestration hooks deferred until after core V3 work ships.

### V3-010 Saga-Aware Routing/Weight Profiles (Deferred)
- hypothesis: mode-specific strategic context improves relevance.
- change: optional profile map for active saga that biases source and context weights.
- success metric: higher accepted-proposal ratio during focused periods.
- guardrail: explicit profile selection only; no hidden auto-switching.
- rollout: defer until core v3 scope is shipped and stable.

## Decision Log

Record only finalized choices.

| Date | Decision | Rationale | Owner |
|---|---|---|---|
| 2026-03-05 | `micro` moved to isolated hourly cron | non-blocking chat + simpler ops boundary | Max + Codex |
| 2026-03-05 | heartbeat simplified to no-op | remove flawed active-user gate dependence | Max + Codex |
| 2026-03-05 | v3 scope trimmed to 006/008/004/003 | radical simplicity and lower implementation risk | Max + Codex |
| 2026-03-05 | V3-010 kept as deferred | useful later but not worth current complexity | Max + Codex |
| 2026-03-05 | V3-013 added as active with manual catalog model | full repertoire access now, orchestration later | Max + Codex |

## Experiment Cards

Use this template before implementing non-trivial v3 changes.

```md
### EXP-<id>: <title>
- hypothesis:
- change:
- success metric:
- failure guardrail:
- rollout scope:
- rollback:
- evidence links:
```

## Open Questions

1. For V3-003, which fields are mandatory at first enforcement pass?
2. For V3-006, what is the exact retry/timeout policy per source type?
3. For V3-004, what minimum status JSON shape should remain stable for cron tooling?
4. What acceptance threshold closes V3 core and keeps V3-010 deferred?
5. Which manual specialist selection patterns should become default playbooks first?

## Next Review Prompt

When revisiting this file, answer:
1. What changed in runtime reality since last edit?
2. Which active items moved to shipped?
3. Are we still doing only what is worth it, and avoiding over-engineering?
