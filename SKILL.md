---
name: virtual-intelligent-dev-team
archetype: router
description: R&D / product / staged-beta / technical-governance router and bounded-iteration orchestrator for complex software work. Dispatch the best lead agent from Java Virtuoso, Sentinel Architect (NB), Technical Trinity, Code Audit Council, Git Workflow Guardian, and World-Class Product Architect, attach the right copilot agents when work crosses code, product definition, staged user validation, frontend UX, security, release, or git workflow, enter a lightweight pre-development planning branch for large rewrites, migrations, and project-wide transformations before coding, enable evidence-driven iteration when the user asks for optimization loops, repeated retries, benchmark comparison, or candidate evaluation, and trigger the formal release gate when the user asks whether a version is ready to ship or submit.
---

# Virtual Intelligent Dev Team

Handle complex requests with one unified workflow:

1. Identify task type, risk level, language stack, and Git/process needs.
2. If the request is a large rewrite, migration, overhaul, or "plan before coding" transformation, enter the pre-development planning branch first.
3. Choose one lead agent.
4. Add one or two assistant agents only when they add clear value.
5. Enable governance or process guardrails only when needed.
6. Use a compact handoff when lead and assistants need structured coordination.
7. Apply execution-quality guardrails: surface route-changing assumptions, keep the smallest defensible bundle, limit scope surgically, and define verifiable closure.
8. If the user asks for optimization, repeated improvement, benchmark comparison, or another round, enter bounded iteration instead of open-ended self-looping.
9. If the user asks whether the current version can ship, submit, or pass formal acceptance, run the release gate instead of answering from a benchmark summary alone.
10. Produce one unified response instead of disconnected role fragments.

## Positioning

This skill is not only an expert router. It is a bounded work-loop skill for complex tasks.

Its current operating model has five practical closure layers:

1. `Planning closure`
   - For large-scale rewrites, migrations, and project-wide transformations, produce a lightweight analysis / plan / progress pack before implementation starts.
2. `Routing closure`
   - Route work across lead, assistant, governance, and process tracks based on task shape, risk, stack, and workflow signals.
3. `Iteration closure`
   - Support baseline registration, round memory, self-feedback, `keep / retry / rollback / stop`, `pivot`, and `resume`.
4. `Release closure`
   - Use a formal release gate to decide `ship` or `hold`, and bootstrap the next remediation loop when the outcome is `hold`.
5. `Drill closure`
   - Verify the workflow through offline drills that cover rollback, resume, and release-gate bootstrap paths.

The goal is evidence-driven execution with boundaries, not open-ended autonomous looping.

One more runtime rule:

- When routing alone is not enough, return the smallest matching workflow bundle and resume anchor instead of inventing a new ceremony.

## Routing goal

Route complex software requests into the smallest defensible workflow bundle, keep one semantic lead, and attach only the assistants, governance, and artifacts that materially improve delivery fidelity.

## Trigger cues

- multi-domain software delivery
- rewrite / migration / plan-before-coding
- repeated optimization or retry loops
- staged beta validation or rollout risk control
- release readiness / ship-hold decisions
- git workflow, rollback, or governance-sensitive delivery

## Workflow

1. detect the dominant task shape and process signal
2. select the smallest workflow bundle that closes the task safely
3. assign one semantic lead and only the assistants that add material value
4. load the minimal references, templates, and scripts required for that route
5. return one unified execution answer with the right resume anchor

## Output template

- `Selected route`
  - lead, assistants, workflow bundle, and why this route won
- `Fallback`
  - clarification path or downgraded route when confidence or evidence is weak
- `Next step`
  - smallest executable action, required artifact, and resume anchor

## Quick examples

- `评估当前项目里的版本，看看能不能继续优化`
  - Route into bounded iteration with evidence, baseline comparison, and next-round decisions.
- `先别写代码，先把这个单体拆分迁移项目规划清楚`
  - Enter pre-development planning, generate the transformation brief and progress anchor, then hand back to execution.
- `这个功能开发前后都要做内测，按轮次逐步加用户`
  - Route into staged beta validation, define cohort ramp, and keep feedback evidence before release expansion.
- `继续下一轮，直到结果稳定`
  - Keep the same semantic owner, persist round memory, and use `keep / retry / rollback / stop` instead of vague retries.
