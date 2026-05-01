# Tooling Command Index

这份索引只做一件事：

`按当前动作，告诉你该用哪个脚本、模板和验证入口。`

不要在 `SKILL.md` 里维护整本命令手册。

## 一、最常用入口

- 路由检查

```bash
python scripts/route_request.py --text "<user request>" --config references/routing-rules.json
```

- skill 回归验证

```bash
python scripts/validate_virtual_team.py --pretty
```

- 执行动作前先做合法性校验

```bash
python scripts/verify_action.py --text "<user request>" --check process-skill --process-skill bounded-iteration --pretty
```

```bash
python scripts/verify_action.py --text "<user request>" --check git-workflow --pretty
```

```bash
python scripts/verify_action.py --text "<user request>" --check worktree --pretty
```

```bash
python scripts/verify_action.py --text "<user request>" --check workflow-bundle --pretty
```

```bash
python scripts/verify_action.py --text "<user request>" --check bundle-bootstrap --pretty
```

```bash
python scripts/verify_action.py --text "/auto <user request>" --check auto-mode --pretty
```

- `workflow-bundle` 校验现在会返回：
  - `workflow_bundle_source`
  - `workflow_bundle_source_explanation`
  - 适合在高风险、多阶段或“为什么是这条流程”容易被误解时先解释再执行
- `bundle-bootstrap` 校验现在会返回：
  - 当前 bundle 是否必须先初始化
  - `progress_anchor_recommended` 是否和 `resume_anchor` 对齐
  - `resume_anchor` 是否真的落在 bootstrap 产物与恢复清单里
  - 当前仓库里的 bootstrap 产物是 `missing / partial / ready` 哪种状态
- `verify_action.py` 的 JSON 结果契约见：
  - `references/verify-action-result.schema.json`
- `auto-mode` 校验会额外确认：
  - 当前请求是否显式使用 `/auto`
  - 当前 workflow 是否在自动白名单里
  - 如果是 `go`，本地是否已经存在 `.skill-auto/auto-run-plan.json`
  - `safe / background / resume` 子协议是否已经落成 machine-readable profile

```bash
python scripts/verify_action.py --text "<user request>" --check assistant-delta-contract --pretty
```

- 机械契约 lint

```bash
python scripts/lint_virtual_team_contract.py --pretty
```

- benchmark eval 配置契约见：
  - `references/benchmark-evals.schema.json`
- benchmark 结果契约见：
  - `references/benchmark-run-result.schema.json`
- `run_benchmarks.py` / `lint_virtual_team_contract.py` 现在会先校验：
  - `evals/evals.json` 的 JSON schema
  - eval `id` 是否重复
  - `benchmark-results.json` 的核心结构

- Git guardrail

```bash
python scripts/git_workflow_guardrail.py
```

- 输出骨架生成

```bash
python scripts/generate_response_pack.py --text "<user request>" --repo . --output .tmp-response-pack.md
```

默认会在同目录生成 `.tmp-response-pack.json` 作为 sidecar。

```bash
python scripts/generate_response_pack.py --text "<user request>" --repo . --template planning --output .tmp-response-pack.md
```

```bash
python scripts/generate_response_pack.py --text "<user request>" --repo . --template release --output .tmp-response-pack.md
```

```bash
python scripts/generate_response_pack.py --text "<中文请求>" --repo . --language zh --output .tmp-response-pack.md
```

```bash
python scripts/generate_response_pack.py --text "<user request>" --repo . --output .tmp-response-pack.md --json-output .tmp-response-pack.sidecar.json
```

- 默认 `--language auto`
  - 请求里有中文时优先输出中文骨架
  - 也可以显式用 `--language zh` 或 `--language en` 覆盖
- 输出骨架会同时带出 `workflow_bundle`、`bundle_confidence` 和 `workflow_bundle_source`
- 用户可见输出里也应带出 `workflow_bundle_source_explanation`
  - 特别适合 release / planning / iteration 这类容易被问“为什么要先走这条流程”的场景
