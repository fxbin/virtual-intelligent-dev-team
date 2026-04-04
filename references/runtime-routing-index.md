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

常见 lead 速记：

- review / audit / security -> `Code Audit Council`
- Git / branch / PR / rebase -> `Git Workflow Guardian`
- Java / Spring / JVM -> `Java Virtuoso`
- UI / React / redesign -> `World-Class Product Architect`
- business / growth / pricing -> `Executive Trinity`
- unfamiliar domain / compliance -> `Omni-Architect`
- general engineering -> `Technical Trinity`
- high-risk / research-first / conflict-heavy -> `Sentinel Architect (NB)`

## 三、场景 runbook

请求像固定多角色模式时，读：

- `scenario-runbooks.md`
- `pre-development-planning-playbook.md`

典型场景：

- Large-scale transformation planning
- Startup MVP
- Audit and fix
- Strategy with technical landing
- Regulated or unfamiliar domain build
- Frontend UX with backend coupling
- High-risk production change
- Repeated-failure or root-cause debugging
- Evidence-driven iteration

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
- memory 与 evidence
  - `agency-inspired-loop-patterns.md`
  - `memory-model.md`
  - `evidence-ledger-schema.md`
  - `baseline-registry.md`
  - `rollback-and-stop-rules.md`
- `mutation-catalog-patterns.md`

## 六、root cause / release / Git

- repeated failure / 根因排查
  - `root-cause-escalation-playbook.md`
- release gate / offline acceptance
  - `offline-loop-drill-playbook.md`
  - `release-gate-playbook.md`
- Git / worktree
  - `git-workflow-playbook.md`
  - `using-git-worktrees-playbook.md`

执行前如果不确定“该不该开某个 process lane / release gate / iteration / lead 组合”，先回到：

- `tooling-command-index.md`
  - 用 `verify_action.py` 先做一次动作合法性校验
  - 用 `lint_virtual_team_contract.py` 检查索引、命令和 process contract 是否漂移
