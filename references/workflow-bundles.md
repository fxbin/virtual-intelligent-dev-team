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
  2. create a compact system map when the target area is unfamiliar or multi-module
  3. create the planning pack
  4. split execution into vertical slices with `AFK` / `HITL` classifications
  5. create or refresh the progress anchor
  6. hand back to normal implementation routing
- Primary references:
  - `references/pre-development-planning-playbook.md`
  - `references/pre-development-output-template.md`
  - `references/system-map-protocol.md`
  - `references/vertical-slice-delivery-protocol.md`
- Default resume anchor:
  - `docs/progress/MASTER.md`

## 2. `product-spec-deliver`

- Use when:
  - the request starts from product scope, user flow, acceptance criteria, or frontend/backend contract alignment
  - the lead needs to turn product thinking into an implementation-ready slice
- Default sequence:
  1. define the target user and primary outcome
  2. lock the smallest acceptable scope
  3. sharpen shared language when product terms are ambiguous
  4. write the user flow and acceptance criteria
  5. split build work into vertical slices when the feature spans multiple layers
  6. surface frontend/backend contract questions before implementation
- Primary references:
  - `references/product-delivery-playbook.md`
  - `references/shared-language-and-decision-capture.md`
  - `references/vertical-slice-delivery-protocol.md`
  - `assets/product-delivery-brief-template.md`
  - `scripts/init_product_delivery.py`
- Default resume anchors:
  - `.skill-product/current-slice.md`
  - `.skill-product/acceptance-criteria.md`

### Optional stage councils under `product-spec-deliver`

Use `references/stage-council-protocol.md` when product or prototype work is too
broad for a single product generalist but does not justify a new top-level lead.

Stage councils are overlays:

- they keep `World-Class Product Architect` as lead
- they keep `product-spec-deliver` as the workflow bundle
- they change only the phase roles, gates, and artifacts inside the product
  delivery journey
- they hand back into Team Engine Lite before implementation or release claims

Available councils:

| Council | Use when | Required handoff |
| --- | --- | --- |
| `product-discovery-council` | PRD, product strategy, requirements, user research, competitor analysis, metrics, roadmap, sprint, stakeholder, or brainstorm work needs phase-level specialists | accepted scope, P0/P1/P2, non-goals, acceptance criteria, roadmap or sequencing delta |
| `prototype-design-council` | high-fidelity prototype, runnable HTML prototype, design system, visual design, page design, brand tone, accessibility, or interaction design needs phase-level specialists | design brief, design tokens or system choice, prototype readiness, visual quality and accessibility gates |

Default stage council artifact:

- `.skill-product/stage-council-plan.json`

Template:

- `assets/stage-council-plan-template.json`

## 3. `quick-slice-deliver`

- Use when:
  - the request is a narrow implementation, bug fix, or small feature slice
  - the route needs enough structure to avoid drift but does not need a full product brief, planning branch, or iteration loop
- Default sequence:
  1. clarify only route-changing gaps
  2. use `references/goal-framing-protocol.md` when the slice has drift-prone success evidence or explicit non-goals
  3. build or name the feedback loop first when the slice is a bug or regression
  4. record intent, non-goals, acceptance criteria, and verification evidence
  5. create or refresh durable project context when needed
  6. implement the smallest coherent change
  7. use `references/anti-entropy-governance.md` when the fix adds guards, fallbacks, adapters, or retires an old owner
  8. run targeted verification and self-review before presenting
- Primary references:
  - `references/quick-slice-delivery-playbook.md`
  - `references/feedback-loop-first-protocol.md`
  - `assets/quick-slice-brief-template.md`
  - `assets/delivery-status-template.yaml`
  - `assets/project-context-template.md`
  - `scripts/init_quick_slice.py`
  - `scripts/init_project_context.py`
- Default resume anchors:
  - `.skill-delivery/current-slice.md`
  - `.skill-delivery/status.yaml`
  - `.skill-context/project-context.md`

## 4. `beta-feedback-ramp`

- Use when:
  - the request is about internal beta, staged user validation, or a round-by-round cohort ramp
  - the team needs feedback before locking release confidence, not just a static PRD
