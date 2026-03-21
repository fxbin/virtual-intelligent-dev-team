# Rollback And Stop Rules

Use these rules whenever bounded iteration is enabled.

## Rollback Triggers

Rollback the candidate when any of these happen:

- benchmark score regresses
- validator or regression suite fails
- a critical requirement is violated
- the candidate improves one metric by breaking a more important constraint
- the change introduces new ambiguity without measurable upside

When a rollback command exists for the candidate worktree, execute it and capture a post-rollback snapshot before continuing to the next round.
When the round used a candidate patch and no rollback command exists, reverse that patch and capture the post-rollback snapshot before continuing.
When the loop is running offline for many rounds, consider a plan-defined `max_consecutive_non_keep_rounds` guard so repeated `retry` / `rollback` outcomes do not consume the whole budget without a new `keep`.
When autonomous generation is enabled, use `auto_pivot_on_stagnation` only if the next move can stay evidence-backed; otherwise prefer a hard stop over a blind pivot.

## Stop Triggers

Stop the loop when:

- the objective is met
- the round cap is reached
- the same hypothesis already failed twice
- no objective evidence is available for the next round
- the remaining improvements are too speculative for the current task

## Keep Rule

Keep only if:

- evidence shows improvement or a safer equivalent outcome
- no higher-priority constraint regressed
- the change is explainable and reproducible

## Retry Rule

Retry only if:

- the hypothesis still makes sense
- the previous round failed for fixable execution reasons
- the next attempt changes the evidence quality, not just the wording

## User-Facing Safety Rule

For live user work, prefer an early `stop` over a low-confidence extra round.

## Long-Loop Rule

For explicit offline loops that run very deep:

- keep the active baseline rollbackable at all times
- write round memory and self-feedback every round
- rebuild the iteration context chain before continuing
- prefer deterministic patch artifacts or stable apply/rollback scripts over ad hoc shell edits
- prefer stopping over drifting when the loop loses a clear next hypothesis
