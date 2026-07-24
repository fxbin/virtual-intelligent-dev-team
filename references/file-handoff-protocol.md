# File Handoff Protocol

## 核心规则

角色间交接必须落文件,禁止 prompt 粘贴。

Worker→Verifier、Lead→Worker、Verifier→Lead 的每次交接都必须产出一个可校验的文件 artifact,由 `verify_action.py` 的 `file-handoff` check 验证存在性和 schema 合法性。

## 交接物类型

| artifact_type | from_role | to_role | 模板 | 说明 |
|---------------|-----------|---------|------|------|
| `WorkOrder` | Lead | Worker | `assets/team-work-order-template.json` | 任务指令,含验收标准 |
| `ImplementationOutput` | Worker | Verifier | 无固定模板,含 diff/commands/tests | Worker 产出物 |
| `VerificationReport` | Verifier | Lead | `assets/completion-evidence-template.json` | 验收结论 |
| `DeliveryCycleReport` | Verifier | Lead | `assets/delivery-cycle-report-template.json` | 周期总结 |
| `RemediationPatch` | Verifier | Worker | 无固定模板,含 instructions | fail 时的修复指令 |

## 交接物 Schema

每个交接文件必须在顶层包含以下 handoff 元数据:

```json
{
  "handoff": {
    "from_role": "Worker",
    "to_role": "Verifier",
    "artifact_type": "ImplementationOutput",
    "artifact_path": ".vidt/handoff/worker-output-001.json",
    "timestamp": "2026-07-07T12:00:00Z"
  }
}
```

字段说明:

- `from_role`:产出方角色(Worker / Verifier / Lead)
- `to_role`:接收方角色(Worker / Verifier / Lead)
- `artifact_type`:交接物类型枚举
- `artifact_path`:文件相对路径(相对于 repo root)
- `timestamp`:ISO 8601 时间戳

## 存储路径

交接文件统一存放在 `.vidt/handoff/` 目录下:

```
.vidt/handoff/
  work-order-<id>.json
  worker-output-<id>.json
  verification-report-<id>.json
  delivery-cycle-report-<id>.json
  remediation-patch-<id>.json
```

`<id>` 为递增序号或基于 timestamp 的唯一标识。

## 校验规则

`verify_action.py --check file-handoff` 执行以下校验:

1. **存在性检查**:当前 cycle 的交接物文件是否存在
2. **schema 检查**:文件是否包含 `handoff` 元数据且字段合法
3. **完整字段检查**:`from_role`、`to_role`、`artifact_type`、`artifact_path`、`timestamp` 五个字段均非空
4. **精确角色契约检查**:每种 `artifact_type` 必须匹配上表中唯一的 `from_role → to_role`,不能只满足任意合法方向
5. **类型枚举检查**:`artifact_type` 是否在允许枚举内
6. **路径身份检查**:`artifact_path` 必须是 repo 内相对路径,解析后必须恰好指向当前被验证的 JSON 文件
7. **时间戳检查**:`timestamp` 必须是带时区的 ISO 8601 时间戳
8. **过滤命中检查**:传入 `--handoff-type` 时,目录中至少有一个该类型 artifact；其他类型不能冒充命中

任一检查失败 → `allowed: false`,Verifier 不启动。目录中任一 JSON artifact 元数据损坏时也 fail closed，不能靠另一个合法文件掩盖。

## 与 Worker Verifier Cycle Protocol 的关系

本协议是 `worker-verifier-cycle-protocol.md` 的硬约束补充。Cycle Objects 节列出的 5 种交接物必须按本协议落文件。

## 与 Circuit Breaker 的关系

file handoff 的文件存在性校验结果作为 circuit breaker 的 1.0 层确定性信号源:

- 文件不存在 → breaker 计数 +1
- schema 不合法 → breaker 计数 +1
- 连续 N 次失败 → breaker open,hard exit

breaker 本身由 `circuit_breaker.py` 实现,本协议只提供信号。
