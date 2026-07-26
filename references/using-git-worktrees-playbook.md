# Using Git Worktrees Playbook

作者：fxbin  
版本：v1.0  
更新日期：2026-03-04

## 目标

在同一仓库下并行处理多任务，避免频繁切分支造成上下文污染。

## 触发条件

- 同时推进 2 个及以上需求
- 需求开发与 hotfix 并行
- 需要稳定分离实验分支和主线分支

## 标准步骤

1. 在主仓库确认基线分支（如 `main` 或 `develop`）是最新状态。
2. 为每个任务创建独立 worktree 目录和分支。
3. 在对应 worktree 内独立开发、提交、推送。
4. 任务完成后按统一 PR 流程合并。
5. 合并后清理已完成任务的 worktree。

## 命令模板

```bash
git worktree list
git worktree add ../wt-feature-a -b feature/a main
git worktree add ../wt-hotfix-xxx -b hotfix/xxx main
git worktree remove ../wt-feature-a
git worktree prune
```

## 命名约定

- worktree 目录：`wt-<branch>`
- 分支名：
  - 功能：`feature/<name>`
  - 修复：`fix/<name>` 或 `hotfix/<name>`
  - 重构：`refactor/<name>`

## 风险控制

- 不在错误 worktree 提交代码。
- 删除 worktree 前确认已推送或已合并。
- 避免在同一个文件上并行大改，降低冲突成本。

## 状态目录归属

worktree 只放代码改动和一次性执行产物；所有 `.vidt/` 状态目录留在主仓库根（state-root），不跟随 worktree。这样状态目录在 worktree 创建、清理、并行运行时都不会丢失或分裂，跨 worktree 的角色交接也天然成立。

完整归属表与路径约定见 [worktree-state-placement-protocol.md](./worktree-state-placement-protocol.md)。关键提醒：

- 在 worktree 内调用 `init_harness_constraints.py` 等脚本时，`--root` 必须指向主仓，而不是 worktree 的 `.` 默认值：

  ```bash
  STATE_ROOT="$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)"
  python scripts/init_harness_constraints.py --root "$STATE_ROOT" --summary "<task>" --pretty
  ```

- 只有 iteration 的 candidate 产物（`.tmp-iteration-round-XX/`、`patches/*.patch`、materialize 落点）跟随 worktree，其余状态一律回主仓。
- 多 agent 各占一个 worktree 时，`.vidt/handoff/` 交接文件放主仓，各 worktree 内的 agent 都向同一个 state-root 读写。
