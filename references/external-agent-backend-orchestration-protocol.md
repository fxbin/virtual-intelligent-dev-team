# External Agent Backend Orchestration Protocol

This protocol defines how `virtual-intelligent-dev-team` can use Codex, Claude Code, OpenCode, or similar tools as external Agent backends.

It is a soft orchestration contract, not a real async runtime implementation.

If the host exposes real subagent spawn / wait / merge primitives, route through `real-subagent-runtime-protocol.md` first. Use this protocol as the fallback when those primitives are unavailable, unproven, or too weak to preserve Worker / Verifier boundaries.

## Boundary

External Agent backends may execute one role at a time:

- Lead
- Worker
- Verifier
- Memory Keeper
- User Response Sentinel

They do not replace:

- `WorkOrder`
- `ImplementationOutput`
- `VerificationReport`
- `RemediationPatch`
- `DeliveryCycleReport`
- `team_engine_gate`
- `team_engine_closure_verdict`

## Backend Declaration

```yaml
agent_backend:
  backend_id:
  provider: "codex | claude_code | opencode | other"
  role: "lead | worker | verifier | memory_keeper | user_response_sentinel"
  invocation_mode: "cli | api | hosted | manual_bridge | simulated"
  workspace_scope:
  input_contract:
  output_contract:
  timeout_policy:
  context_policy: "task_only | artifact_only | summary_plus_artifact | redacted"
  tool_boundary:
  can_write_artifact:
  can_write_verdict:
  can_accept_task:
```

Rules:

- Worker backends can write artifacts but cannot write final verdicts.
- Verifier backends can write verification reports and remediation patches but cannot silently rewrite artifacts.
- Lead backends can create work orders but cannot accept without delivery cycle reports.
- Memory Keeper backends can write verified deltas only.
- User Response Sentinel backends can summarize status but cannot change route.

## Backend Orchestration Plan

```yaml
backend_orchestration_plan:
  orchestration_mode: "soft_external_backend"
  runtime_claim: "soft_orchestration_only"
  task_id:
  objective:
  backend_matrix:
    lead:
      backend_id:
      provider:
      context_policy:
      output_contract:
    worker:
      backend_id:
      provider:
      context_policy:
      output_contract:
    verifier:
      backend_id:
      provider:
      context_policy:
      output_contract:
  isolation_contract:
    shared_full_context_allowed: false
    worker_reads_verifier_private_reasoning: false
    verifier_reads_worker_private_reasoning: false
    user_messages_route_to: "lead"
  fallback_policy:
    unavailable_backend:
    malformed_output:
    role_boundary_violation:
    max_cycles_exhausted:
  required_outputs:
    - WorkOrder
    - ImplementationOutput
    - VerificationReport
    - RemediationPatch
    - DeliveryCycleReport
  backend_orchestration_verdict:
```

## Runtime Claim Levels

### `real_backend_available`

The host can actually start two or more external backends, or separate sessions with isolated context.

Maximum verdict: `pass`

### `single_backend_multi_session`

Only one provider is available, but independent sessions or context windows are created for Worker and Verifier.

Maximum verdict: `pass_with_watch`

### `single_thread_simulated`

The current assistant simulates multiple roles in sequence.

Required claims:

```yaml
runtime_claim: soft_orchestration_only
backend_orchestration_verdict: simulated
team_engine_closure_verdict: pass_with_watch
```

Forbidden claims:

- real async multi-process execution
- A2A message bus
- physical permission isolation
- background recovery

### `unavailable`

Role separation or structured outputs cannot be preserved.

Verdict:

```yaml
backend_orchestration_verdict: hold
```

## Default Use In This Skill

Unless runtime evidence exists, this skill must declare:

```yaml
runtime_claim: soft_orchestration_only
backend_orchestration_verdict: simulated
team_engine_closure_verdict: pass_with_watch
```

This is still useful: it preserves role boundaries and retry discipline while avoiding false claims about infrastructure that the skill repository does not implement.
