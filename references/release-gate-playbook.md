# Release Gate Playbook

Use this playbook when the question is no longer “does the skill benchmark pass?” but “is this version ready to treat as a release candidate?”

## Default Command

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --pretty
```

Default behavior:

- if `.vidt/beta/round-decisions/` exists, the gate automatically enforces the latest `beta-round-gate-result.json`
- if no beta gate result exists but `.vidt/beta/reports/` exists, the gate evaluates the latest valid beta round report
- if `.vidt/beta/` exists but no gate result or valid report can be found, release is `hold` until beta evidence is produced

如果完成证据不在默认路径：

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --completion-evidence .vidt/evidence/release/completion-evidence.json --pretty
```

当发布判断必须显式指定 beta round gate 目录时：

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --beta-decision-dir .vidt/beta/round-decisions --pretty
```

如果目前只有 beta round report，且要显式指定 report 目录：

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --beta-report-dir .vidt/beta/reports --pretty
```

When you want the release gate to close the loop into the iteration workspace automatically:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .vidt/iterations --release-label release-ready --pretty
```

When you want `hold` to bootstrap and immediately execute the next bounded iteration loop:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .vidt/iterations --auto-run-next-iteration-on-hold --hold-loop-max-rounds 3 --pretty
```

## What The Gate Requires

- unit tests pass
- semantic regression validation passes
- eval prompt suite passes
- real offline loop drill passes
- if staged beta validation is in scope or `.vidt/beta/` exists, the latest beta round gate must be `advance`
- structured completion evidence exists, passes `references/completion-evidence.schema.json`, has result `passed`, confidence `A | B`, leaves no uncovered scope or residual risk, and includes `evidence_refs` with at least one verifiable command or existing local artifact path

## Why This Is Separate From Benchmark

The benchmark gate should stay useful for fast iteration.

The release gate is stricter:

- it always includes the real offline loop drill
- it requires structured completion evidence before `ship`, so benchmark green alone cannot become a completion claim
- it emits a ship-or-hold decision
- it writes dedicated release gate artifacts
- it can consume the latest beta round gate result automatically and block ship when beta is still `hold`, `escalate`, or missing
- when a beta remediation brief exists, it should carry the same blockers, evidence requirements, rerun commands, and resume artifacts into the release `hold` follow-up
- when the decision is `ship`, it should bootstrap the post-release feedback workspace so shipped evidence has a formal return path
- when beta is blocking ship, the hold brief should preserve persona / scenario blocker slices so remediation is not generic
- the offline loop drill should also keep exercising the `hold -> bootstrap -> auto-run` path so this closure does not regress silently

## Outputs

- `release-gate-results.json`
- `release-gate-report.md`
- benchmark JSON and markdown artifacts
- offline drill markdown report
- latest beta gate JSON and markdown artifacts when beta enforcement is enabled
- latest beta remediation brief JSON and markdown artifacts when the latest beta gate reopened a loop
- `next-iteration-brief.json` and markdown when the result is `hold`
- `release-closure.json` and markdown when the result is `ship`
- post-release bootstrap artifacts when the result is `ship`
- `iteration-plan.release-gate.json`, `open-loops.md`, and `iteration-context-chain.md` when `hold` bootstraps an iteration workspace
- git-detached `repo-copy` plus blocker-specific remediation and target artifacts under `artifacts/release-gate-hold/` inside the copied repo when `hold` seeds the next self-mutation chain

## Decision Rule

- `ship`
  - all benchmark checks and offline drill checks passed
  - if beta evidence is enabled or `.vidt/beta/` exists, the latest beta round gate is `advance`
  - completion evidence is complete and supports the release claim, including verifiable `evidence_refs`
  - if an iteration workspace is provided, the gate can archive a reusable release-ready baseline and sync distilled patterns
  - the gate should also bootstrap `.vidt/post-release/` so telemetry and real-user feedback can reopen the next loop without inventing a new structure later
- `hold`
  - any gate failed
  - beta `hold`, `escalate`, or missing beta gate evidence is a first-class release blocker, even when benchmark evidence is green
  - missing, invalid, partial, failed, or risky completion evidence is a first-class release blocker, even when benchmark and beta gates are green
  - the gate should emit a next-iteration brief that states blockers, objective hints, evidence requirements, persona / scenario blocker slices when beta evidence exists, and the recommended rerun path back into bounded iteration
  - if the latest beta gate already emitted a remediation brief, the release `hold` brief should inherit its required evidence, recommended commands, and resume artifacts instead of recomputing a generic retry path
  - if an iteration workspace is provided, the gate can bootstrap a runnable iteration plan, a blocker-specific mutation catalog, and a copied candidate repo, then optionally execute it immediately
