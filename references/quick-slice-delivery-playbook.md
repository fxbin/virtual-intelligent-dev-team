# Quick Slice Delivery Playbook

Use this playbook when a request is a small implementation, bug fix, or narrow feature slice that is clear enough to build without a full product brief, planning branch, or iteration loop.

## Lead

- Default lead: `Technical Trinity`
- Use `World-Class Product Architect` when the small slice is primarily UI / UX / React.
- Use `Java Virtuoso` when the small slice is Java / Spring / JVM-specific.
- Add `Git Workflow Guardian` only when commit, branch, push, PR, or worktree actions are explicit.

## Default Sequence

1. Clarify only route-changing gaps.
2. For bugs or regressions, establish the feedback loop first using `references/feedback-loop-first-protocol.md`.
3. Record the intent, non-goals, acceptance criteria, and verification command.
4. Create or refresh project context only when durable project rules are missing or stale.
5. Implement the smallest coherent change.
6. Run targeted verification and self-review.
7. Present changed files, evidence, and any residual risk.

## Required Outputs

- quick slice brief
- delivery status
- acceptance criteria
- verification evidence
- feedback loop evidence when the slice is a bug or regression
- residual risk or follow-up

## Guardrails

- Do not expand a quick slice into a full product brief.
- Do not use this path for rewrites, migrations, high-risk refactors, repeated failures, or release readiness decisions.
- Do not skip the Harness constraint gate when code implementation begins.
- Do not patch a bug without a repro, trace, test, fixture, or explicitly stated blocker.
- If the request becomes multi-round, switch to bounded iteration.
- If the request becomes product-definition heavy, switch to `product-delivery-playbook.md`.
- If the request becomes governance or rollback heavy, switch to `technical-governance-playbook.md`.

## Resume Anchors

- `.vidt/delivery/current-slice.md`
- `.vidt/delivery/status.yaml`
- `.vidt/context/project-context.md`
