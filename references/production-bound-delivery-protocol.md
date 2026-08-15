# Production-Bound Delivery Protocol

Use this protocol when a delivery slice changes or depends on a remote production system: database/schema, managed functions, cloud deployment, hosted configuration, external API resources, queues, storage, DNS, identity/provider configuration, or another control plane that cannot be proven by repository CI alone.

This protocol strengthens Delivery and Release closure. It does **not** add a seventh closure layer.

## Core rule

> **Code green is not production green.**

A production-bound change is complete only when the evidence required by its actual blast radius is green.

Classify evidence into three planes:

```text
Code plane
  repository state, tests, lint, build, semantic/regression checks

Control plane
  migration applied, function/config deployed, resource exists, expected version active

Production data plane
  real request/read/write/behavior proves the deployed path works end to end
```

Not every task needs all three. If a task mutates a production control plane, code-plane evidence alone can never support `ship`.

## 1. External-system preflight

Before the first remote mutation, record a compact preflight:

```yaml
provider: <provider/service>
account_or_org: <resolved account/org when available>
resource_name: <human-readable name>
resource_id: <canonical provider ID/ref>
resource_id_source: <provider read/list/CLI/dashboard evidence>
required_capability: <read/write/deploy/migrate/etc>
verified_capability: <what the current connection can actually do>
auth_boundary: <app permission / provider OAuth scope / API token / local CLI>
secret_boundary: <what must never be pasted/logged/committed>
fallback_execution: <agent tool | operator CLI | manual console>
resume_anchor: <artifact/file/Issue/PR checkpoint>
```

### Resource identity rule

Never diagnose a remote permission problem from a cached or remembered project/resource ID when the provider can resolve the current resource.

Resolve identity first:

```text
human name
   ↓
provider list/read
   ↓
canonical resource ID
   ↓
capability probe
   ↓
permission diagnosis
```

A stale resource ID can look exactly like an authorization failure.

### Permission-layer rule

Distinguish:

```text
host/app action permission
provider OAuth/API scope
provider project/org role
resource-specific policy
```

`Allow all actions` at one layer does not prove write permission at another.

## 2. Remote mutation ladder

Use the least destructive verified action that can prove the next assumption.

Default ladder:

```text
read identity/status
→ capability/read probe
→ dry-run / plan / diff
→ bounded mutation
→ read-back control-plane verification
→ production data-plane smoke
```

Do not skip directly from local code to destructive remote mutation when a provider exposes a dry-run, plan, migration list, diff, preview, or equivalent safety step.

## 3. Operator CLI handoff

When the agent cannot safely or reliably execute the remote mutation, operator execution is a first-class mode, not an ad-hoc escape hatch.

A valid handoff must contain:

1. **Exact working directory / target**
2. **Exact commands**
3. **Dry-run or read-only command first**, when available
4. **Expected safe output / invariant**
5. **Explicit stop conditions**
6. **Secrets boundary** — tell the operator to enter secrets locally and never paste them back
7. **Resume checkpoint** — what result to return, and where the automated workflow resumes

Example shape:

```text
Run:
  <read/list command>

Continue only if:
  <single expected pending change>

STOP if:
  <unexpected migration / resource / destructive diff>

Then run:
  <bounded mutation>

Return:
  <non-secret status/output fields>
```

The lead must not claim the mutation succeeded until operator evidence or provider read-back proves it.

## 4. Migration-history drift

For migration-backed systems, treat schema state and migration history as related but distinct truth sources.

Before a push:

```text
local migration history
        ↕ compare
remote migration history
        ↓
actual intended pending set
```

### Fail-closed rules

- Local-only historical migration + equivalent remote-only migration: **stop and reconcile identity/version first**.
- Unexpected remote-only migrations: **stop and inspect**.
- Dry-run includes more migrations than intended: **stop**.
- Never use history-repair commands merely to make the list look clean unless the database state and intended authoritative history justify the repair.
- Prefer correcting the side that is actually wrong. Do not rewrite production history to preserve a mistaken local filename/version.

## 5. Semantic/presentation boundary

Production instrumentation, completion detection, authorization, gating, analytics, and workflow state must depend on stable semantics, not presentation text.

Prefer:

```text
data-decision="SHIP"
semantic_code="blocked"
event_name="capstone_completed"
```

over:

```text
visibleText === "SHIP"
button.innerText === "Approved"
localizedLabel === "可以发布"
```

This rule is mandatory when localization, copy experiments, theming, or UI redesign can change visible text without changing product semantics.

## 6. Production evidence matrix

Before `ship`, list only the planes relevant to the task and mark them explicitly.

Example:

```markdown
| Plane | Required | Evidence | Result |
|---|---|---|---|
| Code | yes | CI + semantic QA | pass |
| Control | yes | migration version + function version | pass |
| Data | yes | production zh-CN row persisted | pass |
```

If any required plane is unknown, the release decision is `hold`.

## 7. Connector/tool degradation

A connected tool becoming unavailable does not erase the plan.

When a provider connector fails mid-flow:

1. preserve the last verified provider/resource identity;
2. mark the unverified mutation as pending, never successful;
3. downgrade to the safest available execution mode (provider CLI/manual console) if the user wants to proceed;
4. give a structured operator handoff;
5. resume at **verification**, not at assumption.

Do not repeat already-verified discovery unless the resource identity itself may have changed.

## 8. Completion contract

A production-bound slice can be accepted only when:

- code evidence is fresh for the shipped commit;
- every required remote mutation has control-plane proof;
- every required user-visible/data path has production smoke proof;
- unexpected remote drift is reconciled;
- secrets were not exposed in handoffs or evidence;
- residual unverified scope is explicitly zero or causes `hold`.

## Non-goals

- Provider-specific command catalogs in this core protocol.
- Requiring production access for local-only work.
- Replacing provider-native migration/deployment safety mechanisms.
- Treating a smoke test as a substitute for unit/semantic verification.
