# Virtual Intelligent Dev Team

`virtual-intelligent-dev-team` 是一个面向复杂软件工作的智能协作项目。

它不只是”专家角色路由器”，而是把研发、产品、分轮内测、技术治理、发布门禁、显式 `/auto` 自动运行，以及状态驱动恢复，收拢成一个可持续迭代的闭环工作流。

一句话说：

它适合接手”单个专家已经不够、单轮回答也不够”的复杂软件任务。

---

## 🚀 5 分钟快速上手

### 1. 最简单的使用场景（小切片交付）

```bash
# 场景：实现一个小功能或修复一个 bug
/virtual-intelligent-dev-team 实现用户登录功能的邮箱验证
```

**会发生什么：**
- 自动路由到 `Technical Trinity`（通用后端工程专家）
- 生成 Quick Slice Brief（包含目标、范围、验收条件）
- 实现代码并保留 delivery status 和完成证据
- 给出下一步建议（测试、提交、发布门禁等）

### 2. 模糊想法确认（意图确认）

```bash
# 场景：有一个想法，不确定该从产品、原型、技术还是架构入手
/virtual-intelligent-dev-team 我想做一个用户画像功能
```

**会发生什么：**
- 先给出 5 个确认方向选项：
  - `product-opportunity`：产品机会验证
  - `prototype-exploration`：原型探索
  - `technical-feasibility`：技术可行性评估
  - `architecture-risk`：架构风险分析
  - `delivery-plan`：交付拆解
- 用户选择后，路由到对应的 Lead Agent 或 Workflow Bundle

### 3. 大重构规划（开发前规划）

```bash
# 场景：需要重构认证系统
/virtual-intelligent-dev-team 重构认证系统，从 Session 改为 JWT
```

**会发生什么：**
- 路由到 `Sentinel Architect`（高风险变更治理）
- 激活 Pre-Development Planning Playbook
- 生成 Planning Pack（包含阶段计划、通道笔记、进度锚点）
- 提供多阶段执行路径和回滚点

### 4. 产品定义（产品发现专家团）

```bash
# 场景：定义产品 PRD
/virtual-intelligent-dev-team 帮我定义一个知识管理产品的 PRD
```

**会发生什么：**
- 路由到 `World-Class Product Architect`
- 激活 `product-discovery-council`（产品发现专家团）
- 提供产品战略模板、用户研究模板、竞品分析模板
- 生成结构化 PRD

### 5. 自动化运行（显式 /auto）

```bash
# 场景：自动化执行多轮优化
/virtual-intelligent-dev-team /auto 优化 API 响应时间
```

**会发生什么：**
- 进入 Setup → Go 两阶段协议
- 先建立 automation state（包含目标、检查点、恢复锚点）
- 执行有边界的迭代优化
- 保留状态文件供后续 resume

---

## 项目定位

这个项目最适合三类问题：

- 复杂研发交付
  - 例如小切片实现、大重构、迁移、跨模块联动、技术治理
- 产品与研发协同
  - 例如需求澄清、验收标准、前后端协作、分轮 beta
- 模糊想法分流
  - 例如用户只给出一个猜想，不确定该做产品验证、原型探索、技术可行性、架构风险还是交付拆解
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
- 模糊猜想的意图确认反问：先让用户在 `product-opportunity`、`prototype-exploration`、`technical-feasibility`、`architecture-risk`、`delivery-plan` 中确认方向，确认后才把 provisional route 收敛成最终路线
- 大型重构、迁移、拆分、技术治理
- 多轮优化、benchmark、回滚、resume
- 产品定义、验收标准、分轮 beta 内测
- 产品发现专家团与原型设计专家团：在 `product-spec-deliver` 内按需展开阶段内 specialists，但不替换顶层 lead
- release gate 与 post-release feedback loop
- 完成证据门禁：`done / ready / ship / handoff` 之前必须有结构化 completion evidence，且 `evidence_refs` 要能指向可验证命令或本地 artifact
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
- `意图确认`
  - 低信息量或模糊猜想不会直接硬路由，会先给出目标 lead / workflow bundle / stage council 选项，让用户确认切入方向。
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
- `完成证据门禁`
  - 非平凡完成声明必须保留 action、result、covered scope、uncovered scope、residual risk、confidence grade 和 evidence refs；release gate 会拒绝只有 benchmark 绿、但缺少完成证据的 `ship`。
