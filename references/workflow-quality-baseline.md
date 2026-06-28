# Workflow Quality Baseline

Use this baseline when changing routing wording, workflow bundles, output
contracts, or regression cases.

The goal is not to make every request heavier. The goal is to keep the virtual
team useful under real engineering pressure:

- route when routing adds value
- stay cheap when the task is small
- preserve fresh evidence before completion claims
- keep durable artifacts lazy
- expose authority boundaries instead of implying runtime power the host does
  not provide

## Quality Dimensions

### Trigger Accuracy

Representative prompts should select the expected lead, process lane, and
workflow bundle.

Check both directions:

- false negative: a risky request stays on a vague fast path
- false positive: a simple request opens a full team ceremony

### Fast-Path Cheapness

Small factual questions, version checks, tiny wording edits, and read-only
status checks should remain compact.

Fast-path work may still name:

- the immediate intent
- the smallest baseline read
- the verification evidence

It should not create delivery, beta, planning, or iteration workspaces unless
the task risk changes.

### Output Compactness

Output depth scales with risk.

- Low-risk: short answer, direct evidence, residual risk if any.
- Medium-risk: route, acceptance evidence, touched boundary, next step.
- High-risk: planning pack, Worker / Verifier cycle, release or governance
  evidence, resume anchor.

Do not emit every possible section from the `SKILL.md` Output template or
`response-pack-sidecar.schema.json` when the selected bundle did not activate
that lane.

### Evidence Freshness

Completion, readiness, release, commit, and handoff claims require fresh
evidence.

Evidence must name:

- action or command
- result or exit status
- covered scope
- uncovered scope
- residual risk
- confidence grade

Worker self-report is not completion evidence. Team Engine Lite completion
requires Verifier evidence and a DeliveryCycleReport when active.

### Artifact Laziness

Durable artifacts are for continuity, not decoration.

Create or refresh workspaces only when the selected bundle requires a persisted
resume trail, such as:

- `.skill-delivery/`
- `.skill-product/`
- `.skill-beta/`
- `.skill-governance/`
- `.skill-iterations/`
- `.skill-post-release/`
- `.skill-harness/`

Do not create a durable workspace for simple Q&A, tiny edits, or route-only
answers.

### Authority Boundary

This skill can produce:

- route recommendations
- workflow bundles
- draft plans
- evidence ledgers
- release recommendations
- soft or real subagent runtime plans when host evidence supports them

It cannot produce host-independent final authority over deployment, merge,
release, user approval, production safety, or evidence sufficiency.

When a runtime claim depends on host capability, state the current claim:

- `soft_orchestration_only`
- `real_subagent_runtime_eligible`
- `real_subagent_runtime_proven`

### Goal Boundary

For broad or failure-prone work, lock goal, success evidence, stop condition,
and non-goals before implementation. Use
`references/goal-framing-protocol.md`.

### Anti-Entropy

When work adds guards, fallbacks, adapters, duplicate owners, compatibility
paths, or cleanup, verify whether an old path should retire. Use
`references/anti-entropy-governance.md`.

## Regression Matrix Expectations

When changing this skill, representative cases should cover:

- route-positive examples for each bundle
- fast-path negative examples
- evidence-before-completion examples
- artifact-laziness examples
- anti-entropy examples
- goal-boundary examples
- context-pressure or resume examples

Add samples before expanding trigger wording. If a trigger fails, diagnose the
failure layer first instead of stuffing every keyword into `SKILL.md`.
