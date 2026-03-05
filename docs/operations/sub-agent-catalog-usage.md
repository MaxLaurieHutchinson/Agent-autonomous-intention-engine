# Sub-Agent Catalog Usage (Manual Model)

This project exposes a full specialist prompt repertoire via a pinned submodule:
- `external/agency-agents`

The usage model in this phase is explicit/manual selection only.

## Why Manual in This Phase

- preserves deterministic runtime behavior
- avoids hidden orchestration side effects
- keeps human-in-the-loop control for specialist invocation
- keeps V3 scope aligned with radical simplicity

## Source and Attribution

Catalog source:
- fork: `https://github.com/MaxLaurieHutchinson/agency-agents`
- pinned submodule commit: `c6c51b4`

Upstream credit:
- original repertoire foundation: `https://github.com/msitarzewski/agency-agents`

## Access Pattern

1. Pick specialist from [Sub-Agent Roster](../reference/sub-agent-roster.md).
2. Read the selected agent markdown file in `external/agency-agents/<division>/<agent>.md`.
3. Apply specialist guidance explicitly in current task.
4. Record which specialist was used in PR notes/evidence for traceability.

## Guardrails

- no runtime auto-spawn behavior in this phase
- no hidden policy-based specialist invocation
- any future orchestration hooks must be explicit, toggle-gated, and replay-traceable

## Recommended Starter Sets

High-signal set for current V3 execution:
- `testing/testing-reality-checker.md`
- `product/product-sprint-prioritizer.md`
- `specialized/agents-orchestrator.md`
- `engineering/engineering-ai-engineer.md`
- `support/support-analytics-reporter.md`

## Validation

Use:

```bash
python scripts/validate_subagent_repertoire.py
```

Validation ensures:
- submodule commit is pinned
- 51 specialists are present across expected divisions
- frontmatter completeness for specialist metadata
- no broken local markdown links in submodule docs
