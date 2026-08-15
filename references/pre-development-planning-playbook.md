# Pre-Development Planning Playbook

Use this playbook when the request is not "just implement it", but "rewrite this", "migrate that", "overhaul the project", "plan before coding", or "start the next broad Epic after a release/phase transition".

This is a lightweight planning branch for `virtual-intelligent-dev-team`, not a full replacement for execution routing.

## When To Enter This Branch

Enter when the user asks for one or more of these:

- rewrite a project or major subsystem
- migrate language, framework, architecture, or deployment shape
- project-wide refactor with unclear task boundaries
- plan first, code later
- phase the work before implementation starts
- start a new broad Epic after several delivery/release slices where roadmap, Issues, or production truth may have drifted

Do not force this branch for simple single-feature work.

## Goals

Before coding starts, produce enough structure to keep the transformation stable:

1. lock scope, target state, constraints, and priorities
2. reconcile current project truth when the plan follows a release, major migration, Product Gate, or multi-Issue delivery train
3. analyze the current system at the level needed for planning
4. produce a compact system map when the target area is unfamiliar or multi-module
5. produce a phased task breakdown with vertical slices and acceptance criteria
6. note `AFK` / `HITL` boundaries, parallel lanes, and merge risk when multi-agent execution is realistic
7. create a durable progress anchor that future sessions can resume from

## Default Lead Shape

- Default lead: `Technical Trinity`
- Escalate or attach `Sentinel Architect (NB)` when the request is high-risk, research-first, production-sensitive, or conflict-heavy
- Add `Git Workflow Guardian` only when branch / worktree / PR delivery is already part of the ask
- Add `World-Class Product Architect` when the new Epic depends on a product/validation gate or when stale roadmap priorities may change what should be built next

## Minimum Planning Pack

Create or refresh these artifacts when the branch is active:

- `docs/analysis/project-overview.md`
- `docs/plan/task-breakdown.md`
- `docs/progress/MASTER.md`
- `docs/progress/phase-1-<name>.md`
- the remaining default phase trackers such as `docs/progress/phase-2-architecture.md`, `phase-3-execution.md`, and `phase-4-cutover.md`

## Optional Artifacts

Add these only when complexity warrants them:

- `docs/analysis/module-inventory.md`
- `docs/analysis/risk-assessment.md`
- `docs/plan/dependency-graph.md`
- `docs/plan/milestones.md`
- additional `docs/progress/phase-N-<name>.md` files beyond the default multi-phase skeleton
- a project-truth reconciliation result when current runtime/repository/Issue/decision artifacts may disagree

## Resume Protocol

If `docs/progress/MASTER.md` already exists:

- read it first
- identify the active phase and next step
- continue from the recorded resume point
- do not restart planning from scratch unless the user changed the transformation goal

If a canonical roadmap/master Issue exists, compare it with the progress anchor instead of assuming the older artifact is still current.

## Project-Truth Preflight

Before planning a broad next phase after a release, migration, or Product Gate, apply `references/project-truth-reconciliation-protocol.md` when drift is plausible.

At minimum classify existing work:

```text
NOW
GATED
LATER
STALE
```

Check especially for:

- Issues whose prerequisites conflict with the current Master/Roadmap decision;
- completed work still shown as open/current;
- paused platform work accidentally listed as next;
- stale external resource IDs, migration names, branch names, commands, or endpoints;
- a release that is merged but not production-verified;
- a post-release hotfix that changed an invariant without updating canonical docs.

Do not plan a broad new Epic from materially contradictory truth sources.

## Planning Flow

1. Confirm the transformation goal:
   - scope
   - target state
   - hard constraints
   - primary priority
   - reference-bounded scope — any trigger-style or interception-style
     interaction in the scope must carry a concrete reference basis: a design
     link, a doc verbatim quote, or a user verbatim quote. Do not advance a
     change on inferred business intent alone. Prefer a strong-signal keyword
     checklist for scope identification over free-form semantic judgment, and
     record which reference backs each trigger so later phases can audit it
2. Reconcile truth when required:
   - runtime state
   - default-branch/repository state
   - Issue/PR state
   - canonical roadmap/decision state
   - external resource identifiers
   - active vs gated vs stale work
3. Analyze only what is needed:
   - architecture and entry points
   - key modules and dependencies
   - major risks and coupling
   - system map using `references/system-map-protocol.md` when module ownership or callers are unclear
4. Produce the plan:
   - phases
   - vertical slices using `references/vertical-slice-delivery-protocol.md`
   - acceptance criteria
   - dependencies
   - `AFK` / `HITL` classification
   - optional parallel lanes and merge-risk notes
   - release-train shape only when several slices genuinely need one integration candidate
5. Create the progress anchor:
   - current phase
   - next step
   - blockers
   - session log
   - canonical truth sources
   - explicit gated/paused work
6. Hand back to normal execution routing:
   - implementation work returns to the standard lead / assistant / governance path
   - optimization work returns to bounded iteration
   - production-bound work adds `production-bound-delivery-protocol.md`
   - multi-PR integrated release work adds `release-train-protocol.md`
   - ship / hold decisions return to release gate

## Output Expectations

When this branch is active, the user-facing answer should include:

1. what transformation is being planned
2. what artifacts were created or refreshed
3. what truth sources were reconciled, if applicable
4. what the first execution phase is
5. what future sessions should read first
6. whether `.vidt/context/project-context.md` now carries the planning resume context
7. what work is explicitly gated/paused rather than merely omitted

For the user-facing answer shape, use:

- `references/pre-development-output-template.md`

## Templates

Use only the templates you need:

- `assets/pre-development-project-overview-template.md`
- `assets/pre-development-task-breakdown-template.md`
- `assets/pre-development-progress-master-template.md`
- `assets/pre-development-phase-template.md`
- `assets/project-context-template.md`
- `references/system-map-protocol.md`
- `references/vertical-slice-delivery-protocol.md`
- `references/project-truth-reconciliation-protocol.md`
