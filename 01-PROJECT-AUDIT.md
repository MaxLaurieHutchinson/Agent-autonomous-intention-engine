# Project Audit and Consolidation Decisions

## Scope Reviewed
- `<WORKSPACE>/projects/DayDream`
- `<WORKSPACE>/projects/Ash-time`
- `<WORKSPACE>/projects/Intention`
- `<WORKSPACE>/projects/The-Intention-Engine`
- `<WORKSPACE>/memory/knowledge`

## What Each Project Is Good At

| Source | Strengths | Gaps | Keep | Merge Target |
|---|---|---|---|---|
| DayDream | Memory model (`INTENT/REFLECT/KNOWLEDGE`), workflow discipline, status markers | Name overlap, duplicated docs, split between monolith and modular knowledge | Keep memory loop and status patterns | Core Memory module |
| Ash Time | Autonomous runtime concepts, cost/budget controls, morning brief, approval queue | Separate identity from DayDream, multiple autonomy variants, no single canonical policy | Keep autonomous execution model and budgeting | Autonomy Runtime module |
| Intention | Philosophy and narrative-driven framing | Not operationalized end-to-end | Keep `PHILOSOPHY.md` as constitution | Constitution module |
| The-Intention-Engine | Bridge design between discovery and backlog, saga/chapter model, proposal flow | Still mostly conceptual, not fully wired to live runtime | Keep proposal + saga integration model | Decision and Planning module |
| memory/knowledge | Modular tactical library (`patterns/`, `frameworks/`, `insights/`) | Needs deterministic loading strategy and indexing | Keep as tactical library | Knowledge module |

## Ash Time v3 Prompt Extraction
From `<WORKSPACE>/ash/prompts/ash-time-system-v3.md`, keep these high-value mechanics:
- Dynamic OODA loop with explicit `Sense -> Orient -> Decide -> Act -> Reflect`.
- Opportunity scoring formula: `(Value x Urgency) / (Effort x Risk)`.
- Sub-agent spawn gates: independence threshold + budget threshold + max parallel cap.
- Dynamic budget allocation and reserve model.
- Reflection cadence and quality bar before surfacing outputs.
- Dynamic output mode selection (full brief, scannable, hybrid) based on signal level.

Conflicts to resolve in unification:
- Budget mismatch (`£0.05/session` vs `£2.00/day` appears in same file).
- Prompt includes duplicate sections and repeated architectures.
- Mixed path conventions (`/workspace/...` vs current workspace absolute paths).
- Tone naming (`boss`) should be normalized to `human`.

## Main Overlaps Creating Friction
- Two competing knowledge sources: `DAYDREAM_KNOWLEDGE.md` vs modular `memory/knowledge/`
- Two autonomy concepts: `DayDream TIME` vs `Ash Time`
- Multiple product names for one system
- Human approval model is inconsistent (strict in some docs, full autonomy in others)

## Consolidation Decisions
1. Canonical product name: `Intention Engine`.
2. `PHILOSOPHY.md` is the constitutional "why" layer.
3. `memory/knowledge/` is the tactical library. Deprecate monolithic `DAYDREAM_KNOWLEDGE.md`.
4. Unify `DayDream TIME` + `Ash Time` into one `Scout Runtime` with budget and policy classes.
5. Keep saga/chapter/intention structure for backlog to preserve narrative coherence.
6. Use one deterministic OODA pipeline from discovery to execution.

## Resulting Module Map
- Constitution: Intention philosophy
- Memory: Intent + Reflect + daily logs
- Knowledge: Modular library
- Scout Runtime: Autonomous trend and opportunity discovery
- OODA Filter: Relevance, alignment, risk scoring
- Planner: Converts proposals to saga-linked intentions
- Worker Runtime: Executes proactive tasks
- Evidence + Reflector: Validates outcomes, captures learnings
