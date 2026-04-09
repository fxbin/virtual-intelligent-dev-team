# Automation Resume Decision Matrix

这份矩阵定义 `inspect_automation_state.py` 如何把 machine-readable automation state 转成可执行恢复决策。

目标不是只输出“最近一次状态文件”，而是直接回答：

- 现在处于哪种恢复场景
- 应该读哪份 playbook
- 下一条最合适的命令是什么
- 当前还卡着哪些阻塞条件

## 1. `auto-run-setup`

- 决策：`resume-explicit-go`
- 含义：setup 已经完成，下一步进入显式 `go`
- 默认命令：
  - `python scripts/run_auto_workflow.py --mode go --plan .skill-auto/auto-run-plan.json --pretty`
- 主要 playbook：
  - `references/auto-run-playbook.md`
  - 如果是根因链路，再加 `references/root-cause-escalation-playbook.md`
  - 如果是发布链路，再加 `references/release-gate-playbook.md`
  - 如果是发布后链路，再加 `references/post-release-feedback-playbook.md`

## 2. `release-gate-result`

### 当 `decision = ship`

- 决策：`release-ship-continue-post-release`
- 含义：发布门禁已通过，下一步进入 post-release feedback
- 优先命令：
  - 使用 `follow_up.post_release_bootstrap.recommended_command`
- 主要 playbook：
  - `references/release-gate-playbook.md`
  - `references/post-release-feedback-playbook.md`

### 当 `decision = hold`

- 决策：`release-hold-reopen-iteration`
- 含义：发布仍被阻塞，下一步回到 bounded iteration / hold brief
- 优先命令：
  - 使用 hold brief 里的第一条 `recommended_commands`
- 主要 playbook：
  - `references/release-gate-playbook.md`
  - `references/iteration-protocol.md`

## 3. `post-release-feedback-result`

### 当 `decision = monitor`

- 决策：`post-release-monitor-continue`
- 含义：继续观察，不重新开 remediation
- 主要 playbook：
  - `references/post-release-feedback-playbook.md`

### 当 `decision = iterate`

- 决策：`post-release-reopen-iteration`
- 含义：真实线上反馈已触发 corrective slice
- 主要 playbook：
  - `references/post-release-feedback-playbook.md`
  - `references/iteration-protocol.md`

### 当 `decision = escalate`

- 决策：`post-release-escalate-governance`
- 含义：问题已经不是单纯产品修补，而是要进入治理升级
- 主要 playbook：
  - `references/post-release-feedback-playbook.md`
  - `references/technical-governance-playbook.md`

## 4. Guardrails

- `inspect_automation_state.py` 优先读 companion result，而不是只看 state 顶层字段
- 没有 companion result 时，才回退为通用恢复命令
- `resume_from_automation_state.py` 只消费 `decision_card.recommended_command`
- 默认先 dry-run，只有显式 `--execute` 才允许真正执行
- 恢复执行必须命中受控 allowlist，不能把任意 shell 命令透传出去
- 决策卡必须同时给出：
  - `decision_id`
  - `decision_label`
  - `decision_reason`
  - `resume_strategy`
  - `recommended_command`
  - `playbooks`
  - `blocking_conditions`