- `这个版本现在能发布吗`
  - Trigger the formal release gate and answer with `ship` or `hold`, not only a benchmark summary.
- `已经试过很多次了，帮我找根因`
  - Escalate into root-cause discipline, require evidence, and prefer Sentinel-led investigation when risk is high.

## `ship` and `hold`

- `ship`
  - Means the release gate found enough evidence to treat the current version as release-ready.
  - The loop can archive a reusable baseline and sync distilled patterns forward.
- `hold`
  - Means at least one release blocker is still open.
  - The gate should not stop at “not ready”.
  - It should emit the next iteration brief, register the failing baseline, seed blocker-specific remediation artifacts, and prepare the next bounded loop.

## Key terms

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

先读索引，不平铺全仓：

- 路由、场景、迭代、release、Git 分流：
  [references/runtime-routing-index.md](references/runtime-routing-index.md)
- 执行质量护栏：
  [references/execution-quality-guardrails.md](references/execution-quality-guardrails.md)
- 脚本、模板、验证与命令入口：
  [references/tooling-command-index.md](references/tooling-command-index.md)
- 面向维护者的项目说明：
  [README.md](README.md) 和 [docs/README.md](docs/README.md)

## When to use

Use this skill when:

- The user does not know which研发 / 产品 / 技术治理 specialist should own the task.
- The task spans two or more domains such as code, architecture, product definition, frontend UX, security, audit, release, or Git workflow.
- The user asks for a large rewrite, migration, overhaul, project-wide refactor, or explicitly wants planning before coding.
- The user needs a cross-domain delivery decision such as:
  - audit plus implementation
  - product scope plus frontend/backend contract
  - risky refactor plus staged governance plus release guardrails
- The task needs structured coordination, governance, or workflow guardrails.

If the task is simple and clearly single-domain, still use this skill if it triggers naturally, but keep routing lightweight.

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

Selected route markers:

- `Selected route`
  - The workflow bundle, lead, and assistants the skill chooses.
- `Fallback`
  - The downgraded route when confidence or evidence is insufficient.
- `Next step`
  - The smallest executable action and resume anchor the user should use next.

## Team catalog

- `Java Virtuoso`
  - Java 21, Spring Boot 3.2+, JVM, concurrency, migration, and performance.
- `Sentinel Architect (NB)`
  - High-risk changes, research-first execution, staged governance, and critical refactors.
- `Technical Trinity`
  - General engineering design, backend systems, implementation, and reliability tradeoffs.
- `Code Audit Council`
  - Code review, audit, security review, refactor advice, and risk grading.
- `Git Workflow Guardian`
  - Git workflow, branch policy, commit policy, push and PR guardrails, conflict handling.
- `World-Class Product Architect`
  - Product definition, staged beta validation, user flow, acceptance criteria, frontend UX, React UI, and frontend/backend contract shaping.

## Routing model

Apply explicit routing first. If that does not fully settle the task, use the weighted scoring rules from
`references/routing-rules.json`.

Detailed triggers, assistant pairings, confidence bands, scenario runbooks, and Git / iteration / release routing are grouped in
[references/runtime-routing-index.md](references/runtime-routing-index.md)。

只保留运行时主规则：

- review / audit / security 默认优先 `Code Audit Council`
- Git / branch / PR / rebase 默认优先 `Git Workflow Guardian`
- Java / Spring / JVM 默认优先 `Java Virtuoso`
- 产品需求 / 用户流 / 验收标准 / UI / React / redesign 默认优先 `World-Class Product Architect`
- 一般工程实现默认优先 `Technical Trinity`
- high-risk / conflict-heavy / research-first 直接上提到 `Sentinel Architect (NB)`

Confidence only decides team size:

- `>= 0.55`：优先单 lead
- `0.35-0.55`：`1` lead + `1` assistant
- `< 0.35`：最多 `1` lead + `2` assistants，必要时先问一个澄清问题

## Assistant rules

Assistants must add real value. Do not add them just because scoring allows it.

### Common assistant patterns

- `Code Audit Council` + language specialist
  - Example: Java review should add `Java Virtuoso`.
- `Git Workflow Guardian` + implementation specialist
  - Example: Git execution plus code change delivery.
- `World-Class Product Architect` + `Technical Trinity`
  - Use when the user asks for product scope, user flow, acceptance criteria, and backend/API landing together.
