# Self-Optimization Architecture

This skill is no longer only a router. It can also act as a bounded optimization orchestrator when the user asks for repeated improvement, benchmark-driven tuning, or candidate comparison.

## Goal

Turn one-shot team dispatch into a controlled loop:

1. dispatch the right lead and assistants
2. execute one candidate change or one decision slice
3. evaluate with evidence
4. decide `keep`, `retry`, `rollback`, or `stop`
5. preserve only the memory that improves the next round

## Layers

## 1. Dispatch Layer

- Pick the semantic owner first.
- Keep that semantic owner through the whole loop.
- Add assistants only when they materially improve the next move.
- Attach process skills when the request also implies Git workflow, worktree isolation, or bounded iteration.

## 2. Execution Layer

- A round must have one explicit objective.
- A round should change one meaningful variable at a time.
- Do not mix redesign, bugfix, benchmark, and release steps into the same evidence judgment.
- For software projects, prefer a Dev↔QA style loop: implement, evaluate, decide, then move.
- When the next round is synthesized from memory, convert that synthesized candidate into one executable mutation artifact or workspace change before benchmarking.
- Prefer an in-repo deterministic materializer when the mutation can be described as structured file operations.
- Prefer a deterministic `mutation_catalog` when repeated feedback should compile into the next round's `mutation_plan` instead of relying on ad-hoc mutation commands.

## 3. Evaluation Layer

- Every round must have observable evidence.
- Preferred evidence:
  - validator output
  - benchmark or regression output
  - test result
  - reproducible before and after comparison
- "It feels better" is not sufficient evidence.

## 4. Memory Layer

- Keep short-lived round memory for the current attempt.
- Keep one self-feedback file for the current attempt.
- Keep open loops for unresolved issues.
- Distill only stable patterns into reusable memory.
- Rebuild one compact context chain instead of replaying the full history every round.
- Persist loop-level progress so a deep offline run can resume from the latest completed round instead of restarting.

## 5. Evidence Layer

- Record intent, candidate change, evidence, result, and decision.
- Treat the iteration ledger as append-only.
- If the evidence is missing or inconclusive, prefer `retry` or `stop`, not `keep`.

## 6. Rollback Layer

- Roll back when quality regresses, a constraint is violated, or the candidate change creates net-new risk.
- Stop when the loop has insufficient evidence, exhausted retry budget, or reached the round cap.
- Treat same-hypothesis retry budget as an enforced guardrail, not a suggestion.
- Optionally stop when the loop hits too many consecutive non-keep rounds, even if the hard round cap has not been reached yet.
- When autonomous mode is active, optionally pivot to a fresh bottleneck instead of halting immediately after stagnation, but keep that pivot explicit and persisted.

## Activation Conditions

Enable bounded iteration when the request includes signals such as:

- optimize this repeatedly
- run another round
- benchmark it
- compare against baseline
- keep iterating until stable
- repeated failed attempts with evidence required

## Non-Goals

- No infinite self-improvement loop.
- No rewriting the whole plan every round.
- No hidden objective changes mid-loop.
- No preserving speculative memory as if it were validated knowledge.

## Online vs Offline

- Online user-facing mode:
  - default to `1-3` rounds
  - optimize for responsiveness and safety
- Offline optimization mode:
  - can run deeper loops, including `100+` rounds for explicit software-project optimization
  - must still keep round caps, evidence, rollback rules, and resumable checkpoints
