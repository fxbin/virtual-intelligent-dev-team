# Iteration Protocol

Use this protocol when the skill enters bounded iteration mode.

## Round 0: Lock the Objective

Before iterating, write down:

- target outcome
- baseline state
- main metric or evidence source
- constraints that must not regress
- maximum round count

If these are not clear, ask one clarifying question or stop the loop.

Register the baseline before the first comparison so later rounds do not drift to an implicit reference.
Lock the semantic owner before the first round so the loop controller does not erase the real domain lead.

## Round Structure

Each round should follow the same shape.

1. Define one candidate change
2. State why this candidate is being tested
3. Run validation or benchmark
4. Record evidence
5. Make one decision

If the local state machine is enabled, the cycle should also write:

- round `state.json`
- updated ledger
- updated reflection
- updated round memory
- updated self-feedback
- rebuilt iteration context chain
- refreshed open loops
- workspace snapshots before and after repo mutations when the round touches a candidate worktree
- loop progress state after each completed round when the multi-round controller is active

If the candidate lives in an isolated repo or git worktree, benchmark that candidate directly instead of re-benchmarking the controller workspace.
If the candidate change is packaged as a patch artifact, apply that patch inside the candidate repo or worktree before benchmarking and record the patch path plus strip count in local state.
If autonomous candidate generation is enabled, the next round must be synthesized from the latest round memory, self-feedback, current open loops, and distilled patterns.
If the loop needs to turn a synthesized candidate into a real change, write one candidate brief and let a materializer command convert that brief into a patch artifact or workspace mutation before the round is benchmarked.
If the candidate brief contains a structured `mutation_plan`, the built-in materializer can generate that patch artifact without an external command.
If the plan provides a deterministic `mutation_catalog`, the controller may synthesize the next round's `mutation_plan` from feedback/context matches and record `mutation_plan_source` plus `mutation_focus` for replayability.
If the loop runs offline across many rounds, persist `loops/<plan>-state.json` after each completed round and only resume when the plan content still matches the recorded digest.

## Decision Contract

Allowed decisions:

- `keep`
  - The candidate improved the objective without violating constraints.
- `retry`
  - The direction is still plausible, but evidence is insufficient or the implementation was incomplete.
- `rollback`
  - The change caused regression, instability, or violated a hard constraint.
- `stop`
  - The loop reached diminishing returns, round cap, or evidence no longer supports another move.

## Default Caps

- User-facing live request: up to `3` rounds
- Offline benchmark or optimization session: up to `120` rounds unless a stricter cap is defined
- Explicit offline software-project self-optimization: can exceed `100` rounds when rollback and evidence remain intact
- Same hypothesis retry budget: up to `2` attempts
- Consecutive non-keep budget: optional, plan-defined, and disabled unless explicitly set
- Auto pivot on stagnation: optional, plan-defined, and disabled unless explicitly set

Represent the repeated idea with a stable `hypothesis_key`.
If the same `hypothesis_key` already consumed its retry budget through `retry` or `rollback`, stop or pivot instead of looping on it again.
If the loop keeps producing consecutive `retry` / `rollback` decisions without a new `keep`, an optional `max_consecutive_non_keep_rounds` budget may stop the loop before it burns more offline rounds.
If autonomous generation is active and `auto_pivot_on_stagnation` is enabled, the controller may block the exhausted `hypothesis_key`, pivot to the next actionable focus, and continue instead of halting immediately.

## Evidence Requirements

Prefer these checks in order:

1. deterministic validator
2. benchmark or regression suite
3. targeted tests
4. structured before and after comparison

When the candidate repo uses a non-standard evaluation entrypoint, provide an explicit benchmark command instead of assuming `scripts/run_benchmarks.py`.
When the round mutates a software-project worktree, use either an explicit apply command or an explicit candidate patch before the benchmark, not both.
When the round uses patch artifacts, keep `candidate_patch` or `candidate_patch_template` plus `patch_strip` in the plan so the mutation stays reproducible across deep offline loops.
When synthesized candidates need implementation help, keep `candidate_brief` or `candidate_brief_template` plus `materialize_command` or `materialize_command_template` in the plan so the mutation step is explicit and replayable.
When the mutation is expressible as deterministic file edits, prefer `mutation_plan.operations` plus the built-in materializer over opaque shell commands.
When recurring feedback patterns should map to deterministic edits, keep a top-level `mutation_catalog` in the plan so the controller can synthesize `mutation_plan` without relying on a free-form external generator.
When the loop is optimizing its own control files such as `routing-rules.json`, `regression-cases.json`, or `evals.json`, prefer JSON-aware mutation operations like `json_set`, `json_merge`, `json_delete`, and `json_append_unique` instead of full-file rewrites.
When rollback handling is automatic and the round used a patch artifact, reverse the patch if no explicit rollback command exists.
When the controller resumes an interrupted loop, continue from the next unfinished round instead of rerunning completed rounds.
When resumability matters, keep loop-level `decision_counts` and `consecutive_non_keep_rounds` in state so stagnation guardrails survive interruptions.
When auto-pivot is enabled, persist `blocked_hypothesis_keys`, `pivot_history`, and any `pending_generation_reason` so the next autonomous round can resume the intended pivot path after interruption.

If no objective signal exists, do not claim the round improved the result.

## Escalation Rule

Escalate or attach stronger governance when:

- repeated retries fail
- the task is production-critical
- rollback cost is high
- the loop is about root cause, not simple polish

## Closure Rule

When the loop ends:

- finalize the iteration ledger
- write a round reflection
- preserve the last round memory and self-feedback chain
- distill reusable patterns only if they held across evidence
