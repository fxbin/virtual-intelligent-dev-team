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

## Supporting References

| File | Purpose |
|------|---------|
| [subagent-exec-guide.md](./subagent-exec-guide.md) | Subagent spawning patterns |
| SKILL.md Output template | Response structure requirements |

---

*This index only includes files actively referenced by core scripts. See `tooling-command-index.md` for script-to-reference mappings.*
