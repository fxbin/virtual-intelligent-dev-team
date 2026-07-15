# Iteration State Machine

> **State Schema**:本状态机是 `references/state-schema-spec.md` 中 layer 4(Iteration)的具体实现。
> 所有权:`iteration` 字段只能由 layer 4 写入,其他层只读。
> 不变量:`PlanWellFormed` 和 `RouteConsistent` 必须在进入 `initialized` 状态前满足。

Bounded iteration should follow a fixed local state machine.

## States

## 1. `initialized`

- round workspace exists
- ledger and reflection files exist
- baseline label and objective are locked
- candidate workspace snapshot may be captured before mutation

## 2. `benchmarked`

- candidate benchmark report exists
- report path is recorded
- benchmark failure is treated as evidence, not ignored
- optional apply command or candidate patch has already mutated the candidate workspace when the round requires code changes

## 3. `evaluated`

- candidate is compared against the baseline
- result is translated into one decision

## 4. `closed`

- decision is written to local state
- ledger and reflection are updated
- open loops are refreshed
- kept rounds may be promoted to a new baseline
- distilled patterns may be rebuilt from accepted rounds
- rollback command or reverse patch may run and capture a post-rollback snapshot when regression handling is enabled

## Transition Rules

- `initialized -> benchmarked`
  - only after a candidate report exists
- `benchmarked -> evaluated`
  - only after baseline and candidate can both be read
- `evaluated -> closed`
  - only after a decision is made

## Allowed Decisions

- `keep`
- `retry`
- `rollback`
- `stop`

## Failure Handling

- missing baseline registry: stop the cycle
- missing benchmark report: stop the cycle
- malformed benchmark JSON: stop the cycle
- inconclusive comparison: close with `retry`

## 显式失败路径(P1-9)

### Worker 三次重试失败

触发条件:`cycle_count >= max_cycles` 且 Verifier verdict 仍为 `fail`

路径:
1. 回滚到最后一个 `passed` 状态的 ImplementationOutput(如有)
2. 无 `passed` 历史 → 回滚到 WorkOrder 初始状态
3. circuit breaker 的 `verifier` 层 `record_failure`
4. 状态转为 `escalated`,通知人

恢复条件:人决定 `keep_baseline`(接受当前 baseline)/ `rewrite_workorder`(修改目标)/ `abort`(放弃)

### Verifier 连续两次 reject

触发条件:Verifier 连续两次返回 `fail` 且 RemediationPatch 方向一致(同一根因)

路径:
1. 标记为"同根因 retry"
2. circuit breaker 的 `verifier` 层 `record_failure`
3. 状态转为 `escalated`,通知人
4. 人审查 RemediationPatch 是否可行

恢复条件:人决定 `adjust_patch`(调整补丁)/ `change_verifier`(更换 Verifier)/ `accept_risk`(接受风险)

### Intent drift 探针

触发条件:Worker 产出的 artifact 与 WorkOrder 的 objective 语义偏离

检测方式:
- 关键词覆盖率:WorkOrder objective 中的关键词在 ImplementationOutput 中的覆盖率 < 60%
- 文件变更范围:Worker 修改的文件超出 WorkOrder 的 `tool_boundary` 和 `context_boundary`
- 新增抽象:Worker 引入 WorkOrder 未要求的 interface/factory/config(YAGNI 检测)

路径:
1. 标记为 `intent_drift`
2. Verifier verdict = `fail`,RemediationPatch = "删除偏离 intent 的变更"
3. circuit breaker 的 `delivery` 层 `record_failure`(如果 intent drift 连续发生)

恢复条件:Worker 从 WorkOrder 重新出发,不做偏离 intent 的变更
