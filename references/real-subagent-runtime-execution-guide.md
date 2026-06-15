# Real Subagent Runtime - Execution Guide

**版本：** 1.0.0  
**定位：** 真实 Subagent 运行时的实际调用执行指南  
**适用：** Virtual Intelligent Dev Team 的 real_subagent_runtime 模式

---

## 问题诊断

### 当前状态（部分不足）

**现有协议已经很好地定义了：**
- ✅ Runtime 声明（real_subagent_runtime / single_backend_multi_session / soft_orchestration_only）
- ✅ 角色边界（Lead / Worker / Verifier / Explorer / Memory Keeper）
- ✅ SubagentRuntimePlan 合同
- ✅ 并行规则和合并验收条件

**但缺少：**
- ❌ **实际的 Agent 调用指令模板**
- ❌ **具体的 Prompt 构造示例**
- ❌ **真正的执行步骤**

---

### 目标状态（补充）

本指南不替代 `real-subagent-runtime-protocol.md`，而是**补充实际执行层**。

**补充内容：**
- ✅ 如何实际调用 Agent tool
- ✅ Worker/Verifier/Explorer 的 Prompt 模板
- ✅ 并行执行的具体步骤
- ✅ 输出收集和合并的实际操作

---

## 执行前提检查

在调用 Subagent 前，必须先确认：

### 1. Runtime 能力检查

```markdown
【Runtime 能力声明】

当前环境支持：
- [ ] real_subagent_runtime - 真正的独立 subagent（有 spawn/wait/merge 工具）
- [ ] single_backend_multi_session - 独立会话但非完全管理
- [ ] soft_orchestration_only - 单线程角色模拟

经检查，本次运行时声明为：`{runtime_claim}`
```

### 2. 激活条件检查

```markdown
【激活条件】

满足以下条件之一：
- [ ] 用户显式要求："multi-agent" / "subagents" / "parallel agents" / "spawn agents" / "多 agent" / "并行 agent"
- [ ] 用户要求 `/auto` 且工作流在白名单中
- [ ] Lead 判断任务需要并行执行（需向用户说明理由）

本次激活原因：{activation_reason}
```

### 3. SubagentRuntimePlan

在 spawn 前，Lead 必须产出：

```yaml
subagent_runtime_plan:
  runtime_claim: "real_subagent_runtime"
  activation_reason: "用户要求并行实现 3 个独立模块"
  workflow_bundle: "parallel_implementation"
  max_subagents: 4
  spawn_policy:
    user_explicit_or_auto_required: true
    no_default_swarm: true
    blocking_work_stays_local: true
  agents:
    - role: "worker"
      task: "实现模块 A"
      write_scope: "src/module-a/**"
      context_policy: "模块 A 的需求和接口"
      output_contract: "ImplementationOutput"
      can_write_artifact: true
      can_write_verdict: false
    - role: "worker"
      task: "实现模块 B"
      write_scope: "src/module-b/**"
      context_policy: "模块 B 的需求和接口"
      output_contract: "ImplementationOutput"
      can_write_artifact: true
      can_write_verdict: false
    - role: "verifier"
      task: "验证所有实现"
      write_scope: "无（只读）"
      context_policy: "所有 Worker 输出 + 需求"
      output_contract: "VerificationReport"
      can_write_artifact: false
      can_write_verdict: true
  merge_policy:
    lead_merges_only: true
    verifier_before_acceptance: true
    conflict_resolution: "Verifier fail → Lead 裁决"
  fallback:
    unavailable_runtime: "降级为串行单 Agent 执行"
    malformed_output: "标记为 hold，要求重试或人工介入"
    role_boundary_violation: "拒绝接受，要求修正"
```

---

## 实际执行指令

### 场景 1: 并行实现（多个独立模块）

**适用：** 用户要求实现多个互不依赖的功能模块

