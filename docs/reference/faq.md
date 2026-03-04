# FAQ

## What does the engine actually do?

It continuously discovers candidate opportunities, scores and routes them with guardrails, and writes auditable artifacts (proposals, metrics, replay bundles, logs, reflections).

## Where is OODA used?

OODA is implemented behaviorally in the run pipeline:
- Observe: source discovery
- Orient: keyword extraction + scoring
- Decide: risk classification + routing
- Act: persistence + budget application
- Reflect: metrics/reflect/replay outputs

## Is BDI implemented?

Not as explicit runtime model objects yet. Current behavior is BDI-like but implicit.

## Is Rubber Duck implemented?

Not as a first-class runtime module. It is planned as a future extension for structured challenge/reasoning loops.

## How does philosophy affect behavior?

`PHILOSOPHY.md` text is tokenized together with `INTENT.md`; extracted keywords influence candidate relevance scoring.

## What are proposals?

Markdown decision artifacts that represent routed opportunities. They are persisted into queue directories (`approved`, `inbox`, `deferred`, `rejected`).

## What are metrics?

Daily JSON rollups of run summaries. They track operational throughput, route outcomes, budget progression, and discovery error counts.

## What belongs in cron vs heartbeat?

- Heartbeat: short, interruption-aware micro checks.
- Cron: fixed-time isolated jobs (deep run, brief generation).

## What is `agents/cron` vs `cron`?

- `cron/` stores templates/prompts.
- `agents/cron/` stores executable scripts that patch or reconcile live scheduler payloads.

## Why does `status` show `degraded`?

Any of these can degrade health:
- config validation errors
- detected announce-delivery failures in OpenClaw jobs state
- recent runtime errors in logs

## Why can `validate` return warnings with `status: ok`?

`validate` distinguishes hard config errors from operational readiness warnings (for example missing `memory/INTENT.md`).
