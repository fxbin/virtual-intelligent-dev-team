# Release Gate Playbook

Use this playbook when the question is no longer “does the skill benchmark pass?” but “is this version ready to treat as a release candidate?”

## Default Command

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --pretty
```

当发布判断必须受最近一轮 beta round gate 约束时：

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --beta-decision-dir .skill-beta/round-decisions --pretty
```

如果目前只有 beta round report，还没有提前产出 gate 结果：

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --beta-report-dir .skill-beta/reports --pretty
```

When you want the release gate to close the loop into the iteration workspace automatically:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --release-label release-ready --pretty
```

When you want `hold` to bootstrap and immediately execute the next bounded iteration loop:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --auto-run-next-iteration-on-hold --hold-loop-max-rounds 3 --pretty
```

## What The Gate Requires

- unit tests pass
- semantic regression validation passes
- eval prompt suite passes
- real offline loop drill passes
- if staged beta validation is in scope, the latest beta round gate must be `advance`

## Why This Is Separate From Benchmark

The benchmark gate should stay useful for fast iteration.

The release gate is stricter:

- it always includes the real offline loop drill
- it emits a ship-or-hold decision
- it writes dedicated release gate artifacts
- it can consume the latest beta round gate result and block ship when beta is still `hold` or `escalate`
- the offline loop drill should also keep exercising the `hold -> bootstrap -> auto-run` path so this closure does not regress silently

## Outputs

- `release-gate-results.json`
- `release-gate-report.md`
- benchmark JSON and markdown artifacts
- offline drill markdown report
- latest beta gate JSON and markdown artifacts when beta enforcement is enabled
- `next-iteration-brief.json` and markdown when the result is `hold`
- `release-closure.json` and markdown when the result is `ship`
- `iteration-plan.release-gate.json`, `open-loops.md`, and `iteration-context-chain.md` when `hold` bootstraps an iteration workspace
- git-detached `repo-copy` plus blocker-specific remediation and target artifacts under `artifacts/release-gate-hold/` inside the copied repo when `hold` seeds the next self-mutation chain

## Decision Rule

- `ship`
  - all benchmark checks and offline drill checks passed
  - if beta evidence is enabled, the latest beta round gate is `advance`
  - if an iteration workspace is provided, the gate can archive a reusable release-ready baseline and sync distilled patterns
- `hold`
  - any gate failed
  - beta `hold` or `escalate` is a first-class release blocker, even when benchmark evidence is green
  - the gate should emit a next-iteration brief that states blockers, objective hints, evidence requirements, and the recommended rerun path back into bounded iteration
  - if an iteration workspace is provided, the gate can bootstrap a runnable iteration plan, a blocker-specific mutation catalog, and a copied candidate repo, then optionally execute it immediately