```markdown
我现在启动并行实现。

【重要】我会**并行唤起 N 个独立 Worker Agent**，每个 Worker 负责一个模块的实现，**互不干扰**。实现完成后，唤起 1 个 Verifier Agent 验证所有实现。

## SubagentRuntimePlan
{显示上面的 plan}

---

## Worker Agent 1: 实现模块 A
[唤起独立 Agent - Worker]

Prompt:
---
你是一个 Worker Agent，负责实现模块 A。

**角色边界：**
- 你只能编辑 `src/module-a/**` 目录下的文件
- 你必须返回 ImplementationOutput
- 你不能写最终 pass / ship / accepted

**任务：**
{module_a_requirements}

**上下文：**
- 模块 A 的接口定义：{interface_spec}
- 依赖的其他模块：{dependencies}
- 现有代码结构：{current_structure}

**输出要求：**
返回 JSON 格式的 ImplementationOutput：
{
  "role": "worker",
  "task": "实现模块 A",
  "write_scope": "src/module-a/**",
  "implementation_summary": "...",
  "files_changed": [
    {"path": "src/module-a/index.ts", "change_type": "created | modified"},
    ...
  ],
  "tests_added": [...],
  "dependencies_added": [...],
  "known_issues": [...],
  "self_reported_done": true
}

不要输出最终 verdict（pass/fail），只输出实现结果。
---

[等待 Worker 1 输出] → 保存为 worker_1_output

---

## Worker Agent 2: 实现模块 B
[唤起独立 Agent - Worker]

Prompt:
---
你是一个 Worker Agent，负责实现模块 B。

**角色边界：**
- 你只能编辑 `src/module-b/**` 目录下的文件
- 你必须返回 ImplementationOutput
- 你不能写最终 pass / ship / accepted

**任务：**
{module_b_requirements}

**上下文：**
- 模块 B 的接口定义：{interface_spec}
- 依赖的其他模块：{dependencies}
- 现有代码结构：{current_structure}

**输出要求：**
返回 JSON 格式的 ImplementationOutput（同上）
---

[等待 Worker 2 输出] → 保存为 worker_2_output

---

## Verifier Agent: 验证所有实现
[唤起独立 Agent - Verifier]

Prompt:
---
你是一个 Verifier Agent，负责验证所有 Worker 的实现。

**角色边界：**
- 你不能编辑文件
- 你必须返回 VerificationReport
- 你可以输出 verdict: pass / fail / hold

**Worker 输出：**

Worker 1 (模块 A):
{worker_1_output}

Worker 2 (模块 B):
{worker_2_output}

**验证任务：**
1. 检查每个模块是否完成需求
2. 检查接口是否正确实现
3. 检查是否有明显 bug
4. 检查测试覆盖率
5. 检查是否违反写作用域（Worker 只能改自己的目录）

**输出要求：**
返回 JSON 格式的 VerificationReport：
{
  "role": "verifier",
  "verdict": "pass | fail | hold",
  "verified_workers": [
    {
      "worker_id": "worker_1",
      "task": "实现模块 A",
      "result": "pass | fail",
      "issues": [
        {
          "severity": "high | medium | low",
          "description": "...",
          "file": "...",
          "suggestion": "..."
        }
      ]
    },
    ...
  ],
  "overall_verdict_reasoning": "...",
  "remediation_required": true/false,
  "remediation_patch": {
    "file": "...",
    "change": "..."
  }
}

如果发现问题，verdict 必须是 fail 或 hold，并提供 remediation_patch。
---

[等待 Verifier 输出] → 保存为 verifier_report

---

## Lead Integrator: 合并和验收
[在主线程执行，不是独立 Agent]

我（Lead）现在执行合并和验收：

1. 检查所有 Worker 是否完成
   - Worker 1: {worker_1_output.self_reported_done}
   - Worker 2: {worker_2_output.self_reported_done}

2. 检查 Verifier 判决
   - Verdict: {verifier_report.verdict}
   - Remediation required: {verifier_report.remediation_required}

3. 决策：
   - 如果 verdict = pass → 接受所有实现
   - 如果 verdict = fail → 应用 remediation_patch 或要求 Worker 重试
   - 如果 verdict = hold → 向用户请求判断

4. 生成 DeliveryCycleReport：
{
  "runtime_claim": "real_subagent_runtime",
  "subagent_ids": ["worker_1", "worker_2", "verifier"],
  "checked_gates": ["implementation_complete", "tests_added", "no_scope_violation"],
  "remaining_risks": [...],
  "final_acceptance": "accepted | hold"
}

最终判断：{final_acceptance}
```

---

### 场景 2: Worker-Verifier 循环（需要迭代修正）

**适用：** Worker 实现后 Verifier 发现问题，需要重试

```markdown
## 第 1 轮：Worker 实现

[唤起 Worker Agent]
Prompt: {实现任务}
[等待输出] → worker_output_v1

---

## 第 1 轮：Verifier 验证

[唤起 Verifier Agent]
Prompt: 验证 {worker_output_v1}
[等待输出] → verifier_report_v1

Verifier 判决：fail
原因：缺少错误处理

---

## 第 2 轮：Worker 重试

[唤起 Worker Agent - 重试]
Prompt:
---
你是 Worker Agent，你的上一轮实现被 Verifier 拒绝。

**上一轮输出：**
{worker_output_v1}

**Verifier 反馈：**
{verifier_report_v1}

**RemediationPatch：**
{verifier_report_v1.remediation_patch}

请根据反馈修正实现。你可以：
1. 应用 RemediationPatch
2. 或者提出更好的修正方案

输出格式同 ImplementationOutput。
---

[等待输出] → worker_output_v2

---

## 第 2 轮：Verifier 验证

[唤起 Verifier Agent]
Prompt: 验证 {worker_output_v2}
[等待输出] → verifier_report_v2

Verifier 判决：pass

---

## Lead 验收

循环次数：2
最终 verdict：pass
接受实现：worker_output_v2
```

---

### 场景 3: Explorer + Worker（先探索后实现）

**适用：** 代码库陌生，需要先探索再实现

```markdown
## Phase 1: 探索代码库

[唤起 Explorer Agent]

Prompt:
---
你是 Explorer Agent，负责探索代码库以回答问题。

**角色边界：**
- 你只能读取文件，不能编辑
- 你必须返回结构化的探索结果

**任务：**
找到以下信息：
1. 用户认证模块在哪里？
2. 当前使用的认证方式是什么？
3. 认证相关的测试在哪里？
4. 是否有现成的认证中间件？

**探索方法：**
- 搜索关键词：auth, authentication, login, session
- 查找配置文件
- 查找测试文件

**输出格式：**
{
  "role": "explorer",
  "findings": [
    {
      "question": "...",
      "answer": "...",
      "evidence_files": [...],
      "confidence": "high | medium | low"
    }
  ]
}
---

[等待 Explorer 输出] → explorer_result

---

## Phase 2: 实现

现在我们知道了代码库结构，可以启动 Worker。

[唤起 Worker Agent]

Prompt:
---
你是 Worker Agent，负责添加新的认证功能。

**代码库上下文（来自 Explorer）：**
{explorer_result.findings}

**任务：**
基于现有认证模块，添加 OAuth 支持。

现有认证在：{existing_auth_path}
你需要创建：src/auth/oauth-provider.ts

...
---

[等待 Worker 输出] → worker_output
```

---

## 关键执行规则

### 规则 1: Runtime 声明诚实

**必须根据实际能力声明 runtime。**

❌ 错误：
```
我会唤起真正的独立 subagent（但实际上环境不支持）
```

✅ 正确：
```
【Runtime 能力检查】
当前环境：无 spawn/wait/merge 工具
Runtime 声明：soft_orchestration_only
执行方式：单 Agent 串行执行，但保持角色边界
```

### 规则 2: 角色边界强制

**即使是 soft_orchestration，也必须保持角色边界。**

- Worker 不能给自己 pass
- Verifier 不能直接修改 Worker 产出
- Lead 必须收集所有输出后再合并

### 规则 3: 并行执行条件

**只有在任务真正独立时才并行。**

可并行：
- 多个模块实现（write_scope 不重叠）
- 多个独立文件的修改
- 多个独立的探索任务

不可并行：
- Worker 和 Verifier（Verifier 依赖 Worker 输出）
- 前后依赖的实现任务
- 主线程的 blocking 任务

### 规则 4: 输出完整性

**每个 Agent 必须返回完整的输出合同。**

Worker → ImplementationOutput
Verifier → VerificationReport
Explorer → ExplorationResult
Lead → DeliveryCycleReport

### 规则 5: 失败处理

**Verifier fail 后的处理路径：**

1. Lead 检查 remediation_patch
2. 如果 patch 合理 → 应用 patch 或启动 Worker 重试
3. 如果 patch 不合理 → hold，请求用户判断
4. 如果超过 max_cycles → escalated，停止重试

---

## 实施检查清单

在 Virtual Intelligent Dev Team 执行 Subagent 调用时，检查：

- [ ] 是否先声明了 runtime_claim？
- [ ] 是否满足激活条件（用户显式要求或 `/auto`）？
- [ ] 是否产出了 SubagentRuntimePlan？
- [ ] 每个 Agent 是否有独立的 Prompt？
- [ ] 每个 Agent 的 write_scope 是否不重叠？
- [ ] Worker 是否避免了自己给 pass？
- [ ] Verifier 是否产出了 VerificationReport？
- [ ] Lead 是否产出了 DeliveryCycleReport？
- [ ] 是否记录了 subagent_ids 或 backend_ids？

---

## 与 real-subagent-runtime-protocol.md 的关系

| 文档 | 定位 | 内容 |
|------|------|------|
| **real-subagent-runtime-protocol.md** | 合同层 | 定义角色、边界、状态机、验收条件 |
| **本文档（execution-guide）** | 执行层 | 提供实际调用指令、Prompt 模板、步骤 |

**阅读顺序：**
1. 先读 `real-subagent-runtime-protocol.md` 理解规则
2. 再读本文档学习如何实际执行

---

**协议版本：** 1.0.0  
**最后更新：** 2026-06-15  
**状态：** 执行指南（补充协议）
