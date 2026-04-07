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

- 机械契约 lint

```bash
python scripts/lint_virtual_team_contract.py --pretty
```

- Git guardrail

```bash
python scripts/git_workflow_guardrail.py
```

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

## 三、bounded iteration 资产

模板：

- `assets/iteration-ledger-template.md`
- `assets/round-reflection-template.md`
- `assets/round-memory-template.md`
- `assets/self-feedback-template.md`
- `assets/distilled-patterns-template.md`
- `assets/iteration-plan-template.json`
- `references/project-memory-lite.md`

## 三点五、project memory lite

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

## 四、iteration 命令

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

## 五、release / drill / compare

- offline drill

```bash
python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty
```

- release gate

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --pretty
```

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
- 需要跨会话恢复时，优先只推荐一个主锚点，再补最多两个 supporting artifacts
- 改了路由、索引、playbook、脚本命令后，先跑 `lint_virtual_team_contract.py`，再跑 `validate_virtual_team.py`
- 开发前规划分支只在大改造、迁移、重写、先规划后开发时启用
- iteration 深循环时，先开本索引，再补对应 playbook
- `run_release_gate.py` 优先用于 `ship / hold` 判断，不用 benchmark 结果硬代替
- `run_iteration_loop.py --resume` 只对同一 plan 文件恢复
- loop controller 逻辑改动后，优先跑 `offline drill` 再叫它稳定
