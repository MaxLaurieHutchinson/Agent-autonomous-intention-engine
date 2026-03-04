# Project Audit and Consolidation Decisions

## Scope Reviewed
- historical DayDream memory model
- Ash Time runtime model
- Intention philosophy layer
- prior Intention Engine proposal pipeline

## What We Keep (v2.1)
| Source | Strength Retained | v2.1 Outcome |
|---|---|---|
| DayDream | Markdown-first memory discipline | `memory/INTENT.md`, `memory/REFLECT.md`, proposal queues remain file-first |
| Ash Time v3 | OODA execution loop + cost awareness | Mode profiles and budget model in `config/runtime.json` |
| Intention | Constitutional decision filter | `philosophy/PHILOSOPHY.md` as policy source |
| Intention Engine (early) | Proposal scoring/routing pipeline | Deterministic run + replay bundle + status health contract |

## Risks Found in Earlier Versions
- hardcoded local paths in runtime core
- permissive policy defaults (`policy_guarded` auto-approval)
- command drift between heartbeat docs and real entrypoints
- weak operational replay/debug visibility

## v2.1 Decisions
1. One deployable runtime, two active modes (`micro`, `deep`) and one deferred mode (`research_deep` disabled).
2. Config-first path and threshold controls.
3. Safe-by-default guardrails.
4. Deterministic artifacts per run.
5. Wrapper-first execution contract for cron/heartbeat alignment.

## Out of Scope in This Phase
- full `research_deep` orchestration
- long-loop academic multi-agent execution layer
- autonomous external actioning beyond current policy boundaries
