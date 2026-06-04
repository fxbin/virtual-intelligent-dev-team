# Anti-Entropy Governance

Use this reference when a change may add or retire paths, owners, fallbacks,
adapters, guards, compatibility branches, or source-of-truth behavior.

The default preference is to reduce internal entropy. Do not preserve old paths
just because they exist.

## When To Activate

Activate as a governance overlay when any of these appear:

- duplicate owners
- stale fallback branches
- extra guard or adapter layers
- local patches around a deeper owner problem
- cleanup that may delete internal behavior
- migration or compatibility work
- schema, persistence, public API, or source-of-truth boundaries

Do not activate for pure additive work with no retirement decision, tiny edits,
or read-only Q&A.

## Classification

Classify the target before changing it:

- `code-retirement`
  - internal source code, stale triggers, duplicate owners, dead fallbacks
- `contract-carrying-code`
  - schemas, migrations, public APIs, host install or discovery behavior
- `derived-state`
  - generated files, caches, rebuildable indexes
- `persistent-state`
  - live database rows, uploaded source-of-truth files, identity, permission,
    billing, audit, queue, or non-rebuildable business data

## Decision Paths

Choose one:

- `delete-first`
  - internal code retirement when no proven external dependency blocks removal
- `compat-exception`
  - compatibility path remains because active external dependency evidence
    exists
- `confirmation-first`
  - persistent-state or irreversible source-of-truth changes require scoped
    user confirmation before destructive execution

Unknown dependency is not active dependency evidence.

## Anti-Entropy Declaration

Before retiring or preserving a path, state:

```yaml
anti_entropy_declaration:
  deletion_class:
  old_path_or_object:
  new_canonical_owner:
  preserved_behavior:
  retired_behavior:
  external_boundary_touched:
  source_of_truth_data_risk:
  user_confirmation_required:
```

If `user_confirmation_required: true`, stop destructive execution and ask for
explicit scoped confirmation.

## Verification

Do not verify only that tests are green. Verify that the owner and path shape
are correct:

- main-path check: new canonical owner carries the intended behavior
- lingering-reference check: old path is gone or intentionally retained
- negative check: retired behavior no longer activates
- compatibility check: retained path has active dependency evidence
- regression check: user-visible behavior remains within scope

## Completion Closure

When this overlay was active, completion output must include:

- path chosen: `delete-first`, `compat-exception`, or `confirmation-first`
- what was retired or preserved
- evidence for owner correctness
- remaining entropy or retirement follow-up

