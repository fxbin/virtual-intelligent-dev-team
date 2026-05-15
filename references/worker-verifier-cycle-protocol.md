# Worker Verifier Cycle Protocol

This protocol prevents the same agent from being both the player and the referee in software delivery.

It applies to implementation, refactor, bug fix, audit remediation, release readiness, beta remediation, and root-cause loops.

## Cycle Objects

Every verification cycle must preserve:

1. `WorkOrder`
2. `ImplementationOutput`
3. `VerificationReport`
4. `DeliveryCycleReport`

When the Verifier returns `fail`, the cycle must also preserve:

5. `RemediationPatch`

## Worker Contract

The Worker may produce:

- code changes
- docs changes
- config changes
- migration plans
- test additions
- command output summaries

The Worker must report:

- produced artifacts
- commands run
- tests run
- assumptions
- known risks
- `self_reported_done: true`

`self_reported_done` only triggers verification. It is not completion.

## Verifier Contract

The Verifier checks the Worker output against acceptance gates.

Allowed verdicts:

- `pass`
- `fail`
- `hold`

Rules:

- `pass` requires all required gates checked and passed.
- `fail` requires a non-empty `RemediationPatch`.
- `hold` requires a blocker, missing evidence, permission gap, or route-changing ambiguity.
- The Verifier should reference concrete artifacts, commands, tests, logs, or file paths whenever possible.

## Default Acceptance Gates

### Implementation Gates

- `scope_gate`
- `acceptance_criteria_gate`
- `tests_or_verification_gate`
- `regression_risk_gate`
- `harness_constraint_gate`
- `role_separation_gate`
- `delivery_cycle_report_gate`

### Audit Gates

- `finding_evidence_gate`
- `severity_gate`
- `remediation_patch_gate`
- `false_positive_risk_gate`
- `verification_plan_gate`

### Release Gates

- `release_gate_result_gate`
- `blocking_issue_gate`
- `rollback_gate`
- `post_release_feedback_gate`
- `ship_hold_evidence_gate`

## Retry Rules

Retry is allowed only when:

- Verifier verdict is `fail`
- `cycle_count < max_cycles`
- `RemediationPatch.instructions` is non-empty
- Worker restarts from the previous `ImplementationOutput` plus the remediation patch

Retry must not:

- discard already passed gates
- broaden scope without Lead approval
- overwrite user changes unrelated to the task
- change the output contract mid-cycle

## Stop Rules

The Engine stops when:

- Verifier returns `pass`
- Verifier returns `hold`
- `max_cycles` is reached
- acceptance gates conflict
- tool, permission, or workspace blockers prevent verification
- the user changes the route

The Lead may accept only after `DeliveryCycleReport.next_state = accepted`.
