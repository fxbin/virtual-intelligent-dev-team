# Virtual Intelligent Dev Team 贡献指南

感谢你对 Virtual Intelligent Dev Team 的关注！这份指南将帮助你理解如何为这个项目做出贡献。

---

## 📋 目录

1. [项目哲学](#项目哲学)
2. [贡献类型](#贡献类型)
3. [文档规范](#文档规范)
4. [Schema 规范](#schema-规范)
5. [Eval 规范](#eval-规范)
6. [提交流程](#提交流程)
7. [质量检查清单](#质量检查清单)

---

## 项目哲学

在开始贡献之前，请理解 Virtual Intelligent Dev Team 的核心设计哲学：

### 1. 确定性优于灵活性

- **Worker-Verifier 分离**：执行者和验证者必须分离，避免"自己验证自己"
- **状态驱动恢复**：优先从机器可读的状态文件恢复，而不是对话上下文
- **完成证据门禁**：非平凡完成声明必须有结构化证据

### 2. 显式优于隐式

- **显式 /auto**：只有用户显式输入 `/auto` 才进入自动运行，不擅自自动化
- **意图确认**：模糊请求先确认方向（product-opportunity / prototype-exploration / technical-feasibility / architecture-risk / delivery-plan）
- **Goal Framing**：容易漂移的任务先锁定 success evidence、stop condition 和 non-goals

### 3. 有边界优于无限循环

- **max_cycles**：迭代优化必须有最大轮次限制
- **bounded iteration**：优化循环是有边界、有证据、有回滚点的
- **escalation policy**：超出边界后必须升级给人工决策

### 4. 治理优于增长

- **Anti-Entropy Governance**：遇到 fallback / duplicate owner / adapter 增长时，先判断是否该删除旧路径
- **Workflow Quality Baseline**：用 6 个维度（trigger accuracy、fast-path cheapness、output compactness、evidence freshness、artifact laziness、authority boundary）约束 skill 迭代
- **Baseline Registry**：所有基线和硬约束必须注册

---

## 贡献类型

### 1. 新增 Lead Agent

如果你想添加新的 Lead Agent（例如新的技术栈专家、新的治理角色）：

**必须包含：**
- [ ] 在 `references/agent-catalog.md` 中添加 Agent 定义
- [ ] 明确 Agent 的职责边界（什么该做、什么不该做）
- [ ] 定义 Agent 的激活条件（什么时候路由到这个 Agent）
- [ ] 提供至少 3 个典型使用场景
- [ ] 在 `evals/evals.json` 中添加至少 2 个 eval 案例

**示例结构：**
```markdown
## Rust Performance Expert

**职责：**
- Rust 性能优化、内存安全、并发模型
- unsafe 代码审查与治理
- Cargo 工作流与工具链集成

**不负责：**
- 非 Rust 技术栈
- 产品定义或 UI 设计

**激活条件：**
- 用户明确提到 Rust 或 Cargo
- 涉及系统级性能优化或内存安全问题
- 需要 unsafe 代码审查

**典型场景：**
1. 优化 Rust 服务的内存占用
2. 审查 unsafe 代码块的安全性
3. 重构 Rust 并发模型
```

### 2. 新增 Workflow Bundle

如果你想添加新的工作流包（例如新的交付流程、新的质量门禁）：

**必须包含：**
- [ ] 在 `SKILL.md` 的 `## Workflow Bundles` 中注册，并在 `references/playbook-index.md` 添加入口
- [ ] 创建对应的 playbook 文件（`references/<workflow-name>-playbook.md`）
- [ ] 定义清晰的输入和输出契约
- [ ] 提供模板文件（如果有）
- [ ] 在 `evals/evals.json` 中添加至少 3 个 eval 案例

**Playbook 必须包含的章节：**
1. **When to Use**：什么时候使用这个工作流
2. **Input Contract**：需要什么输入
3. **Output Contract**：输出什么结果
4. **Steps**：执行步骤
5. **Quality Gates**：质量门禁条件
6. **Rollback**：如何回滚
7. **Examples**：典型示例

### 3. 新增 Stage Council（阶段专家团）

如果你想添加新的阶段专家团（例如 Security Audit Council、Performance Optimization Council）：

**必须包含：**
- [ ] 在 `references/stage-council-protocol.md` 中添加定义
- [ ] 明确专家团的组成（3-5 个专家角色）
- [ ] 定义专家团的激活条件
- [ ] 提供协调模板（如果需要多轮协作）
- [ ] 在 `evals/evals.json` 中添加至少 2 个 eval 案例

**示例结构：**
```markdown
## Security Audit Council

**组成：**
- Security Architect：架构层安全审查
- Penetration Tester：渗透测试与漏洞发现
- Compliance Expert：合规性检查（GDPR、SOC 2 等）

**激活条件：**
- 用户明确要求安全审查
- 涉及认证、授权、数据加密等高风险变更
- 发布门禁中需要安全签名

**协调模式：**
1. Security Architect 先分析架构风险
2. Penetration Tester 执行渗透测试
3. Compliance Expert 检查合规性
4. 三方汇总出 Security Audit Report
```

### 4. 新增 Schema 定义

如果你想添加新的数据契约（例如新的报告格式、新的状态定义）：

**必须遵循：**
- [ ] 使用 JSON Schema Draft 2020-12
- [ ] 文件名使用 `<name>.schema.json`
- [ ] 必须包含 `$schema`、`$id`、`title`、`description`
- [ ] 所有必填字段必须在 `required` 数组中声明
- [ ] 所有枚举值必须有注释说明含义
- [ ] 在 `references/` 目录中添加对应的使用说明文档（`<name>-schema.md`）

**Schema 模板：**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:skill-hub:virtual-intelligent-dev-team:<name>.schema",
  "title": "<Title>",
  "description": "<Description>",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "string",
      "description": "字段说明"
    }
  },
  "additionalProperties": false
}
```

### 5. 新增 Eval 案例

如果你想添加新的测试案例：

**必须遵循：**
- [ ] 在 `evals/evals.json` 中追加（不要新建文件）
- [ ] `id` 必须是递增的整数
- [ ] `category` 必须是已有类别或有充分理由的新类别
- [ ] `input.task` 必须清晰描述场景
- [ ] `expected_behavior` 必须是可验证的行为
- [ ] `verification_points` 必须列出至少 3 个验证点

**Eval 模板：**
```json
{
  "id": 94,
  "category": "workflow-bundle",
  "name": "quick-slice-delivery-with-git-worktree",
  "description": "测试使用 Git Worktree 进行小切片交付",
  "input": {
    "task": "在 Git Worktree 中实现用户登录功能",
    "context": {
      "use_worktree": true
    }
  },
  "expected_behavior": "应该创建 worktree、生成 quick slice brief、实现代码、验证、提交、返回主分支",
  "verification_points": [
    "使用 git worktree add 创建隔离环境",
    "生成包含目标、范围、验收条件的 brief",
    "实现代码并保留 delivery status",
    "使用 git worktree remove 清理"
  ],
  "metadata": {
    "priority": "high",
    "estimated_cycles": 1
  }
}
```

---

## 文档规范

### 文件命名

- **Playbook**：`<workflow-name>-playbook.md`
- **Protocol**：`<protocol-name>-protocol.md`
- **Template**：`<template-name>-template.md`
- **Schema 说明**：`<schema-name>-schema.md`
- **Index/Catalog**：`<name>-catalog.md` 或 `<name>-index.md`

### 文档结构

所有参考文档必须包含以下章节（如适用）：

1. **标题与简介**（必须）
2. **When to Use**（如适用）
3. **核心内容**（必须）
4. **Examples**（强烈推荐）
5. **References**（如有依赖其他文档）

### Markdown 规范

- 使用 ATX 风格标题（`#` 而不是下划线）
- 代码块必须指定语言
- 列表项使用 `-` 而不是 `*`
- 强调使用 `**粗体**` 而不是 `*斜体*`
- 链接使用相对路径（同目录文件）或绝对路径（跨目录文件）

### 中英文混排规范

- 中英文之间不需要空格（项目使用中文为主）
- 专有名词使用英文原文（例如 Worker-Verifier、Quick Slice、Goal Framing）
- 技术术语首次出现时可以用中文注释：`Team Engine Lite（轻量团队引擎）`

---

## Schema 规范

### 基本要求

1. **使用 JSON Schema Draft 2020-12**
   ```json
   {
     "$schema": "https://json-schema.org/draft/2020-12/schema"
   }
   ```

2. **$id 命名规范**
   ```json
   {
     "$id": "urn:skill-hub:virtual-intelligent-dev-team:<name>.schema"
   }
   ```

3. **必须包含 title 和 description**
   ```json
   {
     "title": "完整标题",
     "description": "详细描述这个 Schema 的用途"
   }
   ```

4. **禁止 additionalProperties（除非有充分理由）**
   ```json
   {
     "additionalProperties": false
   }
   ```

### 字段规范

- 所有字段必须有 `description`
- 枚举值必须有注释说明含义
- 时间戳使用 ISO 8601 格式（`format: "date-time"`）
- 避免使用 `any` 类型，必须明确类型

### 示例字段定义

```json
{
  "verdict": {
    "type": "string",
    "enum": ["pass", "fail", "hold"],
    "description": "验证结果：pass（通过）、fail（需要重试）、hold（需要更多信息或冲突解决）"
  },
  "cycle_number": {
    "type": "integer",
    "minimum": 1,
    "description": "当前循环轮次（从 1 开始）"
  },
  "created_at": {
    "type": "string",
    "format": "date-time",
    "description": "创建时间戳（ISO 8601）"
  }
}
```

---

## Eval 规范

### Eval 文件结构

所有 eval 案例必须添加到 `evals/evals.json` 中，不要创建单独的文件。

### Eval 案例结构

```json
{
  "id": 94,                           // 必须：递增整数
  "category": "workflow-bundle",      // 必须：类别
  "name": "descriptive-name",         // 必须：描述性名称（kebab-case）
  "description": "简短描述",          // 必须：一句话描述
  "input": {                          // 必须：输入
    "task": "用户任务描述",
    "context": {}                     // 可选：额外上下文
  },
  "expected_behavior": "期望行为",    // 必须：可验证的期望行为
  "verification_points": [            // 必须：至少 3 个验证点
    "验证点 1",
    "验证点 2",
    "验证点 3"
  ],
  "metadata": {                       // 可选：元数据
    "priority": "high",               // 优先级
    "estimated_cycles": 1             // 预计轮次
  }
}
```

### 现有类别

- `agent-routing`：Agent 路由
- `workflow-bundle`：工作流包
- `quality-gate`：质量门禁
- `automation`：自动化运行
- `multi-agent`：多 Agent 协作
- `state-recovery`：状态恢复
- `anti-entropy`：反熵治理
- `beta-validation`：Beta 验证

### 新增类别的标准

如果你需要新增类别，必须满足以下条件：

1. 至少有 3 个 eval 案例属于这个类别
2. 这个类别代表一个独立的功能维度
3. 无法归入现有类别

---

## 提交流程

### 1. Fork 并创建分支

```bash
git checkout -b feature/<feature-name>
# 或
git checkout -b fix/<bug-name>
```

### 2. 进行修改

- 遵循上述规范
- 确保文档清晰
- 添加必要的 eval 案例

### 3. 自检清单

运行以下检查（如果适用）：

```bash
# 检查 JSON Schema 有效性
npx ajv-cli validate -s references/<name>.schema.json

# 检查 evals.json 有效性
jq empty evals/evals.json

# 检查 Markdown 链接
npx markdown-link-check references/**/*.md
```

### 4. 提交

```bash
git add .
git commit -m "feat(agent): 添加 Rust Performance Expert

- 在 agent-catalog.md 中添加定义
- 提供 3 个典型使用场景
- 添加 2 个 eval 案例
"
```

**Commit Message 规范：**
- 使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式
- 类型：`feat`、`fix`、`docs`、`refactor`、`test`、`chore`
- 范围：`agent`、`workflow`、`schema`、`eval`、`protocol`
- 描述：简短清晰，使用中文

### 5. 创建 Pull Request

在 PR 描述中包含：

1. **What**：做了什么改动
2. **Why**：为什么需要这个改动
3. **How**：如何实现的
4. **Checklist**：完成了哪些检查

**PR 模板：**
```markdown
## What
添加 Rust Performance Expert Agent

## Why
当前缺少 Rust 专项专家，导致 Rust 性能优化和 unsafe 代码审查无法得到专业支持

## How
- 在 agent-catalog.md 中定义 Agent 职责和激活条件
- 提供 3 个典型场景
- 添加 2 个 eval 案例（Rust 性能优化、unsafe 代码审查）

## Checklist
- [x] 遵循 Agent 添加规范
- [x] 添加至少 2 个 eval 案例
- [x] 文档清晰完整
- [x] JSON Schema 有效（如适用）
- [x] Commit message 符合规范
```

---

## 质量检查清单

在提交 PR 之前，请确保完成以下检查：

### 文档类贡献

- [ ] 文件命名符合规范
- [ ] 必须章节完整
- [ ] 示例清晰可执行
- [ ] 链接有效（相对路径正确）
- [ ] 中英文混排规范
- [ ] 在 `references/playbook-index.md` 或 `references/tooling-command-index.md` 中添加索引

### Schema 类贡献

- [ ] 使用 JSON Schema Draft 2020-12
- [ ] `$id` 命名符合规范
- [ ] 所有字段有 `description`
- [ ] 枚举值有注释
- [ ] `additionalProperties: false`（除非有理由）
- [ ] JSON 语法有效（通过 `jq empty` 检查）
- [ ] 添加对应的 `<name>-schema.md` 说明文档

### Eval 类贡献

- [ ] 追加到 `evals/evals.json`（不新建文件）
- [ ] `id` 递增且唯一
- [ ] `category` 有效
- [ ] `verification_points` 至少 3 个
- [ ] `expected_behavior` 可验证
- [ ] JSON 语法有效

### Agent 类贡献

- [ ] 在 `agent-catalog.md` 中添加定义
- [ ] 职责边界清晰（该做什么、不该做什么）
- [ ] 激活条件明确
- [ ] 至少 3 个典型场景
- [ ] 至少 2 个 eval 案例

### Workflow 类贡献

- [ ] 在 `SKILL.md` 的 `## Workflow Bundles` 中注册
- [ ] 创建 playbook 文件
- [ ] 输入输出契约清晰
- [ ] 提供模板（如适用）
- [ ] 至少 3 个 eval 案例
- [ ] 定义质量门禁条件
- [ ] 提供回滚机制

---

## 常见问题

### Q: 我可以修改现有的 Agent 定义吗？

A: 可以，但需要谨慎。如果修改会影响现有行为，请：
1. 在 PR 中说明影响范围
2. 更新相关的 eval 案例
3. 检查是否需要迁移指南

### Q: 我可以删除旧的 Workflow 吗？

A: 可以，但必须遵循 Anti-Entropy Governance：
1. 确认旧 Workflow 已被更好的替代方案覆盖
2. 检查是否有项目依赖这个 Workflow
3. 提供迁移路径（如果有依赖）
4. 在 PR 中说明删除理由

### Q: 我的贡献需要多少 eval 案例？

A: 最少要求：
- 新 Agent：2 个 eval
- 新 Workflow：3 个 eval
- 新 Protocol：2 个 eval
- 新 Schema：1 个 eval（如果有对应的 Workflow）

### Q: 我可以用英文写文档吗？

A: 可以，但优先使用中文。如果你更擅长英文，可以先用英文写，maintainer 会帮助翻译。

### Q: 我的 PR 多久会被 review？

A: 通常在 3 个工作日内。如果超过 5 个工作日没有回应，请在 PR 中 @maintainer。

---

## 联系方式

如果你有任何疑问，可以通过以下方式联系：

- 提交 Issue
- 在 PR 中评论
- 加入讨论组（如有）

---

**感谢你的贡献！每一个改进都让 Virtual Intelligent Dev Team 变得更好。**
