# Response Pack Sidecar Schema

版本：`response-pack-sidecar/v1`

这份文档定义 `generate_response_pack.py` 在写出 Markdown 时同步生成的 JSON sidecar 结构。
可执行 schema 见：`references/response-pack-sidecar.schema.json`

目标：

- 让下游脚本直接消费结构化输出，而不是反向解析 Markdown
- 保持 `response_pack / verify_action / release_gate` 三条输出链的解释层一致
- 给后续 benchmark、automation、workspace bootstrap 提供稳定接口

## 顶层字段

- `schema_version`
  - 当前固定为 `response-pack-sidecar/v1`
- `language`
  - `en | zh`
- `template`
  - `default | review | planning | release | iteration`
- `team_dispatch`
- `execution_result`
- `evidence`
- `next_action`
- `resume`
- `git_workflow`
- `governance`
- 可选：`planning_pack`
- 可选：`optimization_loop`

## `team_dispatch`

- `lead_agent`
- `assistant_agents`
- `workflow_bundle`
- `bundle_confidence`
- `workflow_bundle_source`
- `route_reason`
- `workflow_source_explanation`

## `execution_result`

- `key_conclusion`
- `key_decision`
- `main_risks`

## `evidence`

- `route_evidence`
- `workflow_source_explanation`
- `process_skills`
- `assistant_delta_contract`

`assistant_delta_contract`:

- `enabled`
- `summary`

## `next_action`

- `smallest_executable_action`
- `current_owner`

## `resume`

- `progress_anchor`
- `resume_artifacts`

## `git_workflow`

- `using_git_worktrees`
- `git_workflow`
- `suggested_branch`
- `suggested_commit`
- `suggested_pr_title`

## `governance`

- `roundtable_enabled`
- `selected_track`
- `risk_level`
- `dual_sign_required`

## 可选块

`planning_pack`:

- `recommended_anchor`
- `workflow_steps`

`optimization_loop`:

- `round_cap_online`
- `round_cap_offline`
- `allowed_decisions`
- `resume_anchor`

## 兼容性规则

- 新增字段：
  - 允许向后兼容新增
- 重命名或删除字段：
  - 必须升级 `schema_version`
- 若 `schema_version` 变化：
  - 同步更新 `tooling-command-index.md`
  - 同步更新相关 benchmark / tests
  - 同步更新 `references/response-pack-sidecar.schema.json`

## 执行约束

- `generate_response_pack.py` 在写 sidecar 前会先跑 schema 校验
- `lint_virtual_team_contract.py` 会校验：
  - 文档版本
  - `.schema.json`
  - helper 常量
  - 代表性 payload 的 schema 通过性
