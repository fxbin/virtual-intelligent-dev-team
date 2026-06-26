# Closure Type Pipelines

Workflow bundles organized by closure type for consistent execution patterns.

## Closure Types

Three fundamental closure types cover all workflow patterns:

| Closure Type | Description | Characteristics |
|-------------|-------------|-----------------|
| **Delivery** | Produce deliverables with acceptance criteria | Narrow slice, product spec, audit fix, full rewrite |
| **Governance** | Decision gates with pass/fail/hold outcomes | Change safety, release readiness |
| **Lifecycle** | Multi-round evolution with feedback loops | Iteration, beta rollout, post-release feedback |

## 参数化 Pipeline 设计

### 1. Delivery Pipeline

```yaml
pipeline: delivery
parameters:
  scope: [narrow_slice, product_spec, audit_fix, full_rewrite]
  planning_required: [yes, no]
  verification_mode: [self_review, verifier_cycle, none]

template:
  init: "init_{scope}_context"
  execute: "execute_delivery"
  verify: "verify_{verification_mode}"
  report: "delivery_cycle_report"
  resume_anchor: ".skill-delivery/current-{scope}.md"
```

### 2. Governance Pipeline

```yaml
pipeline: governance
parameters:
  gate_type: [change_safety, release_readiness]
  decision_mode: [ship_hold, pass_fail, fast_track]

template:
  assess: "assess_current_state"
  evaluate: "evaluate_against_criteria"
  decide: "make_{decision_mode}_decision"
  remediate: "generate_remediation_plan"  # if needed
  resume_anchor: ".skill-governance/{gate_type}-report.md"
```

### 3. Lifecycle Pipeline

```yaml
pipeline: lifecycle
parameters:
  lifecycle_type: [iteration, beta_rollout, post_release_feedback, auto_run, knowledge_capture]
  round_based: [yes, no]
  auto_advance: [yes, no]

template:
  setup: "setup_{lifecycle_type}_context"
  loop_entry: "enter_round_or_phase"
  execute: "execute_current_round"
  evaluate: "evaluate_round_outcome"
  transition: "decide_continue_stop_or_rollback"
  capture: "capture_learnings"
  resume_anchor: ".skill-lifecycle/{lifecycle_type}-state.json"
```

## Pipeline Selection

Router selects pipeline based on task characteristics:

| Task Pattern | Pipeline | Key Parameters |
|-------------|----------|----------------|
| Narrow implementation or bug fix | delivery | scope=narrow_slice |
| Product scope with acceptance criteria | delivery | scope=product_spec |
| Security audit with remediation | delivery | scope=audit_fix |
| Large rewrite or migration | delivery | scope=full_rewrite |
| Git workflow safety check | governance | gate_type=change_safety |
| Release readiness decision | governance | gate_type=release_readiness |
| Optimization with multiple rounds | lifecycle | lifecycle_type=iteration |
| Staged rollout with feedback | lifecycle | lifecycle_type=beta_rollout |
| Post-release monitoring | lifecycle | lifecycle_type=post_release_feedback |
| Automated background execution | lifecycle | lifecycle_type=auto_run |
| Project knowledge capture | lifecycle | lifecycle_type=knowledge_capture |
