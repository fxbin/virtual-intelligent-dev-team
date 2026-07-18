# Team Engine Lite Subgraph Protocol

> **定位变更**(P1-8):从"第七层独立闭环"降级为"Delivery closure 内的 Worker/Verifier 子图"。
> Verifier 独立性由"禁止上游预判下游"硬约束(P0-3)保证,而非独立成层。
> 详见 `references/verifier-extraction-guide.md` 的痛驱动抽取路径。

This protocol turns virtual software-team coordination from role routing into a replayable delivery contract.

It does not claim a real async multi-process runtime by itself. It defines the delivery contract this skill can enforce inside a host such as Codex, Claude Code, OpenCode, or a manual bridge.

When the host exposes actual spawn / wait / merge primitives and the task is eligible, Team Engine Lite may be upgraded through `real-subagent-runtime-protocol.md`. Without that runtime evidence, the route must keep `runtime_claim: soft_orchestration_only`.

## Purpose

`virtual-intelligent-dev-team` already routes work to leads, assistants, workflow bundles, release gates, and resume anchors.

Team Engine Lite adds a stricter rule:

- an implementer cannot final-approve its own work
- a release or delivery answer cannot rely only on worker self-report
- every non-trivial delivery loop must preserve a work order, worker output, verifier report, remediation patch when needed, and delivery cycle report
- max cycles and escalation are explicit instead of model-decided

## Roles

### Lead

The control plane.

Responsibilities:

- understand the user goal
- choose the smallest defensible workflow bundle
- create the `WorkOrder`
- assign Worker and Verifier roles
- merge accepted results
- stop, retry, or escalate based on `DeliveryCycleReport`

Forbidden:

- accepting a task without verifier evidence
- treating `worker_output.self_reported_done = true` as final completion
- hiding a `hold` or `fail` verdict behind a polished summary
- making final judgment statements about Worker output before Verifier returns a verdict (e.g., "should be fine", "can ship", "will pass")

### Worker

The production plane.

Responsibilities:

- implement, refactor, debug, write docs, generate plans, or produce the requested artifact
- keep the change scoped to the `WorkOrder`
- return `ImplementationOutput`
- name assumptions, touched artifacts, commands, and known risks

Forbidden:

- setting final `pass`, `ship`, or `accepted`
- editing the Verifier verdict
- removing the previous failure reason during retry

### Verifier

The quality plane.

Responsibilities:

- inspect Worker output against acceptance gates
- run or request objective checks when available
- return `VerificationReport`
- produce a `RemediationPatch` on `fail`
- return `hold` when evidence, permissions, or requirements are insufficient

Forbidden:

- replacing evidence with preference
- passing work without checking required gates
- silently rewriting the worker artifact and calling it verified

### Engine

The deterministic scheduling plane.

Responsibilities:

- move tasks through legal states
- enforce `max_cycles`
- require `RemediationPatch` before retry
- generate `DeliveryCycleReport`
- preserve resume anchors and evidence

### Human

The decision plane for ambiguity, risk, cost growth, permissions, and exhausted cycles.

## State Machine

Legal states:

- `planned`
- `spawned`
- `running`
- `produced`
- `verifying`
- `retrying`
- `passed`
- `failed`
- `spec_violation`
- `hold`
- `escalated`
- `human_resolved`
- `resumed`
- `accepted`

Legal transitions:

```text
planned -> spawned
spawned -> running
running -> produced
produced -> verifying
verifying -> passed
verifying -> retrying
verifying -> hold
verifying -> failed
verifying -> spec_violation
retrying -> running
spec_violation -> retrying
spec_violation -> escalated
passed -> accepted
hold -> escalated
failed -> escalated
escalated -> human_resolved
human_resolved -> resumed
resumed -> running
resumed -> accepted
```

Hard rules:

- `accepted` can only follow `passed` or `resumed`(人工接受)
- `retrying` requires `remediation_patch`
- `passed` requires `verification_report.verdict = pass`
- `failed` or `hold` requires blocker evidence or human escalation
- `spec_violation` requires an objective spec reference, evidence, and a remediation patch
- `cycle_count > max_cycles` must become `escalated`
- `human_resolved` requires human decision record(介入者、决策、理由)
- `resumed` 只能从 `human_resolved` 转入

