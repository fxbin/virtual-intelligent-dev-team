# Evidence Ledger Schema

Every bounded-iteration round should be recorded in a consistent shape.

## Required Fields

| Field | Purpose |
| --- | --- |
| `round_id` | Unique round identifier |
| `objective` | What this round is trying to improve |
| `baseline` | Starting point or previous accepted result |
| `candidate_change` | The exact change being tested |
| `expected_gain` | Why this candidate might help |
| `evidence` | Validator, benchmark, tests, screenshots, or comparable proof |
| `regression_check` | What was checked to prevent silent regressions |
| `decision` | `keep`, `retry`, `rollback`, or `stop` |
| `decision_reason` | Why that decision was made |
| `next_action` | What happens in the next round or at closure |

## Minimal JSON Shape

```json
{
  "round_id": "round-03",
  "objective": "improve routing stability for mixed frontend-plus-git requests",
  "baseline": "v4.1.0 benchmark",
  "candidate_change": "rebalance semantic owner before Git process overlay",
  "expected_gain": "keep product ownership while preserving safe delivery steps",
  "evidence": [
    "python scripts/validate_virtual_team.py --pretty",
    "python scripts/run_benchmarks.py --pretty"
  ],
  "regression_check": [
    "frontend regression cases still pass",
    "git guardrail plan ordering unchanged"
  ],
  "decision": "keep",
  "decision_reason": "new case passes and prior benchmark categories remain stable",
  "next_action": "distill the routing pattern and stop"
}
```

## Evidence Quality Rules

- Prefer machine-checked evidence over narrative claims.
- Compare against a known baseline when possible.
- Record regressions explicitly, not only improvements.
