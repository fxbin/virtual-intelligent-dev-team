# Harness Engineering Constraint Protocol

Use this protocol whenever a routed request can lead to code changes.

The rule is simple: create or refresh the constraint file before implementation.
The agent may inspect code first, but it should not start editing production files
until the current engineering constraints are explicit.

## Required Artifact

- `.skill-harness/engineering-constraints.md`

Initialize it with:

```bash
python scripts/init_harness_constraints.py --root . --summary "<task summary>" --pretty
```

## Required Sections

- `Scope`
  - in-scope files, modules, behavior, and user-visible surface
  - out-of-scope work that must not be pulled into the current change
- `Non-Negotiable Constraints`
  - compatibility, API, data, security, performance, UX, and repo rules that must hold
- `Forbidden Changes`
  - known tempting edits that would create drift or violate ownership boundaries
- `Verification Evidence`
  - commands, artifacts, screenshots, logs, or manual checks that close the loop
- `Rollback And Stop Conditions`
  - concrete conditions that force rollback, pause, clarification, or escalation

## Routing Rule

For code-facing bundles, expose a machine-readable `harness_constraint_gate` with:

- `required: true`
- `reference: references/harness-engineering-constraint-protocol.md`
- `artifact: .skill-harness/engineering-constraints.md`
- `command: python scripts/init_harness_constraints.py --root . --summary "<task summary>" --pretty`
- `verification_check`

Code-facing bundles:

- `plan-first-build`
- `product-spec-deliver`
- `audit-fix-deliver`
- `govern-change-safely`
- `root-cause-remediate`
- `direct-execution`

Release, beta, and post-release routes can keep the gate optional until they move
from evidence gathering into implementation.