- `发布与反馈闭环`
  - 不只做发布前 gate，也覆盖发布后的反馈回写与下一轮修复入口。
- `阶段专家团`
  - 产品战略、PRD、用户研究、竞品、指标、路线图等请求可激活 `product-discovery-council`；高保真原型、设计系统、可运行 HTML 原型与可访问性审查可激活 `prototype-design-council`。两者都是 `World-Class Product Architect` 下面的 overlay，不会把简单任务升级成新顶层团队。

## 能力矩阵

| 维度 | 本项目提供什么 | 普通多专家提示词常见缺口 |
| --- | --- | --- |
| 任务路由 | 选择主负责人、协同者、治理轨道 | 往往只是平铺多个角色视角 |
| 日常交付 | 小切片 brief、项目上下文、状态锚点 | 容易直接跳到实现，缺少可恢复上下文 |
| 执行模式 | 支持手动模式与显式 `/auto` | 通常没有明确模式切换 |
| 恢复能力 | 状态优先恢复、resume、恢复锚点 | 容易依赖上下文记忆 |
| 迭代能力 | 有边界的多轮优化、基线、回滚决策 | 常见问题是无限"再来一轮" |
| 发布治理 | release gate、completion evidence、hold 后续修复入口 | 常停留在"建议发/不发"或只看 benchmark 结果 |
| 上线后闭环 | post-release feedback loop | 很少覆盖上线后的反馈回写 |
| 产品协同 | 支持产品、研发、技术治理联动 | 容易偏单一研发视角 |
| 阶段专家团 | 产品发现与原型设计可按需展开 council overlay | 常见做法要么单专家过载，要么所有任务都进重流程 |
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
- `references/playbook-index.md`
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

## v5.0.0 Highlights

v5.0 把"路由可见性 + Agent Manifest 治理 + 多语言覆盖"合并为一次发版，对应迭代路线图 §2.1 与 §2.4 的内容：

- **治理基础（§2.1）**
  - 决策日志从 `.skill-metrics/governance_events.jsonl` 迁移到 `.skill-metrics/decision-log.jsonl`，字段契约见 `references/decision-log.schema.json`。新字段 `decision` / `verifier` / `reason` / `evidence` 全部 optional，向后兼容。一次性迁移入口：`scripts/migrate_governance_events.py`。
  - 6 个 Lead Agent 全部扩展 `Constraints`（硬护栏）和 `Evidence Requirements`（完成前必备证据）字段，叙述版在 `references/agent-catalog.md`，机器可读版在 `references/routing-rules.json → agent_rules[*]`。
  - Harness 健康检查：`scripts/check_harness_health.py` 一次性覆盖 Agent Identity / Agent Manifest / Routing Rules / Workflow Bundles / Decision Log / Language Profiles 6 项检查，输出 HEALTHY / DEGRADED / BROKEN。
  - 决策日志 Dashboard：`scripts/inspect_decision_log.py` 输出 JSON / Markdown / 自包含 HTML（无第三方依赖）。

- **多语言 Profile 系统（§2.4）**
  - `references/language-profiles.yaml`（schema `language-profiles/v1`）覆盖 9 种语言：java / kotlin / swift / cpp / csharp / php / ruby / elixir / scala。每种语言包含 ecosystem / conventions / verification / harness_constraints 四类上下文，由 LLM 在 agent 工作内存中按需注入。
  - `references/routing-rules.json → language_profiles` 从 4 个扩展到 13 个：保留 python / go / nodejs / rust，新增 java / kotlin / swift / cpp / csharp / php / ruby / elixir / scala。Java 仍由 `Java Virtuoso` 独立处理。
  - 完整性校验：`scripts/check_language_profiles.py` 校验 yaml ↔ json 单向一致性、必填字段、关键词重叠率。
  - 三层解耦：路由（JSON）/ 上下文（YAML）/ 约束（YAML + Agent Manifest），加新语言只影响对应层。

- **v5.5 已完成**
  - 沉降精简：references/ 95 → 88 文件，I类组件内联至 SKILL.md
  - 领域特化 Agent：Data Pipeline Guardian + API Contract Sentinel
  - 平台化架构预留：`.skill-harness/trigger.yaml`（v0.5 schema）

- **v5.7.0 — SKILL.md 结构清理**
  - 删除重复的 Quick examples 和 Key terms 章节
  - 清理 4 个死引用（output-contract.md, runtime-routing-index.md, workflow-bundles.md, decision-log-schema.md）
  - 重写 Description：8 个 agent 全列出，精简至 280 字符
  - Runtime Routing 表补齐 2 条新路由（data-pipeline-govern, api-contract-govern）

