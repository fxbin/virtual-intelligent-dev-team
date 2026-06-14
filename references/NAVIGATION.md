# Virtual Intelligent Dev Team 文档导航

这份导航按功能簇组织全部 88 个参考文档，帮助你快速定位需要的资料。

---

## 🎯 核心架构（必读）

### 路由与入口
- [runtime-routing-index.md](runtime-routing-index.md) - **运行时路由索引**（最常用）
- [agent-catalog.md](agent-catalog.md) - **6 个核心 Lead Agent 目录**（最高优先级）
- [dispatch-activation-cards.md](dispatch-activation-cards.md) - 派工激活卡
- [workflow-bundle-catalog.md](workflow-bundle-catalog.md) - 工作流包目录
- [output-contract.md](output-contract.md) - 输出契约

### 核心协议
- [team-engine-lite-protocol.md](team-engine-lite-protocol.md) - **Team Engine Lite 确定性闭环**（最高质量轴）
- [worker-verifier-cycle-protocol.md](worker-verifier-cycle-protocol.md) - Worker-Verifier 循环
- [vertical-slice-delivery-protocol.md](vertical-slice-delivery-protocol.md) - 垂直切片交付协议

### 硬约束与基线
- [workflow-quality-baseline.md](workflow-quality-baseline.md) - **工作流质量基线**
- [trigger-health-baseline.md](trigger-health-baseline.md) - 触发健康基线
- [baseline-registry.md](baseline-registry.md) - 基线注册表
- [execution-quality-guardrails.md](execution-quality-guardrails.md) - 执行质量护栏

---

## 👥 团队派工与专家路由

### Lead Agents（6 个核心）
- [agent-catalog.md](agent-catalog.md) - **完整 Agent 目录**
  - Java Virtuoso: Java 21, Spring Boot 3.2+, JVM 性能
  - Sentinel Architect: 高风险变更治理
  - Technical Trinity: 通用后端工程、系统设计
  - Code Audit Council: 审核、安全评估、可维护性分析
  - Git Workflow Guardian: 分支策略、Git 工作流安全
  - World-Class Product Architect: 产品定义、UX 架构、前端设计

### 阶段专家团（Stage Councils）
- [stage-council-protocol.md](stage-council-protocol.md) - **阶段专家团协议**
  - Product Discovery Council: 产品战略、PRD、用户研究
  - Prototype Design Council: 高保真原型、设计系统、HTML 原型

### 意图确认与路由
- [intent-confirmation-protocol.md](intent-confirmation-protocol.md) - 意图确认机制
- [provisional-route-confirmation.md](provisional-route-confirmation.md) - 临时路由确认

---

## 🏭 工作流包（Workflow Bundles）

### Quick Slice Delivery（小切片交付）
- [quick-slice-delivery-playbook.md](quick-slice-delivery-playbook.md) - **快速切片交付手册**
- [quick-slice-brief.md](quick-slice-brief.md) - 快速切片简报
- [project-context-refresh.md](project-context-refresh.md) - 项目上下文刷新
- [delivery-status.md](delivery-status.md) - 交付状态

### Pre-Development Planning（开发前规划）
- [pre-development-planning-playbook.md](pre-development-planning-playbook.md) - **开发前规划手册**
- [planning-pack-template.md](planning-pack-template.md) - 规划包模板
- [phase-plan-template.md](phase-plan-template.md) - 阶段计划模板
- [lane-notes-template.md](lane-notes-template.md) - 通道笔记模板
- [progress-anchor-template.md](progress-anchor-template.md) - 进度锚点模板

### Bounded Iteration（有边界迭代）
- [iteration-protocol.md](iteration-protocol.md) - **迭代协议**
- [bounded-iteration-patterns.md](bounded-iteration-patterns.md) - 有边界迭代模式
- [benchmark-iteration-playbook.md](benchmark-iteration-playbook.md) - Benchmark 迭代手册
- [iteration-memory.md](iteration-memory.md) - 迭代记忆
- [self-feedback-ledger.md](self-feedback-ledger.md) - 自反馈账本

