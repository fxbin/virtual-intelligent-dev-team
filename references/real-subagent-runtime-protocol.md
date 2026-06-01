# Real Subagent Runtime Protocol

This protocol upgrades Team Engine Lite from role-separated soft orchestration to a controlled real subagent runtime when the host actually exposes spawn / wait / merge capabilities.

It is not the default mode. Use it only when real subagent tools are available and the task benefits from independent parallel work.

## Runtime Boundary

Allowed runtime claims:

- `real_subagent_runtime`
  - The host can spawn one or more separate subagents with independently scoped prompts and collect their final outputs.
- `single_backend_multi_session`
  - The host can create independent sessions, but not a fully managed workflow engine.
- `soft_orchestration_only`
  - No reliable subagent runtime is available; use the existing external-agent backend protocol.

Never claim `real_subagent_runtime` when the current host only simulates roles in one thread.

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
