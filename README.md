# Virtual Intelligent Dev Team

`virtual-intelligent-dev-team` 是一个面向复杂软件工作的智能协作项目。

它不只是“专家角色路由器”，而是把研发、产品、分轮内测、技术治理、发布门禁、显式 `/auto` 自动运行，以及状态驱动恢复，收拢成一个可持续迭代的闭环工作流。

一句话说：

它适合接手“单个专家已经不够、单轮回答也不够”的复杂软件任务。

## 项目定位

这个项目最适合三类问题：

- 复杂研发交付
  - 例如小切片实现、大重构、迁移、跨模块联动、技术治理
- 产品与研发协同
  - 例如需求澄清、验收标准、前后端协作、分轮 beta
- 版本与闭环治理
  - 例如多轮优化、release gate、post-release feedback loop、resume

## 为什么不是普通多专家提示词

很多“虚拟团队”方案，主要解决的是“换几个角色来回答”。

这个项目想解决得更深一层：

- 不只换角色
  - 还要判断谁主负责、谁协同、是否需要治理
- 不只给建议
  - 还要给出执行路径、恢复锚点和下一步
- 不只做开发前
  - 还覆盖 beta、release、post-release feedback
- 不只做单轮问答
  - 还支持有边界的多轮优化和状态恢复

所以它更像一个“复杂软件工作的闭环协调层”，而不是一个“多身份回答器”。

## 适合解决什么问题

- 复杂研发任务的 lead agent 路由与协同
- 大型重构、迁移、拆分、技术治理
- 多轮优化、benchmark、回滚、resume
- 产品定义、验收标准、分轮 beta 内测
- release gate 与 post-release feedback loop
- trigger health 与 workflow quality baseline，避免该触发不触发、误触发、过度流程化或 completion claim 证据不足
- goal framing：对宽目标、重复失败、release、beta、multi-agent 等任务先锁定 success evidence、stop condition 和 non-goals
- anti-entropy governance：对 fallback growth、duplicate owner、adapter / guard 膨胀、delete vs compat 和 source-of-truth 删除边界做治理
- 显式 `/auto` 自动运行与状态优先恢复
- Team Engine Lite 的 Worker / Verifier 分离、RemediationPatch 和 DeliveryCycleReport
- 受控真实 Subagent runtime eligibility：显式 multi-agent/subagent 请求或合格 `/auto` 工作流可生成 `SubagentRuntimePlan`，但只有宿主提供 spawn / wait / merge 证据时才声明真实 runtime

## 核心能力

- `默认手动模式`
  - 默认是人工驱动模式，不会擅自进入自动运行。
- `显式 /auto`
  - 只有显式输入 `/auto` 才会进入自动运行分支。
- `setup -> go`
  - 自动运行保持两阶段协议，先建状态，再执行。
- `safe / background / resume`
  - 自动子协议支持安全预演、后台执行、状态恢复。
- `状态优先恢复`
  - 恢复优先读取机器可读的 automation state，而不是靠对话猜测上下文。
- `小切片交付`
  - 小型功能或 bugfix 默认保留 quick slice brief、project context、delivery status 和验证证据。
- `目标边界`
  - 对容易漂移的任务先形成 goal frame，明确 success evidence、stop condition、non-goals 和当前 stop state。
- `工作流质量基线`
  - 用 trigger accuracy、fast-path cheapness、output compactness、evidence freshness、artifact laziness 和 authority boundary 约束 skill 迭代。
- `反熵治理`
  - 遇到 duplicate owner、fallback、adapter、guard 或兼容路径增长时，先判断旧路径该删除、保留兼容，还是需要用户确认。
- `Team Engine Lite`
  - code-facing、release-facing、Git-facing 与 remediation 路线默认保留 Worker / Verifier 分离、max-cycle retry、RemediationPatch 和 DeliveryCycleReport。
- `受控真实 Subagent runtime eligibility`
  - 显式 multi-agent / subagent / parallel agent 请求会生成受控计划、角色边界、spawn policy、merge policy 和 fallback；没有宿主 runtime evidence 时仍保持 `soft_orchestration_only`。
