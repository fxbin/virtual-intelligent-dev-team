# Memory Model

Bounded iteration needs memory, but not uncontrolled history replay.

Project Memory Lite sits above per-round iteration memory.

Use it when:

- the task spans sessions
- a planning pack needs a durable resume point
- release gate or remediation needs one stable handoff anchor

The default lightweight anchors are defined in `references/project-memory-lite.md`.

## Memory Tiers

## 1. Round Memory

Short-term record for one round.

Store:

- objective
- candidate change
- evidence summary
- decision
- next action

This memory is ephemeral and can be compressed aggressively.

## 2. Self Feedback

Compact critique from the completed round.

Store:

- what helped
- what regressed
- what single variable should change next
- what evidence should be collected next

This is the bridge between one round and the next.

## 3. Open Loops

Carry only unresolved items across rounds.

Examples:

- missing benchmark
- unresolved regression
- unclear tradeoff
- blocker that needs user input

Open loops should be concise and actionable.
Preserve whether a loop is still active or has just been resolved so later rounds do not re-open already-closed work by accident.

## 4. Distilled Patterns

Store only reusable conclusions that survived evidence.

Examples:

- a routing pattern that consistently picked the right lead
- a guardrail sequence that reduced delivery risk
- a benchmark step that catches regressions early

Do not store one-off guesses as patterns.
Keep one compact evidence snapshot with each distilled pattern so later rounds know why the pattern was trusted.

When a kept round is accepted, rebuild distilled patterns from the accepted-round history instead of appending free-form notes by hand.

## 5. Iteration Context Chain

Rebuild one compact context file from all completed rounds.

The next round should prefer this chain over manually replaying every artifact.

It should include:

- round memory snapshots
- self-feedback snapshots
- current open loops
- distilled patterns

## 6. Project Memory Lite

Use a minimal persistent anchor when the loop or planning work must survive a pause.

Preferred anchors:

- `docs/progress/MASTER.md`
- `.skill-iterations/current-round-memory.md`
- `.skill-iterations/distilled-patterns.md`

This tier should point to the latest stable resume surface, not duplicate every
per-round file.

Autonomous candidate generation should read this compact chain first and only fall back to raw per-round files when the chain is missing or stale.

## Retention Rules

- Keep the latest round memory in full.
- Keep the latest self-feedback in full.
- Keep recent open loops until resolved.
- Distill stable lessons into patterns.
- Rebuild one compact context chain for the next round.
- Drop stale or contradicted reflections.

## What Not To Do

- Do not reload every prior round by default.
- Do not merge speculative notes into evergreen guidance.
- Do not let memory silently change the objective.
- Do not return more resume artifacts than the next session actually needs.
