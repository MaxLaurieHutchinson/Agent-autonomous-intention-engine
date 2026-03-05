# Cognitive Frameworks

This document separates what is implemented now from what is roadmap.

## Status Matrix

| Framework | Status | How It Appears |
|---|---|---|
| OODA | Implemented | Encoded in discovery/scoring/routing/persistence/reflection pipeline |
| BDI | Planned | No explicit `belief/desire/intention` domain model types yet |
| Rubber Duck | Planned | No dedicated multi-agent duck-loop orchestrator yet |

## OODA (Implemented)

### Observe
- Candidate collection from configured source adapters (`reddit`, `hackernews`, `github`, `fixture`, `rss`, `arxiv`).

### Orient
- Weighted keyword extraction from configured `context_sources` (for example `INTENT`, `PHILOSOPHY`, and `memory/knowledge/*`).
- Candidate scoring using relevance, AI signal, engagement, urgency decay, effort penalties, and risk.

### Decide
- Risk classification:
  - `human_gate` for always-human keywords
  - `policy_guarded` for guarded keywords
  - `auto_safe` otherwise
- Route decision:
  - `approved`, `inbox`, or `deferred` from thresholds and policy flags

### Act
- Proposal markdown persisted to route-specific queue.
- Budget state consumed unless `--dry-run`.

### Reflect
- Reflection entry appended to `memory/REFLECT.md`.
- Daily metrics rollup updated.
- Replay bundle persisted.

## BDI (Planned, Not Yet First-Class)

Current runtime has BDI-like behavior but not explicit BDI data structures.

Approximate mapping today:
- Beliefs: discovered candidates + observed health/budget state
- Desires: implicit in `INTENT.md` + philosophy keywords + scoring objective
- Intentions: routed proposals and approved queue

What is missing for explicit BDI:
- typed belief store and updates
- explicit desire prioritization model
- intention lifecycle manager with adoption/reconsideration policies

## Rubber Duck (Planned, Not Yet Engine Primitive)

Potential role in this project:
- challenge high-impact proposals before approval
- run structured contradiction checks on risk assumptions
- provide adversarial reflection for deep mode outputs

Current state:
- no dedicated duck-loop module
- no additional routing stage for multi-perspective challenge

## Specialist Repertoire Access (Implemented, Manual)

V3 includes deterministic access to a full specialist prompt repertoire through:
- pinned submodule: `external/agency-agents`
- indexed roster: `docs/reference/sub-agent-roster.md`
- usage model: manual specialist selection only

Important boundary in this phase:
- no runtime auto-spawn of specialists
- no hidden orchestration behavior changes in the core run loop

## Why Keep This Separation

Mixing planned frameworks with as-built behavior causes operator confusion and weakens observability.

Rule used in this repo:
- if it exists in runtime behavior and tests, mark as implemented
- if it is design intent only, mark as roadmap
