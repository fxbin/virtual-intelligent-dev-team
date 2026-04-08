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
4. Use heterogeneous archetypes, not one generic “user”.
5. Capture every feedback item with scenario, severity, and proposed action.
6. Expand only when the previous round's exit criteria are explicitly met.

## Required outputs

- beta program overview
- round-by-round cohort matrix
- feedback ledger with severity and action
- per-round exit criteria
- expand / hold / escalate recommendation

## Default user archetypes

- first-time novice
- daily operator
- power user
- skeptical evaluator
- edge-case breaker

## Guardrails

- Do not treat “more users” as validation by itself; sample structure matters.
- Do not skip the pre-build or concept-smoke round when the product promise is still unstable.
- Do not expand cohort size before blocker-level signals are closed or explicitly accepted.
- Do not flatten all feedback into one list; keep round, scenario, and severity attached.
