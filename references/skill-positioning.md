# Virtual Intelligent Dev Team：能力定位与闭环说明

这份文档用于解释 `virtual-intelligent-dev-team` 在当前项目中的定位、能力边界与典型使用方式。

如果你更关心“它实际是怎么跑起来的”，可继续阅读：
`workflow-sequences.md`

它不是一个只负责“分配专家角色”的 skill，也不是一个无边界自动循环器。  
它更准确的定位是：

> 一个面向复杂任务的、可验证、可回退、有边界的工作闭环 skill。

---

## 1. 它解决的不是“回答问题”，而是“把任务闭环做完”

普通的专家路由 skill，重点通常是：

- 识别任务类型
- 选择一个合适专家
- 给出一轮建议

而 `virtual-intelligent-dev-team` 的目标更进一步：

- 先判断应该由谁主导
- 再组织必要的协作与治理
- 如果任务不是“一轮回答就结束”，则进入有边界的多轮迭代
- 如果任务进入正式验收阶段，则通过 release gate 判断 `ship` 或 `hold`
- 如果被判定为 `hold`，不是停在原地，而是自动铺设下一轮修复路径

所以它的核心价值不是“多角色”，而是“复杂任务的执行闭环”。

---

## 2. 当前已经形成的 4 层闭环

### 2.1 路由闭环

它会根据信号决定：

- 谁是 lead
- 是否需要 assistant
- 是否需要 governance
- 是否需要 process / Git guardrail

它处理的不是单一技术标签，而是综合：

- 任务类型
- 风险等级
- 技术栈
- Git / 提交流程
- 是否存在跨域耦合
- 是否需要根因分析或正式验收

这意味着它可以把“路由”从简单分类，提升为“任务执行入口”。

### 2.2 迭代闭环

当用户要求：

- 继续优化
- 多轮对比
- 看看还能不能更好
- 直到稳定为止
- 做 benchmark / regression 驱动迭代

这个 skill 不会用模糊的“再试一次”来应付，而是进入 bounded iteration。

它当前支持：

- baseline 注册与复用
- round memory
- self-feedback
- `keep / retry / rollback / stop`
- `pivot`
- `resume`
- distilled patterns 同步

这让每一轮不是孤立尝试，而是能基于上一轮证据做下一轮决策。

### 2.3 发布闭环

当问题从“跑分是否通过”变成“当前版本是否可以发布/提交/验收”时，会进入 formal release gate。

release gate 的输出不是笼统结论，而是明确二分：

- `ship`
- `hold`

其中：

- `ship` 表示当前证据足够支撑发布候选
- `hold` 表示仍存在 release blocker

更关键的是，`hold` 不只是“失败”，而是下一轮闭环的起点。

当前实现中，`hold` 会自动生成：

- next iteration brief
- failing baseline 注册
- blocker-specific mutation catalog
- remediation artifacts
- targets artifacts
- 可执行的 iteration workspace 起点
- 必要时直接 auto-run 下一轮

### 2.4 实测闭环

这个 skill 不只是“设计上闭环”，而是已经用离线 drill 做了关键路径验证。

当前覆盖的关键路径包括：

- `rollback -> keep`
- `pivot -> resume`
- `release-gate hold -> bootstrap -> auto-run`

这意味着它不是停留在文档概念上，而是已经把核心闭环路径做了真实演练。

---

## 3. `ship` 和 `hold` 应该怎么理解

### `ship`

`ship` 的含义不是“绝对完美”，而是：

- 当前关键 gate 已通过
- 已有足够证据支撑交付或发布候选判断
- 可以把当前结果视为阶段性可接受版本

通常还会伴随：

- release closure artifact
- release-ready baseline archive
- distilled patterns 同步

### `hold`

`hold` 的含义不是“本轮白做了”，而是：

- 当前版本还不适合进入发布态
- 已识别出明确 blocker
- 下一轮修复需要有针对性的起点，而不是重新从零开始

所以 `hold` 的价值在于：

- 不让迭代断掉
- 不让问题描述丢失
- 不让下一轮再次从空白状态起步

---

## 4. 常见使用场景

### 场景 A：复杂任务先判断该谁负责

用户可能会说：

- “这个需求到底应该从架构、代码还是 Git 流程先下手？”
- “这个问题我不知道该找谁看。”

这时它主要发挥的是**路由闭环**。

### 场景 B：当前版本还可以继续优化吗

用户可能会说：

- “评估当前项目里的版本。”
- “继续下一轮。”
- “还能不能继续优化？”

这时它主要发挥的是**迭代闭环**。

### 场景 C：已经试了很多次，要找根因

用户可能会说：

- “已经改过很多轮了还是不对。”
- “别再 blind patch 了，帮我找根因。”

这时它会转入**root-cause discipline**，优先证据、日志、配置、复现条件，而不是继续盲改。

### 场景 D：判断当前版本是否可以发布

用户可能会说：

- “现在达成闭环了吗？”
- “先发布一个版本吧。”
- “当前版本能 ship 吗？”

这时它主要发挥的是**发布闭环**。

---

## 5. 为什么说它不是“无边界自我迭代”

因为它的迭代机制是有约束的：

- 有 baseline
- 有轮次状态
- 有 evidence check
- 有 keep / rollback 决策
- 有 stop 条件
- 有 pivot 条件
- 有 resume 机制
- 有 release gate 作为正式验收边界

所以它不是无限循环地“自己改自己”，而是：

> 在明确目标、明确证据、明确回退规则的前提下，进行受约束的自迭代。

这也是它与“泛化自动代理幻想”最大的区别。

---

## 6. 关键术语速记

### baseline

本轮或当前候选的对照基线，用于判断是否真的变好。

### round memory

当前轮次的短时记忆，记录：

- 做了什么
- 出了什么问题
- 哪些信号值得下一轮继承

### self-feedback

基于当前轮证据形成的自反馈，不是泛泛总结，而是为下一轮提供可执行优化方向。

### keep

保留当前轮结果，并将其晋升为更优基线或可接受状态。

### retry

当前方向未完全失败，但证据还不足以保留，需要同一方向再做有限重试。

### rollback

当前轮结果带来回归或风险，需要撤回到上一个稳定状态。

### stop

继续迭代的收益已经不足，或证据不足，或达到边界，应停止本轮循环。

### pivot

当前假设已经耗尽价值，需要切换到新的瓶颈或新方向。

### resume

从持久化的 loop state 继续，而不是从头再跑一遍。

---

## 7. 当前项目里，这个 skill 的实际效果

在当前仓库中，`virtual-intelligent-dev-team` 已经不只是一个“角色路由模板”，而是具备以下工程效果：

1. 能把复杂请求变成明确 lead / assistant / governance 的执行分工  
2. 能把“继续优化”变成带证据的 bounded iteration  
3. 能把“能不能发版”变成 formal release gate 判断  
4. 能在 `hold` 之后继续自动铺设下一轮修复起点  
5. 能通过 offline drill 证明关键闭环路径没有只停留在纸面

如果要用一句话总结它当前的效果，可以写成：

> 它把“专家路由”升级成了“复杂任务的阶段性完整闭环执行框架”。

这个表述相对稳妥，也更适合放在工程说明里。
