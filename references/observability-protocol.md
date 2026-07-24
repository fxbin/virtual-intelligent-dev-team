# Observability Protocol

- **版本**: v6.0.0
- **生效**: 2026-07-15
- **范围**: 六层闭环（Planning / Routing / Delivery / Iteration / Release / Drill）与 Team Engine Lite 交付子图的可观测性契约
- **定位**: 给系统装「故障会自己说话」的神经系统，先于压测落地

---

## 一、Purpose & Scope

本协议定义 metrics / logs / traces 三件套的**最小可操作契约**，用于回答两个问题：

1. 某层现在健康吗？（metrics）
2. 某次产出为什么偏离了意图？（logs + traces）

本协议**不定义**：仪表盘、告警规则、聚合看板、分布式追踪后端、metrics 持久化存储。这些属于 Non-Goals。

本协议是 `scripts/emit_telemetry.py` 和 `scripts/inspect_decision_log.py` 的**唯一契约来源**。脚本不得发明本协议未定义的字段。

---

## 二、Three Pillars（三件套定义与收敛上限）

### 2.1 Metrics

每层暴露 **3 个** metrics，不多不少：

| Metric | 类型 | 含义 | 采集者 |
|---|---|---|---|
| `layer_latency_seconds` | gauge | 该层单次执行耗时（秒） | emit_telemetry.py |
| `layer_failure_count` | counter | 该层累计失败次数（自进程启动） | emit_telemetry.py |
| `breaker_state` | enum(closed/open/half_open) | 该层 circuit breaker 当前状态 | emit_telemetry.py（读 circuit_breaker.py 状态文件） |

**收敛上限**：
- 不新增 p50/p95/p99 聚合（p99 由 inspect_decision_log.py 在报告期窗口内计算，不实时聚合）
- 不新增自定义业务 metric（如「路由命中率」属 decision-log 范畴，不进 metrics）
- 不新增 histogram / summary 类型

### 2.2 Logs

日志即 **decision-log**（`.vidt/metrics/decision-log.jsonl`），由 `route_request.py` / `verify_action.py` / `run_release_gate.py` 写入。本协议**不新增**日志源。

inspect_decision_log.py 的扩展仅**读取**已有 decision-log + breaker 状态文件 + telemetry jsonl，产出 health 报告，**不新增**写入。

### 2.3 Traces

层间 trace 由 `emit_telemetry.py` 写入 `.vidt/metrics/telemetry.jsonl`，每条记录一个 `step_id` 的完整层间流转：

```json
{
  "timestamp": "2026-07-15T12:34:56Z",
  "step_id": "step-20260715-001",
  "layer": "delivery",
  "latency_seconds": 12.4,
  "outcome": "success",
  "breaker_state_before": "closed",
  "breaker_state_after": "closed",
  "drift_score": 0.15,
  "drift_flag": false,
  "work_order_ref": "wo-20260715-001",
  "artifact_ref": "src/auth.py",
  "sampled": true,
  "sampling_rate": 1.0
}
```

**收敛上限**：
- 不引入 OpenTelemetry / Jaeger / Zipkin
- 不做跨进程 trace 传播（单进程层间 trace 足够）
- 不做 span 树形嵌套（扁平 step_id 序列即可）

---

## 三、Per-Layer SLO（每层 1 个可操作契约）

每层**只定义 1 个 SLO**，写成可操作契约（违反 → breaker 记 failure，非空话 KPI）。SLO 是 **advisory**（不 hard fail 阻塞当前执行），但累计违反触发 breaker。

| Layer | SLO | 阈值 | 违反后果 |
|---|---|---|---|
| Planning | WorkOrder 接收到 route_decision 派发的 p99 延迟 | < 30s | breaker 记 1 次 failure |
| Routing | route_request 解析到 WorkOrder 派发的 p99 延迟 | < 10s | breaker 记 1 次 failure |
| Delivery | Worker 接 WorkOrder 到产出 artifact 的 p99 延迟 | < 120s | breaker 记 1 次 failure |
| Iteration | Verifier 反馈到 Worker 修正完成的循环 p99 延迟 | < 90s | breaker 记 1 次 failure |
| Release | release_gate 评估完成 p99 延迟 | < 60s | breaker 记 1 次 failure |
| Drill | offline loop drill 单场景完整执行 p99 延迟 | < 300s | breaker 记 1 次 failure |
| Verifier | verify_action 单 check 执行 p99 延迟 | < 15s | breaker 记 1 次 failure |

