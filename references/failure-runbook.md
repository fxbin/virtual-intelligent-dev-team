# 失败路径 Runbook

> **来源**:Kelsey R3/R4
> **用途**:每种失败模式的 retry policy、escalation gate、恢复路径
> **前置条件**:P0-4 circuit breaker 已落地(breaker 是失败路径的执行机制)

---

## 一、失败模式分类

| 失败模式 | 所属层 | breaker 层名 | 严重程度 |
|---------|-------|-------------|---------|
| Worker 三次重试失败 | Delivery(层 3) | verifier | 高 |
| Verifier 同根因 reject | Delivery(层 3) | verifier | 高 |
| Intent drift | Delivery(层 3) | delivery | 中 |
| Routing 错误 Lead | Routing(层 2) | routing | 中 |
| Baseline 丢失 | Iteration(层 4) | iteration | 高 |
| JSON corrupt | Iteration(层 4) | iteration | 中 |
| Resume/Plan drift | Planning + Iteration | planning | 中 |
| Release gate 假 ship | Release(层 5) | release | 高 |
| Verifier 永远 pass | Delivery(层 3) | verifier | 高 |

---

## 二、每种失败模式的 Runbook

### FM-1: Worker 三次重试失败

**触发**:`cycle_count >= max_cycles` 且 Verifier verdict 仍为 `fail`

**Retry Policy**:
- max_cycles 内:Worker 从 RemediationPatch 重新出发
- max_cycles 耗尽:不再 retry,直接 escalate

**Escalation Gate**:
1. 回滚到最后一个 `passed` 状态的 ImplementationOutput(如有)
2. 无 `passed` 历史 → 回滚到 WorkOrder 初始状态
3. circuit_breaker.record_failure("verifier", "max_cycles_exceeded")
4. 状态转为 `escalated`

**恢复路径**:
- 人决定 `keep_baseline` → 状态转为 `human_resolved` → `resumed` → `accepted`
- 人决定 `rewrite_workorder` → 状态转为 `human_resolved` → `resumed` → `running`(新 cycle)
- 人决定 `abort` → 状态转为 `human_resolved` → 流程终止

### FM-2: Verifier 同根因 reject

**触发**:Verifier 连续两次返回 `fail` 且 RemediationPatch 方向一致

**Retry Policy**:
- 第一次 fail:正常 retry
- 第二次 fail(同根因):标记"同根因 retry",不再自动 retry

**Escalation Gate**:
1. circuit_breaker.record_failure("verifier", "same_root_cause_reject")
2. 状态转为 `escalated`
3. 人审查 RemediationPatch 可行性

**恢复路径**:
- 人决定 `adjust_patch` → 状态转为 `human_resolved` → `resumed` → `running`
- 人决定 `change_verifier` → 状态转为 `human_resolved` → `resumed` → `verifying`(新 Verifier)
- 人决定 `accept_risk` → 状态转为 `human_resolved` → `resumed` → `accepted`(带 risk 标记)

### FM-3: Intent drift

**触发**:Worker 产出偏离 WorkOrder 的 objective

**检测方式**:
- 关键词覆盖率 < 60%
- 文件变更超出 tool_boundary / context_boundary
- 引入未请求的抽象(YAGNI 检测命中)

**Retry Policy**:
- 第一次 drift:Verifier 返回 `fail`,RemediationPatch = "删除偏离 intent 的变更"
- 连续 drift:circuit_breaker.record_failure("delivery", "intent_drift")

**Escalation Gate**:
- 连续 3 次 drift → 状态转为 `escalated`

**恢复路径**:
- 人决定 `reject_drift` → 状态转为 `human_resolved` → `resumed` → `running`(从 WorkOrder 重新出发)
- 人决定 `accept_drift` → 状态转为 `human_resolved` → `resumed` → `verifying`(接受 drift,继续验证)

### FM-4: Routing 错误 Lead

