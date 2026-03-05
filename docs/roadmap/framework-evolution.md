# Framework Evolution Roadmap (BDI + Rubber Duck)

This roadmap extends the current runtime without breaking its deterministic/file-first core.

## Principles for Evolution

- preserve current CLI contract
- keep replay determinism measurable
- add capabilities behind explicit config toggles
- avoid hidden autonomous behavior shifts

## Current Baseline

Implemented now:
- OODA run loop
- risk/routing guardrails
- replay bundles
- file-first state and logs

Not yet first-class:
- BDI state model
- Rubber Duck challenge loop

## Phase 1: Explicit BDI Layer (Planned)

Goal: make belief/desire/intention state explicit and inspectable.

Proposed additions:
- belief snapshot artifact per run (derived from sources/status/budget)
- desire model from intent + philosophy + queue pressure
- intention transition record (candidate -> proposal -> queue)

Constraints:
- no change to existing `run/status/validate/replay` command names
- replay must include BDI-derived fields deterministically

## Phase 2: Rubber Duck Challenge Loop (Planned)

Goal: improve decision quality for high-impact actions.

Proposed behavior:
- optional pre-route challenge stage for selected items
- structured contradiction checks on assumptions and risk labels
- challenge outcomes written to replay/decision artifacts

Activation model:
- off by default
- enabled per mode or per risk class through config

## Phase 3: Research-Deep Activation (Planned)

Goal: enable `research_deep` safely once observability and controls are sufficient.

Readiness gates:
- stable deep mode determinism
- bounded cost and checkpoint policy
- proven operator visibility on failure modes

## Backward Compatibility Policy

For framework evolution:
- preserve existing artifacts
- add new files/fields additively
- document versioned schema changes in `CHANGELOG.md`

## Success Criteria

- no loss of deterministic replay guarantees
- no ambiguity between implemented and planned behavior
- clean operator ergonomics for both local and OpenClaw deployment contexts