- `外部 Agent 后端软编排`
  - 可以把 Codex / Claude Code / OpenCode 当作角色后端，但默认只声明 `soft_orchestration_only`，不虚假声称真实异步多进程 runtime。
- `有边界的迭代优化`
  - 优化循环是有边界、有证据、有回滚点的，不做无限自转。
- `发布与反馈闭环`
  - 不只做发布前 gate，也覆盖发布后的反馈回写与下一轮修复入口。

## 能力矩阵

| 维度 | 本项目提供什么 | 普通多专家提示词常见缺口 |
| --- | --- | --- |
| 任务路由 | 选择主负责人、协同者、治理轨道 | 往往只是平铺多个角色视角 |
| 日常交付 | 小切片 brief、项目上下文、状态锚点 | 容易直接跳到实现，缺少可恢复上下文 |
| 执行模式 | 支持手动模式与显式 `/auto` | 通常没有明确模式切换 |
| 恢复能力 | 状态优先恢复、resume、恢复锚点 | 容易依赖上下文记忆 |
| 迭代能力 | 有边界的多轮优化、基线、回滚决策 | 常见问题是无限"再来一轮" |
| 发布治理 | release gate、hold 后续修复入口 | 常停留在"建议发/不发" |
| 上线后闭环 | post-release feedback loop | 很少覆盖上线后的反馈回写 |
| 产品协同 | 支持产品、研发、技术治理联动 | 容易偏单一研发视角 |
| Beta 验证 | 分轮内测、模拟用户、cohort ramp、反馈门禁 | 通常只有静态测试计划，没有结构化分轮验证 |
| 工作流质量 | 触发健康、快路径廉价、证据新鲜度、artifact 懒创建、authority boundary | 容易越改越重，或把方法建议误说成最终权威 |
| 反熵治理 | delete-first / compat-exception / confirmation-first 路径选择 | 常见做法是不断加 fallback 或 guard |
| Subagent runtime | 显式请求时输出受控计划，真实执行必须有宿主 spawn / wait / merge 证据 | 容易把角色扮演误称为真实多 Agent runtime |
| 离线验证 | offline loop drill 验证回滚与恢复路径 | 很少验证关键闭环路径是否真的跑通 |

## 快速开始

如果你第一次使用，建议从这三种方式开始：

```text
$virtual-intelligent-dev-team 帮我接管这次重构，并给出可执行分工。
$virtual-intelligent-dev-team /auto setup 这个项目级迁移。
$virtual-intelligent-dev-team 判断当前版本是否可以 release。
```

对应的理解方式是：

- 不带 `/auto`
  - 走手动模式，适合高风险任务和需要逐轮确认的场景
- 带 `/auto setup`
  - 先建立自动化状态和恢复锚点
- 再执行 `/auto go`
  - 进入自动执行阶段

## 适合与不适合

更适合：

- 复杂研发任务
- 跨产品与研发的交付协同
- 需要多轮优化、恢复和发布治理的工作

不太适合：

- 纯商业战略
- 融资、定价、泛咨询
- 非软件交付型的轻量一次性问题

## 目录结构

```text
virtual-intelligent-dev-team/
├── SKILL.md
├── README.md
├── VERSION
├── LICENSE
├── agents/
├── assets/
├── docs/
├── evals/
├── references/
├── scripts/
└── tests/
```

目录职责分层：

- `SKILL.md`
  - 运行时契约、触发边界、主流程
- `docs/`
  - 面向维护者与开源使用者的说明文档
- `references/`
  - 路由规则、playbook、schema、真源细则
- `assets/`
  - 模板、样例、卡片
- `scripts/`
  - 校验、导出、自动运行、恢复、发布辅助脚本
- `tests/`
  - 语义回归与契约测试

## 快速入口

- 使用说明：
  - [docs/usage-guide.md](docs/usage-guide.md)
- 设计理念：
  - [docs/design-philosophy.md](docs/design-philosophy.md)
- 文档索引：
  - [docs/README.md](docs/README.md)

如果你想先上手：

- 读 `README.md`
- 再读 `docs/usage-guide.md`

如果你想先理解设计：

- 读 `docs/design-philosophy.md`
- 再读 `SKILL.md`

