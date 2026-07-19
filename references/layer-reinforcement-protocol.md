# 六层闭环与交付子图加固协议

> **来源**:Martin Fowler + Adrian Cockcroft + Kelsey + Sam Newman R3 共识
> **用途**:六层闭环与 Team Engine Lite 交付子图的独立校验、状态机提升、降级行为、Drill 扩展、SLO、信息隐藏、人工介入点
> **前置条件**:P0-4 circuit breaker 已落地(每层 breaker 是加固的基础)

---

## 一、层间独立校验(Martin)

每层入口必须独立校验前置条件,不默认信任上一层。

| 层 | 入口校验 | 校验失败动作 |
|----|----------|-------------|
| 1 Planning | 用户请求非空、有可判定目标 | 拒绝,要求澄清 |
| 2 Routing | Plan 存在、验收标准非空 | 降级到 Direct Answer |
| 3 Delivery | Route decision 存在、Lead 已分配 | 拒绝,回退到 Routing |
| 4 Iteration | VerificationReport(fail)存在、RemediationPatch 非空 | 跳过,保持 baseline |
| 5 Release | DeliveryCycleReport(accepted)存在 | 拒绝,回退到 Delivery |
| 6 Drill | 注入场景定义完整 | 跳过该场景 |
| D1 Team Engine Lite 子图 | WorkOrder 存在、Worker/Verifier 角色已分配 | 拒绝,不启动 cycle |

原则:校验失败时,层可以选择降级或回退,但不能跳过校验直接执行。

---

## 二、状态机提升(Martin)

Team Engine Lite 的 legal states/transitions 模式向上提升,覆盖六层闭环与交付子图。

### 统一状态机模板

每层必须定义:

```yaml
layer_state_machine:
  layer: "<层名>"
  legal_states:
    - idle
    - in_progress
    - done
    - failed
    - degraded
  legal_transitions:
    - idle -> in_progress
    - in_progress -> done
    - in_progress -> failed
    - in_progress -> degraded
    - degraded -> in_progress
    - failed -> idle
  entry_guard: "<入口校验条件>"
  exit_guard: "<出口校验条件>"
  degradation_path: "<降级行为>"
```

### 各层状态定义

| 层 | idle → in_progress 触发 | done 条件 | degraded 条件 |
|----|------------------------|----------|--------------|
| 1 Planning | 用户请求到达 | Goal + 验收标准锁定 | 目标模糊,降级为 advisory |
| 2 Routing | Plan done | Lead + Assistants 分配完成 | 路由失败,降级到 Direct Answer |
| 3 Delivery | Route done | VerificationReport(pass) | Worker 失败,降级到 retry/escalate |
| 4 Iteration | VerificationReport(fail) | keep/stop 决策 | retry 预算耗尽,降级到 escalate |
| 5 Release | DeliveryCycleReport(accepted) | ship/hold 决策 | gate 失败,降级到 hold+bootstrap |
| 6 Drill | 注入场景到达 | drill 报告生成 | 场景无法执行,跳过 |
| D1 子图 | WorkOrder 创建 | DeliveryCycleReport 生成 | max_cycles 耗尽,降级到 escalate |

---

## 三、每层 Circuit Breaker + 降级行为(Adrian/Kelsey)

基于 P0-4 的 `circuit_breaker.py`,每层配置独立的 breaker。

| 层 | breaker 层名 | max_consecutive_failures | 降级行为(breaker open 时) |
|----|-------------|------------------------|--------------------------|
| 1 Planning | planning | 3 | 降级到 advisory(只给建议不执行) |
| 2 Routing | routing | 3 | 降级到 Direct Answer |
| 3 Delivery | delivery | 3 | 降级到 hold,等待人工介入 |
| 4 Iteration | iteration | 3 | 保持 baseline,停止 retry |
| 5 Release | release | 2 | 降级到 hold,不 ship |
| 6 Drill | drill | 5 | 跳过该场景,继续下一个 |
| D1 子图 | verifier | 3 | 降级到 hold,escalate 到人 |

