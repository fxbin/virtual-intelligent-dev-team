# Post-Release Feedback Playbook

Use this playbook when the version has already shipped and the team needs a structured loop for telemetry, dogfood, support, real-user feedback, production hotfixes, and project-truth writeback.

## Lead

- Default lead: `World-Class Product Architect`
- Common assistant: `Technical Trinity`
- Add `Sentinel Architect (NB)` when production-impacting regressions, telemetry incidents, remote-control-plane drift, or governance escalation are explicit.

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
7. For a bounded production regression discovered after a valid release closure, prefer a dedicated hotfix Issue/branch and keep the original release closure intact. Apply the relevant targeted checks plus the release QA that protects the affected invariant.
8. If the shipped issue invalidates the release-level contract broadly, or proves the original release was never actually complete, escalate instead of pretending it is a routine hotfix.
9. Sync shipped feedback back into product-delivery anchors so the next slice and acceptance criteria absorb real-world evidence.
10. Sync governance writebacks when the shipped version reveals release-process, rollback, incident-response, external-system preflight, or stale monitor-loop gaps.
11. Run `project-truth-reconciliation-protocol.md` after a material release/hotfix/phase transition when roadmap, Issues, resource identifiers, migration names, commands, or current gates may have drifted.
12. Reopen bounded iteration only when the shipped evidence justifies a new corrective slice.

## Hotfix rule

A post-release bug should not automatically reopen the full release train.

Default bounded path:

```text
production signal
→ dedicated bug Issue
→ fix/<issue>
→ targeted verification
→ relevant release/regression QA
→ PR to default branch
→ production verification
→ truth writeback if an invariant changed
```

Preserve the original release label/closure and link the hotfix back to it.

Reopen/escalate the broader release only when the defect shows that:

- required production evidence was falsely considered complete;
- a release-wide invariant is invalid;
- rollback/recovery cannot remain bounded;
- multiple surfaces share the same root cause and require coordinated remediation.

## Project-truth reconciliation

Post-release state is not complete merely because production is healthy. Before the next broad planning cycle, reconcile:

```text
runtime truth
repository/default-branch truth
Issue/PR truth
roadmap/decision truth
external resource identifiers
```

Typical drift found in real delivery includes:

- child Issues still open after a release branch integration;
- stale prerequisites that conflict with the current Master/Roadmap decision;
- old project/resource IDs still present in docs or PR descriptions;
- migration filenames/version IDs that no longer match remote history;
- a new Product Gate decision not reflected in older Issues.

Use [project-truth-reconciliation-protocol.md](./project-truth-reconciliation-protocol.md) rather than fixing these ad hoc.

## Required outputs

- post-release rollout summary
- machine-readable post-release signal report
- post-release feedback ledger
- post-release triage summary
- machine-readable post-release decision result
- next iteration brief when the result is `iterate` or `escalate`
- product writeback for shipped feedback
- governance writeback when release control or production risk must change
- hotfix link/evidence when a bounded production regression is repaired
- project-truth reconciliation result when release/phase drift is plausible

## Guardrails

- Do not flatten telemetry, support, community, and dogfood into one vague “feedback” bucket.
- Do not reopen bounded iteration without a machine-readable signal report.
- Do not treat “some users complained” as enough evidence; severity, area, and affected-user context should stay attached.
- Do not discard the release closure context; post-release feedback should stay linked to the shipped release label and release gate artifacts.
- Do not let shipped feedback bypass product or governance writeback when a real remediation loop is opened.
- Do not keep returning `monitor` once unresolved feedback has crossed the explicit monitor-window threshold.
- Do not turn a bounded UI/content regression into a full release reopen without evidence that release-level closure is invalid.
- Do not start a new broad Epic from contradictory roadmap/Issue/resource truth; reconcile first.
