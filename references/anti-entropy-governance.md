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

## Data Channel Constraint

Keep judgment in the LLM and data acquisition in scripts. The two must not be
mixed in the same step.

External data sources — issue trackers, doc platforms, design specs, API
contracts, dashboards — must be reached through dedicated script channels, not
through a generic fetch primitive driven by the LLM. The LLM only reads the
file the script landed on disk.

Activate this constraint when any of these appear:

- a step needs content from a tool that offers a structured or scripted surface
- the same data may be re-read across rounds or sessions
- the evidence for a decision must be replayable or auditable

Rules:

- one source, one channel: each external data source has a named script that
  fetches, normalizes, and writes a local file; the LLM consumes that file
- no inline generic fetch: the LLM must not fetch arbitrary URLs to gather task
  inputs; route the fetch through the channel and read the result
- land before deciding: the success signal of a long-running command is a file
  that exists on disk, not stdout; assert presence and then reason over the file
- cite the file, not the fetch: when evidence is referenced, point at the landed
  artifact path so the same input can be re-read on resume

This keeps inputs deterministic and replayable. A resumed session reads the
same landed files instead of re-asking the LLM to re-derive what it fetched.

