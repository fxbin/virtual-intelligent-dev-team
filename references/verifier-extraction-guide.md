# Verifier 抽取指南

> **来源**:Kent Beck R4 分歧 2 收敛
> **用途**:定义何时将 Team Engine Lite 子图中的 Verifier 抽取为横切节点
> **核心原则**:痛驱动重构,不预先分层(speculation)

---

## 一、为什么不预先抽取

Kent Beck 的原则:预先分层是 speculation。

- 层 7 已降级为 Delivery 内子图(P1-8),Verifier 是子图内的角色
- 在没有真实痛点时,抽取 Verifier 为横切节点会增加不必要的间接层
- 痛了再拆,不痛不拆

---

## 二、痛驱动重构的触发条件

当以下任一条件满足时,考虑抽取 Verifier 为横切节点:

### 触发条件 1:Iteration/Release 层出现独立验收需求

**信号**:Iteration 层(层 4)或 Release 层(层 5)需要直接调用 Verifier,而不经过 Delivery 子图。

**示例**:Release gate 需要独立验证发布候选,而不是依赖 Delivery 子图的 VerificationReport。

**动作**:将 Verifier 抽取为横切节点,允许 Iteration 和 Release 层直接调用。

### 触发条件 2:测试变难(mock 需钻进 Delivery 内部)

**信号**:为 Iteration 或 Release 层写测试时,需要 mock Delivery 子图的内部状态才能测试 Verifier。

**示例**:测试 Release gate 时,需要构造完整的 DeliveryCycleReport 才能触发 Verifier 逻辑。

**动作**:将 Verifier 抽取为独立节点,减少测试的依赖深度。

### 触发条件 3:跨层验收需求出现

**信号**:多个层需要共享同一套验收标准,但各自维护副本导致不一致。

**示例**:Delivery 和 Release 都需要检查"测试通过",但各自实现了不同的检查逻辑。

**动作**:将验收逻辑抽取为横切节点,供多个层共享。

---

## 三、抽取路径

抽取按以下顺序进行,每步只在痛了才走:

```text
子图内角色 → 可复用 node → 横切节点
```

### 步骤 1:子图内角色(当前状态)

- Verifier 是 Delivery 子图内的角色
- 只在 Delivery 子图内被调用
- 输入:ImplementationOutput;输出:VerificationReport

### 步骤 2:可复用 node

- Verifier 逻辑提取为可复用的函数/模块
- 仍由 Delivery 子图调用,但逻辑独立
- 其他层可以 import 但不直接调用

### 步骤 3:横切节点

- Verifier 成为独立的横切节点
- 多个层(Delivery、Iteration、Release)可直接调用
- 有独立的输入契约和输出契约
- 有独立的 circuit breaker 层

---

## 四、抽取后的影响

如果 Verifier 被抽取为横切节点:

| 影响项 | 变更 |
|--------|------|
| `team-engine-lite-protocol.md` | Verifier 从子图角色升级为横切节点,引用本指南 |
| `verify_action.py` | 新增 `verifier-cross-layer` check,验证跨层调用的合法性 |
| `circuit-breaker-config.json` | 新增 `verifier-cross-layer` breaker 层 |
| `complexity-ladder.md` | 抽取后必须走 ladder 判断是否合理 |

---

## 五、抽取决策记录

每次抽取决策必须写入 decision-log:

```json
{
  "event": "verifier_extraction",
  "timestamp": "<ISO 8601>",
  "trigger_condition": "<触发条件编号>",
  "evidence": "<痛点证据>",
  "decision": "extract_to_reusable_node | extract_to_cross_cutting",
  "impacted_layers": ["<受影响的层>"],
  "ladder_evaluated": true
}
```

---

## 六、不做什么

| 排除项 | 理由 |
|--------|------|
| 不在无痛点时预先抽取 | Kent Beck:speculation |
| 不抽取 Worker | Worker 是执行层,不需要跨层复用 |
| 不抽取 Lead | Lead 是控制层,跨层复用会破坏控制平面/执行平面分离 |
