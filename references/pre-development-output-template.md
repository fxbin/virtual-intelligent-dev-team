# Pre-Development Planning Output Template

Use this template when the request is routed into the pre-development planning branch.

Keep the response compact. The goal is to make the transformation executable, not to dump a manual.

## Suggested User-Facing Shape

```markdown
## Planning Pack
- Transformation: <what is being rewritten / migrated / overhauled>
- Scope: <in scope>
- Target: <target state>
- Constraints: <hard constraints>
- Priority: <what matters most>

## Artifacts
- Created or refreshed:
  - docs/analysis/project-overview.md
  - docs/plan/task-breakdown.md
  - docs/progress/MASTER.md
  - docs/progress/phase-1-<name>.md

## First Execution Phase
- Phase 1 goal: <what phase 1 achieves>
- First task: <smallest executable next action>
- Parallel lanes: <none / brief lane summary>
- Merge risk: <low / medium / high>

## Resume Point
- Read first: docs/progress/MASTER.md
- Current status: <active phase / task>
- Blockers: <none / short note>
```

## Rules

- Keep the planning summary short enough to scan in one screen.
- Mention only the artifacts that actually exist.
- If the planning pack is partial by design, say what is intentionally deferred.
- If `docs/progress/MASTER.md` already existed, say that the plan was resumed rather than created fresh.
