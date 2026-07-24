# State Schema 规范

> **来源**:Leslie Lamport + Harrison R4 分歧 1 收敛
> **用途**:统一六层闭环与 Team Engine Lite 子图的 state schema,同时保留边界(合并容器不合并所有权)
> **核心原则**:中间状态可观测,不变量可证明

---

## 一、Harrison 方案:合并容器不合并所有权

state 存储在统一容器中,但每层的写入权归该层所有。

```yaml
LayerState:
  plan:
    reducer: last-writer-wins
    writers: [layer1]
  route:
    reducer: last-writer-wins
    writers: [layer2]
  delivery:
    reducer: last-writer-wins
    writers: [layer3, layer7_subgraph]
  iteration:
    reducer: last-writer-wins
    writers: [layer4]
  release:
    reducer: last-writer-wins
    writers: [layer5]
  shared:
    reducer: merge
    writers: [layer1, layer2, layer3, layer4, layer5]
```

### 字段说明

| 字段 | reducer | writers | 含义 |
|------|---------|---------|------|
| plan | last-writer-wins | [layer1] | 规划层的输出(Goal + 验收标准) |
| route | last-writer-wins | [layer2] | 路由层的输出(Lead + Assistants) |
| delivery | last-writer-wins | [layer3, layer7_subgraph] | 交付层 + 子图的输出 |
| iteration | last-writer-wins | [layer4] | 迭代层的输出(retry/keep/stop) |
| release | last-writer-wins | [layer5] | 发布层的输出(ship/hold) |
| shared | merge | [all layers] | 跨层共享的只读上下文 |

### 所有权规则

- 每个字段只能由 `writers` 列表中的层写入
- 其他层只能读取,不能写入
- `shared` 字段所有层可写,但使用 merge reducer(不覆盖)
- 违反所有权 → `verify_action.py` 的 spec-violation check

---

## 二、Leslie 的不变量定义

不变量是跨层的可证明条件,不依赖单层的善意。

### 不变量 1:PlanWellFormed

```python
PlanWellFormed(plan_state):
    return (
        plan_state.goal is not None
        and plan_state.acceptance_criteria is not None
        and len(plan_state.acceptance_criteria) > 0
        and all(c.is_decidable for c in plan_state.acceptance_criteria)
    )
```

- 任务有可判定验收标准
- "可判定" = 能通过 diff/grep/命令执行来验证

### 不变量 2:RouteConsistent

```python
RouteConsistent(route_state, plan_state):
    return (
        route_state.lead_agent is not None
        and route_state.lead_agent.capabilities >= plan_state.required_capabilities
        and route_state.workflow_bundle is not None
    )
```

- agent 能力 ⊇ 任务需求
- workflow_bundle 非空

### 不变量 3:DeliveryComplete

```python
DeliveryComplete(delivery_state):
    return (
        delivery_state.implementation_output is not None
        and delivery_state.verification_report is not None
        and delivery_state.verification_report.verdict == "pass"
    )
```

- 交付完成 = 有实现输出 + 有验证报告 + verdict = pass

### 不变量 4:ReleaseEvidenceBacked

```python
ReleaseEvidenceBacked(release_state, delivery_state):
    return (
        release_state.decision in ["ship", "hold"]
        and (
            release_state.decision == "hold"
            or (
                release_state.decision == "ship"
                and DeliveryComplete(delivery_state)
                and release_state.gate_result.overall_status == "ship"
            )
        )
    )
```

- ship 决策必须有证据支撑

---

## 三、中间状态保留

以下中间状态必须可观测(不合并、不跳过):

| 中间状态 | 含义 | 可观测方式 |
|---------|------|-----------|
| `plan_done ∧ route_pending` | 规划完成但尚未路由 | decision-log 事件 |
| `route_done ∧ delivery_pending` | 路由完成但尚未交付 | decision-log 事件 |
| `delivery_done ∧ iteration_pending` | 交付完成但验收未通过 | VerificationReport |
| `iteration_done ∧ release_pending` | 迭代完成但尚未发布 | DeliveryCycleReport |

这些中间状态是 Leslie 论证可组合性的基础。合并层会让这些状态不可见,从而无法证明流程的正确性。

---

## 四、State 持久化

state 持久化到 `.vidt/harness/layer-state.json`:

```json
{
  "plan": { ... },
  "route": { ... },
  "delivery": { ... },
  "iteration": { ... },
  "release": { ... },
  "shared": { ... },
  "invariants": {
    "plan_well_formed": true,
    "route_consistent": true,
    "delivery_complete": false,
    "release_evidence_backed": false
  }
}
```

### 与 Workspace Journal 的关系

state 是快照,journal 是事件流(P1-10)。state 可从 journal replay 重建。

---

## 五、与现有协议的关系

| 现有协议 | 本规范的关系 |
|---------|------------|
| `iteration-state-machine.md` | Iteration 层的状态机是本规范 layer 4 的具体实现 |
| `team-engine-lite-protocol.md` | Team Engine Lite 的状态机是 Delivery 子图的具体实现；状态容器沿用兼容标识 `layer7_subgraph` |
| `automation-state.schema.json` | 自动化状态文件是 `shared` 字段的持久化形式 |
| `circuit-breaker-config.json` | 每层 breaker 的状态独立于 layer state |
