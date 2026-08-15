# Project Truth Reconciliation Protocol

Use this protocol after a release, major migration, phase transition, or any workflow where Issues/docs/resource identifiers may have drifted from the system that actually shipped.

It also applies before starting a new Epic when the current roadmap may contain stale preconditions.

## Core rule

> **The next planning cycle must start from reconciled truth, not from yesterday's plan.**

A project can be operationally correct while its roadmap, Issues, docs, resource IDs, migration names, commands, and status language are stale. That drift is dangerous for human and AI contributors because future routing starts from those artifacts.

## Truth sources

Classify project truth into four groups:

```text
Runtime truth
  what is actually deployed / persisted / reachable

Repository truth
  default branch, canonical docs, current file/resource identifiers

Work-management truth
  Issues, PRs, milestones, checklists, dependency gates

Decision truth
  current product phase, stop lines, paused work, next gate
```

No single source is automatically authoritative for every field.

## 1. Reconciliation triggers

Run reconciliation when any of these occurs:

- final release PR merged;
- production rollout completes;
- migration/resource identifier changed;
- child PRs were integrated through a release branch;
- a post-release hotfix changes the accepted state;
- a Product Gate changes which work is active/paused;
- a new Epic is about to begin after several prior slices;
- an operator or agent discovers contradictory planning artifacts.

## 2. Minimum reconciliation pass

### A. Default branch / release state

Verify:

- expected release commit is on the default branch;
- production deployment points to the intended commit/version where relevant;
- required post-merge smoke is complete;
- release/feature branches are not being mistaken for production truth.

### B. Issue state

Check for:

- child Issues completed in code but still open;
- Issues auto-closed unexpectedly by default-branch merge;
- parent Issue closed before all production gates passed;
- old prerequisites that conflict with the current Master/Roadmap decision;
- paused work that is accidentally listed as next.

Do not bulk-close Issues only for cleanliness. Close only when exit criteria are actually satisfied.

### C. Canonical docs

Identify the canonical planning/spec/status documents and update them when reality changed.

Typical fields:

```text
current phase
completed milestones
next action
paused/gated work
resource IDs
migration filenames/versions
production commands
route/API/schema contracts
known hotfixes
```

If several docs claim to be the source of truth, choose or document an ownership hierarchy instead of editing them independently forever.

### D. External resource identifiers

Search for stale:

- project refs/IDs;
- deployment IDs;
- migration versions;
- branch names;
- endpoint URLs;
- renamed files/commands.

A human-readable resource name and its canonical provider ID should not disagree silently.

## 3. Plan-drift check before a new Epic

Before planning the next major feature, compare open work against the current decision model.

Classify existing work:

```text
NOW
  directly advances the current product/engineering gate

GATED
  valid, but blocked on an explicit decision/evidence gate

LATER
  desirable but not justified by the current phase

STALE
  already completed, superseded, contradictory, or no longer applicable
```

This prevents a stale Issue from pulling the team back into speculative platform completeness.

## 4. Canonical-plan conflict rule

When an old Issue conflicts with a newer explicit Master/Roadmap decision:

1. verify which artifact owns current decision truth;
2. update the stale Issue rather than silently ignoring it;
3. preserve the reason for the gate/change;
4. ensure future agents reading only repository/work-management artifacts derive the same execution order.

## 5. Hotfix writeback

A post-release hotfix should write back only what changed:

- link bug Issue to shipped release;
- preserve original release closure;
- record new production verification;
- update canonical docs only if the hotfix changes an invariant, operational command, or known limitation.

Do not rewrite the original release narrative as though the bug never existed.

## 6. Reconciliation output

For drift-prone projects, preserve a concise result:

```yaml
release_or_phase: <label>
runtime_truth: pass|hold
repository_truth: pass|hold
issue_truth: pass|hold
decision_truth: pass|hold
stale_items_fixed:
  - <item>
remaining_gated_items:
  - <item>
next_action: <single current action>
canonical_sources:
  - <path/issue>
```

A `hold` means the project may be technically running, but the workflow should not claim planning closure or start a broad new Epic from unreconciled state.

## 7. Scope control

Truth reconciliation is not a refactor opportunity.

Do not:

- redesign the roadmap while merely fixing stale status;
- close unresolved Issues to make the board look clean;
- rename resources without need;
- rewrite historical decision records;
- turn a status reconciliation into new product scope.

## Exit criteria

Reconciliation passes when:

- runtime/repository/work-management/decision artifacts no longer materially contradict each other;
- stale identifiers that could route future work incorrectly are removed or explicitly deprecated;
- current gated vs active work is clear;
- the next action is derivable from canonical artifacts without relying on chat memory.
