# Audited Example Run

This walkthrough is a reproducible protocol check for the repository's decision and replay behaviour. It is not a benchmark, a production run, or evidence of user adoption.

## What the Fixture Exercises

The offline fixture includes fixed intent and philosophy inputs plus three deliberately different candidates:

| Candidate | Expected control | Reason |
| --- | --- | --- |
| Token rotation review | Human gate | `token` is configured as always requiring human review |
| Replay test summary | Config-driven route | No sensitive keyword overrides the score-based route |
| OAuth migration evaluation | Policy guarded | `oauth` and `migration` are configured guarded terms |

Exact route destinations also depend on the checked-in scoring thresholds and intent/philosophy keywords. The current replay command verifies the final routing calculation from captured decision values; it does not recompute candidate scoring from the original source items.

## Reproduce It

```bash
python -m pip install -e .
python -m intention_engine_core.cli --config config/audited-example.json validate --json
python -m intention_engine_core.cli --config config/audited-example.json run --mode micro
python -m intention_engine_core.cli --config config/audited-example.json replay --run-id <run-id>
```

The run command returns the `run_id`. The replay result should report `"status": "ok"` and an empty `mismatches` array.

## Inspect the Evidence

Open `data/audited-example/runs/<run-id>/` and review:

- `inputs.json`: the captured candidates and run context
- `scores.json`: computed values and autonomy classes
- `decisions.json`: selected routes
- `config-hash.txt`: the configuration fingerprint used by the run

These generated files are intentionally ignored by Git. They are local runtime evidence, not curated screenshots or pre-written expected output.

The fixture inputs remain under `fixtures/audited-example/`, so an unrelated local OpenClaw workspace cannot change this rehearsal.

## Claim Limit

This example demonstrates reproducibility and control routing against synthetic fixture data. It does not establish model quality, business value, throughput, production reliability, or the effectiveness of a live operator workflow.
