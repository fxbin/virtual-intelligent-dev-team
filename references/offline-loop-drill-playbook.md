# Offline Loop Drill Playbook

Use this playbook when you want more than unit tests and benchmark summaries.

## Goal

Prove that the bounded self-optimization loop works end to end in real files and real loop state:

- `rollback`
- `keep`
- auto `pivot`
- `resume`
- release gate `hold -> bootstrap -> auto-run`

## Default Drill Entrypoint

```bash
python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty
```

The drill creates temporary candidate repos and workspaces, runs real loop controllers, and writes a markdown report.

## Covered Scenarios

### 1. Rollback Then Keep

What it proves:

- built-in mutation materialization can produce patch artifacts
- `run_iteration_loop.py` can drive explicit multi-round candidates
- rollback can reverse a regressing patch
- keep can promote the next accepted baseline
- open loops move from active to resolved

### 2. Pivot Then Resume

What it proves:

- autonomous candidate generation can continue after an initial failed round
- same-hypothesis retry budget can block an exhausted idea
- auto pivot can switch to the next bottleneck
- interrupted offline loops can resume safely from persisted state

### 3. Release Gate Hold Bootstrap

What it proves:

- the formal release gate can enter `hold` deterministically
- `hold` can register a failing baseline and seed a git-detached `repo-copy`
- blocker-specific mutation catalog entries are written before the next loop starts
- blocker-specific remediation and target artifacts are materialized into the copied repo
- `--auto-run-next-iteration-on-hold` can immediately converge into the next bounded round

## Success Criteria

Treat the drill as passing only if:

- scenario 1 decisions are `rollback -> keep`
- scenario 2 decisions are `rollback -> keep`
- scenario 2 records one pivot
- scenario 2 resumes from persisted state instead of restarting
- scenario 3 reaches `hold`, bootstraps the copied repo, and auto-runs one `keep` round
- the markdown drill report is written successfully

## When To Run

Run this before calling the loop “closed enough” after changes to:

- iteration orchestration
- baseline promotion
- mutation materialization
- rollback behavior
- resume logic
- pivot logic
- release gate hold bootstrap logic

## 六层与交付子图 Drill 场景(P1-6 扩展)

现有场景覆盖层 4(Iteration)和层 5(Release)。以下场景扩展到六层闭环与 Team Engine Lite 子图:

### 4. Routing 返回错误 Lead

What it proves:

- Routing 层(层 2)在收到不匹配的任务信号时能被检测到
- circuit breaker 的 routing 层能记录失败
- 降级到 Direct Answer 的路径可观测

### 5. Verifier 永远 Pass(模拟失灵)

What it proves:

- Delivery closure(层 3)内 Team Engine Lite 子图的 Verifier 失灵能被 circuit breaker 检测
- 连续 N 次假 pass 后 breaker open
- escalation 队列文件有记录

### 6. Baseline 被删

What it proves:

- Iteration 层(层 4)在 baseline 丢失时能 stop the cycle
- 不会静默继续执行

### 7. JSON Corrupt

What it proves:

- benchmark JSON 损坏时 Iteration 层能 stop the cycle
- 不会把损坏数据当作结果

### 8. Resume/Plan Drift

What it proves:

- resume state 与 plan content 不一致时能被检测
- 不会基于过时的 plan 继续 resume

### 9. Contract Mismatch

What it proves:

- 前后端接口不对齐时 Delivery 层(层 3)的 contract check 能拦截
- 不会在不一致的基础上继续开发

### 10. Release Gate 假 Ship

What it proves:

- Release 层(层 5)在 gate 返回 ship 但证据缺失时能 hold
- 不会基于虚假证据发布

## 扩展成功标准

在原有成功标准基础上,追加:

- 场景 4-10 各自的失败注入能触发对应的降级行为
- circuit breaker 的 escalation 队列有对应记录
- 每个场景的 drill 报告独立可观测

## Guardrail

Keep the drill artifacts local and disposable. They are process evidence, not skill content.