**p99 计算窗口**：最近 20 次该层执行记录（滚动窗口，不持久化历史 p99）。窗口内样本 < 5 时不计算 p99，SLO 标 `insufficient_data` 不记 failure。

**重试上限**（Delivery 层专属，写成可操作契约）：
- Worker 接 WorkOrder 到产出 artifact，失败重试 **≤ 2 次**必须升级人工
- 第 3 次失败直接写 escalation-queue.jsonl，不进第 4 次

---

## 四、Intent Drift Probe（核心）

### 4.1 drift_score 定义

intent drift 探针检测 Worker 产出是否偏离 WorkOrder 意图。drift_score ∈ [0.0, 1.0]，由 3 个子分平均：

| 子分 | 计算方式 | 数据源 |
|---|---|---|
| `keyword_miss_rate` | 1 - (WorkOrder 关键词在产出 artifact 中出现数 / WorkOrder 关键词总数) | WorkOrder.text + 产出文件内容 |
| `tool_boundary_breach_rate` | 越界文件数 / 产出文件总数 | WorkOrder.tool_boundary + 产出文件路径 |
| `unrequested_abstraction_rate` | 引入未请求抽象数 / max(产出变更数, 1) | WorkOrder.scope + 产出 diff（新增的类/模块/配置项） |

```python
drift_score = (keyword_miss_rate + tool_boundary_breach_rate + unrequested_abstraction_rate) / 3
```

### 4.2 阈值与熔断联动

| drift_score | drift_flag | 后果 |
|---|---|---|
| ≤ 0.30 | false | 正常，记 telemetry |
| 0.30 < score ≤ 0.50 | true（warn） | 记 telemetry，breaker 不记 failure |
| > 0.50 | true（critical） | 记 telemetry + breaker 记 1 次 failure |

**熔断联动**：drift_score > 0.50 记 failure，连续达该层 `max_consecutive_failures`（见 circuit-breaker-config.json）触发 breaker open。

此阈值与 [failure-runbook.md](./failure-runbook.md) FM-3 Intent drift 对齐：
- FM-3 关键词覆盖率 < 60% ⟺ keyword_miss_rate > 0.40
- FM-3 连续 3 次 drift → escalated ⟺ Delivery 层 max_consecutive_failures=3

### 4.3 采样率

- **默认采样率 = 1.0（全量）**：每个 WorkOrder 的产出都跑 drift 探针
- 采样率 < 1.0 时**必须**用 `known-shortcut:` 标注：

```json
{
  "sampled": false,
  "sampling_rate": 0.3,
  "known_shortcut": "采样率 0.3 会漏掉低频 drift（< 30% 的 WorkOrder 被探针覆盖）；升级路径：将 sampling_rate 调至 1.0 实现全量覆盖"
}
```

**known-shortcut 标注强制项**：
1. 天花板：当前采样率漏掉什么
2. 升级路径：如何回到全量

未标注 known-shortcut 的低采样率记录视为协议违反（evals 校验）。

---

## 五、Emit Contract（emit_telemetry.py 输出 schema）

`emit_telemetry.py` 是**唯一**的 telemetry 写入者。输出到 `.vidt/metrics/telemetry.jsonl`，每行一条 JSON。

### 5.1 必填字段（13 项）

| 字段 | 类型 | 说明 |
|---|---|---|
| `timestamp` | string(ISO8601) | 记录时间，UTC |
| `step_id` | string | 步骤唯一标识，格式 `step-YYYYMMDD-NNN` |
| `layer` | enum | planning / routing / delivery / iteration / release / drill / verifier |
| `latency_seconds` | float | 该层单次执行耗时 |
| `outcome` | enum | success / failure / held / degraded |
| `breaker_state_before` | enum | closed / open / half_open |
| `breaker_state_after` | enum | closed / open / half_open |
| `drift_score` | float | 见 §4.1，非 delivery 层填 0.0 |
| `drift_flag` | bool | drift_score > 0.30 时 true |
| `work_order_ref` | string | 关联的 WorkOrder ID（可空串） |
| `artifact_ref` | string | 产出文件路径（可空串） |
| `sampled` | bool | 是否被采样 |
| `sampling_rate` | float | 当前采样率 [0.0, 1.0] |