### 人工介入点一等公民(P1-9)

人工介入不是 fallback,是流程中的一等公民。

| 介入点 | 触发条件 | 人的权力 | 恢复状态 |
|--------|---------|---------|---------|
| Delivery escalate | max_cycles 耗尽 | keep_baseline / rewrite_workorder / abort | resumed |
| Verifier 同根因 reject | 连续两次同根因 fail | adjust_patch / change_verifier / accept_risk | resumed |
| Intent drift | Worker 偏离 WorkOrder | reject_drift / accept_drift | resumed |
| Hold | 证据不足 | provide_evidence / abort | resumed |

人工介入决策必须写入 decision-log:

```json
{
  "event": "human_intervention",
  "timestamp": "<ISO 8601>",
  "intervener": "<角色或人>",
  "trigger": "<触发条件>",
  "decision": "<决策>",
  "rationale": "<理由>",
  "resume_state": "resumed"
}
```

## Standard Objects

### WorkOrder

```yaml
work_order:
  task_id:
  workflow_bundle:
  objective:
  lead_role:
  worker_role:
  verifier_role:
  input_artifacts:
  output_artifacts:
  acceptance_gates:
  dependency_ids:
  max_cycles:
  tool_boundary:
  context_boundary:
  backend_binding:
  permissions:
  resume_anchor:
```

### ImplementationOutput

```yaml
implementation_output:
  task_id:
  cycle_id:
  worker_role:
  produced_artifacts:
  artifact_delta:
  commands_run:
  tests_run:
  assumptions:
  known_risks:
  self_reported_done: true
```

### VerificationReport

```yaml
verification_report:
  task_id:
  cycle_id:
  verifier_role:
  verdict: "pass | fail | hold | spec_violation"
  checked_gates:
    - gate_id:
      passed:
      evidence:
  confirmed_issues:
    - issue_id:
      severity:
      evidence:
      fix_priority:
  remediation_patch:
    patch_id:
    instructions:
    must_keep:
    must_change:
    forbidden_changes:
  evidence_refs:
  false_positive_risk:
```

### RemediationPatch

```yaml
remediation_patch:
  patch_id:
  source_verification_report:
  worker_restart_from:
  instructions:
  must_keep:
  must_change:
  forbidden_changes:
  acceptance_delta:
```

### DeliveryCycleReport

```yaml
delivery_cycle_report:
  task_id:
  workflow_bundle:
  current_state:
  cycle_count:
  max_cycles:
  lead_role:
  worker_role:
  verifier_role:
  producer_can_self_pass: false
  checked_gates:
  verifier_verdict:
  confirmed_issues:
  remediation_patch:
  final_artifacts:
  evidence_refs:
  resume_anchor:
  backend_orchestration_verdict:
  human_escalation:
  next_state:
  team_engine_closure_verdict:
```

## Workflow Defaults

For code-facing bundles, Team Engine Lite is required:

- `plan-first-build`
- `product-spec-deliver`
- `quick-slice-deliver`
- `audit-fix-deliver`
- `govern-change-safely`
- `root-cause-remediate`
- `ship-hold-remediate`

For beta and post-release bundles, Team Engine Lite is required when the result opens implementation, remediation, rollout, or release decisions.

For `direct-execution`, Team Engine Lite is optional unless the task touches code, release, Git, or user-visible product behavior.

## Closure Verdict

`team_engine_closure_verdict` values:

- `pass`
  - verifier passed all required gates and evidence is available
- `pass_with_watch`
  - soft orchestration is structurally correct, but true backend/runtime isolation is not proven
- `hold`
  - required evidence, permissions, or role separation is missing
- `escalated`
  - max cycles, conflicting gates, or human decision required

Default for this skill is `pass_with_watch` unless a real external runtime proves independent role sessions and replayable artifacts.