### Release Gate（发布门禁）
- [release-gate-playbook.md](release-gate-playbook.md) - **发布门禁手册**
- [completion-evidence-protocol.md](completion-evidence-protocol.md) - 完成证据协议
- [ship-hold-decision-rubric.md](ship-hold-decision-rubric.md) - Ship/Hold 决策标准
- [remediation-brief-template.md](remediation-brief-template.md) - 补救简报模板

### Post-Release Feedback（发布后反馈）
- [post-release-feedback-playbook.md](post-release-feedback-playbook.md) - **发布后反馈手册**
- [feedback-loop-first-protocol.md](feedback-loop-first-protocol.md) - 反馈循环优先协议
- [root-cause-escalation-playbook.md](root-cause-escalation-playbook.md) - 根因升级手册

---

## 🎭 质量门禁与证据体系

### 完成证据门禁
- [completion-evidence-protocol.md](completion-evidence-protocol.md) - **完成证据协议**（核心）
- [evidence-ledger-schema.md](evidence-ledger-schema.md) - 证据账本 Schema
- [completion-evidence.schema.json](completion-evidence.schema.json) - 完成证据 Schema
- [release-gate-result.schema.json](release-gate-result.schema.json) - 发布门禁结果 Schema

### 质量护栏
- [execution-quality-guardrails.md](execution-quality-guardrails.md) - 执行质量护栏
- [harness-engineering-constraint-protocol.md](harness-engineering-constraint-protocol.md) - Harness 约束门禁
- [mutation-catalog-patterns.md](mutation-catalog-patterns.md) - 变更目录模式

---

## 🔄 多 Agent 编排协议

### 三层编排协议
- [team-engine-lite-protocol.md](team-engine-lite-protocol.md) - **Team Engine Lite 确定性闭环**
- [worker-verifier-cycle-protocol.md](worker-verifier-cycle-protocol.md) - **Worker-Verifier 循环**
- [external-agent-backend-orchestration-protocol.md](external-agent-backend-orchestration-protocol.md) - **外部 Agent 后端软编排**

### Real Subagent Runtime（真实子 Agent 运行时）
- [real-subagent-runtime-protocol.md](real-subagent-runtime-protocol.md) - **真实 Subagent Runtime 协议**
- [subagent-runtime-plan.md](subagent-runtime-plan.md) - Subagent Runtime 计划
- [subagent-spawn-policy.md](subagent-spawn-policy.md) - Subagent 生成策略

### 编排模板与输出
- [coordination-handoff-templates.md](coordination-handoff-templates.md) - 协调交接模板
- [delivery-cycle-report.schema.json](delivery-cycle-report.schema.json) - 交付周期报告 Schema
- [remediation-patch-template.md](remediation-patch-template.md) - 补救补丁模板

---

## 🚀 自动化运行（/auto）

### 显式 /auto 协议
- [auto-run-playbook.md](auto-run-playbook.md) - **自动运行手册**（核心）
- [setup-go-protocol.md](setup-go-protocol.md) - Setup-Go 两阶段协议
- [safe-background-resume-protocol.md](safe-background-resume-protocol.md) - Safe/Background/Resume 子协议

### 自动化状态与恢复
- [automation-state.schema.json](automation-state.schema.json) - **自动化状态 Schema**
- [automation-resume-execution.schema.json](automation-resume-execution.schema.json) - 自动化恢复执行 Schema
- [automation-resume-decision-matrix.md](automation-resume-decision-matrix.md) - 自动化恢复决策矩阵
- [state-driven-recovery-protocol.md](state-driven-recovery-protocol.md) - 状态驱动恢复协议

---

## 🎯 产品与前端专项

### Product Discovery Council
- [product-discovery-playbook.md](product-discovery-playbook.md) - 产品发现手册
- [product-strategy-template.md](product-strategy-template.md) - 产品战略模板
- [user-research-template.md](user-research-template.md) - 用户研究模板
- [competitive-intel-template.md](competitive-intel-template.md) - 竞品情报模板