- 当前推荐结构：
  - `Execution Result`
  - `Evidence`
  - `Next Action`
  - `Resume`
  - 再进入 `Git Workflow / Governance / Bundle Bootstrap / Beta Program / Planning Pack / Optimization Loop`
- `verify_action.py` 现在也会回传 `explanation_card`
  - 适合在执行前把 `workflow_bundle / source explanation / next action / resume anchor` 直接喂给别的脚本
- JSON sidecar 的稳定字段说明见：
  - `references/response-pack-sidecar-schema.md`
- 可执行 schema 见：
  - `references/response-pack-sidecar.schema.json`
- `generate_response_pack.py` 写 sidecar 前会先做 schema 校验
- benchmark 断言优先用 `response_pack_json <path> is/contains ...`
  - 只在需要验证 Markdown 文案骨架时才继续用 `response_pack contains ...`
- 如果 eval runner 不是默认路由：
  - `verify_action_json <path> ...`
  - `release_gate_json <path> ...`
- 结构化断言额外支持：
  - `<path> exists`
  - `<path> does not exist`
  - `<path> is null`
  - `<path> is not null`
  - `<path> length is <n>`
  - `<path> >= <number>` / `<=` / `>` / `<`

## 二、开发前规划资产

模板：

- `assets/pre-development-project-overview-template.md`
- `assets/pre-development-task-breakdown-template.md`
- `assets/pre-development-progress-master-template.md`
- `assets/pre-development-phase-template.md`
- `references/pre-development-output-template.md`

常用初始化命令：

```bash
python scripts/init_pre_development_plan.py --root . --task-name "<task-name>" --task-description "<task-description>" --phase-name foundation --pretty
```

默认会同时生成完整多阶段 planning 骨架：

- `docs/progress/phase-1-<name>.md`
- `docs/progress/phase-2-architecture.md`
- `docs/progress/phase-3-execution.md`
- `docs/progress/phase-4-cutover.md`

## 三、产品交付资产

模板：

- `assets/product-delivery-brief-template.md`
- `assets/product-contract-questions-template.md`
- `references/product-delivery-playbook.md`

常用初始化命令：

```bash
python scripts/init_product_delivery.py --root . --pretty
```

## 四、已发布反馈资产

模板：

- `assets/post-release-rollout-summary-template.md`
- `assets/post-release-feedback-ledger-template.md`
- `assets/post-release-signal-report-template.json`
- `assets/post-release-triage-summary-template.md`
- `references/post-release-feedback-playbook.md`
- `references/post-release-feedback-report.schema.json`
- `references/post-release-feedback-result.schema.json`

常用初始化命令：

```bash
python scripts/init_post_release_feedback.py --root . --pretty
```

```bash
python scripts/evaluate_post_release_feedback.py --report .skill-post-release/current-signals.json --pretty
```

- `run_release_gate.py` 在 `ship` 时会自动初始化 `.skill-post-release/`
- `evaluate_post_release_feedback.py` 会把结果判断为：
  - `monitor`
  - `iterate`
  - `escalate`
- 当结果是 `iterate / escalate`：
  - 会自动生成 `next-iteration-brief.json`
  - 会把 shipped feedback 写回产品资产
  - 必要时会把升级信息写回技术治理资产

## 四点五、显式自动运行资产

模板：

- `assets/auto-run-plan-template.json`
- `references/auto-run-playbook.md`
- `references/automation-state.schema.json`
- `references/automation-resume-decision-matrix.md`
- `references/automation-resume-execution.schema.json`

恢复入口：

```bash
python scripts/inspect_automation_state.py --repo . --pretty
```

```bash
python scripts/inspect_automation_state.py --repo . --workflow ship-hold-remediate --pretty
```

受控恢复执行入口：

```bash
python scripts/resume_from_automation_state.py --repo . --pretty
```

