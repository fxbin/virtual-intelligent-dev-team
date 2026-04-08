# Workflow Bundles

Use workflow bundles when routing should return more than a lead agent.

A bundle is the smallest reusable delivery journey for a recurring request shape.
It helps the lead answer:

- what sequence to run first
- which artifacts should exist before the next step
- what the default resume anchor is

Bundles are not new skills. They are runtime coordination packs built on top of
existing routing, planning, iteration, release, and Git rules.

## 1. `plan-first-build`

- Use when:
  - the user wants a rewrite, migration, architecture overhaul, or project-wide refactor
  - the user explicitly says "plan first", "research first", or "先规划再开发"
- Default sequence:
  1. lock scope, target, and constraints
  2. create the planning pack
  3. create or refresh the progress anchor
  4. hand back to normal implementation routing
- Primary references:
  - `references/pre-development-planning-playbook.md`
  - `references/pre-development-output-template.md`
- Default resume anchor:
  - `docs/progress/MASTER.md`

## 2. `product-spec-deliver`

- Use when:
  - the request starts from product scope, user flow, acceptance criteria, or frontend/backend contract alignment
  - the lead needs to turn product thinking into an implementation-ready slice
- Default sequence:
  1. define the target user and primary outcome
  2. lock the smallest acceptable scope
  3. write the user flow and acceptance criteria
  4. surface frontend/backend contract questions before implementation
- Primary references:
  - `references/product-delivery-playbook.md`
  - `assets/product-delivery-brief-template.md`
  - `scripts/init_product_delivery.py`
- Default resume anchors:
  - `.skill-product/current-slice.md`
  - `.skill-product/acceptance-criteria.md`

## 3. `beta-feedback-ramp`

- Use when:
  - the request is about internal beta, staged user validation, or a round-by-round cohort ramp
  - the team needs feedback before locking release confidence, not just a static PRD
- Default sequence:
  1. define the beta objective, exit criteria, and round boundaries
  2. initialize simulated-user profiles and a per-round simulation config
     - source persona defaults from `references/simulation-persona-library.json`
     - source cohort defaults from `references/simulation-cohort-fixtures.json`
     - source scenario defaults from `references/simulation-scenario-packs.json`
     - source trace defaults from `references/simulation-trace-catalog.json`
  3. preview the resolved fixture so the exact persona / scenario / trace mix is inspectable
  4. diff the current fixture against the previous round before execution so expansion drift is explicit
  5. start with a small simulated or seed-user cohort
  6. preserve session-level traces before synthesizing the round report
  7. sync generated feedback rows back into the ledger and inspect blocker slices by persona and scenario
  8. expand sample size only when the previous round clears its gate
  9. log structured feedback and severity before release or rollout decisions
  10. for `round-1+`, require the gate to consume fixture diff evidence before allowing expansion
- Primary references:
  - `references/beta-validation-playbook.md`
  - `assets/beta-cohort-matrix-template.md`
  - `assets/simulated-user-profile-template.json`
  - `assets/beta-simulation-config-template.json`
  - `scripts/init_beta_validation.py`
  - `scripts/evaluate_beta_round.py`
- Default resume anchors:
  - `.skill-beta/program-overview.md`
  - `.skill-beta/cohort-matrix.md`
  - `.skill-beta/feedback-ledger.md`

## 4. `audit-fix-deliver`

- Use when:
  - the request combines review or audit with remediation
  - the request includes review now and commit / push / PR later
- Default sequence:
  1. findings first
  2. separate blockers from improvements
  3. define the smallest safe remediation step
  4. enter Git delivery only if requested
- Primary references:
  - `references/scenario-runbooks.md`
  - `references/coordination-handoff-templates.md`
- Default resume anchors:
  - `.skill-iterations/current-round-memory.md`
  - `.skill-iterations/distilled-patterns.md`

## 5. `govern-change-safely`

- Use when:
  - the request is primarily about staged execution, rollback, release hygiene, branch policy, or workflow safety
  - Git workflow and technical governance matter more than feature design
- Default sequence:
  1. define owner, execution mode, and stop conditions
  2. lock the smallest safe next action
  3. define verification evidence and rollback conditions
  4. only then enter Git or release actions
- Primary references:
  - `references/technical-governance-playbook.md`
  - `assets/technical-governance-change-plan-template.md`
  - `scripts/init_technical_governance.py`
- Default resume anchors:
  - `.skill-governance/change-plan.md`
  - `.skill-governance/release-checklist.md`

## 6. `root-cause-remediate`

- Use when:
  - the user says previous fixes failed
  - the issue still reproduces
  - logs, repro, runtime state, or root cause are central
  - bounded iteration is needed to compare evidence-backed fixes
- Default sequence:
  1. freeze guesswork
  2. collect missing evidence
  3. validate the smallest hypothesis
  4. remediate safely
  5. keep or rollback based on evidence
- Primary references:
  - `references/root-cause-escalation-playbook.md`
  - `references/iteration-protocol.md`
  - `references/memory-model.md`
- Default resume anchors:
  - `.skill-iterations/current-round-memory.md`
  - `.skill-iterations/distilled-patterns.md`

## 7. `ship-hold-remediate`

- Use when:
  - the user asks whether the current version can ship
  - formal acceptance, release readiness, or submit/hold judgment is needed
- Default sequence:
  1. run the release gate
  2. answer `ship` or `hold`
  3. if staged beta validation exists, enforce the latest beta round gate before `ship`
  4. if `hold`, create the next remediation brief
  5. resume via iteration or planning artifacts only when needed
- Primary references:
  - `references/release-gate-playbook.md`
  - `references/offline-loop-drill-playbook.md`
  - `references/beta-validation-playbook.md`
- Default resume anchors:
  - `evals/release-gate/release-gate-report.md`
  - `evals/release-gate/next-iteration-brief.json`

## Bundle Contract

Every bundle should expose:

- `workflow_bundle`
- `workflow_reason`
- `workflow_steps`
- `workflow_bundle_bootstrap`
- `progress_anchor_recommended`
- `resume_artifacts`

When a bundle needs workspace initialization before real delivery starts, the
bootstrap contract should make three things explicit:

- which command initializes the bundle workspace
- which artifacts must exist after bootstrap
- which resume anchor should match `progress_anchor_recommended`

The lead owns the journey narrative. Assistants only return the delta needed for
the current step.