### v5.0.1 — Decision Log Dashboard 视觉重做（patch bump）

在 v5.0.0 基础上，仅重做 `scripts/inspect_decision_log.py` 的 `render_html()` 与 `render_markdown()`：

- **Hero section**：深色渐变（#0f172a → #1e293b → #312e81）+ 双 radial-gradient 高光（紫 + 蓝）+ HEALTHY/EMPTY 状态徽章
- **设计 token 系统**：CSS variables 统一颜色 / 字号 / 圆角 / 阴影；语义色 `--info` / `--ok` / `--warn` / `--err` / `--accent`
- **4 个差异化 KPI 卡片**：events=蓝、throughput=紫、first/last=绿，hover 微抬升 + 阴影加深
- **5 个分布卡片用语义色 bar**：
  - Decision Distribution：🧭 icon，delivery_held=amber / release_hold=red / fast_track=purple
  - Verifier Distribution：✅ icon，pass=green / fail=red / hold=amber / n_a=gray
  - Lead Agent Distribution：👥 icon，neutral info
  - Track Distribution：🚦 icon，regular=blue / fast=purple
  - Risk Distribution：⚠️ icon，low=green / medium=amber / high=red
- **Hourly Throughput 改为 inline SVG sparkline**：紫色渐变 area fill + 线 + peak 红点 + 极值坐标
- **响应式**：`auto-fit` grid 在 < 640px 折叠为单列；KPI 网格降为 2 列
- **可访问性**：`aria-label` / `aria-hidden` / contrast ≥ 4.5 / tabular-nums 数字对齐
- **零依赖**：无 CDN、无 JS、无外部字体（系统字体栈）

MarkDown 报告同步升级：emoji section 标题 + ASCII bar + sparkline code block。

### v5.0.2 — Dashboard i18n + KPI 联动 + a11y v2（patch bump）

在 v5.0.1 基础上扩展 `scripts/inspect_decision_log.py`：

- **i18n 中英双语**：新增 `STRINGS` 字典（28 个 key × 2 语言）+ CLI `--language en|zh|auto`；`auto` 从 `LC_ALL` / `LANG` / `locale` 探测；fallback 永远走英文。`<html lang>`、`<title>`、hero / KPI / 分布标题 / 空状态 / footer 全部本地化。
- **CSS-only KPI ↔ 分布卡片 hover 联动**（零 JS，纯 `:has()`）：
  - KPI 卡片带 `data-focus="total|recent|history|latest"`
  - 分布卡片带 `data-focus`（decision/verifier=latest, lead=total, track=history, risk=recent）
  - hover 任意 KPI → 对应 dist-card 边框高亮 + 其他卡片淡化；反向同理
  - hover 任意 dist-row → 所有卡片中同 `data-key` 行高亮（如 hover `low` 在 Risk 卡片，所有卡片的 `low` 行都亮）
  - `:focus-within` 支持键盘焦点联动（Tab 即可触发）
- **a11y v2**：
  - **Skip link**：`<a class="skip-link" href="#main">` 默认隐藏，`:focus` 时显示在左上角
  - **键盘导航**：所有 `.kpi` 和 `.dist-row` 加 `tabindex="0"`；`:focus-visible` 全局蓝色描边
  - **ARIA 完整**：`role="list"` / `role="listitem"` / `aria-label` / `aria-labelledby` / `aria-live="polite"`（health badge）
  - **SVG 标题**：`<title>` 子元素让屏幕阅读器读出 sparkline 数据
  - **`prefers-reduced-motion`**：把所有 transition / animation 降到 0.01ms
  - **`prefers-contrast: more`**：边框加粗到 2px、文字加深、focus 描边加粗到 4px

中文样例产物：`/tmp/vidt-zh.html`（28.9KB）/ `/tmp/vidt-zh.md`（2.6KB）。

## 版本

当前版本见 [VERSION](VERSION)。

## 致谢与参考来源

本项目的迭代优化模式部分参考了 [agency-agents](https://github.com/msitarzewski/agency-agents) 的设计思路，并在其基础上适配了本 skill 的闭环工作流、状态恢复与发布治理等能力。

相关的模式提炼见 [references/bounded-iteration-patterns.md](references/bounded-iteration-patterns.md)。

## License

本项目使用 [MIT License](LICENSE)。
