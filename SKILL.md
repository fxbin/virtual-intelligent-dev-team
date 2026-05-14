---
name: virtual-intelligent-dev-team
archetype: router
description: R&D / product / quick-slice / staged-beta / technical-governance router and bounded-iteration orchestrator for complex software work. Dispatch the best lead agent from Java Virtuoso, Sentinel Architect (NB), Technical Trinity, Code Audit Council, Git Workflow Guardian, and World-Class Product Architect; attach copilots only when useful; use quick slice delivery for narrow implementation or bug-fix work; enter pre-development planning for large rewrites, migrations, and project-wide transformations; enable evidence-driven iteration for optimization loops, repeated retries, benchmark comparison, or candidate evaluation; and trigger the formal release gate when the user asks whether a version is ready to ship or submit.
---

# Virtual Intelligent Dev Team

Route complex software work into the smallest defensible delivery workflow, keep one semantic lead, and close the task with verifiable evidence and a resume anchor.

## Positioning

This skill is not only an expert router. It is a bounded work-loop skill for complex tasks.

It has six practical closure layers:

1. `Planning closure`
   - Large rewrites, migrations, and project-wide transformations get a lightweight analysis / plan / progress pack before implementation.
2. `Routing closure`
   - Work is routed across lead, assistant, governance, and process tracks based on task shape, risk, stack, and workflow signals.
3. `Delivery closure`
   - Narrow feature and bug-fix slices use a quick slice brief, durable project context, delivery status, targeted verification, and self-review.
4. `Iteration closure`
   - Optimization loops preserve baseline, round memory, self-feedback, `keep / retry / rollback / stop`, `pivot`, and `resume`.
5. `Release closure`
   - Release readiness uses a formal `ship` / `hold` gate and bootstraps the next remediation loop when needed.
6. `Drill closure`
   - Offline drills verify rollback, resume, and release-gate bootstrap paths.

Runtime rule:

- When routing alone is not enough, return the smallest matching workflow bundle and resume anchor instead of inventing a new ceremony.

## Routing goal

Route complex software requests into the smallest defensible workflow bundle, keep one semantic lead, and attach only assistants, governance, and artifacts that materially improve delivery fidelity.

## Trigger cues

- multi-domain software delivery
- quick implementation or bug-fix slice
- rewrite / migration / plan-before-coding
- repeated optimization or retry loops
- staged beta validation or rollout risk control
- release readiness / ship-hold decisions
- git workflow, rollback, or governance-sensitive delivery

## When to use

Use this skill when:

- The user does not know which研发 / 产品 / 技术治理 specialist should own the task.
- The task spans two or more domains such as code, architecture, product definition, frontend UX, security, audit, release, or Git workflow.
- The user asks for a small implementation or bug-fix slice that needs quick context, acceptance criteria, and verification.
- The user asks for a large rewrite, migration, overhaul, project-wide refactor, or explicitly wants planning before coding.
- The user needs a cross-domain delivery decision such as audit plus implementation, product scope plus API contract, risky refactor plus staged governance, or release guardrails.
- The task needs structured coordination, governance, or workflow guardrails.

Use bounded iteration only when the request benefits from it:

- explicit optimization loops
- benchmark or regression comparison
- repeated retries with evidence required
- candidate comparison before committing to a direction

Use pre-development planning only when the request benefits from it:

- rewrite or migrate a whole project or major subsystem
- architecture overhaul before implementation
- project-wide refactor with dependency-aware phase planning
- "plan first, code later" requests that need durable progress tracking

If the task is simple and clearly single-domain, keep routing lightweight.

## Workflow