breaker 配置文件:`references/circuit-breaker-config.json`

---

## 四、Drill 扩展到六层与交付子图(Adrian)

现有 drill 只覆盖 Iteration(层 4)和 Release(层 5)。扩展到全部六层与 Team Engine Lite 子图:

| Drill 场景 | 注入的失败 | 验证的层 |
|-----------|----------|---------|
| Routing 返回错误 lead agent | 路由到不匹配的 Lead | 层 2 |
| Verifier 永远 pass | Verifier 失灵 | D1 子图 + 层 3 |
| baseline 被删 | 基准文件丢失 | 层 4 |
| JSON corrupt | benchmark JSON 损坏 | 层 4 |
| resume/plan drift | resume state 与 plan 不一致 | 层 1 + 层 4 |
| contract mismatch | 前后端接口不对齐 | 层 3 |
| Release gate 假 ship | gate 返回 ship 但证据缺失 | 层 5 |

详见 `references/offline-loop-drill-playbook.md` 的扩展场景。

---

## 五、每层 SLO + on-call(Kelsey)

每层定义 P99、失败次数阈值、escalation 路径。

```yaml
layer_slo:
  layer: "<层名>"
  p99_latency: "<目标延迟>"
  failure_threshold: "<连续失败次数阈值,触发 breaker>"
  escalation_path:
    - target: "<角色或人>"
      condition: "<触发条件>"
```

SLO 定义是 advisory(不 hard fail),用于可观测性和容量规划。

---

## 六、信息隐藏(Sam)

每层只暴露输入契约 + 输出契约,agent 只加载当前层 prompt。

| 层 | 输入契约 | 输出契约 | agent 不应看到的 |
|----|---------|---------|-----------------|
| 1 Planning | 用户请求 | Goal + 验收标准 | 路由细节、agent 分配 |
| 2 Routing | Plan | Lead + Assistants + workflow_bundle | Worker 执行细节 |
| 3 Delivery | Route decision + WorkOrder | ImplementationOutput + VerificationReport | Release gate 细节 |
| 4 Iteration | VerificationReport(fail) | RemediationPatch + 新 ImplementationOutput | Release 决策 |
| 5 Release | DeliveryCycleReport(accepted) | ship/hold 决策 | Drill 场景 |
| 6 Drill | 注入场景 | drill 报告 | 生产流程细节 |
| D1 子图 | WorkOrder | DeliveryCycleReport | 其他层的 state |

实现方式:hook 注入(P1-19)只加载当前层所需的 spec 条目。

---

## 七、人工介入点一等公民(Kelsey)

人工介入不是 fallback,而是流程中的一等公民。

### 介入点

| 介入点 | 触发条件 | 人的权力 |
|--------|---------|---------|
| Planning hold | 目标模糊 | 澄清或拒绝 |
| Routing override | 路由不合适 | 更换 Lead |
| Delivery escalate | max_cycles 耗尽 | 接受/拒绝/重试 |
| Iteration stop | retry 预算耗尽 | keep/rollback/stop |
| Release hold | gate 失败 | ship/hold/bootstrap |
| Drill review | drill 发现韧性缺口 | 修复或接受风险 |

### 介入状态流转

```text
hold -> escalated -> human_resolved -> resumed
```

- `hold`:流程暂停,等待介入
- `escalated`:已通知人,等待响应
- `human_resolved`:人做出决策
- `resumed`:基于人的决策恢复流程

人工介入决策必须写入 decision-log,包含:介入者、决策、理由、时间戳。

---

## 八、与复杂度 Ladder 的关系

每次加固后必须走 `references/complexity-ladder.md` 的 5 步判断,防止加固导致协议膨胀。

加固是加法,ladder 是减法,两者制衡。
