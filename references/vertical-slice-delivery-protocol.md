# Vertical Slice Delivery Protocol

Use this micro-practice when planning, product delivery, or implementation work
must be split into independently verifiable chunks.

## Goal

Prefer thin tracer bullets over horizontal layer plans. Each slice should prove a
complete path through the system and leave evidence a verifier can check.

## Slice Rules

A valid vertical slice:

- delivers one narrow end-to-end behavior
- crosses all required layers for that behavior
- is demoable or testable on its own
- has explicit acceptance criteria
- has named dependencies
- avoids speculative work for future slices

Avoid horizontal slices such as "create schema", "build API", "build UI" unless
the slice is intentionally a technical prerequisite with no user-visible path
available yet.

## AFK / HITL Split

Classify each slice:

- `AFK`
  - Can be implemented and verified by agents from existing context.
- `HITL`
  - Requires user/domain decision, design review, access, credentials, or
    irreversible trade-off approval.

Prefer AFK slices when possible, but do not hide a real human decision inside an
AFK ticket.

## Slice Shape

```markdown
## Slice: <name>

- Type: AFK | HITL
- Behavior:
- Blocked by:
- Interfaces touched:
- Acceptance criteria:
- Verification evidence:
- Non-goals:
```

## Integration With Existing Bundles

- `plan-first-build`
  - Use vertical slices in `docs/plan/task-breakdown.md`.
- `product-spec-deliver`
  - Use vertical slices when turning a product brief into a buildable slice.
- `quick-slice-deliver`
  - Keep one active slice; split only when the request no longer fits one
    verifiable behavior.
- `root-cause-remediate`
  - Convert the proven fix path into the smallest regression slice after the
    root cause is validated.

## Completion Evidence

When active, completion should name:

- slice names and `AFK` / `HITL` classifications
- dependencies
- acceptance criteria
- verification evidence for each slice
- any deliberately deferred horizontal prerequisite
