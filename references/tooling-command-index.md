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

## 三、产品交付资产

模板：

- `assets/product-delivery-brief-template.md`
- `assets/product-contract-questions-template.md`
- `references/product-delivery-playbook.md`

常用初始化命令：

```bash
python scripts/init_product_delivery.py --root . --pretty
```

## 四、内测验证资产

模板：

- `assets/beta-program-overview-template.md`
- `assets/beta-cohort-matrix-template.md`
- `assets/beta-feedback-ledger-template.md`
- `assets/simulated-user-profile-template.json`
- `assets/beta-simulation-config-template.json`
- `assets/beta-round-report-template.json`
- `references/beta-validation-playbook.md`
- `references/simulated-user-profile.schema.json`
- `references/beta-simulation-config.schema.json`
- `references/beta-simulation-event.schema.json`
- `references/beta-simulation-run.schema.json`
- `references/beta-round-report.schema.json`
- `references/beta-round-gate-result.schema.json`

常用初始化命令：

```bash
python scripts/init_beta_validation.py --root . --pretty
```

```bash
python scripts/init_beta_simulation.py --root . --round-id round-0 --phase "pre-build concept smoke" --objective "<objective>" --pretty
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

## 五、技术治理资产

模板：

- `assets/technical-governance-change-plan-template.md`
- `assets/technical-governance-release-checklist-template.md`
- `references/technical-governance-playbook.md`

常用初始化命令：

```bash
python scripts/init_technical_governance.py --root . --pretty
```

## 六、bounded iteration 资产

模板：

- `assets/iteration-ledger-template.md`
- `assets/round-reflection-template.md`
- `assets/round-memory-template.md`
- `assets/self-feedback-template.md`
- `assets/distilled-patterns-template.md`
- `assets/iteration-plan-template.json`
- `references/project-memory-lite.md`

## 六点五、project memory lite

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

## 七、iteration 命令

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

## 七、release / drill / compare

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

- benchmark eval runner 支持：
  - `route`
  - `verify_action`
  - `release_gate`

- benchmark compare

```bash
python scripts/compare_benchmark_results.py --baseline <baseline-report> --candidate <candidate-report> --pretty
```

## 六、promotion / sync / materialize

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

## 七、使用原则

- 高风险、多阶段、多人协作前，先用 `verify_action.py` 确认 process skill / lead assignment / release gate / iteration 是否真的该开
- 如果路由返回了 `product-spec-deliver`、`beta-feedback-ramp` 或 `govern-change-safely`，再额外跑一次 `bundle-bootstrap`，确认起盘动作和恢复锚点没有漂移
- 需要跨会话恢复时，优先只推荐一个主锚点，再补最多两个 supporting artifacts
- 改了路由、索引、playbook、脚本命令后，先跑 `lint_virtual_team_contract.py`，再跑 `validate_virtual_team.py`
- 开发前规划分支只在大改造、迁移、重写、先规划后开发时启用
- iteration 深循环时，先开本索引，再补对应 playbook
- `run_release_gate.py` 优先用于 `ship / hold` 判断，不用 benchmark 结果硬代替
- `run_iteration_loop.py --resume` 只对同一 plan 文件恢复
- loop controller 逻辑改动后，优先跑 `offline drill` 再叫它稳定