### Prototype Design Council
- [prototype-design-playbook.md](prototype-design-playbook.md) - 原型设计手册
- [design-system-template.md](design-system-template.md) - 设计系统模板
- [html-prototype-template.md](html-prototype-template.md) - HTML 原型模板
- [accessibility-checklist.md](accessibility-checklist.md) - 可访问性检查清单

### Product Delivery
- [product-delivery-playbook.md](product-delivery-playbook.md) - 产品交付手册
- [prd-template.md](prd-template.md) - PRD 模板
- [acceptance-criteria-template.md](acceptance-criteria-template.md) - 验收标准模板

---

## 🔧 技术治理

### Architecture & Design
- [architecture-deepening-protocol.md](architecture-deepening-protocol.md) - 架构深化协议
- [system-map-protocol.md](system-map-protocol.md) - 系统地图协议
- [technical-governance-playbook.md](technical-governance-playbook.md) - 技术治理手册

### Git & Workflow
- [git-workflow-playbook.md](git-workflow-playbook.md) - Git 工作流手册
- [using-git-worktrees-playbook.md](using-git-worktrees-playbook.md) - Git Worktree 使用手册
- [git-safety-protocol.md](git-safety-protocol.md) - Git 安全协议

---

## 🧪 Beta 与内测

### Beta 验证流程
- [beta-validation-playbook.md](beta-validation-playbook.md) - **Beta 验证手册**
- [beta-cohort-plan.schema.json](beta-cohort-plan.schema.json) - Beta 群组计划 Schema
- [beta-ramp-plan.schema.json](beta-ramp-plan.schema.json) - Beta 爬坡计划 Schema
- [beta-round-report.schema.json](beta-round-report.schema.json) - Beta 轮次报告 Schema

### Beta 门禁与补救
- [beta-round-gate-result.schema.json](beta-round-gate-result.schema.json) - Beta 轮次门禁结果 Schema
- [beta-remediation-brief.schema.json](beta-remediation-brief.schema.json) - Beta 补救简报 Schema

### Beta 模拟
- [beta-simulation-manifest.schema.json](beta-simulation-manifest.schema.json) - Beta 模拟清单 Schema
- [beta-simulation-config.schema.json](beta-simulation-config.schema.json) - Beta 模拟配置 Schema
- [beta-simulation-run.schema.json](beta-simulation-run.schema.json) - Beta 模拟运行 Schema
- [beta-simulation-event.schema.json](beta-simulation-event.schema.json) - Beta 模拟事件 Schema
- [beta-simulation-diff.schema.json](beta-simulation-diff.schema.json) - Beta 模拟差异 Schema
- [simulation-trace-catalog.json](simulation-trace-catalog.json) - 模拟追踪目录
- [simulation-trace-catalog.schema.json](simulation-trace-catalog.schema.json) - 模拟追踪目录 Schema

---

## 🎪 特殊机制

### Goal Framing（目标框定）
- [goal-framing-protocol.md](goal-framing-protocol.md) - **目标框定协议**
- [goal-frame-template.md](goal-frame-template.md) - 目标框架模板
- [stop-condition-template.md](stop-condition-template.md) - 停止条件模板

### Anti-Entropy Governance（反熵治理）
- [anti-entropy-governance.md](anti-entropy-governance.md) - **反熵治理**
- [fallback-growth-detection.md](fallback-growth-detection.md) - Fallback 增长检测
- [duplicate-owner-resolution.md](duplicate-owner-resolution.md) - 重复 Owner 解决

### Offline Loop Drill（离线循环演练）
- [offline-loop-drill-playbook.md](offline-loop-drill-playbook.md) - 离线循环演练手册
- [rollback-drill-template.md](rollback-drill-template.md) - 回滚演练模板
- [resume-drill-template.md](resume-drill-template.md) - 恢复演练模板

---

## 📊 Benchmark 与评估

