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

## Guardrail

Keep the drill artifacts local and disposable. They are process evidence, not skill content.