- Default sequence:
  1. define the beta objective, exit criteria, and round boundaries
  2. initialize simulated-user profiles and a per-round simulation config
     - keep a machine-readable cohort plan at `.skill-beta/cohort-plan.json`
     - keep a machine-readable ramp plan at `.skill-beta/ramp-plan.json`
     - source persona defaults from `references/simulation-persona-library.json`
     - source cohort defaults from `references/simulation-cohort-fixtures.json`
     - source scenario defaults from `references/simulation-scenario-packs.json`
     - source trace defaults from `references/simulation-trace-catalog.json`
  3. preview the resolved fixture so the exact persona / scenario / trace mix is inspectable
  4. reconcile cohort plan against the resolved fixture so planned sessions, persona counts, scenario coverage, and trace coverage are explicit
  5. diff the current fixture against the previous round before execution so expansion drift is explicit
  6. start with a small simulated or seed-user cohort
  7. preserve session-level traces before synthesizing the round report
  8. sync generated feedback rows back into the ledger and inspect blocker slices by persona and scenario
  9. expand sample size only when the previous round clears its gate
  10. log structured feedback and severity before release or rollout decisions
  11. for `round-1+`, require the gate to consume cohort-plan evidence, ramp-plan evidence, and fixture diff evidence before allowing expansion
  12. if the beta gate returns `hold` or `escalate`, create the next remediation brief instead of stopping at the verdict
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

## 5. `audit-fix-deliver`

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

## 6. `govern-change-safely`

- Use when:
  - the request is primarily about staged execution, rollback, release hygiene, branch policy, or workflow safety
  - Git workflow and technical governance matter more than feature design
- Default sequence:
  1. define owner, execution mode, and stop conditions
  2. lock the smallest safe next action
  3. define verification evidence and rollback conditions
  4. classify delete / compatibility / source-of-truth risk with `references/anti-entropy-governance.md` when old paths, fallbacks, duplicate owners, schema, persistence, or source-of-truth surfaces are touched
  5. only then enter Git or release actions
- Primary references:
  - `references/technical-governance-playbook.md`
  - `assets/technical-governance-change-plan-template.md`
  - `scripts/init_technical_governance.py`
- Default resume anchors:
  - `.skill-governance/change-plan.md`
  - `.skill-governance/release-checklist.md`

## 7. `root-cause-remediate`

- Use when:
  - the user says previous fixes failed
  - the issue still reproduces
  - logs, repro, runtime state, or root cause are central
  - bounded iteration is needed to compare evidence-backed fixes
- Default sequence:
  1. freeze guesswork
  2. frame success evidence and stop conditions when previous attempts drifted
  3. establish the smallest reliable feedback loop before diagnosis
  4. collect missing evidence
  5. validate one falsifiable hypothesis at a time
  6. prefer owner correction or path retirement over fallback growth when evidence supports it
  7. remediate safely
  8. keep or rollback based on evidence
- Primary references:
  - `references/root-cause-escalation-playbook.md`
  - `references/feedback-loop-first-protocol.md`
  - `references/iteration-protocol.md`
  - `references/memory-model.md`
- Default resume anchors:
  - `.skill-iterations/current-round-memory.md`
  - `.skill-iterations/distilled-patterns.md`

## 8. `ship-hold-remediate`

- Use when:
  - the user asks whether the current version can ship
  - formal acceptance, release readiness, or submit/hold judgment is needed
- Default sequence:
  1. run the release gate
  2. answer `ship` or `hold`
  3. if staged beta validation exists, enforce the latest beta round gate before `ship`
  4. if `ship`, bootstrap the post-release feedback loop so shipped evidence has a formal re-entry point
  5. if `hold`, create the next remediation brief, and inherit the latest beta remediation brief when one already exists
  6. resume via iteration, post-release, or planning artifacts only when needed
- Primary references:
  - `references/release-gate-playbook.md`
  - `references/offline-loop-drill-playbook.md`
  - `references/beta-validation-playbook.md`
