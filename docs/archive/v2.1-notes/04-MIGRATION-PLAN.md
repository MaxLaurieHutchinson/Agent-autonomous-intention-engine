# Migration Plan: MAIN -> DEV (v2.1)

## Target
Prepare a clean DEV branch with v2.1 runtime + full notes pack, without disturbing PR #1.

## Phase 1 - Branching
1. Clone fresh from `main`.
2. Create `dev` from `origin/main`.
3. Keep `codex/runtime-hardening-v1-0-1` untouched.

## Phase 2 - Runtime Port
1. Port runtime core:
- `src/intention_engine_core/runtime.py`
- `src/intention_engine_core/path_resolver.py`
- `src/intention_engine_core/cli.py`
2. Port config + schema:
- `config/runtime.json`
- `config/runtime.schema.json`
3. Port ops/cron helpers:
- `ops/ie_micro.sh`, `ops/ie_deep.sh`, `ops/ie_status.sh`
- `cron/templates/intention-engine-orchestrator-v2.md`
- `agents/cron/reconcile-intention-engine-jobs.sh`

## Phase 3 - Portability and Hygiene
1. Normalize repo-root path behavior.
2. Ensure `.gitignore` excludes generated runtime outputs.
3. Keep wrappers executable.

## Phase 4 - Notes and Runbook
1. Update `README`, `CHANGELOG`, and `01..10` docs to v2.1 reality.
2. Keep numbered docs pack under `docs/` for consistency.

## Phase 5 - Verification
1. Run compile checks and unit/integration tests.
2. Run validate + micro dry-run + status smoke.
3. Add CI workflow to enforce baseline checks.

## Phase 6 - Delivery
1. Push `dev`.
2. Open PR `dev -> main` with intent/decisions/evidence.
3. Note overlap with PR #1 in PR description.
