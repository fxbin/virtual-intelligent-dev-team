# Playbook Index

Quick reference for playbooks and protocols used by core scripts.

## Delivery Playbooks

| Playbook | Used By | Purpose |
|----------|---------|---------|
| [quick-slice-delivery-playbook.md](./quick-slice-delivery-playbook.md) | check_harness_health.py | Narrow, time-boxed implementation |
| [product-delivery-playbook.md](./product-delivery-playbook.md) | check_harness_health.py | Product spec with acceptance criteria |
| [pre-development-planning-playbook.md](./pre-development-planning-playbook.md) | route_request.py, check_harness_health.py | Large rewrite/migration planning |
| [git-workflow-playbook.md](./git-workflow-playbook.md) | route_request.py, check_harness_health.py | Git-sensitive delivery |

## Governance Playbooks

| Playbook | Used By | Purpose |
|----------|---------|---------|
| [release-gate-playbook.md](./release-gate-playbook.md) | route_request.py, check_harness_health.py, run_release_gate.py | Ship/hold decisions |
| [technical-governance-playbook.md](./technical-governance-playbook.md) | route_request.py, check_harness_health.py | Technical decision gates |

## Lifecycle Playbooks

| Playbook | Used By | Purpose |
|----------|---------|---------|
| [beta-validation-playbook.md](./beta-validation-playbook.md) | route_request.py, check_harness_health.py | Staged rollout with feedback |
| [post-release-feedback-playbook.md](./post-release-feedback-playbook.md) | route_request.py, check_harness_health.py | Post-release monitoring |
| [root-cause-escalation-playbook.md](./root-cause-escalation-playbook.md) | check_harness_health.py, inspect_automation_state.py | Escalation paths |
| [offline-loop-drill-playbook.md](./offline-loop-drill-playbook.md) | run_release_gate.py | Deep iteration without blocking |
| [auto-run-playbook.md](./auto-run-playbook.md) | inspect_automation_state.py | Automated iteration cycles |

## Core Protocols

| Protocol | Used By | Purpose |
|----------|---------|---------|
| [agent-catalog.md](./agent-catalog.md) | check_harness_health.py | Lead agents scope and constraints |
| [mode-selection-protocol.md](./mode-selection-protocol.md) | SKILL.md | Output mode boundaries |
| [execution-quality-guardrails.md](./execution-quality-guardrails.md) | route_request.py | Quality guardrails reference |
| [harness-engineering-constraint-protocol.md](./harness-engineering-constraint-protocol.md) | route_request.py | Code-facing constraints |
| [team-engine-lite-protocol.md](./team-engine-lite-protocol.md) | route_request.py | Code/release/Git verification |
| [worker-verifier-cycle-protocol.md](./worker-verifier-cycle-protocol.md) | route_request.py | Implementation verification |
| [external-agent-backend-orchestration-protocol.md](./external-agent-backend-orchestration-protocol.md) | route_request.py | External agent backend |
| [real-subagent-runtime-protocol.md](./real-subagent-runtime-protocol.md) | route_request.py | Real vs mock subagent rules |
| [shared-language-and-decision-capture.md](./shared-language-and-decision-capture.md) | route_request.py | Shared language practices |
| [feedback-loop-first-protocol.md](./feedback-loop-first-protocol.md) | route_request.py | Feedback loop practices |
| [vertical-slice-delivery-protocol.md](./vertical-slice-delivery-protocol.md) | route_request.py, lint_virtual_team_contract.py | Vertical slice delivery |
| [system-map-protocol.md](./system-map-protocol.md) | route_request.py | System mapping |
| [change-localization-protocol.md](./change-localization-protocol.md) | route_request.py | Token-budget convergence to exact change sites |
| [project-knowledge-pyramid-protocol.md](./project-knowledge-pyramid-protocol.md) | route_request.py | Tiered, drift-checked target-project knowledge map |
| [worktree-state-placement-protocol.md](./worktree-state-placement-protocol.md) | route_request.py | State-directory placement under worktree execution |
| [architecture-deepening-protocol.md](./architecture-deepening-protocol.md) | route_request.py | Architecture deepening |
| [stage-council-protocol.md](./stage-council-protocol.md) | route_request.py | Stage council overlay |
| [iteration-protocol.md](./iteration-protocol.md) | route_request.py, inspect_automation_state.py | Iteration lifecycle |
| [automation-resume-decision-matrix.md](./automation-resume-decision-matrix.md) | inspect_automation_state.py | Resume decision matrix |
| [using-git-worktrees-playbook.md](./using-git-worktrees-playbook.md) | route_request.py | Git worktree workflows |
| [response-pack-sidecar-schema.md](./response-pack-sidecar-schema.md) | lint_virtual_team_contract.py | Response pack schema |
| [goal-framing-protocol.md](./goal-framing-protocol.md) | workflow-quality-baseline.md | Goal frame and drift control |
| [anti-entropy-governance.md](./anti-entropy-governance.md) | technical-governance-playbook.md, workflow-quality-baseline.md | Duplicate-path and fallback growth control |
| [workflow-quality-baseline.md](./workflow-quality-baseline.md) | regression-cases.json | Workflow quality baseline |
| [trigger-health-baseline.md](./trigger-health-baseline.md) | regression-cases.json | Trigger health diagnostics |
| [observability-protocol.md](./observability-protocol.md) | emit_telemetry.py, inspect_decision_log.py, verify_action.py | Observability three pillars and per-layer SLO |
| [workflow-bundles.md](./workflow-bundles.md) | check_harness_health.py | 12 workflow bundle definitions and confidence levels |
| [state-schema-spec.md](./state-schema-spec.md) | verify_action.py | State field ownership and layer-write contract |

