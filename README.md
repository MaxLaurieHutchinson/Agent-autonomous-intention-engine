# Intention Engine

Intention Engine is a deterministic, file-first autonomous decision loop for discovering work, routing risk, and producing auditable outputs.

It is designed for two realities at once:
- operator-first use in an OpenClaw workspace
- clean packaging and documentation for public reuse

## Core Contract

Install and use the canonical CLI:

```bash
python3 -m pip install -e .
```

```bash
intention-engine --config config/runtime.json run --mode <micro|deep|research_deep> [--dry-run]
intention-engine --config config/runtime.json status --json
intention-engine --config config/runtime.json validate --json
intention-engine --config config/runtime.json replay --run-id <run-id>
```

Workspace bootstrap:

```bash
bash ops/bootstrap-workspace.sh
```

## How It Works

One run follows this sequence:

1. Observe: pull candidates from configured sources.
2. Orient: extract weighted keywords from context sources (INTENT, PHILOSOPHY, knowledge files) and score candidates.
3. Decide: classify risk (`auto_safe`, `policy_guarded`, `human_gate`) and route (`approved`, `inbox`, `deferred`).
4. Act: persist proposals and update budget state (unless `--dry-run`).
5. Reflect: write replay bundle, metrics rollup, and a reflection entry.

## Runtime Artifacts

- proposals: `memory/proposals/{approved,inbox,deferred,rejected}`
- budget state: `data/intention-engine-budget.json`
- replay bundles: `data/intention-engine-runs/<run-id>/`
- metrics: `memory/metrics/intention-engine-YYYY-MM-DD.json`
- logs: `logs/engine.jsonl`
- reflections: `memory/REFLECT.md`

## Philosophy and Safety

`philosophy/PHILOSOPHY.md` (or configured `memory/PHILOSOPHY.md`) is actively used in scoring through keyword extraction.

Safe defaults in `config/runtime.json`:
- `allow_policy_guarded_auto = false`
- `research_deep.enabled = false`

Discovery defaults are zero-secrets in this phase:
- typed source adapters only (`reddit`, `hackernews`, `github`, `fixture`, `rss`, `arxiv`)
- no API-key integrations enabled in core runtime contract

## OpenClaw Scheduling Model

- Heartbeat (workspace-level) should trigger interruption-aware micro decisions.
- Cron (isolated runs) should own fixed-time deep run and morning brief orchestration.
- `cron/` contains prompts/templates.
- `agents/cron/` contains executable reconciliation scripts.

## Documentation

Read the full handbook at [docs/INDEX.md](docs/INDEX.md).
Governance contract: [docs/governance/engineering-governance.md](docs/governance/engineering-governance.md).

## Fresh Clone Setup

1. Bootstrap workspace state:
   - `bash ops/bootstrap-workspace.sh`
2. Validate config and paths:
   - `intention-engine --config config/runtime.json validate --json`
3. Run a dry micro smoke:
   - `intention-engine --config config/runtime.json run --mode micro --dry-run`

## Stability Status

Implemented now:
- deterministic OODA-style run loop
- risk-aware routing and guardrails
- replayability and operational health surfaces
- weighted context-source cognitive orientation
- adapter-based source discovery with deterministic filters and canonical dedupe

Planned (not implemented as first-class runtime modules yet):
- explicit BDI state model
- Rubber Duck multi-agent reasoning loops
