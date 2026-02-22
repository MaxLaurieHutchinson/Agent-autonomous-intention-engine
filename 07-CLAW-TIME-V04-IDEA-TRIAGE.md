# CLAW TIME v0.4 Idea Triage

Reviewed source:
- `<WORKSPACE>/projects/openclaw/CLAW_TIME_BRIEF_v0.4.md`
- `<WORKSPACE>/projects/openclaw/UBIQUITOUS_LANGUAGE.md`
- `<WORKSPACE>/projects/openclaw/CODEX_REVIEW_PROMPT.md`

Goal: keep the useful ideas, remove over-complication, and align to the unified Intention Engine.

## Decision Matrix

### Keep (Adopt Now)
1. Agent Loop Driver as stateless runner.
Reason: aligns with current file-first architecture and keeps runtime simple.

2. OODA as the canonical execution loop.
Reason: already central to Intention Engine; low complexity, high clarity.

3. Reflection Engine concept (multi-perspective synthesis).
Reason: useful when bounded; map to Scout/Builder/Critic/Reflector roles.

4. Skill-first approach ("everything is a skill").
Reason: reusable operational unit; compatible with current workflow.

5. Semantic fallback principle.
Reason: reliability win; should be implemented as controlled rollback for prompt/templates/workflows.

### Simplify (Adopt with Constraints)
1. "Neurons" bundle (`SKILL.md` + metadata + validation).
Keep concept, simplify implementation:
- Use existing skill format first.
- Add only minimal metadata in one file (`neuron.json`) when needed.
- Avoid deep folder version trees until usage justifies it.

2. Parallel orchestration (Gastown-style references).
Keep bounded model only:
- max parallel workers = 3.
- only when tasks are independent + budget allows.
- default serial execution.

3. Ralph Loop / machine-verifiable completion.
Keep as optional per workflow:
- use for high-risk automations and scripts.
- do not force on all exploratory/research tasks.

4. WebMCP-native execution idea.
Keep as future-compatible preference, not hard dependency:
- first strategy: use native tool/API available.
- fallback: current browser automation.
- do not block runtime on WebMCP adoption.

### Drop (Too Much for Now)
1. Fully autonomous self-installing evolutionary skills.
Drop for production v1.
Why: high blast radius and governance complexity.
Replacement: proposal-only skill evolution with human gate for install/activation.

2. "Collective intelligence" as a primary product layer.
Drop as core requirement.
Why: narrative-heavy framing can obscure practical execution.
Replacement: keep concrete role outputs and reflection summaries.

3. Large-scale persistence concerns ("thousands of runs") as immediate design driver.
Drop for now.
Why: premature scaling pressure.
Replacement: file-based state + optional SQLite later if bottlenecks appear.

## Hard Boundaries for v1
- No autonomous skill installation.
- No autonomous external public actions.
- No uncontrolled self-modification loops.
- No new infrastructure layer unless an observed bottleneck demands it.

## What to Pull Into Intention Engine Immediately
- Add "Semantic Fallback" to runtime policies.
- Add optional validation hooks to high-risk workflows.
- Add a simple role-based multi-agent reflection template.

## Suggested v1.1 Additions (Small, Concrete)
1. `memory/policies/fallbacks.md` for rollback rules.
2. `memory/templates/proposal-skill-evolution.md` for safe skill upgrade proposals.
3. `memory/templates/reflection-multi-role.md` for role synthesis (Scout/Builder/Critic).

## Final Recommendation
Use CLAW TIME v0.4 as an idea mine, not as the implementation blueprint.
Adopt its strongest execution mechanics, but keep Intention Engine's current minimalist architecture and governance model.
