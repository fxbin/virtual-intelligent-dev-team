# Runtime Routing Index

这份索引只做两件事：

1. 告诉你当前请求该先开哪组参考文件
2. 避免在 `SKILL.md` 里重复维护长路由清单

## 一、定位说明与中文讲解

先读这些：

- `skill-positioning.md`
  - 对外定位、中文术语、常见误解
- `workflow-sequences.md`
  - 中文流程 walkthrough
- `auto-run-playbook.md`
  - 显式 `/auto` 协议、setup/go 两阶段、`safe/background/resume` 子协议和自动白名单
- `automation-resume-decision-matrix.md`
  - automation state 如何映射成 resume 决策、命令与 playbook
- `tooling-command-index.md`
  - 包含 `inspect_automation_state.py` 与 `resume_from_automation_state.py` 的恢复 / 执行入口
- `product-delivery-playbook.md`
  - 产品定义到实现切片的默认打法
- `beta-validation-playbook.md`
  - 开发前后分轮内测、用户递增与反馈门禁的默认打法
- `post-release-feedback-playbook.md`
  - 已发版版本的反馈回流、监控、回写与 reopen 闭环
- `technical-governance-playbook.md`
  - 风险控制、发布控制、Git 治理的默认打法

## 二、路由与协作

请求在“谁做 lead、要不要 assistant、怎么 handoff”上不明确时，读这一组：

- `agent-catalog.md`
  - 详细触发器、anti-pattern
- `routing-score-matrix.md`
  - 权重、置信度解释
- `routing-rules.json`
  - 评分和排除规则真源
- `coordination-handoff-templates.md`
  - lead / assistant 紧凑交接模板
- `dispatch-activation-cards.md`
  - assistant 激活卡
- `workflow-bundles.md`
  - 默认交付旅程与恢复锚点

常见 lead 速记：

- review / audit / security -> `Code Audit Council`
- Git / branch / PR / rebase -> `Git Workflow Guardian`
- Java / Spring / JVM -> `Java Virtuoso`
- 产品需求 / 用户流 / 验收标准 / UI / React / redesign -> `World-Class Product Architect`
- general engineering -> `Technical Trinity`
- high-risk / research-first / conflict-heavy -> `Sentinel Architect (NB)`

## 三、场景 runbook

请求像固定多角色模式时，读：

- `scenario-runbooks.md`
- `pre-development-planning-playbook.md`
- `workflow-bundles.md`

典型场景：

- Large-scale transformation planning
- Audit and fix
- Product slice to delivery
- Beta validation with staged cohorts
  - simulation persona library / cohort fixtures / scenario packs / trace catalog / config / trace
- Frontend UX with backend coupling
- Technical governance hardening
- High-risk production change
- Repeated-failure or root-cause debugging
- Evidence-driven iteration

如果不仅要知道“谁做 lead”，还要知道“默认走哪条交付旅程、恢复点在哪”，补读：

- `workflow-bundles.md`
- `project-memory-lite.md`
- beta 分轮验证时再补读：
  - `beta-validation-playbook.md`
  - `tooling-command-index.md` 里的 round report / gate 命令

## 四、开发前规划

用户明确要“先规划再开发”、大规模重写、迁移、架构改造时，先读：

- `pre-development-planning-playbook.md`

需要模板时再打开：

- `assets/pre-development-project-overview-template.md`
- `assets/pre-development-task-breakdown-template.md`
- `assets/pre-development-progress-master-template.md`
- `assets/pre-development-phase-template.md`
- `references/pre-development-output-template.md`

## 五、bounded iteration

用户要求优化、再来一轮、benchmark 比较、候选比较、持续迭代时，按簇打开：

- 架构与 round contract
  - `self-optimization-architecture.md`
  - `iteration-protocol.md`
  - `iteration-state-machine.md`
  - `loop-orchestration.md`
  - 如果用户显式写 `/auto`，再补读 `auto-run-playbook.md`
- memory 与 evidence
  - `agency-inspired-loop-patterns.md`
  - `memory-model.md`
  - `evidence-ledger-schema.md`
  - `baseline-registry.md`
  - `rollback-and-stop-rules.md`
- `mutation-catalog-patterns.md`
- `project-memory-lite.md`

## 六、root cause / release / Git

- repeated failure / 根因排查
  - `root-cause-escalation-playbook.md`
- release gate / offline acceptance
  - `offline-loop-drill-playbook.md`
  - `release-gate-playbook.md`
  - 如果用户显式写 `/auto`，再补读 `auto-run-playbook.md`
  - 如果发布前还存在 staged beta，再补读 `beta-validation-playbook.md`
  - 如果版本已经 ship，要继续做真实反馈回流，再补读 `post-release-feedback-playbook.md`
- Git / worktree
  - `git-workflow-playbook.md`
  - `using-git-worktrees-playbook.md`

执行前如果不确定“该不该开某个 process lane / release gate / iteration / lead 组合”，先回到：

- `tooling-command-index.md`
  - 用 `verify_action.py` 先做一次动作合法性校验
  - 高风险执行前，可分别确认 `git-workflow` 和 `worktree` 是否真的该开
  - 用 `lint_virtual_team_contract.py` 检查索引、命令和 process contract 是否漂移
