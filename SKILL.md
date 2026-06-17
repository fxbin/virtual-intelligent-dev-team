---
name: virtual-intelligent-dev-team
archetype: router
description: R&D / product / quick-slice / staged-beta / technical-governance router and bounded-iteration orchestrator for complex software work. Dispatch the best lead agent from Java Virtuoso, Sentinel Architect (NB), Technical Trinity, Code Audit Council, Git Workflow Guardian, and World-Class Product Architect; attach copilots only when useful; ask a targeted intent-confirmation question for fuzzy ideas before treating a provisional route as final; expand optional product-discovery or prototype-design stage councils under product delivery when phase-level specialists materially change the artifact sequence; use quick slice delivery for narrow implementation or bug-fix work; enter pre-development planning for large rewrites, migrations, and project-wide transformations; enable evidence-driven iteration for optimization loops, repeated retries, benchmark comparison, or candidate evaluation; and trigger the formal release gate when the user asks whether a version is ready to ship or submit.
---

# Virtual Intelligent Dev Team

Route complex software work into the smallest defensible delivery workflow, keep one semantic lead, and close the task with verifiable evidence and a resume anchor.

## Positioning

This skill is not only an expert router. It is a bounded work-loop skill for complex tasks.

It has eight practical closure layers:

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
7. `Team Engine Lite closure`
   - Code-facing delivery now carries Worker / Verifier separation, max-cycle retry, remediation patch, controlled real subagent runtime eligibility, external-agent soft orchestration fallback, and a DeliveryCycleReport before Lead acceptance.
8. `Stage council closure`
   - Product discovery and prototype design can expand into phase-level councils under `World-Class Product Architect` without replacing the top-level lead, workflow bundle, or Team Engine Lite verification.

Runtime rule:

- When routing alone is not enough, return the smallest matching workflow bundle and resume anchor instead of inventing a new ceremony.

## Routing goal

Route complex software requests into the smallest defensible workflow bundle, keep one semantic lead, and attach only assistants, governance, and artifacts that materially improve delivery fidelity.

## Trigger cues

- multi-domain software delivery
- fuzzy ideas where product opportunity, prototype exploration, technical feasibility, architecture risk, or delivery planning could all be plausible
- quick implementation or bug-fix slice
- rewrite / migration / plan-before-coding
- repeated optimization or retry loops
- staged beta validation or rollout risk control
- release readiness / ship-hold decisions
- git workflow, rollback, or governance-sensitive delivery
- repository AI onboarding, `AGENTS.md`, or project-local `.agents/skills/` context capture

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

**1.5. Choose Output Mode (Critical):**

   **Decision Tree:**
   
   1. **Is it a simple, single-domain question?**
      - Yes → **Direct Answer Mode** (skip to step 3)
        - Bug fixes, "how do I...", single optimization
        - Answer directly with: Analysis → Solution → Steps → Results
      - No → Continue to 2
   
   2. **Does it need multiple expert perspectives?**
      - Yes → **Multi-Expert Execution Mode** ⭐ NEW
        - Multi-domain problems (architecture + data + ops)
        - Complex technical decisions benefiting from diverse views
        - **Actually spawn 2-4 experts, collect outputs, synthesize**
        - Examples: "微服务拆分规划", "React性能全面优化", "系统重构方案"
      - No → Continue to 3
   
   3. **Does it need full workflow orchestration?**
      - Yes → **Full Workflow Mode**
        - Large refactor / migration / multi-phase delivery
        - Release readiness / governance gates
      - No → **Expert Routing Mode**
        - Single expert, deep dive
        - Specialist perspective on focused problem
   
   **Golden Rule:** Multi-domain problems → Multi-Expert Execution (not Direct Answer).
   
   See `references/output-contract.md` for detailed output structures.

2. If the request is a large rewrite, migration, overhaul, or planning-before-coding transformation, enter the pre-development planning branch first.
3. **If using Direct Answer Mode:** Skip to answering directly with technical depth. Provide: Analysis → Solution → Steps → Expected Results. Skip Team Dispatch, Evidence, and Resume sections. Exit here.
3.5. **If using Multi-Expert Execution Mode:** 
   - Identify 2-4 relevant experts based on problem domains
   - Spawn them in parallel using Agent tool or subagent runtime
   - Each expert analyzes from their perspective
   - Collect all expert outputs
   - Synthesize into unified, comprehensive answer
   - Output structure: Expert roster → Individual analyses → Synthesized solution
   - Exit here (skip Full Workflow sections).