### Benchmark 系统
- [benchmark-iteration-playbook.md](benchmark-iteration-playbook.md) - Benchmark 迭代手册
- [benchmark-evals.schema.json](benchmark-evals.schema.json) - Benchmark Evals Schema
- [benchmark-run-result.schema.json](benchmark-run-result.schema.json) - Benchmark 运行结果 Schema

---

## 🛠️ 工具与命令

### 工具索引
- [tooling-command-index.md](tooling-command-index.md) - **工具命令索引**

---

## 📚 快速查询表

### 按场景查找文档

| 场景 | 推荐文档 |
|------|----------|
| **新手入门** | agent-catalog.md → quick-slice-delivery-playbook.md → completion-evidence-protocol.md |
| **小功能开发** | quick-slice-delivery-playbook.md |
| **大重构规划** | pre-development-planning-playbook.md |
| **多轮优化** | iteration-protocol.md → bounded-iteration-patterns.md |
| **发布前检查** | release-gate-playbook.md → completion-evidence-protocol.md |
| **发布后反馈** | post-release-feedback-playbook.md |
| **产品定义** | product-discovery-playbook.md → prd-template.md |
| **原型设计** | prototype-design-playbook.md |
| **Beta 内测** | beta-validation-playbook.md |
| **自动化运行** | auto-run-playbook.md → automation-state.schema.json |
| **Git 工作流** | git-workflow-playbook.md |

### 按角色查找文档

| 角色 | 核心文档 |
|------|----------|
| **Java Virtuoso** | agent-catalog.md（Java 专项） |
| **Sentinel Architect** | architecture-deepening-protocol.md + technical-governance-playbook.md |
| **Technical Trinity** | quick-slice-delivery-playbook.md + vertical-slice-delivery-protocol.md |
| **Code Audit Council** | execution-quality-guardrails.md + mutation-catalog-patterns.md |
| **Git Workflow Guardian** | git-workflow-playbook.md + using-git-worktrees-playbook.md |
| **World-Class Product Architect** | product-discovery-playbook.md + prototype-design-playbook.md |

---

## 📖 推荐阅读路径

### 第一天（核心理解）
1. [agent-catalog.md](agent-catalog.md) - 了解 6 个核心 Lead Agent
2. [runtime-routing-index.md](runtime-routing-index.md) - 理解路由机制
3. [quick-slice-delivery-playbook.md](quick-slice-delivery-playbook.md) - 最常用的工作流
4. [team-engine-lite-protocol.md](team-engine-lite-protocol.md) - Worker-Verifier 分离

### 第二天（质量与门禁）
5. [completion-evidence-protocol.md](completion-evidence-protocol.md) - 完成证据门禁
6. [release-gate-playbook.md](release-gate-playbook.md) - 发布门禁
7. [workflow-quality-baseline.md](workflow-quality-baseline.md) - 工作流质量基线

### 第三天（高级工作流）
8. [pre-development-planning-playbook.md](pre-development-planning-playbook.md) - 大重构规划
9. [iteration-protocol.md](iteration-protocol.md) - 有边界迭代
10. [beta-validation-playbook.md](beta-validation-playbook.md) - Beta 内测

### 第四天（产品与前端）
11. [product-discovery-playbook.md](product-discovery-playbook.md) - 产品发现
12. [prototype-design-playbook.md](prototype-design-playbook.md) - 原型设计
13. [stage-council-protocol.md](stage-council-protocol.md) - 阶段专家团

### 第五天（自动化与治理）
14. [auto-run-playbook.md](auto-run-playbook.md) - 自动化运行
15. [anti-entropy-governance.md](anti-entropy-governance.md) - 反熵治理
16. [real-subagent-runtime-protocol.md](real-subagent-runtime-protocol.md) - 真实 Subagent Runtime

---

**文档总数**: 88 个参考文档  
**最后更新**: 2026-06-14  
**维护者**: Virtual Intelligent Dev Team

如有疑问，请查阅 [README.md](../README.md) 或提交 Issue。
