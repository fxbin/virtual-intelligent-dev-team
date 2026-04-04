# Pre-Development Planning Playbook

Use this playbook when the request is not "just implement it", but "rewrite this", "migrate that", "overhaul the project", or "plan before coding".

This is a lightweight planning branch for `virtual-intelligent-dev-team`, not a full replacement for execution routing.

## When To Enter This Branch

Enter when the user asks for one or more of these:

- rewrite a project or major subsystem
- migrate language, framework, architecture, or deployment shape
- project-wide refactor with unclear task boundaries
- plan first, code later
- phase the work before implementation starts

Do not force this branch for simple single-feature work.

## Goals

Before coding starts, produce enough structure to keep the transformation stable:

1. lock scope, target state, constraints, and priorities
2. analyze the current system at the level needed for planning
3. produce a phased task breakdown with acceptance criteria
4. note parallel lanes and merge risk when multi-agent execution is realistic
5. create a durable progress anchor that future sessions can resume from

## Default Lead Shape

- Default lead: `Technical Trinity`
- Escalate or attach `Sentinel Architect (NB)` when the request is high-risk, research-first, production-sensitive, or conflict-heavy
- Add `Git Workflow Guardian` only when branch / worktree / PR delivery is already part of the ask

## Minimum Planning Pack

Create or refresh these artifacts when the branch is active:

- `docs/analysis/project-overview.md`
- `docs/plan/task-breakdown.md`
- `docs/progress/MASTER.md`
- `docs/progress/phase-1-<name>.md`

## Optional Artifacts

Add these only when complexity warrants them:

- `docs/analysis/module-inventory.md`
- `docs/analysis/risk-assessment.md`
- `docs/plan/dependency-graph.md`
- `docs/plan/milestones.md`
- additional `docs/progress/phase-N-<name>.md` files

## Resume Protocol

If `docs/progress/MASTER.md` already exists:

- read it first
- identify the active phase and next step
- continue from the recorded resume point
- do not restart planning from scratch unless the user changed the transformation goal

## Planning Flow

1. Confirm the transformation goal:
   - scope
   - target state
   - hard constraints
   - primary priority
2. Analyze only what is needed:
   - architecture and entry points
   - key modules and dependencies
   - major risks and coupling
3. Produce the plan:
   - phases
   - tasks
   - acceptance criteria
   - dependencies
   - optional parallel lanes and merge-risk notes
4. Create the progress anchor:
   - current phase
   - next step
   - blockers
   - session log
5. Hand back to normal execution routing:
   - implementation work returns to the standard lead / assistant / governance path
   - optimization work returns to bounded iteration
   - ship / hold decisions return to release gate

## Output Expectations

When this branch is active, the user-facing answer should include:

1. what transformation is being planned
2. what artifacts were created or refreshed
3. what the first execution phase is
4. what future sessions should read first

For the user-facing answer shape, use:

- `references/pre-development-output-template.md`

## Templates

Use only the templates you need:

- `assets/pre-development-project-overview-template.md`
- `assets/pre-development-task-breakdown-template.md`
- `assets/pre-development-progress-master-template.md`
- `assets/pre-development-phase-template.md`
