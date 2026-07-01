# Workflow Bundles

Use workflow bundles when routing should return more than a lead agent. A bundle is the smallest reusable delivery journey for a recurring request shape.

## 1. `plan-first-build`

- **Use when**: rewrite, migration, architecture overhaul, or "plan first" requests
- **Sequence**:
  1. Lock scope, target, and constraints
  2. Create compact system map when target area is unfamiliar
  3. Create planning pack
  4. Split execution into vertical slices with AFK/HITL classifications
  5. Create progress anchor and durable `.skill-context/project-context.md`
  6. Hand back to normal implementation routing
- **Resume anchor**: `docs/progress/MASTER.md`

## 2. `product-spec-deliver`

- **Use when**: product scope, user flow, acceptance criteria, or frontend/backend contract alignment
- **Sequence**:
  1. Define target user and primary outcome
  2. Lock smallest acceptable scope
  3. Sharpen shared language when product terms are ambiguous
  4. Write user flow and acceptance criteria
  5. Split build work into vertical slices when feature spans layers
  6. Surface frontend/backend contract questions before implementation
- **Resume anchors**: `.skill-product/current-slice.md`, `.skill-product/acceptance-criteria.md`

## 3. `audit-fix-deliver`

- **Use when**: review findings and remediation path in one motion
- **Sequence**:
  1. Findings first
  2. Separate blockers from follow-up improvements
  3. If P0/P1/P2 batch fixes requested: freeze findings, build batch order, fix one batch, verify, commit
  4. Resume anchor: last verified batch

## 4. `govern-change-safely`

- **Use when**: Git workflow, branch strategy, PR sequencing, or merge safety
- **Sequence**:
  1. Assess current branch state and work-in-progress
  2. Determine safest change path (worktree, branch, or patch)
  3. Execute with rollback plan
  4. Verify clean state before proceeding

## 5. `ship-hold-remediate`

- **Use when**: release readiness decisions
- **Sequence**:
  1. Run release gate checks
  2. Produce `ship` / `hold` decision with evidence
  3. If `hold`: generate remediation plan with priority order
  4. Resume anchor: release-gate report

## 6. `bounded-iteration`

- **Use when**: optimization loops, benchmark comparison, repeated retries
- **Sequence**:
  1. Lock objective: target outcome, baseline, metric, constraints, max rounds
  2. Each round: define candidate → state hypothesis → validate → record evidence → decide (`keep`/`retry`/`rollback`/`stop`)
  3. Closure: finalize ledger, write reflection, preserve patterns
- **Caps**: live requests ≤3 rounds, offline ≤120 rounds, same hypothesis ≤2 retries

## 7. `beta-feedback-ramp`

- **Use when**: staged validation or rollout risk control
- **Sequence**:
  1. Define cohort and success criteria
  2. Run staged rollout with feedback capture
  3. Analyze signals and decide ramp/hold/rollback
  4. Resume anchor: beta status report

## Bundle Confidence Levels

| Bundle | Confidence | Source |
|--------|-----------|--------|
| `ship-hold-remediate` | 0.98 | process-skill (explicit release gate) |
| `plan-first-build` | 0.96 | process-skill (explicit planning request) |
| `root-cause-remediate` | 0.93 | process-skill (explicit iteration) |
| `audit-fix-deliver` | 0.88 | keyword+lead |
| `govern-change-safely` | 0.85 | keyword+lead |
| `direct-execution` | 0.35 | fallback (no strong bundle match) |

Use bundle as explicit execution journey when `bundle_confidence >= 0.6`. Keep execution lightweight when `bundle_confidence < 0.6`.
