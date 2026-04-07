# Routing Score Matrix

作者：fxbin  
版本：v2.5  
更新日期：2026-03-04

## 说明

- 本文档用于解释路由机制，不再作为机器可执行配置。
- 机器可执行配置以 `references/routing-rules.json` 为准。
- 推荐维护方式：只改 `routing-rules.json`，本文档按需更新说明。

## 评分模型

1. 显式优先路由  
- `priority_routing_rules` 用于处理“审计优先于语言栈”“明确 Git 流程优先于泛化工程问题”这类硬优先级场景。
- 命中优先规则后先确定主责，再结合分值选择辅助智能体。

2. 正向关键词加分  
- 命中 `positive` 关键词，按权重累加。

3. 负向关键词扣分  
- 命中 `negative` 关键词，按惩罚分扣减。
- 目标：减少误触发和跨域串线。

4. 分值裁剪  
- `final_score = clamp(positive_score - negative_score, 0, max_agent_score)`。

5. 置信度  
- `confidence = top1_score / max(top3_total_score, 1)`。

6. 语言识别  
- `language_profiles` 用于识别 `python/go/nodejs/rust` 等语言栈并给出主责映射。
- 当仅命中语言信号且领域分值不足时，进入“语言驱动模式”。

7. 匹配边界  
- 中文关键词：子串匹配。
- 英文关键词：词边界匹配，避免短词误触发（如 `pr`、`ui`、`go`）。
- Go 语言：裸词 `go` 必须同时命中技术上下文词（如 `backend/api/service`）才生效。

## 阈值策略（可配置）

- `high_confidence`：默认 `0.55`，单主责。
- `medium_confidence`：默认 `0.35`，主责 + 1 辅助。
- 低于 `medium_confidence`：主责 + 2 辅助，并建议澄清。
- `sentinel_overlay_threshold`：默认 `6`，命中即叠加治理流程。
- `default_unknown_lead_agent`：默认 `Technical Trinity`，全 0 分时用于兜底主责。

## Workflow Bundle 置信度

- `bundle_confidence` 解释的是“当前工作流 bundle 的确定性”，不是主责路由分数本身。
- 它和 `confidence` 分开存在：
  - `confidence` 看的是 lead 在候选智能体中的相对占优程度。
  - `bundle_confidence` 看的是请求是否已经落入稳定、可复用的流程旅程。
- 当前口径：
  - `ship-hold-remediate = 0.98`
    - 来源 `process-skill`
    - 正式 release gate 被明确请求时，流程确定性最高。
  - `plan-first-build = 0.96`
    - 来源 `process-skill`
    - 重写 / 迁移 / 先规划后开发场景，先建 planning pack 的路径非常稳定。
  - `root-cause-remediate = 0.93`
    - 来源 `process-skill`
    - 显式 iteration / benchmark / compare / keep improving 场景。
  - `root-cause-remediate = 0.84`
    - 来源 `keyword+lead`
    - 由高风险 lead 或根因排查关键词触发，但还没进入完整 iteration 流程。
  - `audit-fix-deliver = 0.88`
    - 来源 `lead+keyword`
    - 审计 lead 与 review/audit 类关键词同时成立。
  - `audit-fix-deliver = 0.78`
    - 来源 `lead-default`
    - 只有审计 lead 成立，但文本里没有足够强的 review 关键词。
  - `direct-execution = 0.35`
    - 来源 `fallback`
    - 没有更强的流程旅程，保持轻量直执行。
- `workflow_bundle_source` 用来解释这个值为什么成立，当前来源分为：
  - `process-skill`
  - `keyword+lead`
  - `lead+keyword`
  - `lead-default`
  - `fallback`
- 验证建议：
  - 当 `bundle_confidence >= 0.6` 时，允许把 bundle 当作显式执行旅程。
  - 当 `bundle_confidence < 0.6` 时，优先保持轻量执行，不要把 bundle 说成强约束流程。
- 低 lead `confidence` 不等于一定要加 assistants。
  - `process_only`、`language_only`、`unknown_only` 这三类场景，即使 lead `confidence` 很低，也默认不扩成多 assistant，因为问题信息量不足或只是流程/语言驱动。

## 流程技能路由（非主责评分）

- `using-git-worktrees` 与 `git-workflow` 仅作为流程增强，不参与主责智能体打分。
- 当仅命中流程技能而未命中领域智能体时，回退主责为 `Technical Trinity`，进入流程驱动模式。
- 当 `PR/MR` 只是审计上下文而不是 Git 操作意图时，抑制 `git-workflow` 自动触发，避免“审计请求被误判成提交流程”。

## 内置执行能力

- 本 skill 已内置：
  - `references/using-git-worktrees-playbook.md`
  - `references/git-workflow-playbook.md`
- 脚本输出 `process_plan` 可直接执行，无需外部同名 skill。
- 脚本输出 `detected_languages` 与 `language_routing` 可直接用于多语言任务派工。