```bash
python scripts/resume_from_automation_state.py --repo . --workflow post-release-close-loop --execute --pretty
```

常用命令：

```bash
python scripts/run_auto_workflow.py --text "<original-request-without-/auto>" --mode setup --pretty
```

```bash
python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty
```

- 默认仍是手动模式
- 只有显式 `/auto` 才进入自动协议
- 当前只对白名单 workflow 生效：
  - `root-cause-remediate`
  - `ship-hold-remediate`
  - `post-release-close-loop`
- 自动模式必须走 `setup -> go`
- 当前支持子协议：
  - `safe`
  - `background`
  - `resume`
- `setup` 会生成：
  - `.skill-auto/auto-run-plan.json`
  - `.skill-auto/auto-run-plan.md`
  - `.skill-auto/state/*.json`
- `go` 会写回：
  - `.skill-auto/last-run.json`
  - `.skill-auto/last-run.md`
  - 底层 release / post-release automation state
- `inspect_automation_state.py` 会返回：
  - 当前选中的 state
  - `decision_card`
  - 推荐恢复命令
- `resume_from_automation_state.py` 默认只做 dry-run：
  - 读取 `decision_card`
  - 校验推荐命令是否在白名单里
  - 告诉你如果显式加 `--execute` 会跑什么
- 只有显式 `--execute` 时才会真正执行恢复命令
- 执行后会额外沉淀：
  - `.skill-auto/resume-executions/<resume-exec-id>.json`
  - `.skill-auto/resume-executions/<resume-exec-id>.md`
- 其中 JSON ledger 现在受正式 schema 约束：
  - `references/automation-resume-execution.schema.json`
- 当前 allowlist 只开放：
  - `run_auto_workflow.py`
  - `run_release_gate.py`
  - `evaluate_post_release_feedback.py`
  - `init_technical_governance.py`
  - `init_product_delivery.py`
  - `init_iteration_round.py`
- `run_iteration_loop.py`

- `generate_response_pack.py` 在显式 `/auto resume` 请求上还会额外输出：
  - `automation_resume`
  - 包含当前命中的 state、决策卡、dry-run 命令、execute 命令、playbook 和阻塞条件
  - 可恢复锚点
  - 所有已发现 state 的摘要

## 五、内测验证资产

模板：

- `assets/beta-program-overview-template.md`
- `assets/beta-cohort-matrix-template.md`
- `assets/beta-cohort-plan-template.json`
- `assets/beta-feedback-ledger-template.md`
- `assets/beta-ramp-plan-template.json`
- `assets/simulated-user-profile-template.json`
- `assets/beta-simulation-config-template.json`
- `assets/beta-round-report-template.json`
- `references/beta-validation-playbook.md`
- `references/beta-cohort-plan.schema.json`
- `references/beta-ramp-plan.schema.json`
- `references/beta-remediation-brief.schema.json`
- `references/simulated-user-profile.schema.json`
- `references/simulation-persona-library.schema.json`
- `references/simulation-persona-library.json`
- `references/simulation-cohort-fixtures.schema.json`
- `references/simulation-cohort-fixtures.json`
- `references/beta-simulation-config.schema.json`
- `references/beta-simulation-event.schema.json`
- `references/beta-simulation-run.schema.json`
- `references/simulation-scenario-packs.schema.json`
- `references/simulation-scenario-packs.json`
- `references/simulation-trace-catalog.schema.json`
- `references/simulation-trace-catalog.json`
- `references/beta-round-report.schema.json`
- `references/beta-round-gate-result.schema.json`
- `references/beta-simulation-manifest.schema.json`
- `references/beta-simulation-diff.schema.json`

常用初始化命令：

```bash
python scripts/init_beta_validation.py --root . --pretty
```

```bash
python scripts/init_beta_simulation.py --root . --round-id round-0 --phase "pre-build concept smoke" --objective "<objective>" --pretty
```