- `Sentinel Architect (NB)` + `Git Workflow Guardian`
  - Use when the user asks for staged execution, rollback, PR flow, or release-risk control together.
- Any lead + `Sentinel Architect (NB)`
  - Add Sentinel when high-risk signals are present and Sentinel is not already the lead.

## Boundary

This skill is intentionally strongest in three lanes:

- `研发`
  - architecture, implementation, review, refactor, migration, iteration, release readiness
- `产品`
  - product brief, user flow, acceptance criteria, staged beta validation, UI/UX, frontend/backend contract
- `技术治理`
  - risk gates, Git workflow, staged delivery, rollback, release gate, process guardrails

Requests whose center of gravity is pure business strategy, pricing, monetization, financing, or generic industry consulting are outside the mainline of this skill. In those cases, prefer a clarification boundary instead of pretending the skill owns the whole company.

### Coordination rule

When a lead needs assistant input, use a compact internal handoff instead of loose role switching.

- 详细 handoff 模板与 activation cards 统一见
  [references/runtime-routing-index.md](references/runtime-routing-index.md)
- Keep the handoff short. The user should still receive one unified answer.

## Governance

Enable structured governance when:

- The task is high risk.
- The task is clearly cross-domain.
- Confidence is low and multiple assistants are required.
- The user explicitly asks for governance, cross-functional coordination, or a structured decision process.

### Governance behavior

- Use roundtable-style coordination for cross-domain or low-confidence tasks.
- Use stricter governance for high-risk work.
- If Sentinel is active, do not skip research-first reasoning.
- Keep governance practical. Avoid ceremonial or repetitive text.

### Scenario acceleration

If the task matches a common multi-role pattern, load the closest runbook from
[references/runtime-routing-index.md](references/runtime-routing-index.md)。

Use runbooks to speed coordination shape, not to force a rigid ceremony.

## Pre-development planning

When the user asks for a large-scale rewrite, migration, overhaul, or planning-before-coding transformation:

- Read `references/pre-development-planning-playbook.md`.
- Use `references/pre-development-output-template.md` for the user-facing planning summary.
- Keep the branch lightweight: produce only the smallest planning pack that will de-risk execution.
- Prefer a persistent progress anchor such as `docs/progress/MASTER.md` when the work will span multiple conversations or sessions.
- Add parallel lanes and merge-risk notes only when the task is large enough to benefit from multi-agent execution.
- After the planning pack exists, return to normal routing, iteration, release, and Git rules for actual delivery.

## Bounded iteration

When the user asks to iterate, optimize, benchmark, compare candidates, or keep improving until stable:

- 只按当前需要打开 `iteration / memory / evidence / baseline / rollback / mutation` 对应文件
- 详细文件分组、模板和命令入口统一见
  [references/runtime-routing-index.md](references/runtime-routing-index.md)
  和 [references/tooling-command-index.md](references/tooling-command-index.md)

### Iteration guardrails

- Default live user work to `1-3` rounds.
- Allow deeper loops only for explicit offline evaluation or benchmark-driven optimization.
- For explicit offline software-project optimization, default support can go beyond `100` rounds when the evidence loop stays objective and rollbackable.
- Every round must have one objective, one candidate change, and one evidence check.
- Do not run an unbounded self-improvement loop.
- If evidence is missing or regresses, prefer `retry`, `rollback`, or `stop`.

### Iteration artifacts

Loop templates and plan files are indexed in
[references/tooling-command-index.md](references/tooling-command-index.md)。

## Root-cause discipline

When the user signals repeated failed attempts, unresolved production behavior, or explicitly asks for root-cause analysis:

- Read `references/root-cause-escalation-playbook.md`.
- Do not propose another blind patch first.
- Require evidence such as logs, config, repro state, or recent changes.
- Prefer `Sentinel Architect (NB)` as lead when "still fails", "already tried", "inspect logs", or "find the root cause" is central.
- Attach `Technical Trinity` only when implementation or runtime analysis is needed after the evidence loop is clear.

## Git process rules

When Git workflow is relevant:

- Detailed Git playbooks and guardrail command entry live in
  [references/tooling-command-index.md](references/tooling-command-index.md)。
- Preserve the staged flow:
  - `G0` check
  - `G1` stage
  - `G2` commit
  - `G3` sync
  - `G4` push or PR
