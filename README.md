# Intention Engine

[![CI](https://github.com/MaxLaurieHutchinson/Agent-autonomous-intention-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/MaxLaurieHutchinson/Agent-autonomous-intention-engine/actions/workflows/ci.yml)

Intention Engine is a deterministic, file-first decision loop for discovering work, routing risk, and producing replayable outputs.

## Evidence Boundary

This repository is a working reference implementation, not a production service or a claim of unconstrained autonomy. It currently proves:

- config-driven candidate scoring and risk routing
- human gates for sensitive or externally consequential work
- persisted inputs, scores, decisions, budget state, logs, and replay bundles
- deterministic replay of route decisions from captured decision values and routing configuration
- tested core behaviour on Linux and Windows

It does not provide a hosted control plane, distributed execution, multi-user access control, or evidence of production adoption. The OpenClaw scheduling layer is an optional operator integration; the Python runtime remains independently executable.

It is designed for two operating contexts:
- operator-first use in an OpenClaw workspace
- clean packaging and documentation for public reuse

## Why Deterministic Routing

The engine deliberately separates discovery from decision execution. External sources can change between runs. The current replay contract reruns routing against the captured score, relevance, autonomy class, and routing configuration; it does not refetch sources or recompute candidate scoring. This narrow contract makes the final route inspectable without claiming a broader replay capability than the code provides.

## Core Contract

Canonical runtime entrypoint:

```bash
python -m pip install -e .
python -m intention_engine_core.cli --config config/runtime.json run --mode <micro|deep|research_deep> [--dry-run]
```

Other commands:

```bash
python -m intention_engine_core.cli --config config/runtime.json status --json
python -m intention_engine_core.cli --config config/runtime.json validate --json
python -m intention_engine_core.cli --config config/runtime.json replay --run-id <run-id>
```

Wrapper commands:

```bash
bash ops/ie_micro.sh
bash ops/ie_deep.sh
bash ops/ie_status.sh
```

Workspace bootstrap:

```bash
bash ops/bootstrap-workspace.sh
```

## How It Works

One run follows this sequence:

1. Observe: pull candidates from configured sources.
2. Orient: extract keywords from `memory/INTENT.md` plus philosophy text and score candidates.
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

## Inspect One Run and Replay

The repository includes an offline fixture configuration so the decision path can be reproduced without network discovery:

```bash
python -m intention_engine_core.cli --config config/audited-example.json validate --json
python -m intention_engine_core.cli --config config/audited-example.json run --mode micro
python -m intention_engine_core.cli --config config/audited-example.json replay --run-id <run-id>
```

Use the `run_id` from the second command. Then inspect `data/audited-example/runs/<run-id>/inputs.json`, `scores.json`, `decisions.json`, and `config-hash.txt`. The replay succeeds only when the recomputed routes match the captured decisions. See [docs/audited-run.md](docs/audited-run.md) for the decision walkthrough and limits of the evidence.

## Philosophy and Safety

`philosophy/PHILOSOPHY.md` (or configured `memory/PHILOSOPHY.md`) is actively used in scoring through keyword extraction.

Safe defaults in `config/runtime.json`:
- `allow_policy_guarded_auto = false`
- `research_deep.enabled = false`

## OpenClaw Scheduling Model

- Heartbeat (workspace-level) should trigger micro checks and interruption-aware behavior.
- Cron (isolated runs) should own fixed-time deep run and morning brief orchestration.
- `cron/` contains prompt/templates.
- `agents/cron/` contains executable job reconciliation scripts.

## Documentation

Read the full handbook at [docs/INDEX.md](docs/INDEX.md).

## Fresh Clone Setup

1. Install the package:
   - `python -m pip install -e .`
2. Bootstrap workspace state:
   - `bash ops/bootstrap-workspace.sh`
3. Validate config and paths:
   - `python -m intention_engine_core.cli validate --json`
4. Run a dry micro smoke:
   - `bash ops/ie_micro.sh --dry-run`

## Stability Status

Implemented and tested now:
- deterministic OODA-style run loop
- risk-aware routing and guardrails
- replayability and operational health surfaces

Planned (not implemented as first-class runtime modules yet):
- explicit BDI state model
- Rubber Duck multi-agent reasoning loops
