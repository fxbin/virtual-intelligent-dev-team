# Auto Run Playbook

`/auto` 是 `virtual-intelligent-dev-team` 的显式自动运行协议。

默认仍然是手动模式。只有用户明确输入 `/auto`，才允许进入自动模式。

## 1. 触发原则

- `/auto`
  - 进入 `setup` 阶段
  - 只生成自动执行计划，不直接开跑
- `/auto go`
  - 进入 `go` 阶段
  - 只在已存在 `.skill-auto/auto-run-plan.json` 时允许继续
- `/auto safe`
  - 保持两阶段协议
  - 把 stop cap 收紧到单次安全闭环
- `/auto background`
  - 仍然走同步脚本
  - 但额外写 resumable state，供外层 detached / resume 协议消费
- `/auto resume`
  - 优先复用最近一次 plan / state
  - 不绕过显式 `go`

## 2. 当前白名单

第一轮只开放三条 workflow：

- `root-cause-remediate`
- `ship-hold-remediate`
- `post-release-close-loop`

其他 workflow 即使用户写了 `/auto`，也仍然保持手动模式。

## 3. 两阶段协议

### `setup`

目标：

- 识别 workflow
- 生成 `.skill-auto/auto-run-plan.json`
- 生成 `.skill-auto/auto-run-plan.md`
- 生成 `.skill-auto/state/*.json`
- 明确 stop cap、resume anchor、go command、安全护栏
- 明确 `run_style / safety_level / resume_requested`

### `go`

目标：

- 读取 setup 生成的 plan
- 按 workflow 分派到底层脚本
- 输出统一结果、恢复锚点和下一步
- 写统一 automation state

## 4. workflow 对应底层接线

### `root-cause-remediate`

- 初始化 `.skill-iterations/`
- 生成 `iteration-plan.auto.json`
- 开启：
  - `autonomous_candidate_generation`
  - `auto_pivot_on_stagnation`
- 调用：
  - `scripts/run_iteration_loop.py`

### `ship-hold-remediate`

- 调用：
  - `scripts/run_release_gate.py`
- 默认带：
  - `--auto-run-next-iteration-on-hold`

### `post-release-close-loop`

- 初始化 `.skill-post-release/`
- 调用：
  - `scripts/evaluate_post_release_feedback.py`

## 5. 安全护栏

- 默认仍是 manual mode
- `setup -> go` 必须分离
- 不自动执行 destructive git
- 必须先写 plan，再进入 go
- 结果必须带 resume anchor
- `background` 目前只定义 resumable contract，不启动 daemon
- `safe` 会收紧 release hold 自动 remediation 与 iteration cap

## 6. 常用命令

```bash
python scripts/run_auto_workflow.py --text "<original-request-without-/auto>" --mode setup --pretty
```

```bash
python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty
```

产物补充：

- `.skill-auto/state/*.json`
- `evals/release-gate/automation-state.json`
- `.skill-post-release/decisions/automation-state.json`

恢复检查：

```bash
python scripts/inspect_automation_state.py --repo . --pretty
```

这个入口用来读取最近一次 machine-readable automation state，
并给出当前最合适的恢复命令、恢复锚点，以及状态驱动的 playbook 决策。

如果要把这个决策推进到真正执行：

```bash
python scripts/resume_from_automation_state.py --repo . --pretty
```

```bash
python scripts/resume_from_automation_state.py --repo . --execute --pretty
```

- 默认仍然先 dry-run
- 只有显式 `--execute` 才会执行恢复命令
- 执行前会检查推荐命令是否命中受控 allowlist
- 这个入口不会绕过 `/auto` 的 `setup -> go` 两阶段
