# Engineering Governance (Normative)

This is the mandatory operating contract for coding, pull requests, experiments, and GitHub publication.

## 1. Branch and PR Policy

- Branch naming must use `agent-{AgentName}/` for agent-authored work (for example, `agent-ash/<topic>` or `agent-codex/<topic>`).
- No direct pushes to `main` or `dev`.
- Every change lands via PR.
- PRs must be scoped and reviewable; avoid mixed concerns.

## 2. Commit and PR Evidence Requirements

Every PR must include:
- intent: what problem this solves
- decisions: key trade-offs and why
- evidence: exact commands and outcomes

Minimum evidence:
- tests executed
- validation command output
- dry-run or smoke run output for operational changes

## 3. Runtime Contract Guardrails

- Canonical CLI only: `intention-engine --config config/runtime.json ...`
- No legacy command shims.
- No wrapper contract in this phase.
- Human-activity gating belongs to heartbeat/orchestrator policy, not runtime internals.

## 4. Experiment Lifecycle Rules

Experiments must be explicit and bounded.

- Create experiment record before implementation.
- Define: hypothesis, scope, cost cap, abort conditions, and success criteria.
- Mark status as one of: `proposed`, `active`, `stopped`, `promoted`, `archived`.
- Promotion requires evidence that the experiment improves outcomes and preserves safety.

Use [Experiment Protocol](experiment-protocol.md) for the required template.

## 5. GitHub Publication Policy

Before publishing a project/repo or major update:
- remove secrets, private paths, and personal data
- ensure README + runbook + license exist
- confirm tests and validation pass on a fresh install
- add release notes with contract-impact summary

## 6. Safety and Operational Integrity

- default to safe routing (`allow_policy_guarded_auto=false`)
- do not enable `research_deep` by default
- preserve deterministic replay artifacts
- treat announce delivery failures as actionable operational errors