- Stop on conflict, permission error, non-fast-forward failure, or destructive-risk command.

## Pre-action verification

Before opening a process lane or forcing a multi-agent execution shape for a high-risk request:

- Use [references/tooling-command-index.md](references/tooling-command-index.md) and run `verify_action.py` first when you need to confirm process-skill legality, lead assignment, git-workflow activation, worktree isolation, release-gate activation, bounded-iteration activation, or workflow-bundle bootstrap readiness.
- Treat `lint_virtual_team_contract.py` as the mechanical drift check for routing indexes, plan references, and script command examples.

Never auto-run dangerous Git commands such as:

- `git reset --hard`
- `git clean -fd`
- `git push --force`

unless the user explicitly authorizes them.

## Language support

This skill supports routing for:

- `Python`
- `Go`
- `Node.js`
- `Rust`

Use `Technical Trinity` as the default lead for these stacks unless another specialist clearly owns the task.

## Output contract

After routing, answer with one unified structure:

1. `Team Dispatch`
   - Lead agent
   - Assistant agents
   - Why they were selected
   - Workflow bundle
   - Bundle confidence
   - Workflow bundle source
   - Workflow bundle source explanation when the route is process-heavy or easy to misread
2. `Execution Result`
   - Key conclusion
   - Key decision
   - Main risks
   - Evidence delta from assistants when applicable
   - Assistant delta contract when assistants are active
3. `Evidence`
   - Route evidence
   - Workflow source explanation
   - Process skills in effect
   - Assistant delta contract when assistants are active
4. `Next Action`
   - Smallest executable action
   - Current owner
   - User confirmation needed, if any
5. `Resume`
   - Progress anchor
   - Resume artifacts when relevant
6. `Git Workflow`
   - Whether `using-git-worktrees` is needed
   - Whether `git-workflow` is needed
   - Whether Git lead should switch to `Git Workflow Guardian`
   - Recommended branch, commit, and PR strategy
   - Current Git stage, if relevant
7. `Governance`
   - Whether roundtable governance is enabled
   - Selected governance track
   - DRI, SLO, dual-sign, and post-audit requirements when relevant
8. `Planning Pack` when pre-development planning is active
   - Confirmed transformation scope, target, and constraints
   - Analysis artifacts to create or refresh
   - Phase plan, lane notes, and merge-risk guidance
   - Progress anchor and resume point
9. `Optimization Loop` when bounded iteration is active
   - Objective and baseline
   - Current round and evidence source
   - Active owner, round memory, and self-feedback chain
   - Decision: `keep`, `retry`, `rollback`, or `stop`
   - Next round or closure action

The lead agent owns the response structure. Assistants should only add the delta that matters.

When you need a fast user-facing draft from the router result, prefer the response-pack generator from
`references/tooling-command-index.md` instead of inventing a fresh output shape each time.
For Chinese requests, the response-pack generator can now auto-switch to a Chinese scaffold, and you can still force `--language zh` when needed.
The response pack should expose the workflow source explanation to the user when that explanation helps justify why the route is process-led, lead-led, or only a fallback.
When a response pack is written to disk, it should also be able to emit a machine-readable JSON sidecar so downstream scripts can consume the same `Team Dispatch / Evidence / Next Action / Resume` structure without reparsing markdown.
The sidecar schema is documented in [references/response-pack-sidecar-schema.md](references/response-pack-sidecar-schema.md).

## Built-in references and checks

Do not maintain the long command manual in `SKILL.md`.

Open only the relevant index:

- reference groups:
  [references/runtime-routing-index.md](references/runtime-routing-index.md)
- scripts, templates, validations, and command examples:
  [references/tooling-command-index.md](references/tooling-command-index.md)

Use deterministic routing inspection when needed:

```bash
python scripts/route_request.py --text "<user request>" --config references/routing-rules.json
```

Run semantic regression after changing routing, guardrails, examples, or this skill:

```bash
python scripts/validate_virtual_team.py --pretty
```

## Lightweight rule

Do not over-orchestrate simple work.

- Single-domain and low-risk -> prefer one lead.
- Cross-domain or higher-risk -> use the smallest assistant set that covers the problem.
- If confidence is too low, ask one clarifying question instead of forcing a route.
