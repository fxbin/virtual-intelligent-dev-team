# Response Pack Sidecar Schema

版本：`response-pack-sidecar/v1`

这份文档定义 `generate_response_pack.py` 在写出 Markdown 时同步生成的 JSON sidecar 结构。
可执行 schema 见：`references/response-pack-sidecar.schema.json`

目标：

- 让下游脚本直接消费结构化输出，而不是反向解析 Markdown
- 保持 `response_pack / verify_action / release_gate` 三条输出链的解释层一致
- 给后续 benchmark、automation、workspace bootstrap 与 automation resume 提供稳定接口

## 顶层字段

- `schema_version`
  - 当前固定为 `response-pack-sidecar/v1`
- `language`
  - `en | zh`
- `template`
  - `default | review | planning | release | iteration | beta | product | governance`
- `team_dispatch`
- `execution_result`
- `evidence`
- `micro_practices`
- `stage_councils`
- 可选：`intent_confirmation`
- 可选：`scope_boundary`
- `next_action`
- `resume`
- `git_workflow`
- `governance`
- 可选：`beta_program`
- 可选：`bundle_bootstrap`
- 可选：`engineering_constraints`
- 可选：`team_engine`
- 可选：`external_agent_backend`
- 可选：`real_subagent_runtime`
- 可选：`planning_pack`
- 可选：`optimization_loop`
- 可选：`auto_run`
- 可选：`automation_resume`

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

## `micro_practices`

- `names`
- `items`
- `ledger`

`items[]`:

- `name`
- `reference`
- `reason`
- `evidence`

`ledger`:

- `required`
- `command`
- `update_command`
- `evaluation_command`
- `resume_anchor`
- `schema`
- `evaluation_schema`

## `stage_councils`

- `enabled`
- `reference`
- `template`
- `workflow_bundle`
- `activation_rule`
- `explicit_team_request`
- `active_councils`
- `councils`
- `fallback`

`councils[]`:

- `name`
- `lead`
- `activation_reason`
- `roles`
- `sequence`
- `quality_gates`
- `output_artifacts`
- `resume_anchor`

`roles[]`:

- `role`
- `owns`

## `intent_confirmation`

仅在模糊猜想、低信息量请求，或不同切入方向会改变 lead / workflow bundle / stage council 时出现。

- `required`
- `reason`
- `question`
- `option_ids`
- `options`
- `provisional_route`
- `fuzzy_markers`
- `detected_categories`
- `route_choice_markers`

`options[]`:

- `id`
- `label`
- `description`
- `target_lead`
- `target_bundle`
- `target_council`

`provisional_route`:

- `lead_agent`
- `workflow_bundle`
- `bundle_confidence`
- `workflow_bundle_source`

## `scope_boundary`

用于阻断跨 skill 误路由，或标记软件任务信息不足：

- `status`: `in_scope | out_of_scope | insufficient_information`
- `reason`
- `recommended_skill`
- `next_step`

当 `status=out_of_scope` 时，Response Pack 必须使用 `decline-and-reroute`，不得保留 Team Engine、真实 subagent 或交付起盘声明。

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

## `bundle_bootstrap`

- `required`
- `reference`
- `commands`
- `artifacts`
- `resume_anchor`

## `engineering_constraints`

- `required`
- `reference`
- `artifact`
- `command`
- `verification_check`

## `team_engine`

- `required`
- `reference`
- `cycle_reference`
- `workflow_bundle`
- `lead_role`
- `worker_role`
- `verifier_role`
- `max_cycles`
- `acceptance_gates`
- `producer_can_self_pass`
- `leader_accept_requires_cycle_report`
- `verifier_fail_requires_remediation_patch`
- `runtime_claim`
- `team_engine_closure_verdict`
- `reason`

## `external_agent_backend`

- `enabled`
- `reference`
- `orchestration_mode`
- `runtime_claim`
- `backend_orchestration_verdict`
- `team_engine_closure_verdict`
- `required_outputs`
- `boundary_note`

## `real_subagent_runtime`

- `eligible`
- `reference`
- `runtime_claim`
- `candidate_runtime_claim`
- `candidate_multi_session_claim`
- `runtime_evidence_required`
- `runtime_evidence`
- `runtime_downgraded_from`
- `runtime_downgrade_reason`
- `activation_reason`
- `workflow_bundle`
- `max_subagents`
- `tier_selection_algorithm`
- `tier_selection_function`
- `session_circuit_breaker`
- `spawn_policy`
- `agents`
- `merge_policy`
- `fallback`

`runtime_evidence` records all six atomic capabilities, the derived
`real_chain_ready` / `session_chain_ready` decisions, the candidate ceiling,
and the smoke-test result. A single `spawn` or `create_session` flag is not
sufficient evidence for a higher tier.

`fallback` includes `unavailable_runtime`, `multi_session_unavailable`,
`malformed_output`, `role_boundary_violation`, and `session_killed`.

`spawn_policy`:

- `user_explicit_or_auto_required`
- `no_default_swarm`
- `blocking_work_stays_local`
- `parallel_tasks_must_be_independent`
- `code_workers_need_disjoint_write_scopes`

`agents[]`:

- `role`
- `task`
- `write_scope`
- `context_policy`
- `output_contract`
- `can_write_artifact`
- `can_write_verdict`
- `mapped_role`

## `beta_program`

- `simulation_allowed`
- `feedback_anchor`
- `cohort_artifact`
- `cohort_plan_template`
- `cohort_plan_schema`
- `cohort_plan_path`
- `ramp_plan_template`
- `ramp_plan_schema`
- `ramp_plan_path`
- `simulation_profile_template`
- `simulation_profile_dir`
- `simulation_persona_library`
- `simulation_cohort_fixtures`
- `simulation_config_template`
- `simulation_config_dir`
- `simulation_scenario_packs`
- `simulation_trace_catalog`
- `simulation_preview_dir`
- `simulation_diff_dir`
- `simulation_run_dir`
- `simulation_init_command_template`
- `simulation_preview_command_template`
- `simulation_diff_command_template`
- `simulation_run_command_template`
- `simulation_summary_command_template`
- `report_template`
- `report_dir`
- `decision_dir`
- `gate_command_template`
- `rounds`

`rounds[]`:

- `round_id`
- `phase`
- `sample_size`
- `participant_mode`
- `archetypes`
- `goal`
- `exit_criteria`

## 可选块

`planning_pack`:

- `recommended_anchor`
- `workflow_steps`

`optimization_loop`:

- `round_cap_online`
- `round_cap_offline`
- `allowed_decisions`
- `resume_anchor`

`auto_run`:

- `enabled`
- `trigger`
- `requested_phase`
- `execution_mode`
- `run_style`
- `safety_level`
- `resume_requested`
- `detached_ready`
- `workflow_bundle`
- `workflow_supported`
- `requires_explicit_go`
- `eligible_workflows`
- `setup_command`
- `go_command`
- `resume_anchor`
- `state_root`
- `state_dir`
- `plan_json`
- `plan_markdown`
- `automation_state_schema`
- `safety_guards`
- `eligibility_reason`

`automation_resume`:

- `enabled`
- `resume_strategy`
- `state_resume_available`
- `selected_state_path`
- `selection_mode`
- `decision_id`
- `decision_label`
- `decision_reason`
- `recommended_command`
- `resume_anchor`
- `playbooks`
- `blocking_conditions`
- `command_allowed`
- `dry_run_command`
- `execute_command`
- `error`

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
- 稳定区块现在默认拒绝未声明字段
  - 先收紧顶层与 `team_dispatch / execution_result / evidence / next_action / resume / git_workflow / governance`
