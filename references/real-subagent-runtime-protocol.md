# Real Subagent Runtime Protocol

This protocol upgrades Team Engine Lite from role-separated soft orchestration to a controlled real subagent runtime when the host actually exposes spawn / wait / merge capabilities.

It is not the default mode. Use it only when real subagent tools are available and the task benefits from independent parallel work.

## Runtime Boundary

Allowed runtime claims (three tiers, ordered by isolation strength):

- `real_subagent_runtime`
  - The host can spawn one or more separate subagents with independently scoped prompts and collect their final outputs.
  - Strongest isolation: each subagent is a separate process / context with independent memory.
- `single_backend_multi_session`
  - The host can create independent sessions within a single backend, but not a fully managed workflow engine.
  - Session is the circuit-breaker unit: a misbehaving session can be killed, restarted, or context-isolated without tearing down the entire backend.
  - Weaker than `real_subagent_runtime` (sessions share the same backend process / model context), stronger than `soft_orchestration_only` (which has no isolation at all).
- `soft_orchestration_only`
  - No reliable subagent runtime is available; use the existing external-agent backend protocol.
  - `known-shortcut:` no true session isolation — role separation is logical, not runtime-enforced. A misbehaving role cannot be killed or restarted independently.
  - Upgrade path: when the host exposes `create_session` / `kill_session` / `restart_session` capabilities, upgrade to `single_backend_multi_session`.

Never claim `real_subagent_runtime` when the current host only simulates roles in one thread.

### Tier Selection Algorithm

```
if request candidate allows real_subagent_runtime and host proves spawn / wait / merge:
    runtime_claim = real_subagent_runtime
elif request candidate allows single_backend_multi_session and host proves create_session / kill_session / restart_session:
    runtime_claim = single_backend_multi_session
else:
    runtime_claim = soft_orchestration_only
```

The router emits `candidate_runtime_claim` based on request eligibility; the host downgrades to a lower tier when the required capability is missing. The host must never upgrade beyond what it can actually enforce.

Each operation is independent evidence. `spawn=true` without `wait=true` and
`merge=true`, or `create_session=true` without `kill_session=true` and
`restart_session=true`, is incomplete and must fail closed to a lower tier.

## Session as Circuit Breaker Unit

When `runtime_claim` is `single_backend_multi_session`, each session is a circuit-breaker unit:

- **Kill**: a session that exceeds failure threshold (default: 3 consecutive failures) is killed; its partial output is discarded.
- **Restart**: after kill, a fresh session is created with a clean context and a narrowed WorkOrder.
- **Isolate context**: a killed session's context must not leak into the replacement session; only verified artifacts (ImplementationOutput / VerificationReport) carry over.
- **Escalation**: if a session is killed twice for the same failure reason, escalate to human decision rather than retrying indefinitely.

This mirrors the trust-boundary principle: a session that cannot be killed is not a real isolation boundary.

### Session Lifecycle

```
session_created → session_active → session_killed (on failure threshold)
                                 ↘ session_completed (on success)
session_killed → session_restarted (fresh context + narrowed WorkOrder)
session_killed → session_escalated (after 2 kills for same reason)
```

The Lead owns session lifecycle decisions; Workers and Verifiers cannot kill their own sessions.

## Activation Rules

Real subagents are eligible only when at least one trigger is true:

- The user explicitly asks for `multi-agent`, `subagents`, `parallel agents`, `spawn agents`, `agent team`, or equivalent Chinese wording such as `多 agent`、`多智能体`、`并行 agent`、`自主唤起`.
- The user explicitly asks for `/auto` on a workflow that is already in the auto-run whitelist and the host reports real subagent tooling.

High-risk code-facing routes may propose a subagent plan only after the Lead explains why local single-thread execution is insufficient. They must not become eligible by risk alone.

Do not spawn subagents for simple single-domain fixes, low-information requests, or tasks where the next local step is blocked on the delegated result.

## Planning Contract

Before spawning, the Lead must produce a `SubagentRuntimePlan`:

```yaml
subagent_runtime_plan:
  runtime_claim: "real_subagent_runtime | single_backend_multi_session | soft_orchestration_only"
  activation_reason:
  workflow_bundle:
  max_subagents:
  spawn_policy:
    user_explicit_or_auto_required: true
    no_default_swarm: true
    blocking_work_stays_local: true
  agents:
    - role: "worker | verifier | explorer | memory_keeper"
      task:
      write_scope:
      context_policy:
      output_contract:
      can_write_artifact:
      can_write_verdict:
  merge_policy:
    lead_merges_only: true
    verifier_before_acceptance: true
    conflict_resolution:
  fallback:
    unavailable_runtime:
    malformed_output:
    role_boundary_violation:
```

## Role Mapping

- `Lead`
  - Stays in the parent thread.
  - Owns the WorkOrder, spawn decisions, merge, user response, and final acceptance.
- `Worker`
  - May edit only its assigned write scope.
  - Must return `ImplementationOutput`.
  - Cannot write final pass / ship / accepted.
- `Verifier`
  - Reads the Worker output or patch.
  - Returns `VerificationReport` and `RemediationPatch` on fail.
  - Must not silently rewrite Worker artifacts.
- `Explorer`
  - Answers bounded codebase questions.
  - Must not edit files.
- `Memory Keeper`
  - Writes only verified summaries or state deltas when explicitly assigned.

## Parallelism Rules

- Parallel subagents must have independent tasks.
- Code-writing Workers must have disjoint write scopes.
- Verification may run in parallel only when it does not depend on unfinished artifacts; otherwise it waits for Worker output.
- Do not duplicate the parent thread's immediate blocking task in a subagent.
- Close subagents when their output is no longer needed.

## Merge And Acceptance

Lead acceptance requires:

- WorkOrder exists.
- Every spawned subagent has a final output or an explicit timeout / hold record.
- Worker output is reviewed by Verifier when Team Engine Lite is required.
- DeliveryCycleReport records runtime claim, subagent IDs or backend IDs, checked gates, and remaining risks.

If a spawned Worker and Verifier disagree, prefer `hold` unless the Lead can resolve the conflict with objective evidence.

## Fallback

If real subagent tools are unavailable:

- Keep Team Engine Lite active.
- Use `external-agent-backend-orchestration-protocol.md`.
- Set `runtime_claim: soft_orchestration_only`.
- Set `backend_orchestration_verdict: simulated`.
- State that role separation is logical, not runtime-isolated.
- `known-shortcut:` ceiling — no session kill / restart / context isolation; a misbehaving role poisons the shared context. Upgrade path: when host exposes `create_session` / `kill_session` / `restart_session`, upgrade to `single_backend_multi_session` to gain session-level circuit breaking.

### Intermediate fallback: single_backend_multi_session

If the host cannot spawn fully independent subagents but can create / kill / restart sessions within a single backend:

- Set `runtime_claim: single_backend_multi_session`.
- Treat each session as a circuit-breaker unit (see "Session as Circuit Breaker Unit" above).
- `known-shortcut:` ceiling — sessions share the same backend process / model context; a backend-level failure still takes down all sessions. Upgrade path: when host exposes `spawn` / `wait` / `merge`, upgrade to `real_subagent_runtime` for process-level isolation.
