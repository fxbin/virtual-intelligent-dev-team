# Hook 自动注入协议

> **来源**:Trellis / Harrison R5
> **用途**:spec 自动注入,Worker 动手前 routing-rules.json 相关条目通过 hook 挂载进上下文
> **核心原则**:hook 管上下文注入,prompt 只管指令

---

## 一、Hook 类型

### 1. 会话启动 hook = state 初始化

- **触发**:会话/round 开始时
- **动作**:从 journal replay 重建当前 state(P1-10)
- **输出**:当前 state snapshot 供 agent 使用
- **实现**:`automation_state.py` 的 `replay_journal()`

### 2. Sub-agent 调用 hook = entry_reducer 注入 context field

- **触发**:sub-agent(Worker/Verifier)被调用前
- **动作**:根据 route decision,将相关 spec 条目注入 sub-agent 的 context
- **输出**:hook_directives(spec 条目列表)
- **实现**:`route_request.py` 路由完成后输出 hook_directives

### Hook 是 node entry action,不是 edge guard

Harrison 的区分:
- **guard**(边):决定走不走这条边(如 verify_action 的 allowed/fail)
- **hook**(节点入口):决定进节点前把什么塞进 state(如 spec 注入)

---

## 二、Spec 自动注入

### 注入流程

```text
1. route_request.py 路由完成,输出 route decision
2. 根据 route decision 中的 lead_agent 和 workflow_bundle,查询需要注入的 spec 条目
3. 生成 hook_directives:{spec_files: [...], spec_sections: [...]}
4. hook_directives 写入 decision-log,可观测
5. Worker 启动前,hook 将 spec 条目注入 Worker 的 context
6. verify_action.py 验证 Worker 是否读取了 hook 指定的 spec 条目
```

### Spec 条目映射

| Lead Agent | 需注入的 spec 条目 |
|------------|-------------------|
| Java Virtuoso | `routing-rules.json#java-profile`, `language-profiles.yaml#java`, `execution-quality-guardrails.md` |
| API Contract Sentinel | `routing-rules.json#api-contract`, `execution-quality-guardrails.md` |
| Sentinel Architect | `routing-rules.json#architecture`, `anti-entropy-governance.md` |
| Code Audit Council | `routing-rules.json#audit`, `execution-quality-guardrails.md` |
| Git Workflow Guardian | `routing-rules.json#git-workflow`, `git-workflow-playbook.md` |
| World-Class Product Architect | `routing-rules.json#product`, `routing-rules.json#frontend-profile`, `goal-framing-protocol.md`, `execution-quality-guardrails.md` |
| Technical Trinity | `routing-rules.json#fullstack`, `execution-quality-guardrails.md` |
| Data Pipeline Guardian | `routing-rules.json#data`, `execution-quality-guardrails.md` |

### 注入规则

- 只注入与当前 route decision 相关的 spec 条目(不全部注入)
- spec 条目通过 `spec_ref` 字段引用,可追溯
- Worker 不需要手动找规范,hook 自动挂载

---

## 三、Hook 与 Prompt 的分工

| 维度 | Hook | Prompt |
|------|------|--------|
| 职责 | 上下文注入 | 指令 |
| 内容 | spec 条目、state snapshot | 任务目标、验收标准、约束 |
| 时机 | node entry(进节点前) | node body(节点内) |
| 可观测 | hook_directives 写入 decision-log | prompt 在 agent 对话中 |

### 分工原则

- hook 负责"把什么塞进 context"
- prompt 负责"让 agent 做什么"
- 不在 prompt 中拼装 spec 条目(那是 hook 的工作)
- 不在 hook 中给指令(那是 prompt 的工作)

---

## 四、Hook Directives 输出格式

route_request.py 路由完成后,在路由结果中新增 `hook_directives` 字段:

```json
{
  "hook_directives": {
    "spec_files": [
      "references/routing-rules.json",
      "references/execution-quality-guardrails.md"
    ],
    "spec_sections": [
      "routing-rules.json#java-profile",
      "language-profiles.yaml#java"
    ],
    "state_snapshot_ref": "<journal entry hash>",
    "inject_target": "worker"
  }
}
```

### 字段说明

| 字段 | 含义 |
|------|------|
| spec_files | 需注入的完整 spec 文件列表 |
| spec_sections | 需注入的 spec 条目(文件#章节)列表 |
| state_snapshot_ref | journal 中的 state snapshot 引用 |
| inject_target | 注入目标角色(worker/verifier/lead) |

`language-profiles.yaml#<profile>` 只允许引用文件中真实存在的 `profiles.<profile>`；
路由构建 hook 前会执行解析校验，悬空 profile 会 fail-closed。

---

## 五、验证

verify_action.py 新增 `hook-spec-read` check:

- 检查 Worker 是否读取了 hook 指定的 spec 条目
- 未读取 → warning(不 hard fail,记录到 decision-log)
- 多次未读取 → circuit breaker 的 `delivery` 层 record_failure

### 验证逻辑

```python
def _verify_hook_spec_read(result, hook_directives, worker_context):
    """检查 Worker 是否读取了 hook 指定的 spec 条目"""
    spec_sections = hook_directives.get("spec_sections", [])
    read_sections = extract_read_sections(worker_context)
    unread = [s for s in spec_sections if s not in read_sections]
    allowed = len(unread) == 0
    return {
        "allowed": allowed,
        "details": {
            "total_directed": len(spec_sections),
            "total_read": len(read_sections),
            "unread_sections": unread,
        },
        "recommended_next_step": "Read the unread spec sections before proceeding" if not allowed else "All directed spec sections have been read.",
    }
```

---

## 六、与 Workspace Journal 的关系(P1-10)

- hook 注入时从 journal replay 获取当前 state
- hook 注入的 spec 条目通过 `spec_ref` 字段写入 journal
- journal 的 `action=hook_inject` entry 记录每次注入