**触发**:Routing 层返回与任务不匹配的 Lead

**Retry Policy**:
- 不自动 retry,直接降级

**Escalation Gate**:
1. circuit_breaker.record_failure("routing", "wrong_lead")
2. 降级到 Direct Answer(breaker open 时)

**恢复路径**:
- breaker cooldown 后,half-open 探针测试 Routing 是否恢复
- 人可以手动 override 路由

### FM-5: Baseline 丢失

**触发**:Iteration 层找不到 baseline registry

**Retry Policy**:
- 不 retry,直接 stop the cycle

**Escalation Gate**:
1. circuit_breaker.record_failure("iteration", "baseline_missing")
2. 状态转为 `escalated`

**恢复路径**:
- 人恢复 baseline 文件 → 状态转为 `human_resolved` → `resumed` → `initialized`
- 人决定 `rebuild_baseline` → 状态转为 `human_resolved` → `resumed` → `initialized`(从当前状态重建 baseline)

### FM-6: JSON corrupt

**触发**:benchmark JSON 解析失败

**Retry Policy**:
- 不 retry,直接 stop the cycle

**Escalation Gate**:
1. circuit_breaker.record_failure("iteration", "json_corrupt")
2. 状态转为 `escalated`

**恢复路径**:
- 人修复 JSON 文件 → 状态转为 `human_resolved` → `resumed` → `benchmarked`
- 人决定 `regenerate_benchmark` → 状态转为 `human_resolved` → `resumed` → `initialized`(重新跑 benchmark)

### FM-7: Resume/Plan drift

**触发**:resume state 与 plan content 不一致

**Retry Policy**:
- 不 retry,直接 escalate

**Escalation Gate**:
1. circuit_breaker.record_failure("planning", "resume_plan_drift")
2. 状态转为 `escalated`

**恢复路径**:
- 人决定 `align_to_plan` → 状态转为 `human_resolved` → `resumed`(以 plan 为准)
- 人决定 `align_to_resume` → 状态转为 `human_resolved` → `resumed`(以 resume 为准,更新 plan)

### FM-8: Release gate 假 ship

**触发**:Release gate 返回 ship 但证据缺失

**Retry Policy**:
- 不 retry,直接 hold

**Escalation Gate**:
1. circuit_breaker.record_failure("release", "fake_ship")
2. 状态转为 `hold` → `escalated`

**恢复路径**:
- 人补充证据 → 状态转为 `human_resolved` → `resumed` → `accepted`(带补充证据)
- 人决定 `hold` → 状态转为 `human_resolved` → 流程保持在 hold

### FM-9: Verifier 永远 pass(失灵)

**触发**:Verifier 对所有产出都返回 pass,包括故意注入的失败

**Retry Policy**:
- 不 retry,直接 escalate

**Escalation Gate**:
1. circuit_breaker.record_failure("verifier", "always_pass")
2. breaker open 后,所有后续验证被阻断
3. 状态转为 `escalated`

**恢复路径**:
- 人检查 Verifier 逻辑 → 状态转为 `human_resolved` → `resumed` → `verifying`(修复后)
- 人决定 `manual_verify` → 状态转为 `human_resolved` → `resumed` → `accepted`(人工验证)

---

## 三、与 circuit breaker 的关系

每种失败模式都通过 circuit breaker 的 `record_failure` 记录。breaker 是失败路径的执行机制:

- breaker closed:正常流程,失败被记录但允许继续
- breaker open:流程被阻断,必须人工介入
- breaker half_open:放一个试探请求,绿了才恢复

breaker 配置见 `references/circuit-breaker-config.json`。

---

## 四、与人工介入点的关系

所有 escalate 到人的失败模式都走 `hold → escalated → human_resolved → resumed` 状态流转。

人工介入决策必须写入 decision-log,详见 `references/team-engine-lite-protocol.md` 的人工介入点一等公民章节。
