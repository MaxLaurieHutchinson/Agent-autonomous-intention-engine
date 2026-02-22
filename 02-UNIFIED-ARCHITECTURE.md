# Unified Architecture

## System Overview

```text
                  PHILOSOPHY (Constitution)
                            |
                            v
Scout Runtime -> OODA Filter -> Proposal Router -> Saga Planner -> Worker Runtime
      |              |                |                 |               |
      |              v                v                 v               v
Trend Sources    Alignment Score   Queue/Auto      INTENT.md      Artifacts/Outputs
(Reddit/HN/etc)  + Risk Class      Decision        (Sagas)        (docs/code/reports)
      |                                                                   |
      +-----------------------> Reflector + Evidence Engine <-------------+
                                      |
                                      v
                               REFLECT.md + knowledge/
```

## Canonical Runtime Files

Use these as active state files:
- `<WORKSPACE>/memory/PHILOSOPHY.md` (symlink or generated copy from project philosophy)
- `<WORKSPACE>/memory/INTENT.md`
- `<WORKSPACE>/memory/REFLECT.md`
- `<WORKSPACE>/memory/knowledge/`
- `<WORKSPACE>/memory/proposals/inbox/`
- `<WORKSPACE>/memory/proposals/approved/`
- `<WORKSPACE>/memory/proposals/rejected/`
- `<WORKSPACE>/memory/proposals/deferred/`
- `<WORKSPACE>/memory/briefings/`
- `<WORKSPACE>/memory/metrics/`

## Data Contracts

### Proposal Contract (`memory/proposals/inbox/*.md` frontmatter)
```yaml
id: P-2026-02-21-001
title: Evaluate MCP workflow for tool orchestration
source: reddit/r/LocalLLaMA
created_at: 2026-02-21T23:30:00+00:00
saga_id: S02
chapter_id: C05
alignment:
  philosophy: 0.90
  active_intent: 0.85
impact_score: 0.78
risk_score: 0.22
autonomy_class: policy_guarded
recommended_action: Run 60-minute spike and produce comparison memo
acceptance_test: Memo includes fit, effort, risk, and migration recommendation
```

### Intention Contract (`memory/INTENT.md` item)
Each intention must include:
- `id`
- `saga_id` and `chapter_id`
- `narrative_reason` (why this matters in the story)
- `status` (`NOW`, `NEXT`, `LATER`, `COMPLETED`, `BLOCKED`)
- `evidence_target` (what proof will exist when done)

## OODA Pipeline (Deterministic)
1. Observe
- Gather raw discoveries from configured sources.
- Normalize into candidate records.

2. Orient
- Score each candidate against:
  - Philosophy alignment
  - Active saga relevance
  - Cost/effort/risk
  - Evidence potential
- Keep top 2-5 high-signal candidates.

3. Decide
- Route by autonomy class:
  - `auto_safe`: auto-approve and schedule immediately
  - `policy_guarded`: auto-approve if policy allows, else queue
  - `human_gate`: queue for manual decision

4. Act
- Approved proposals become intentions under explicit saga/chapter.
- Worker runtime starts execution based on priority and capacity.

5. Reflect
- Capture what happened, what worked, what changed.
- Update tactical knowledge files when pattern quality is high.

## Narrative Enforcement Rules
- No orphan tasks: every task must belong to a saga and chapter.
- No blind execution: every proposal must include `narrative_reason`.
- No claim-only completion: each completed intention must link to evidence.

## Why This Solves the Current Fragmentation
- One loop instead of parallel systems
- One naming system
- One constitutional filter (`PHILOSOPHY.md`)
- One tactical library (`memory/knowledge/`)
- One proposal-to-intent bridge
