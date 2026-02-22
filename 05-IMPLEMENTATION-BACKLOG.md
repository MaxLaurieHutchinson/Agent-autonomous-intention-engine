# Implementation Backlog (Saga Format)

## Saga S01 - Unify the Engine
Narrative goal: Replace fragmented systems with one autonomous Intention Engine.

### Chapter C01 - Canonical Runtime Setup
- [ ] I001 Create `memory/PHILOSOPHY.md` runtime copy/symlink
- [ ] I002 Create proposal/briefing/metrics runtime directories
- [ ] I003 Create canonical `memory/REFLECT.md`
- [ ] I004 Update boot sequence docs to load canonical files only

### Chapter C02 - Proposal Pipeline
- [ ] I005 Define proposal markdown template with frontmatter
- [ ] I006 Build router logic (`auto_safe`, `policy_guarded`, `human_gate`)
- [ ] I007 Auto-insert approved proposals into saga chapters in `memory/INTENT.md`
- [ ] I008 Add rejection/defer workflows with reasons

### Chapter C03 - Scout Runtime
- [ ] I009 Merge DayDream TIME + Ash Time into one runtime prompt
- [ ] I010 Implement micro-scout trigger on idle
- [ ] I011 Implement nightly deep scout job
- [ ] I012 Implement budget circuit breaker and quality throttling
- [ ] I012a Normalize `ash-time-system-v3.md` into a single canonical prompt (dedupe + path fixes + language normalization)
- [ ] I012b Implement opportunity scoring formula `(Value x Urgency) / (Effort x Risk)` in proposal ranking
- [ ] I012c Implement sub-agent spawn gates (independence, budget, max parallel = 3)
- [ ] I012d Add reflective checkpoints every 20 minutes or 0.05 budget spend

### Chapter C04 - Execution and Reflection
- [ ] I013 Introduce worker role templates (Scout/Analyst/Planner/Builder/Critic/Reflector)
- [ ] I014 Enforce evidence target before completion
- [ ] I015 Write reflection auto-entry template
- [ ] I016 Capture reusable patterns into `memory/knowledge/`

## Saga S02 - Proactive Value Delivery
Narrative goal: Make the engine proactively useful every day without needing prompts.

### Chapter C05 - Briefings and Digests
- [ ] I017 Consolidate to one morning briefing template
- [ ] I018 Add weekly Discovery Digest generation
- [ ] I019 Add weekly KPI report from `memory/metrics/`

### Chapter C06 - Deadline and Staleness Recovery
- [ ] I020 Auto-detect intentions nearing deadlines (<72h)
- [ ] I021 Auto-propose unblock actions for stale tasks (>3 days)
- [ ] I022 Auto-replan `NOW` list when capacity changes

## Definition of Done for This Project
- [ ] Fragmented naming removed from operational docs
- [ ] Canonical architecture in active use
- [ ] Proposal pipeline active and measurable
- [ ] Proactive automations running on schedule
- [ ] Daily operations visibly aligned to `PHILOSOPHY.md`