## 运行流程图

```mermaid
flowchart TD
    A[收到复杂软件任务] --> B{是否显式输入 /auto}
    B -->|否| C[手动模式]
    B -->|是| D["/auto setup"]
    D --> E[建立 automation state]
    E --> F["/auto go 或 resume"]
    F --> G[自动执行入口]

    C --> H[识别任务类型 / 风险 / 技术栈 / Git 与 process 信号]
    G --> H

    H --> I{是否大型改造 / 迁移 / 先规划}
    I -->|是| J["plan-first-build 前置规划和 progress anchor"]
    J --> H
    I -->|否| K{是否窄实现或 bugfix}
    K -->|是| L[quick-slice-deliver]
    K -->|否| M[选择一个 lead agent]

    M --> N{是否需要 assistant / governance / Git guardrail}
    N -->|是| O[加载协同治理或 Git 轨道]
    N -->|否| P[保持轻量路由]
    O --> Q{选择最小 workflow bundle}
    P --> Q
    L --> Q

    Q -->|产品定义到交付| R[product-spec-deliver]
    Q -->|多轮优化或候选比较| S[bounded iteration]
    Q -->|反复失败或根因排查| T[root-cause-remediate]
    Q -->|分轮内测或用户递增| U[beta-feedback-ramp]
    Q -->|发版提交或正式验收| V[ship-hold-remediate]
    Q -->|已发布反馈回流| W[post-release-close-loop]
    Q -->|审计后修复| X[audit-fix-deliver]
    Q -->|发布安全回滚分支策略| Y[govern-change-safely]
    Q -->|AGENTS 或项目知识沉淀| Z[capture-project-knowledge]
    Q -->|常规复杂任务| AA[统一执行与验证]

    R --> AB{是否面向 code release Git remediation}
    S --> AB
    T --> AB
    U --> AB
    V --> AC{release gate 结论}
    W --> AB
    X --> AB
    Y --> AB
    AA --> AB
    Z --> AK[统一输出 + evidence + next step + resume anchor]

    AC -->|ship| W
    AC -->|hold| AD[生成 remediation brief 或 next iteration brief]
    AD --> AB

    AB -->|是| AE[Harness constraint gate]
    AE --> AF[Team Engine Lite]
    AF --> AG[DeliveryCycleReport]
    AG --> AH{Verifier verdict}
    AH -->|pass| AK
    AH -->|fail| AI[RemediationPatch 加有界重试]
    AI --> AF
    AH -->|hold| AJ[升级给 Lead 或 Human 决策]
    AJ --> AK

    AB -->|否| AK
```

## 如何调用

最常见的调用方式：

```text
$virtual-intelligent-dev-team 帮我接管这次重构，并给出可执行分工。
$virtual-intelligent-dev-team /auto setup 这个项目级迁移。
$virtual-intelligent-dev-team 判断当前版本是否可以 release。
```

如果你主要关心运行时规则，优先读：

- `SKILL.md`
- `references/runtime-routing-index.md`
- `references/tooling-command-index.md`

如果你主要关心维护和扩展，优先读：

- `README.md`
- `docs/README.md`

## 校验命令

项目级：

```bash
python3 validate.py --changed
```

skill 级：

```bash
python3 ../scripts/sync_virtual_intelligent_dev_team_version.py --check
python3 ../scripts/sync_virtual_intelligent_dev_team_version.py
python3 skill-forge/scripts/quick_validate.py ./virtual-intelligent-dev-team
python3 -m unittest virtual-intelligent-dev-team.tests.test_routing_and_guardrails
python3 virtual-intelligent-dev-team/scripts/validate_virtual_team.py --pretty
```

## 版本

当前版本见 [VERSION](VERSION)。

## 致谢与参考来源

本项目的迭代优化模式部分参考了 [agency-agents](https://github.com/msitarzewski/agency-agents) 的设计思路，并在其基础上适配了本 skill 的闭环工作流、状态恢复与发布治理等能力。

相关的模式提炼见 [references/bounded-iteration-patterns.md](references/bounded-iteration-patterns.md)。

## License

本项目使用 [MIT License](LICENSE)。