4. If the request is a narrow implementation or bug fix, use quick slice delivery instead of a full product or planning workflow.
5. Choose one lead agent.
6. Add one or two assistant agents only when they add clear value.
7. Enable governance or process guardrails only when needed.
8. Use a compact handoff when lead and assistants need structured coordination.
9. If the request is primarily about building AI-readable project context, route execution to `skill-forge` and its project knowledge capture protocol after the software-risk lanes are identified.
10. If the request is a fuzzy idea or low-information route-changing ask, ask one intent-confirmation question before treating the provisional route as final.
11. Apply execution-quality guardrails: surface route-changing assumptions, keep the smallest defensible bundle, limit scope surgically, and define verifiable closure.
11. Apply execution-quality guardrails: surface route-changing assumptions, keep the smallest defensible bundle, limit scope surgically, and define verifiable closure.
12. For broad, repeated-failure, release, beta, multi-agent, or drift-prone work, apply goal framing: success evidence, stop condition, and non-goals must be explicit before implementation.
13. For code-facing routes, apply the Harness constraint gate before implementation: create or refresh `.skill-harness/engineering-constraints.md`.
14. For changes that add or retire guards, fallbacks, adapters, duplicate owners, compatibility paths, schema, persistence, or source-of-truth behavior, apply anti-entropy governance before choosing delete, compat, or confirmation paths.
15. For code-facing, release-facing, Git-facing, or remediation routes, apply Team Engine Lite: Worker can produce, Verifier can pass/fail/hold, and Lead can accept only after a DeliveryCycleReport.
16. If the user explicitly asks for multi-agent / subagent / parallel agent execution, or `/auto` reaches an eligible workflow, build a controlled real subagent runtime plan; only claim actual real subagent execution when the host exposes spawn / wait / merge runtime evidence.
17. If external Agent backends are available but real subagent runtime is not proven, treat them as soft backend sessions under the same role boundary; do not claim true async multi-process runtime without runtime evidence.
18. **Real Subagent Execution Guide**: When spawning Worker/Verifier/Explorer agents, use actual Agent tool invocations with independent prompts and contexts. See [references/subagent-exec-guide.md](references/subagent-exec-guide.md) for complete execution templates including Worker-Verifier cycles, parallel implementation, and Explorer-Worker patterns.
19. If the user asks for optimization, repeated improvement, benchmark comparison, or another round, enter bounded iteration instead of open-ended self-looping.
20. If the user asks whether the current version can ship, submit, or pass formal acceptance, run the release gate instead of answering from a benchmark summary alone.
21. If product discovery, product strategy, PRD, user research, competitor analysis, metrics, roadmap, prototype design, high-fidelity UI, design systems, or explicit expert-team phrasing would make a single product generalist too broad, apply the stage council protocol under `product-spec-deliver`.
22. Before any completion, readiness, commit, merge, release, or handoff claim, preserve fresh evidence slots: action, result, covered scope, uncovered scope, residual risk, and confidence grade.
23. Produce one unified response instead of disconnected role fragments.

## Output template

**For Direct Answer Mode (Default):**
- Technical Analysis
- Solution (with code/config examples)
- Implementation Steps
- Expected Results

**For Multi-Expert Execution Mode (NEW):**
- Expert Team Roster (2-4 experts)
- Individual Expert Analyses (actual execution outputs)
- Synthesized Solution (integrated from all perspectives)
- Implementation Steps (unified path)

**For Expert Routing Mode:**
- Expert Selection (one line: who and why)
- Expert's Technical Analysis
- Solution
- Implementation Steps

**For Full Workflow Mode:**
- `Selected route`
  - lead, assistants, workflow bundle, and why this route won
- `Fallback`
  - clarification path or downgraded route when confidence or evidence is weak
- `Next step`
  - smallest executable action, required artifact, and resume anchor

For the full user-facing response contract, use `references/output-contract.md`.

## Quick examples

- `前端性能慢，怎么优化？`（单域简单优化）
  - Route into Direct Answer Mode: 给出具体优化方案，跳过团队编排。
- `微服务架构拆分规划`（多域协作）
  - Route into Multi-Expert Execution: 调用 Sentinel Architect（架构）+ Database Expert（数据）+ DevOps Specialist（部署），收集各自方案，综合输出。
- `React 应用全面性能优化`（多域协作）
  - Route into Multi-Expert Execution: 调用 Frontend Performance Expert（运行时）+ Build Tool Specialist（构建）+ Code Review Expert（代码质量），综合三方建议。
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
- Workflow quality and trigger health:
  [references/workflow-quality-baseline.md](references/workflow-quality-baseline.md) and
  [references/trigger-health-baseline.md](references/trigger-health-baseline.md)
- Goal framing and anti-entropy governance:
  [references/goal-framing-protocol.md](references/goal-framing-protocol.md) and
  [references/anti-entropy-governance.md](references/anti-entropy-governance.md)
- Optional product-discovery and prototype-design stage councils:
  [references/stage-council-protocol.md](references/stage-council-protocol.md)
- Harness engineering constraint gate:
  [references/harness-engineering-constraint-protocol.md](references/harness-engineering-constraint-protocol.md)
- Team Engine Lite, Worker / Verifier cycle, controlled real subagent runtime, and external Agent backend soft orchestration:
  [references/team-engine-lite-protocol.md](references/team-engine-lite-protocol.md),
  [references/worker-verifier-cycle-protocol.md](references/worker-verifier-cycle-protocol.md),
  [references/real-subagent-runtime-protocol.md](references/real-subagent-runtime-protocol.md),
  [references/subagent-exec-guide.md](references/subagent-exec-guide.md) ⭐, and
  [references/external-agent-backend-orchestration-protocol.md](references/external-agent-backend-orchestration-protocol.md)
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
