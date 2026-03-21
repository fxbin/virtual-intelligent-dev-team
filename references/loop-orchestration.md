# Loop Orchestration

Use the multi-round loop only when the user explicitly wants repeated optimization until stable, a capped number of rounds, or candidate-by-candidate evaluation.

## Inputs

- one registered baseline label
- one objective
- a candidate plan file
- a round cap
- optional candidate briefs, mutation catalogs, materializer commands, candidate patch artifacts, worktree mutation commands, and rollback commands

## Execution Model

1. load the baseline label
2. optionally synthesize a deterministic `mutation_plan` from the plan's `mutation_catalog` and the latest feedback/context
3. optionally materialize the synthesized candidate brief into a patch artifact or workspace change
4. optionally mutate the candidate worktree through an apply command or patch artifact and capture a workspace snapshot
5. evaluate the next candidate through one stateful round
6. if the round is `keep` and policy allows, advance the active baseline
7. persist loop progress after each completed round so interrupted offline runs can resume safely
8. continue until:
   - the cap is reached
   - the loop hits a halt decision
   - no more candidates remain

## Guardrails

- never run without a round cap
- keep one candidate per round
- do not silently change the active baseline
- preserve the previous baseline when a round rolls back
- rebuild distilled patterns only from accepted rounds
- optionally cap consecutive non-keep rounds so deep offline loops can stop on obvious stagnation before the hard round cap
- optionally auto-pivot after stagnation in autonomous mode by blocking the exhausted hypothesis and choosing the next actionable focus
- do not mix `apply_command` and `candidate_patch` in the same round
- keep the candidate brief and materializer step replayable when the loop must synthesize real code changes
- prefer the built-in materializer when a deterministic `mutation_plan` can express the change
- prefer a deterministic top-level `mutation_catalog` when repeated feedback patterns should map to the same class of mutation
- prefer JSON-aware mutation operations for JSON control files so routing rules, regression registries, and eval inventories can be updated without rewriting whole files
- do not resume from a persisted loop state if the plan content has drifted
- do not mutate a software-project worktree without a rollback path when the loop is expected to keep running offline
