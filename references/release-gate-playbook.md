# Release Gate Playbook

Use this playbook when the question is no longer “does the skill benchmark pass?” but “is this version ready to treat as a release candidate?”

## Default Command

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --pretty
```

## What The Gate Requires

- unit tests pass
- semantic regression validation passes
- eval prompt suite passes
- real offline loop drill passes

## Why This Is Separate From Benchmark

The benchmark gate should stay useful for fast iteration.

The release gate is stricter:

- it always includes the real offline loop drill
- it emits a ship-or-hold decision
- it writes dedicated release gate artifacts

## Outputs

- `release-gate-results.json`
- `release-gate-report.md`
- benchmark JSON and markdown artifacts
- offline drill markdown report

## Decision Rule

- `ship`
  - all benchmark checks and offline drill checks passed
- `hold`
  - any gate failed
