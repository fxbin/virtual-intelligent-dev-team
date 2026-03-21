# Iteration State Machine

Bounded iteration should follow a fixed local state machine.

## States

## 1. `initialized`

- round workspace exists
- ledger and reflection files exist
- baseline label and objective are locked
- candidate workspace snapshot may be captured before mutation

## 2. `benchmarked`

- candidate benchmark report exists
- report path is recorded
- benchmark failure is treated as evidence, not ignored
- optional apply command or candidate patch has already mutated the candidate workspace when the round requires code changes

## 3. `evaluated`

- candidate is compared against the baseline
- result is translated into one decision

## 4. `closed`

- decision is written to local state
- ledger and reflection are updated
- open loops are refreshed
- kept rounds may be promoted to a new baseline
- distilled patterns may be rebuilt from accepted rounds
- rollback command or reverse patch may run and capture a post-rollback snapshot when regression handling is enabled

## Transition Rules

- `initialized -> benchmarked`
  - only after a candidate report exists
- `benchmarked -> evaluated`
  - only after baseline and candidate can both be read
- `evaluated -> closed`
  - only after a decision is made

## Allowed Decisions

- `keep`
- `retry`
- `rollback`
- `stop`

## Failure Handling

- missing baseline registry: stop the cycle
- missing benchmark report: stop the cycle
- malformed benchmark JSON: stop the cycle
- inconclusive comparison: close with `retry`
