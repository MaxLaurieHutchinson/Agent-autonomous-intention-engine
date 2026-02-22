# Migration Plan to One Coherent Project

## Target
Consolidate DayDream + Ash Time + Intention + Intention Engine into a single operational system under `Intention Engine`.

## Phase 1 - Foundation (Day 1)
1. Create canonical design/docs folder (done).
2. Set constitutional source:
- Keep `<WORKSPACE>/projects/Intention/philosophy/PHILOSOPHY.md` as source of truth.
- Create runtime copy or symlink at `<WORKSPACE>/memory/PHILOSOPHY.md`.
3. Create missing runtime directories:
- `memory/proposals/{inbox,approved,rejected,deferred}`
- `memory/briefings`
- `memory/metrics`

## Phase 2 - State Unification (Day 1-2)
1. Keep `memory/INTENT.md` as canonical backlog.
2. Create `memory/REFLECT.md` canonical file and migrate recent DayDream reflections.
3. Treat `memory/knowledge/` as canonical tactical knowledge.
4. Mark `DAYDREAM_KNOWLEDGE.md` as deprecated and stop loading it in boot instructions.

## Phase 3 - Runtime Unification (Day 2-4)
1. Merge `DayDream TIME` and `Ash Time` into one Scout runtime template.
2. Implement proposal frontmatter contract and router.
3. Add auto-routing logic by autonomy class.
4. Ensure every approved proposal is auto-linked to a saga/chapter in `memory/INTENT.md`.
5. Normalize `ash-time-system-v3.md` into a canonical prompt:
- Remove duplicate prompt blocks.
- Resolve budget model to `£2.00/day` with reserve model.
- Normalize references from `boss` to `human`.
- Normalize all filesystem paths to workspace-accurate absolute paths.

## Phase 4 - Automation and Proactivity (Day 4-7)
1. Wire heartbeat loop to trigger micro-scouts and stale-task recovery.
2. Standardize morning briefing generation from one template.
3. Add weekly digest generation from proposal history.
4. Add weekly archive and metric rollup jobs.

## Phase 5 - Stabilization (Week 2)
1. Run in shadow mode for 3 days (observe decisions without acting on guarded classes).
2. Compare output quality and cost vs current state.
3. Promote to full mode and remove legacy duplicate templates.

## Deprecation Map

| Legacy Artifact | Action |
|---|---|
| `memory/DAYDREAM_KNOWLEDGE.md` | Deprecate; replace with `memory/knowledge/` |
| Separate DayDream/Ash Time naming | Keep as module names only |
| Multiple autonomous prompt variants | Keep one canonical Scout runtime prompt |
| Parallel backlog formats | Standardize on saga/chapter/intention in `memory/INTENT.md` |
| Mixed budget rules in prompts | Standardize to one daily budget policy |

## Exit Criteria
- One boot sequence
- One canonical backlog format
- One discovery runtime
- One proposal pipeline
- One briefing pipeline
- Philosophy-linked decisions enforced everywhere
