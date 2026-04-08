# Beta Validation Playbook

Use this playbook when the request is about staged beta validation, internal test cohorts, simulated users, or a round-by-round sample ramp before release.

## Lead

- Default lead: `World-Class Product Architect`
- Common assistant: `Technical Trinity`
- Add `Git Workflow Guardian` only when rollout, branch, PR, or release expansion gates are explicit.

## Default sequence

1. Define the beta objective and the decision that the beta program should unlock.
2. Split the beta into explicit rounds with increasing sample size.
3. Start with a small simulated or seed-user cohort before broadening exposure.
4. Define machine-readable simulated-user profiles instead of one generic “user”.
5. Build each round from the shared persona library and scenario packs before freezing the per-round simulation config.
6. Materialize each round from an explicit cohort fixture and a reusable trace catalog instead of ad-hoc session defaults.
7. Keep a machine-readable ramp plan so each round has an explicit planned sample size, participant mode, and expected cohort shape.
8. Preview the resolved fixture before execution so the exact persona / scenario / trace mix is reviewable.
9. Diff the current round against the previous manifest before execution so cohort expansion or contraction is explicit.
10. Capture every feedback item with scenario, severity, and proposed action, and keep the raw event trace.
11. Sync simulation evidence back into the feedback ledger before judging the round.
12. Expand only when the previous round's exit criteria are explicitly met.
13. For `round-1+`, block `advance` if the ramp plan is missing, the round report drifts from the plan, the fixture diff is missing, or the diff is still marked `review_required`.

## Required outputs

- beta program overview
- round-by-round cohort matrix
- machine-readable ramp plan
- simulated-user profile set
- per-round simulation config
- round-to-round fixture diff
- machine-readable simulation run with event trace
- feedback ledger with severity and action
- machine-readable round report
- blocker breakdown by persona and by scenario
- diff-gated beta round decision
- per-round exit criteria
- expand / hold / escalate recommendation

## Shared libraries

- persona library: `references/simulation-persona-library.json`
- cohort fixtures: `references/simulation-cohort-fixtures.json`
- scenario packs: `references/simulation-scenario-packs.json`
- trace catalog: `references/simulation-trace-catalog.json`
- manifest schema: `references/beta-simulation-manifest.schema.json`
- diff schema: `references/beta-simulation-diff.schema.json`
- ramp plan schema: `references/beta-ramp-plan.schema.json`

默认 archetype 仍然围绕：

- first-time novice
- daily operator
- power user
- skeptical evaluator
- edge-case breaker

## Guardrails

- Do not treat “more users” as validation by itself; sample structure matters.
- Do not skip the pre-build or concept-smoke round when the product promise is still unstable.
- Do not expand cohort size before blocker-level signals are closed or explicitly accepted.
- Do not let the report drift away from the planned ramp; sample size and participant mode should be compared against the machine-readable plan.
- Do not expand or contract fixture coverage silently; compare the manifests and explain any coverage drift.
- Do not flatten all feedback into one list; keep round, scenario, and severity attached.
- Do not rely on only the synthesized report; preserve the simulation trace that explains why a round is `advance`, `hold`, or `escalate`.
- Do not move to the next round without a machine-readable gate result.
