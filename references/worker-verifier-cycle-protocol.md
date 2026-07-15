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

### File Handoff 硬约束

上述 5 种交接物必须按 `file-handoff-protocol.md` 落文件到 `.skill-handoff/` 目录,禁止 prompt 粘贴交接。

每个交接文件必须在顶层包含 `handoff` 元数据(`from_role` / `to_role` / `artifact_type` / `artifact_path` / `timestamp`)。

`verify_action.py --check file-handoff` 会校验交接物的存在性、schema 合法性、角色方向匹配和类型枚举。任一校验失败 → Verifier 不启动。

### Verifier 验收维度扩展

Verifier 的 Allowed verdicts 在 `pass` / `fail` / `hold` 之外新增:

- `spec_violation`:Worker 产出违反 `routing-rules.json` 或相关 spec 文件中的规范

`spec_violation` 是可断言的事实(规范条目可 diff/grep),不是主观判断。与 `fail` 的区别:`fail` 是 WorkOrder 完成度不足(主观判断),`spec_violation` 是规范符合度不足(客观事实)。

发现 `spec_violation` 时,Verifier 返回 `spec_violation` verdict 并触发 `update_spec.py`(如果规范未覆盖该 edge case)。

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
