# Root Cause Escalation Playbook

Use this playbook when the user indicates repeated failed attempts, unresolved production behavior, or asks explicitly for root-cause analysis instead of another quick patch.

## Trigger signals

- "still fails"
- "already tried"
- "multiple attempts"
- "stop guessing"
- "inspect the logs"
- "find the root cause"
- production incident or repeated outage language

## Default team shape

- Lead: `Sentinel Architect (NB)`
- Common assistant: `Technical Trinity`
- Optional assistant: `Code Audit Council` when the failure has security or review implications

## Execution rule

Do not jump straight to a patch. Force a root-cause loop first:

1. State the failure symptom and current blast radius.
2. List what has already been tried.
3. Establish the smallest reliable feedback loop using `references/feedback-loop-first-protocol.md`.
4. Identify the missing evidence.
5. Inspect logs, config, runtime state, and recent changes.
6. Form ranked, falsifiable root-cause hypotheses.
7. Pick the smallest validating step.
8. Only after validation, propose the safest fix.

## Stop conditions

- No logs, traces, config, or repro evidence is available.
- No usable feedback loop can be created from tests, scripts, traces, harnesses, or human-captured evidence.
- The next step would be speculative patching.
- The fix would be destructive or irreversible without rollback.
- The user is asking for production changes without enough evidence.

## Expected output shape

- Symptom
- Feedback loop or blocker
- Evidence reviewed
- Most likely root cause
- Confidence level
- Safest next validating step
- Fix path after validation
- Rollback or containment note
