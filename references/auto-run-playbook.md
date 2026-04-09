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
- 明确 stop cap、resume anchor、go command、安全护栏

### `go`

目标：

- 读取 setup 生成的 plan
- 按 workflow 分派到底层脚本
- 输出统一结果、恢复锚点和下一步

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

## 6. 常用命令

```bash
python scripts/run_auto_workflow.py --text "<original-request-without-/auto>" --mode setup --pretty
```

```bash
python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty
```
