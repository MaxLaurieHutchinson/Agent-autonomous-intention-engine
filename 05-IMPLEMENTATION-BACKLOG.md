# Implementation Backlog (Saga Format)

## Saga S01 - Runtime Hardening
Narrative goal: make runtime deterministic, portable, and safe-by-default.

### Chapter C01 - CLI and Config
- [x] I001 Subcommand CLI (`run`, `status`, `validate`, `replay`)
- [x] I002 Legacy `--mode` compatibility shim
- [x] I003 Add `mode_profiles` with disabled `research_deep`
- [x] I004 Add runtime config schema

### Chapter C02 - Guardrails and Routing
- [x] I005 Config-driven routing thresholds
- [x] I006 Human-gate keyword enforcement
- [x] I007 Default `allow_policy_guarded_auto=false`

### Chapter C03 - Determinism and Operability
- [x] I008 Replay bundles per run
- [x] I009 Structured runtime logs
- [x] I010 Status health contract with announce-failure visibility

## Saga S02 - Runtime Alignment
Narrative goal: remove drift between docs, wrappers, and execution surfaces.

### Chapter C04 - Command Alignment
- [x] I011 Add canonical `ops/ie_*` wrappers
- [x] I012 Add orchestrator v2 cron template
- [x] I013 Add cron job reconciliation script

## Saga S03 - Quality and Docs
Narrative goal: make DEV branch reviewable and easy to adopt.

### Chapter C05 - Validation
- [x] I014 Add unit/integration tests
- [x] I015 Add CI compile + test + smoke checks

### Chapter C06 - Narrative Pack
- [x] I016 Refresh README + CHANGELOG
- [x] I017 Refresh root docs `01..10`

## Deferred
- [ ] D001 Enable and orchestrate `research_deep`
- [ ] D002 Academic multi-agent long-loop execution model