- Default resume anchors:
  - `evals/release-gate/release-gate-report.md`
  - `evals/release-gate/next-iteration-brief.json`

## 9. `post-release-close-loop`

- Use when:
  - the version already shipped and the team needs a structured way to absorb dogfood, telemetry, support, or real-user feedback
  - the question is no longer “can we ship?” but “what should shipped evidence reopen?”
- Default sequence:
  1. initialize the post-release workspace
  2. collect structured feedback and signal evidence into the current report
  3. evaluate whether to `monitor`, `iterate`, or `escalate`
  4. sync product or governance writebacks before reopening remediation
- Primary references:
  - `references/post-release-feedback-playbook.md`
  - `assets/post-release-signal-report-template.json`
  - `scripts/init_post_release_feedback.py`
  - `scripts/evaluate_post_release_feedback.py`
- Default resume anchors:
  - `.skill-post-release/triage-summary.md`
  - `.skill-post-release/current-signals.json`

## 10. `capture-project-knowledge`

- Use when:
  - the request is to create or improve `AGENTS.md`
  - the request is to create project-local `.agents/skills/`
  - the user wants AI onboarding or codebase knowledge capture for future development agents
- Default sequence:
  1. inventory existing guidance, docs, config, tests, scripts, and entrypoints
  2. split only independent analysis lanes and avoid duplicated subagent work
  3. synthesize verified repository facts into concise `AGENTS.md` guidance
  4. create or update only scenario-specific project-local `.agents/skills/`
  5. validate referenced paths, commands, and remaining unknowns
- Primary references:
  - `skill-forge/references/project-knowledge-capture-protocol.md`
- Default resume anchors:
  - `AGENTS.md`
  - `.agents/skills/`

## Bundle Contract

Every bundle should expose:

- `workflow_bundle`
- `workflow_reason`
- `workflow_steps`
- `quality_gate`
- `harness_constraint_gate`
- `workflow_bundle_bootstrap`
- `progress_anchor_recommended`
- `resume_artifacts`
- `workflow_quality_checks`

When a bundle needs workspace initialization before real delivery starts, the
bootstrap contract should make three things explicit:

- which command initializes the bundle workspace
- which artifacts must exist after bootstrap
- which resume anchor should match `progress_anchor_recommended`

The lead owns the journey narrative. Assistants only return the delta needed for
the current step.

Each bundle also inherits the execution-quality guardrails in
`references/execution-quality-guardrails.md`: expose route-changing assumptions,
justify why the bundle is minimal, keep scope surgical, and name the verification
evidence that closes the route.

When a bundle activates one of the engineering micro-practices, keep it as a
small local discipline rather than a new workflow bundle. Initialize the ledger
with `scripts/init_micro_practices.py`, update practice evidence with
`scripts/update_micro_practices.py`, and evaluate it with
`scripts/evaluate_micro_practices.py` before claiming completion:

- `references/shared-language-and-decision-capture.md`
- `references/feedback-loop-first-protocol.md`
- `references/vertical-slice-delivery-protocol.md`
- `references/system-map-protocol.md`
- `references/architecture-deepening-protocol.md`

Code-facing bundles also inherit the Harness engineering constraint protocol in
`references/harness-engineering-constraint-protocol.md`: before implementation,
create or refresh `.skill-harness/engineering-constraints.md` and treat it as the
current constraint source for scope, forbidden changes, verification evidence,
and rollback or stop conditions.

Bundles also inherit `references/workflow-quality-baseline.md`: keep fast paths
cheap, create artifacts lazily, preserve fresh evidence before completion
claims, and state authority boundaries for host-dependent runtime claims.

## Auto Overlay

`/auto` 不是新的 workflow bundle。

它是加在 bundle 外层的显式执行协议，只对白名单开放：

- `root-cause-remediate`
- `ship-hold-remediate`
- `post-release-close-loop`

协议要求：

1. `/auto` 只进入 `setup`
2. `/auto go` 才允许进入 `go`
3. 必须先落 `.skill-auto/auto-run-plan.json`
4. 默认仍是 manual mode
5. `safe / background / resume` 只作为子协议叠加，不改变 bundle 选择本身