```bash
python scripts/preview_beta_simulation_fixture.py --config .skill-beta/simulation-configs/round-0.json --pretty
```

```bash
python scripts/compare_beta_simulation_manifests.py --previous .skill-beta/fixture-previews/round-0/beta-simulation-manifest.json --current .skill-beta/fixture-previews/round-1/beta-simulation-manifest.json --pretty
```

```bash
python scripts/run_beta_simulation.py --config .skill-beta/simulation-configs/round-0.json --pretty
```

```bash
python scripts/summarize_beta_simulation.py --run .skill-beta/simulation-runs/round-0/beta-simulation-run.json --feedback-ledger-out .skill-beta/feedback-ledger.md --round-report-out .skill-beta/reports/round-0.json --pretty
```

```bash
python scripts/init_beta_round_report.py --root . --round-id round-1 --phase "closed beta" --sample-size 12 --participant-mode "seed users" --goal "<goal>" --exit-criteria "<exit-criteria>" --pretty
```

```bash
python scripts/evaluate_beta_round.py --report .skill-beta/reports/round-1.json --pretty
```

- `evaluate_beta_round.py` 现在会消费 round report 里的 fixture diff 证据：
  - `evidence_artifacts.fixture_diff_json`
  - `evidence_artifacts.fixture_diff_markdown`
- `evaluate_beta_round.py` 现在也会消费 cohort plan 证据：
  - `evidence_artifacts.cohort_plan_json`
- `evaluate_beta_round.py` 现在也会消费 ramp plan 证据：
  - `evidence_artifacts.ramp_plan_json`
- 对 `round-1+`：
  - 只要 round report 带了 fixture manifest，就必须带 machine-readable cohort plan
  - cohort plan 和 resolved fixture manifest 的 `planned_sessions / persona counts / scenario coverage / trace coverage` 不一致会直接阻止 `advance`
  - 缺少 ramp plan 证据会直接阻止 `advance`
  - ramp plan 和 round report 不一致也会阻止扩量
  - 缺少 diff 证据会直接阻止 `advance`
  - diff 标记 `review_required` 也会阻止扩量
- 当结果是 `hold / escalate`：
  - 会自动在当前 gate 输出目录生成 `next-round-remediation-brief.json`
  - 同时生成 `next-round-remediation-brief.md`
  - brief 会附带 blocker 列表、推荐重跑命令、resume artifacts，以及 persona / scenario blocker breakdown

## 六、技术治理资产

模板：

- `assets/technical-governance-change-plan-template.md`
- `assets/technical-governance-release-checklist-template.md`
- `references/technical-governance-playbook.md`

常用初始化命令：

```bash
python scripts/init_technical_governance.py --root . --pretty
```

## 七、bounded iteration 资产

模板：

- `assets/iteration-ledger-template.md`
- `assets/round-reflection-template.md`
- `assets/round-memory-template.md`
- `assets/self-feedback-template.md`
- `assets/distilled-patterns-template.md`
- `assets/iteration-plan-template.json`
- `references/project-memory-lite.md`

## 七点五、project memory lite

推荐锚点：

- `docs/progress/MASTER.md`
- `.skill-iterations/current-round-memory.md`
- `.skill-iterations/distilled-patterns.md`

常用初始化命令：

```bash
python scripts/init_project_memory.py --root . --mode planning --pretty
```

```bash
python scripts/init_project_memory.py --root . --mode iteration --pretty
```

```bash
mkdir -p docs/progress
cp assets/pre-development-progress-master-template.md docs/progress/MASTER.md
```

```bash
mkdir -p .skill-iterations
cp assets/round-memory-template.md .skill-iterations/current-round-memory.md
cp assets/distilled-patterns-template.md .skill-iterations/distilled-patterns.md
```

## 八、iteration 命令

- 初始化 round

```bash
python scripts/init_iteration_round.py --workspace .skill-iterations --round-id round-01 --objective "<goal>" --baseline "<baseline>" --pretty
```

