# Agency-Inspired Loop Patterns

This reference distills the useful iteration patterns learned from `agency-agents-main` and adapts them to this skill.

## 1. Preserve The Semantic Owner

- Pick the domain lead first.
- Do not let the loop controller erase the real owner.
- A frontend optimization loop should still belong to `World-Class Product Architect`.
- A strategy optimization loop should still belong to `Executive Trinity`.

## 2. Run A Dev↔QA Evidence Loop

Each round should look like:

1. choose one candidate change
2. implement or apply it
3. run validator, benchmark, or tests
4. decide `keep`, `retry`, `rollback`, or `stop`

Do not skip the evidence step.

## 3. Keep Checkpointed Memory, Not Raw History Replay

- Write one compact round memory file after each round.
- Write one self-feedback file after each round.
- Rebuild a compact context chain for the next round instead of replaying every artifact manually.

## 4. Roll Back To Last Known Good

- Promote only evidence-backed rounds into the baseline registry.
- If a candidate regresses, revert to the active baseline instead of reasoning from a broken state.
- Keep rollback cheap enough that a failed round does not poison later rounds.

## 5. Split Live Loops From Offline Deep Loops

- Live user work should stay short and responsive.
- Offline benchmark or software optimization sessions can run much deeper loops.
- Long loops still need round caps, retry budgets, checkpoints, and explicit stop conditions.

## 6. Treat Feedback As Input To The Next Round

- The next round should read:
  - latest round memory
  - latest self-feedback
  - current open loops
  - distilled patterns
- If the next round needs a real software mutation, emit a compact candidate brief that a materializer step can turn into a patch or workspace change.
- Prefer a deterministic built-in materializer when that mutation can be expressed as structured file operations.
- When the same feedback motifs recur, map them through a deterministic `mutation_catalog` so self-feedback becomes a replayable `mutation_plan`.
- When one hypothesis is exhausted, block it and pivot to the next bottleneck instead of replaying the same motif indefinitely.
- Change only one main variable per round so feedback remains actionable.
