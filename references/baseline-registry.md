# Baseline Registry

Bounded iteration needs a stable baseline reference before it can judge candidates.

## Purpose

The baseline registry records local benchmark reports that can be reused across rounds.

## Storage

- default workspace: `.vidt/iterations/`
- registry file: `.vidt/iterations/baselines/registry.json`
- stored baseline report: `.vidt/iterations/baselines/<label>/benchmark-results.json`

These are local process artifacts and should not be committed by default.

## Registration Rules

- a baseline label should be stable and human-readable
- registering the same label overwrites the stored report for that label
- every entry should include:
  - label
  - registration time
  - source report path
  - stored report path
  - summary

## Suggested Labels

- `stable`
- `pre-change`
- `candidate-accepted`
- `release-v4.2.0`

## Promotion Rule

Only promote a round into a new baseline when its decision is `keep`.

Recommended flow:

1. run one iteration cycle
2. confirm the round is promotion-eligible
3. promote the kept candidate into a new label
4. decide whether that new label should replace the current stable baseline

## Verification Rule

`verify_action.py --check iteration` treats the registry and every registered `stored_report` as one integrity boundary.

- malformed registry JSON fails closed
- a registry entry whose stored report was deleted or moved fails closed
- callers may pass `--iteration-workspace`; otherwise verification uses `<repo>/.vidt/iterations`

Do not infer that a label is usable merely because it still exists in `registry.json`.