- 注册 baseline

```bash
python scripts/register_benchmark_baseline.py --workspace .skill-iterations --label stable --report <baseline-report> --pretty
```

- 单轮 cycle

```bash
python scripts/run_iteration_cycle.py --workspace .skill-iterations --round-id round-01 --objective "<goal>" --baseline-label stable --candidate "<candidate-change>" --candidate-worktree ../wt-round-01 --candidate-output-dir .tmp-iteration-round-01 --promote-label accepted-round-01 --sync-distilled-patterns --pretty
```

- 多轮 loop

```bash
python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.json --pretty
```

- resume 已中断 loop

```bash
python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.json --resume --pretty
```

## 九、release / drill / compare

- offline drill

```bash
python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty
```

- release gate

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --pretty
```

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --beta-decision-dir .skill-beta/round-decisions --pretty
```

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --beta-report-dir .skill-beta/reports --pretty
```

- `run_release_gate.py` 的 JSON 结果契约见：
  - `references/release-gate-result.schema.json`
- 当 `--beta-decision-dir` 指向的最新 beta gate 已经产出 `next-round-remediation-brief.json` 时：
  - `run_release_gate.py` 会把该 brief 的 blockers 吸收到 release blockers
  - `next-iteration-brief.json` 会继承 beta brief 的 `required_evidence`
  - `next-iteration-brief.json` 会继承 beta brief 的 `recommended_commands`
  - `explanation_card.resume_artifacts` 和 release hold brief 会带上 beta brief 与 writeback artifacts，方便跨阶段恢复
- 当 release gate 结果是 `ship`：
  - 会自动初始化 `.skill-post-release/rollout-summary.md`
  - 会自动初始化 `.skill-post-release/current-signals.json`
  - follow-up 里会带出 `post_release_bootstrap`

- benchmark eval runner 支持：
  - `route`
  - `verify_action`
  - `release_gate`

- benchmark compare

```bash
python scripts/compare_benchmark_results.py --baseline <baseline-report> --candidate <candidate-report> --pretty
```

## 十、promotion / sync / materialize

- promote baseline

```bash
python scripts/promote_iteration_baseline.py --workspace .skill-iterations --round-id round-01 --label accepted-round-01 --pretty
```

- sync distilled patterns

```bash
python scripts/sync_distilled_patterns.py --workspace .skill-iterations --pretty
```

- materialize candidate patch

```bash
python scripts/materialize_candidate_patch.py --brief .skill-iterations/candidate-briefs/round-01.json --candidate-root ../wt-round-01 --patch-output .skill-iterations/patches/round-01.patch --pretty
```

## 十一、使用原则

- 高风险、多阶段、多人协作前，先用 `verify_action.py` 确认 process skill / lead assignment / release gate / iteration 是否真的该开
- 如果路由返回了 `product-spec-deliver`、`beta-feedback-ramp` 或 `govern-change-safely`，再额外跑一次 `bundle-bootstrap`，确认起盘动作和恢复锚点没有漂移
- 需要跨会话恢复时，优先只推荐一个主锚点，再补最多两个 supporting artifacts
- 改了路由、索引、playbook、脚本命令后，先跑 `lint_virtual_team_contract.py`，再跑 `validate_virtual_team.py`
- 开发前规划分支只在大改造、迁移、重写、先规划后开发时启用
- iteration 深循环时，先开本索引，再补对应 playbook
- `run_release_gate.py` 优先用于 `ship / hold` 判断，不用 benchmark 结果硬代替
- beta 已经 `hold / escalate` 时，不要手工重写一份 release remediation；优先复用 beta remediation brief 继续收口
- 版本已经 `ship` 后，不要把真实反馈继续塞回 beta；优先走 `.skill-post-release/` 的正式回流链路
- `run_iteration_loop.py --resume` 只对同一 plan 文件恢复
- loop controller 逻辑改动后，优先跑 `offline drill` 再叫它稳定
