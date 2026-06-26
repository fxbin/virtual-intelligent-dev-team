# Closure Type Pipelines

Workflow bundles organized by closure type for consistent execution patterns.

## Closure Types

Three fundamental closure types cover all workflow patterns:

| Closure Type | Description | Characteristics |
|-------------|-------------|-----------------|
| **Delivery** | Produce deliverables with acceptance criteria | Narrow slice, product spec, audit fix, full rewrite |
| **Governance** | Decision gates with pass/fail/hold outcomes | Change safety, release readiness |
| **Lifecycle** | Multi-round evolution with feedback loops | Iteration, beta rollout, post-release feedback |

## Pipeline Parameters

### Delivery Pipeline

**Purpose:** Produce deliverables with acceptance criteria

**Parameters:**
- `scope`: narrow_slice | product_spec | audit_fix | full_rewrite
- `planning_required`: yes | no
- `verification_mode`: self_review | verifier_cycle | none

**Resume anchor:** `.skill-delivery/current-{scope}.md`

### Governance Pipeline

**Purpose:** Decision gates with pass/fail/hold outcomes

**Parameters:**
- `gate_type`: change_safety | release_readiness
- `decision_mode`: ship_hold | pass_fail | fast_track

**Resume anchor:** `.skill-governance/{gate_type}-report.md`

### Lifecycle Pipeline

**Purpose:** Multi-round evolution with feedback loops

**Parameters:**
- `lifecycle_type`: iteration | beta_rollout | post_release_feedback | auto_run | knowledge_capture
- `round_based`: yes | no
- `auto_advance`: yes | no

**Resume anchor:** `.skill-lifecycle/{lifecycle_type}-state.json`

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
