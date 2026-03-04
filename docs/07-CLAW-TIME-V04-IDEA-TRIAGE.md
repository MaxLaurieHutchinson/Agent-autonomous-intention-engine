# CLAW TIME v0.4 Idea Triage (v2.1)

## Goal
Keep useful concepts from CLAW TIME discussions while avoiding architecture bloat.

## Keep (Adopted)
1. Single loop driver with explicit operational contract.
2. OODA framing for discovery and action sequencing.
3. Skill-first execution surfaces via wrappers and scripts.
4. Failure visibility as first-class behavior.

## Simplify (Adopt with Limits)
1. Multi-agent expansion: keep deferred to `research_deep` phase.
2. Complex scheduler orchestration: keep cron template + reconciliation script only.
3. Rich telemetry pipelines: start with JSONL logs and replay bundles.

## Defer (Not in v2.1)
1. Autonomous long-loop research fleets.
2. Distributed sub-agent execution graph.
3. Cross-provider orchestration control plane.

## Decision Rule
When in doubt, choose lower surface area with stronger observability.
