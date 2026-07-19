# 复杂度 Ladder

> **来源**:ponytail 借鉴 + Sam Newman R4 收敛
> **用途**:六层闭环与交付子图逐项判断"该不该保留",防止协议膨胀
> **适用范围**:每次新增协议或加固层后必须走一遍 ladder

---

## 一、Ladder 五步判断

对每一层(或新增的协议/机制)依次走以下 5 步,任一步满足即停:

| 步骤 | 判断问题 | 满足时的动作 |
|------|----------|-------------|
| 1 | 这层需要存在吗? | 不需要 → 删除 |
| 2 | 已有层能覆盖吗? | 能 → 合并到已有层 |
| 3 | 能合并到相邻层吗? | 能 → 合并到相邻层 |
| 4 | 能降级为 advisory 吗? | 能 → 降级为 advisory(warning 不 hard fail) |
| 5 | 只能独立 | 最小化暴露面:只暴露输入契约 + 输出契约 |

### 判断原则

- **痛驱动**:只有当真实失败发生时才走 ladder,不做预防性拆分或合并
- **不可简化红线**:信任边界校验、防数据丢失、安全、可访问性不可降级
- **信息隐藏**(Sam Newman):每层只暴露输入契约 + 输出契约,agent 只加载当前层 prompt
- **ladder 是制衡工具**:每次加固(P1-6)后必须走 ladder,防止加固导致协议膨胀

---

## 二、六层与交付子图 Ladder 评估结果

基于 R4 圆桌讨论的收敛结论,对当前六层闭环与 Team Engine Lite 子图的评估:

### 层 1 — Planning(规划)

- **步骤 5:只能独立**
- **理由**:Planning 定义任务的可判定验收标准,是后续所有层的输入基础。Leslie 的不变量 `PlanWellFormed(plan_state)` 依赖此层独立
- **暴露面**:输入 = 用户请求;输出 = Goal + 验收标准 + 约束

### 层 2 — Routing(路由)

- **步骤 5:只能独立**
- **理由**:Routing 选 Lead 和 assistant agents,是能力匹配层。R4 分歧 1 明确不合并层 1+2,因为中间状态 `plan_done ∧ route_pending` 需要可观测
- **暴露面**:输入 = Plan;输出 = Lead + Assistants + process_skills + workflow_bundle

### 层 3 — Delivery(交付)

- **步骤 5:只能独立,层 7 降级为其子图**
- **理由**:Delivery 是 Worker/Verifier 执行层。层 7(Team Engine Lite)降级为 Delivery 内的子图(P1-8),不独立成层
- **暴露面**:输入 = Route decision + WorkOrder;输出 = ImplementationOutput + VerificationReport

### 层 4 — Iteration(迭代)

- **步骤 5:只能独立**
- **理由**:Iteration 处理 Verifier reject 后的 remediation loop,与 Delivery 的单次执行不同
- **暴露面**:输入 = VerificationReport(fail);输出 = RemediationPatch + 新 ImplementationOutput

### 层 5 — Release(发布)

- **步骤 5:只能独立**
- **理由**:Release 是 ship/hold 决策层,有独立的 gate 集合(release_gate_result_gate / blocking_issue_gate / rollback_gate 等)
- **暴露面**:输入 = DeliveryCycleReport(accepted);输出 = ship/hold 决策 + 发布证据

### 层 6 — Drill(演练)

- **步骤 3:合并到层 5 的并行兄弟**
- **理由**(Harrison R3):Drill 不是线性流程的后续步骤,而是与 Release 并行的验证通道。Drill 注入失败场景,验证其他六层的韧性
- **暴露面**:输入 = 注入场景;输出 = drill 结果 + 韧性报告
- **合并方式**:Drill 作为层 5 的并行兄弟,不作为层 5 的子步骤

### Delivery 子图 — Team Engine Lite（原第七层闭环）

- **步骤 2:降级为 Delivery 内子图**
- **理由**(Harrison + Simon + Kent R4 分歧 2 收敛):Worker/Verifier/Lead 三角色是 Delivery 内的执行机制,不是独立层。Verifier 独立性由"禁止上游预判下游"硬约束(P0-3)保证,而非独立成层
- **暴露面**:保留 Worker/Verifier/Lead 三角色和 legal states/transitions,但定位为 Delivery closure 内子图
- **详见**:`team-engine-lite-protocol.md`(P1-8 后标题改为"Team Engine Lite Subgraph Protocol")

---

## 三、Ladder 触发时机

| 触发事件 | 走 ladder 的层 |
|----------|---------------|
| 新增协议文件 | 新增的协议对应的层 |
| P1-6 闭环加固 | 六层与交付子图 |
| 新增 circuit breaker 层 | breaker 对应的层 |
| 新增 verify_action check | check 对应的层 |
| spec-evolution 触发 | spec 变更影响的层 |

---

## 四、Ladder 输出格式

每次走 ladder 必须产出评估记录,写入 decision-log:

```json
{
  "event": "ladder_evaluation",
  "timestamp": "<ISO 8601>",
  "trigger": "<触发事件>",
  "layer": "<层名>",
  "step_reached": 5,
  "decision": "independent | merge | degrade_to_advisory | delete",
  "rationale": "<判断理由>",
  "red_line_checked": true
}
```