### 5.2 可选字段（采样率 < 1.0 时必填）

| 字段 | 类型 | 说明 |
|---|---|---|
| `known_shortcut` | string | 见 §4.3，天花板 + 升级路径 |

### 5.3 CLI 契约

```bash
python scripts/emit_telemetry.py \
  --layer delivery \
  --step-id step-20260715-001 \
  --latency 12.4 \
  --outcome success \
  --work-order-ref wo-20260715-001 \
  --artifact-ref src/auth.py \
  --drift-score 0.15 \
  [--sampling-rate 1.0] \
  [--repo .]
```

emit_telemetry.py 内部读取 `circuit_breaker.py` 的 `get_state(layer)` 填充 `breaker_state_before` / `breaker_state_after`，调用方不需传入。

---

## 六、Inspect Contract（inspect_decision_log.py 扩展契约）

inspect_decision_log.py **保留**现有 decision-log 报告功能（v5.0.2 契约不变），**新增**每层 health metrics 报告。

### 6.1 新增 CLI

```bash
python scripts/inspect_decision_log.py --health-report [--window 30d] [--repo .]
```

`--health-report` 触发每层 health 报告，输出到 stdout（`--pretty`）或 `--markdown-output` / `--html-output`。

### 6.2 Health Report 字段（每层）

| 字段 | 来源 | 说明 |
|---|---|---|
| `layer` | 枚举 | 六个 closure 或 verifier 子图之一 |
| `slo_target_seconds` | 本协议 §3 | 该层 SLO 阈值（单位：秒） |
| `p99_latency_seconds` | telemetry.jsonl 滚动窗口 | 最近 20 次该层 latency 的 p99 |
| `slo_status` | 计算 | met / violated / insufficient_data |
| `failure_count_window` | telemetry.jsonl | 窗口内 outcome=failure 计数 |
| `drift_critical_count` | telemetry.jsonl | 窗口内 drift_score > 0.50 计数 |
| `breaker_state` | circuit_breaker.py | 当前 breaker 状态 |
| `breaker_open_count` | escalation-queue.jsonl | 窗口内该层 breaker open 次数 |

### 6.3 向后兼容

- 不带 `--health-report` 时，行为与 v5.0.2 完全一致
- footer version 升级为 `6.0.0`（原写死 `5.0.2`）
- HTML dashboard 新增「Layer Health」区块，置于 KPI cards 之后

---

## 七、Non-Goals（明确不做）

1. **不做仪表盘**：不新增独立 dashboard 服务，inspect_decision_log.py 的 HTML 报告是唯一可视化出口
2. **不做告警规则**：不新增 alerting rules 配置，熔断由 circuit_breaker.py 负责
3. **不做聚合看板**：不新增跨层聚合面板，每层独立报告
4. **不做 metrics 持久化**：telemetry.jsonl 是 append-only 日志，不导出到 TSDB
5. **不做分布式 tracing**：不引入 OpenTelemetry SDK，不跨进程传播 trace context
6. **不做实时流**：不新增 WebSocket / SSE 推送，报告按需生成
7. **不做自动根因**：根因分析留给 failure-runbook.md 和人工，本协议只提供数据
8. **不做 ponytail gate**：本协议不把 ponytail 检查产品化为 enforceable gate，只嵌入 known-shortcut 标注

---

## 八、与其他协议的关系

| 协议 | 关系 |
|---|---|
| [layer-reinforcement-protocol.md](./layer-reinforcement-protocol.md) | 本协议的 SLO 是该协议 §每层 SLO 模板的具体化 |
| [circuit-breaker-protocol.md](./circuit-breaker-protocol.md) | 本协议的 drift_score > 0.50 触发该协议的 record_failure |
| [circuit-breaker-config.json](./circuit-breaker-config.json) | 本协议的熔断阈值（max_consecutive_failures）读自该配置 |
| [failure-runbook.md](./failure-runbook.md) | 本协议的 drift 探针与 FM-3 Intent drift 对齐 |
| [workspace-journal-protocol.md](./workspace-journal-protocol.md) | journal 是 event sourcing，telemetry 是 metrics sourcing，两者独立不合并 |
| [complexity-ladder.md](./complexity-ladder.md) | 每个 metric 走 ladder rung-1（YAGNI）判断该不该存在，本协议 §2 已收敛到 3 个 |
