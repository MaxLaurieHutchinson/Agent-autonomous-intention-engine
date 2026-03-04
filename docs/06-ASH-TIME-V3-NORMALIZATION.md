# Ash Time v3 Normalization (v2.1 Mapping)

## Source Intent Preserved
From the Ash Time v3 lineage, v2.1 retains:
- OODA execution rhythm
- budget-aware operation
- opportunity scoring and ranking discipline
- explicit reflection outputs

## What Was Simplified
- collapsed overlapping prompt variants into one runtime contract
- removed duplicated command surfaces and ambiguous operator paths
- replaced mixed policy semantics with explicit routing classes

## v2.1 Concrete Mapping
- OODA runtime -> `scripts/intention_engine.py run --mode micro|deep`
- Budget model -> `config/runtime.json` (`daily_budget_gbp`, `reserve_budget_gbp`, per-mode cost caps)
- Reflection -> `memory/REFLECT.md` + replay bundle artifacts
- Guardrails -> `routing` config + `classify_risk` + deterministic routing

## Constraints Introduced by Design
- safe-by-default: policy-guarded items remain inbox by default
- disabled advanced mode in this phase: `research_deep.enabled=false`
- reproducibility required for every run via replay bundle

## Outcome
Ash Time principles survive as behavior, not duplicate infrastructure.