## Supporting References

Conceptual references not bound to a single script — they document protocols, schemas, and patterns consumed across the workflow.

| File | Purpose |
|------|---------|
| [subagent-exec-guide.md](./subagent-exec-guide.md) | Subagent spawning patterns |
| [coordination-handoff-templates.md](./coordination-handoff-templates.md) | Templates for structured lead-to-assistant handoffs |
| [dispatch-activation-cards.md](./dispatch-activation-cards.md) | Cards for framing assistant activation prompts |
| [evidence-ledger-schema.md](./evidence-ledger-schema.md) | Schema for recording bounded-iteration rounds |
| [loop-orchestration.md](./loop-orchestration.md) | Multi-round optimization loop execution model |
| [mutation-catalog-patterns.md](./mutation-catalog-patterns.md) | Deterministic skill-file mutation patterns |
| [self-optimization-architecture.md](./self-optimization-architecture.md) | Turns one-shot dispatch into controlled optimization loops |
| [spec-evolution-protocol.md](./spec-evolution-protocol.md) | Evolves specs from static rules to self-updating contracts |
| [yagni-guardrail.md](./yagni-guardrail.md) | Detects unrequested abstractions to prevent over-building |
| [complexity-ladder.md](./complexity-ladder.md) | Five-step test for retaining or cutting layers |
| [contract-lock-protocol.md](./contract-lock-protocol.md) | Forces signed contract-spec before cross-team WorkOrders |
| [failure-runbook.md](./failure-runbook.md) | Retry, escalation, and recovery paths per failure mode |
| [hook-injection-protocol.md](./hook-injection-protocol.md) | Injects spec context into workers via hooks |
| [layer-reinforcement-protocol.md](./layer-reinforcement-protocol.md) | Independent checks and fallbacks for the six layers |
| [verifier-extraction-guide.md](./verifier-extraction-guide.md) | Pain-driven rules for extracting the Verifier node |
| [workspace-journal-protocol.md](./workspace-journal-protocol.md) | Append-only event journal for durable progress |
| SKILL.md Output template | Response structure requirements |

---

*This index only includes files actively referenced by core scripts. See `tooling-command-index.md` for script-to-reference mappings.*