1. Identify task type, risk level, language stack, and Git/process needs.
2. If the request is a large rewrite, migration, overhaul, or planning-before-coding transformation, enter the pre-development planning branch first.
3. If the request is a narrow implementation or bug fix, use quick slice delivery instead of a full product or planning workflow.
4. Choose one lead agent.
5. Add one or two assistant agents only when they add clear value.
6. Enable governance or process guardrails only when needed.
7. Use a compact handoff when lead and assistants need structured coordination.
8. Apply execution-quality guardrails: surface route-changing assumptions, keep the smallest defensible bundle, limit scope surgically, and define verifiable closure.
9. For code-facing routes, apply the Harness constraint gate before implementation: create or refresh `.skill-harness/engineering-constraints.md`.
10. If the user asks for optimization, repeated improvement, benchmark comparison, or another round, enter bounded iteration instead of open-ended self-looping.
11. If the user asks whether the current version can ship, submit, or pass formal acceptance, run the release gate instead of answering from a benchmark summary alone.
12. Produce one unified response instead of disconnected role fragments.

## Output template

- `Selected route`
  - lead, assistants, workflow bundle, and why this route won
- `Fallback`
  - clarification path or downgraded route when confidence or evidence is weak
- `Next step`
  - smallest executable action, required artifact, and resume anchor

For the full user-facing response contract, use `references/output-contract.md`.

## Quick examples

- `评估当前项目里的版本，看看能不能继续优化`
  - Route into bounded iteration with evidence, baseline comparison, and next-round decisions.
- `先别写代码，先把这个单体拆分迁移项目规划清楚`
  - Enter pre-development planning, generate the transformation brief and progress anchor, then hand back to execution.
- `这个小 bug 直接修一下并跑回归`
  - Route into quick-slice delivery, preserve the current slice and project context, then implement with targeted verification.
- `这个功能开发前后都要做内测，按轮次逐步加用户`
  - Route into staged beta validation, define cohort ramp, and keep feedback evidence before release expansion.
- `继续下一轮，直到结果稳定`
  - Keep the same semantic owner, persist round memory, and use `keep / retry / rollback / stop` instead of vague retries.
- `这个版本现在能发布吗`
  - Trigger the formal release gate and answer with `ship` or `hold`, not only a benchmark summary.
- `已经试过很多次了，帮我找根因`
  - Escalate into root-cause discipline, require evidence, and prefer Sentinel-led investigation when risk is high.

## Key terms

- `workflow bundle`
  - The smallest reusable delivery journey for the request shape.
- `project context`
  - Durable project rules, commands, architecture constraints, forbidden changes, and verification defaults shared across slices.
- `quick slice`
  - A narrow implementation or bug-fix delivery unit with explicit intent, non-goals, acceptance criteria, and verification evidence.
- `baseline`
  - The comparison anchor for one round or one candidate.
- `round memory`
  - Short-term memory for what changed, what failed, and what should carry into the next round.
- `self-feedback`
  - Compact reflection that turns evidence into the next hypothesis instead of repeating the same attempt.
- `pivot`
  - Switch to a new bottleneck after the current hypothesis is exhausted.
- `resume`
  - Continue from persisted loop state instead of restarting the whole loop.

## Runtime references

Read indexes first; do not flatten the whole skill into this file.

- Route selection, scenarios, iteration, release, and Git split:
  [references/runtime-routing-index.md](references/runtime-routing-index.md)
- Runtime operation rules:
  [references/runtime-operation-contract.md](references/runtime-operation-contract.md)
- Output structure:
  [references/output-contract.md](references/output-contract.md)
- Execution-quality guardrails:
  [references/execution-quality-guardrails.md](references/execution-quality-guardrails.md)
- Harness engineering constraint gate:
  [references/harness-engineering-constraint-protocol.md](references/harness-engineering-constraint-protocol.md)
- Scripts, templates, validation, and command entrypoints:
  [references/tooling-command-index.md](references/tooling-command-index.md)
- Workflow bundles and resume anchors:
  [references/workflow-bundles.md](references/workflow-bundles.md)
- Team catalog:
  [references/agent-catalog.md](references/agent-catalog.md)
- Maintainer-facing project docs:
  [README.md](README.md) and [docs/README.md](docs/README.md)

## Built-in checks

Use deterministic routing inspection when needed:

```bash
python scripts/route_request.py --text "<user request>" --config references/routing-rules.json
```

Run semantic regression after changing routing, guardrails, examples, or this skill:

```bash
python scripts/validate_virtual_team.py --pretty
```
