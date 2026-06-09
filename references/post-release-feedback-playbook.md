# Post-Release Feedback Playbook

Use this playbook when the version has already shipped and the team needs a structured loop for telemetry, dogfood, support, and real-user feedback.

## Lead

- Default lead: `World-Class Product Architect`
- Common assistant: `Technical Trinity`
- Add `Sentinel Architect (NB)` when production-impacting regressions, telemetry incidents, or governance escalation are explicit.

## Default sequence

1. Bootstrap a dedicated post-release workspace instead of mixing shipped feedback into beta artifacts.
2. Keep one machine-readable signal report for the current observation window.
3. Preserve a markdown feedback ledger that maps each signal cluster back to source, severity, area, owner, and evidence.
4. Evaluate the current signal report into one of three outcomes:
   - `monitor`
   - `iterate`
   - `escalate`
5. If the report has unresolved feedback but remains in `monitor` for `report_context.monitor_window_count >= report_context.monitor_escalation_threshold`, escalate the stalled monitor loop into governance instead of watching indefinitely.
6. When the outcome is `iterate` or `escalate`, emit a bounded remediation brief instead of leaving the feedback as an unstructured note dump.
7. Sync shipped feedback back into product-delivery anchors so the next slice and acceptance criteria absorb real-world evidence.
8. Sync governance writebacks when the shipped version reveals release-process, rollback, incident-response gaps, or stale monitor loops.
9. Reopen bounded iteration only when the shipped evidence justifies a new corrective slice.

## Required outputs

- post-release rollout summary
- machine-readable post-release signal report
- post-release feedback ledger
- post-release triage summary
- machine-readable post-release decision result
- next iteration brief when the result is `iterate` or `escalate`
- product writeback for shipped feedback
- governance writeback when release control or production risk must change

## Guardrails

- Do not flatten telemetry, support, community, and dogfood into one vague “feedback” bucket.
- Do not reopen bounded iteration without a machine-readable signal report.
- Do not treat “some users complained” as enough evidence; severity, area, and affected-user context should stay attached.
- Do not discard the release closure context; post-release feedback should stay linked to the shipped release label and release gate artifacts.
- Do not let shipped feedback bypass product or governance writeback when a real remediation loop is opened.
- Do not keep returning `monitor` once unresolved feedback has crossed the explicit monitor-window threshold.
