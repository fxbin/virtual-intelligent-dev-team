# Project Knowledge Pyramid Protocol

Use this protocol when the team is working against a target codebase large or
unfamiliar enough that a single context cannot hold it. The goal is a layered,
always-fresh map of that target project so later steps — routing, planning,
`references/change-localization-protocol.md` — operate from accurate ground
truth instead of stale memory.

This protocol governs knowledge about the **target project being worked on**,
not about this skill's own internals.

## When To Activate

Activate when any of these appear:

- onboarding to a large or unfamiliar target repository
- cross-session handoff where the next session needs the project's structure
- the `plan-first-build` bundle reaches its "create compact system map" step
- recurring edits to a project whose module shape drifts over time
- a localization step (see
  `references/change-localization-protocol.md`) keeps landing on the wrong sites

Do not activate for a one-off edit to a project already held in working memory,
or when the target is a single small file.

## Goal

Maintain a three-tier map of the target project and keep it from going stale.
Each tier carries a different resolution and a different load policy, so the
team reads only the tier the current step needs.

## Three-Tier Pyramid

- **L1 — Overview (preloaded by default)**
  - a single table kept under `5KB` listing the project's modules and their
    one-line responsibilities
  - small enough to live in context for every request against this project
  - source of the "which module family" answer used by localization step 1
- **L2 — Module-level (loaded on demand)**
  - machine-readable per-directory metadata recording the files under each
    module and what each does — a street-level map
  - read only when a step narrows to that module; never preloaded wholesale
  - source of the candidate paths used by localization step 2
- **L3 — Semantic bridge (mandatory reference)**
  - the exact mapping from external tokens (design-system tokens, API field
    names, protocol keys) to engineering identifiers in code
  - treated as authoritative: when the bridge covers a token, code must resolve
    through the bridge and must not hardcode the raw constant (color, size,
    field name) instead
  - closes the gap between design/contract surfaces and implementation

## Drift Detection

A map that is wrong is worse than no map. Keep it fresh:

- record a SHA baseline for every file the pyramid describes
- run a drift check (for example a pre-commit hook) that flags any described
  file whose current SHA no longer matches the baseline
- when a stale signal fires, block the commit and require the pyramid entry to
  be refreshed before proceeding
- the check is a script, per the
  `references/anti-entropy-governance.md` data-channel constraint; the LLM
  reads the drift report, it does not self-assess freshness

## Relationship To Harness Constraints

This protocol complements, and does not replace,
`references/harness-engineering-constraint-protocol.md`:

- the harness constraint file (`.vidt/harness/engineering-constraints.md`)
  governs the **current change** — what is in scope, what is forbidden, what
  evidence closes this task
- this pyramid governs the **target project** — its durable shape, across
  changes and across sessions

Read the pyramid to know where things are; read the harness constraints to know
what this particular change may touch.

## Relationship To System Map

`references/system-map-protocol.md` produces a one-time relational view for a
specific task. This pyramid is the persisted, drift-checked substrate that a
system map is drawn from. When a system map is requested, prefer building it
from the L1/L2 tiers rather than re-discovering the structure from scratch.

## Worktree Behavior

The pyramid and its SHA baseline live in **state-root** (the main repository),
not in any individual worktree. Worktrees share one `.git` but have independent
working trees; the baseline records the main repository's HEAD so drift
detection compares against a stable reference rather than a per-worktree
snapshot. A worktree that needs the map reads it from state-root and never
writes its own copy. See
`references/worktree-state-placement-protocol.md` for state-root resolution.

## Completion Evidence

When this protocol is active, completion must name:

- which tiers were created or refreshed
- the drift baseline recorded (and where)
- any stale entries found and how they were resolved
- whether the pyramid changed the selected workflow bundle's scope or the
  localization candidates
