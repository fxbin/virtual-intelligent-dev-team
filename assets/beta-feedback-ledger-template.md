# Beta Feedback Ledger

| Round | User archetype | Scenario | Signal | Severity | Proposed action | Status |
| --- | --- | --- | --- | --- | --- | --- |
| round-0 | first-time novice | first-run journey | onboarding copy is unclear | P1 | rewrite promise and entry cues | open |
| round-1 | daily operator | repeated core task | step 3 creates friction | P1 | shorten form and clarify progress state | open |
| round-2 | edge-case breaker | interrupted flow | saved state does not recover cleanly | P0 | fix persistence and add regression test | open |

## Severity Rules

- `P0`: blocks completion or creates a trust-breaking failure
- `P1`: major friction that materially harms the target task
- `P2`: real issue but tolerable for the current beta round
- `P3`: polish or follow-up signal
