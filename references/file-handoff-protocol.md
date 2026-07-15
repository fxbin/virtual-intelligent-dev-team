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
    "artifact_path": ".skill-handoff/worker-output-001.json",
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

交接文件统一存放在 `.skill-handoff/` 目录下:

```
.skill-handoff/
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
3. **角色匹配检查**:`from_role` 和 `to_role` 是否符合交接方向(Worker→Verifier / Verifier→Lead / Verifier→Worker)
4. **类型枚举检查**:`artifact_type` 是否在允许枚举内

任一检查失败 → `allowed: false`,Verifier 不启动。

## 与 Worker Verifier Cycle Protocol 的关系

本协议是 `worker-verifier-cycle-protocol.md` 的硬约束补充。Cycle Objects 节列出的 5 种交接物必须按本协议落文件。

## 与 Circuit Breaker 的关系

file handoff 的文件存在性校验结果作为 circuit breaker 的 1.0 层确定性信号源:

- 文件不存在 → breaker 计数 +1
- schema 不合法 → breaker 计数 +1
- 连续 N 次失败 → breaker open,hard exit

breaker 本身由 `circuit_breaker.py` 实现,本协议只提供信号。
