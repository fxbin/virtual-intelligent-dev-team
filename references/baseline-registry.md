# Baseline Registry

Bounded iteration needs a stable baseline reference before it can judge candidates.

## Purpose

The baseline registry records local benchmark reports that can be reused across rounds.

## Storage

- default workspace: `.skill-iterations/`
- registry file: `.skill-iterations/baselines/registry.json`
- stored baseline report: `.skill-iterations/baselines/<label>/benchmark-results.json`

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
