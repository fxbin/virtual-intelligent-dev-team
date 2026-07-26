---
name: virtual-intelligent-dev-team
archetype: router
description: Bounded work-loop router for complex software tasks. Routes to the smallest defensible workflow with one semantic lead from 8 specialists (Java Virtuoso, Sentinel Architect, Technical Trinity, Code Audit Council, Git Workflow Guardian, World-Class Product Architect, Data Pipeline Guardian, API Contract Sentinel), attaches copilots only when useful, asks intent-confirmation for fuzzy ideas, and closes with verifiable evidence.
---

# Virtual Intelligent Dev Team

Route complex software work into the smallest defensible delivery workflow, keep one semantic lead, and close the task with verifiable evidence and a resume anchor.

## Positioning

This skill is a bounded work-loop router for complex tasks. Routing is one of its closures; the full set is six closure layers, one delivery subgraph, and one optional stage-council overlay:

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
Delivery subgraph:

- `Team Engine Lite`（Delivery closure 内子图，非独立层）
   - Code-facing delivery uses Worker / Verifier separation, max-cycle retry, remediation patch, controlled real subagent runtime eligibility, external-agent soft orchestration fallback, and a DeliveryCycleReport before Lead acceptance.
   - Verifier 独立性由"禁止上游预判下游"硬约束(P0-3)保证,而非独立成层。详见 `references/team-engine-lite-protocol.md` 和 `references/verifier-extraction-guide.md`。
Optional overlay:

- `Stage council overlay`
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

## Quick examples

| User request | Route shape | Why |
|-------------|-------------|-----|
| "前端性能慢，怎么优化？" | Direct Answer | Single-domain, well-scoped question |
| "微服务架构拆分规划" | Multi-Expert | Spans architecture, product, and delivery |
| "设计一个用户认证系统" | Full Workflow | Requires product spec + API contract + implementation |
| "这个 PR 有安全问题吗？" | Expert Routing | Clear specialist domain (security audit) |
| "帮我重构这段 Python 代码" | Quick Slice | Code-editing refactor needs delivery evidence |
| "发布这个版本到生产环境" | Full Workflow | Needs release gate + ship/hold decision |
| "设计 Kafka 实时数据管道" | Expert Routing | Clear domain: Data Pipeline Guardian |
| "API 版本兼容性怎么保证" | Expert Routing | Clear domain: API Contract Sentinel |

## Key terms

- **Workflow bundle** - Parameterized pipeline for a closure type (delivery/governance/lifecycle)
- **Quick slice** - Narrow, time-boxed implementation with minimal ceremony
- **Baseline** - Snapshot of current state before changes, for comparison and rollback
- **Round memory** - Accumulated context across iteration rounds
- **Self-feedback** - LLM evaluates its own output against acceptance criteria
- **Pivot** - Change direction based on new evidence or failed validation
- **Resume anchor** - File path where workflow state is preserved for interruption recovery
- **Project context** - Durable project rules, commands, architecture constraints, forbidden changes, and verification defaults shared across slices

## Workflow

1. Identify task type, risk level, language stack, and Git/process needs.
2. Choose the smallest output mode with [references/mode-selection-protocol.md](references/mode-selection-protocol.md): Direct Answer, Multi-Expert Execution, Expert Routing, or Full Workflow.
3. Keep Direct Answer advice-only. If the user asks for code edits, refactors, bug fixes, verification, commits, release readiness, or repeated iteration, route to the smallest delivery bundle instead. Use Multi-Expert Execution only when multiple specialist perspectives materially change the result; spawn real experts only when runtime evidence exists, otherwise label the result as soft expert orchestration.
4. If the request is a narrow implementation or bug fix, use quick slice delivery instead of a full product or planning workflow.
5. Choose one lead agent.
6. Add one or two assistant agents only when they add clear value.
7. Enable governance or process guardrails only when needed.
8. Use a compact handoff when lead and assistants need structured coordination.
9. If the request is primarily about building AI-readable project context, route execution to `skill-forge` and its project knowledge capture protocol after the software-risk lanes are identified.
10. If the request is a fuzzy idea or low-information route-changing ask, ask one intent-confirmation question before treating the provisional route as final.
10.5. Worktree semantic review: `needs_worktree` from the router is a keyword-based first pass, not a final verdict. When it is true, confirm the task genuinely involves parallel work or workspace isolation; if it was a false trigger (e.g. the user mentioned "two" in passing but the work is a single coherent task), downgrade and do not force a worktree. When it is false but the task clearly needs parallel isolation (multiple independent changes that must not interfere), suggest a worktree to the user and explain the benefit. Record the review outcome as a route-changing assumption.
11. Apply execution-quality guardrails: surface route-changing assumptions, keep the smallest defensible bundle, limit scope surgically, and define verifiable closure.
12. For broad, repeated-failure, release, beta, multi-agent, or drift-prone work, apply goal framing: success evidence, stop condition, and non-goals must be explicit before implementation.
13. For code-facing routes, apply the Harness constraint gate before implementation: create or refresh `.vidt/harness/engineering-constraints.md`.
14. For changes that add or retire guards, fallbacks, adapters, duplicate owners, compatibility paths, schema, persistence, or source-of-truth behavior, apply anti-entropy governance before choosing delete, compat, or confirmation paths.
15. For code-facing, release-facing, Git-facing, or remediation routes, apply Team Engine Lite: Worker can produce, Verifier can return pass/fail/hold/spec_violation, and Lead can accept only after a DeliveryCycleReport.
16. If the user explicitly asks for multi-agent / subagent / parallel agent execution, or `/auto` reaches an eligible workflow, build a controlled real subagent runtime plan with three tiers: `real_subagent_runtime` (host exposes spawn / wait / merge), `single_backend_multi_session` (host exposes create_session / kill_session / restart_session; session is the circuit-breaker unit), or `soft_orchestration_only` (no isolation; `known-shortcut:` ceiling). The host downgrades to the highest tier it can actually enforce; never upgrade beyond proven capability.
17. If external Agent backends are available but real subagent runtime is not proven, check whether the host supports `single_backend_multi_session` (session-level circuit breaking) before falling back to `soft_orchestration_only`. `soft_orchestration_only` is the last resort with a `known-shortcut:` ceiling (no session kill / restart / context isolation).
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

**For Multi-Expert Execution Mode:**
- Expert Team Roster (2-4 experts)
- Individual Expert Analyses (actual execution outputs only when real runtime exists; otherwise clearly labeled expert-lens analysis)
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

## Runtime references

Read indexes first; do not flatten the whole skill into this file. Authoritative entry points:

- [references/playbook-index.md](references/playbook-index.md) — playbooks, protocols, and core reference index
- [references/tooling-command-index.md](references/tooling-command-index.md) — scripts, commands, and asset entrypoints
- [references/agent-catalog.md](references/agent-catalog.md) — 8 lead specialists and their constraints
- Maintainer-facing docs: [README.md](README.md) and [docs/README.md](docs/README.md)

## Governance & Observability (v5.0+)

The skill exposes a governance layer alongside the routing layer:

- **Decision log**: every route decision appends one JSON line to
  `.vidt/metrics/decision-log.jsonl`. Schema: `references/decision-log.schema.json`.
- **Agent manifest**: each lead agent in `references/agent-catalog.md` and
  `references/routing-rules.json` declares `Constraints` (hard
  guardrails the LLM must enforce) and `Evidence Requirements` (what the
  agent must produce before claiming done/ready/ship).
- **Health check**: `scripts/check_harness_health.py` validates Agent
  Identity, Agent Manifest, Routing Rules, Workflow Bundles, Decision Log
  readability, and Language Profiles presence.
- **Dashboard**: `scripts/inspect_decision_log.py` summarizes the decision
  log as JSON / Markdown / self-contained HTML.
- **Telemetry**: `scripts/emit_telemetry.py` writes per-layer execution
  traces with intent drift probe to `.vidt/metrics/telemetry.jsonl`
  (contract: [references/observability-protocol.md](references/observability-protocol.md)).
- **Layer health**: `scripts/inspect_decision_log.py --health-report`
  emits per-layer SLO status, failure counts, and breaker state from
  telemetry + circuit breaker state files.
- **Stress scenarios**: `scripts/run_stress_scenarios.py` runs 12
  failure scenarios — 7 multi-role failure scenarios (contract mismatch /
  worker self-pass / lead skips verifier / verifier always-pass / baseline
  deleted / json corrupt / resume plan drift) plus 5 v6.0.1 routing/drill
  scenarios (tier selection boundary / soft fallback downgrade / circuit
  breaker escalation / multi-session lifecycle / soft-orchestration
  degradation), each with ONE runnable check. Output carries `trace_summary`
  (machine-validated: real file paths + caller list, non-empty or scenario
  fails), `fix_scope` (`root-cause` / `symptom`), and `scenario_outcome`
  (`all_scenarios_passed` / `semantic_warning` / `semantic_error`); `symptom`
  triggers benchmark warn, not fail. Status enum: `passed` / `failed` /
  `correctly_not_caught` (see §Release Notes v6.0.1 for migration). Passing
  gate: 12 scenarios executed, `trace_summary` all non-empty, `fix_scope`
  root-cause ratio >= 80%. Field-name consistency enforced by
  `quick_validate.py` (_STRESS_REQUIRED_TOP_FIELDS / _STRESS_VALID_METHODS).

Typical invocations (health snapshot, decision-log summary, markdown/HTML report) live in [references/tooling-command-index.md](references/tooling-command-index.md) §一; stress scenarios in §九.

## Language Profile Loading (v5.0+)

Language support is split into three orthogonal layers:

1. **Routing** — `references/routing-rules.json` → language_profiles
   decides which lead agent handles the request (13 profiles: python / go
   / nodejs / rust / java / kotlin / swift / cpp / csharp / php / ruby /
   elixir / scala).
2. **Context** — `references/language-profiles.yaml` → profiles.<lang>
   injects the matched agent's working memory with ecosystem defaults,
   idiomatic conventions, and canonical verification commands.
3. **Constraints** — `language-profiles.yaml → profiles.<lang>.harness_constraints`
   feeds language-specific guardrails that the LLM must enforce, layered
   on top of the matched agent's `agent_rules[*].constraints`.

When a request matches a language keyword in `routing-rules.json`:

1. Route the task to the profile's `lead_agent`.
2. Load the matching entry from `language-profiles.yaml`; the YAML
   covers all 13 routed language profiles.
3. Inject into the agent's context: ecosystem, conventions, verification
   commands, and `harness_constraints`.

If a new language is added to `routing-rules.json`, add the matching YAML
profile in the same pass so the LLM gets structured ecosystem defaults,
verification commands, and harness constraints. Run
`python scripts/check_language_profiles.py --pretty` to validate the two
files stay in sync.

**Java is an exception**: routing still prefers `Java Virtuoso`, and the
Java entry in `language-profiles.yaml` injects baseline toolchain info
(Gradle / Maven, Spring Boot 3.x, JVM 21+) that complements — but does
not replace — Java Virtuoso's depth.

## Built-in checks

Use deterministic routing inspection when needed:

```bash
python scripts/route_request.py --text "<user request>" --config references/routing-rules.json
```

Run semantic regression after changing routing, guardrails, examples, or this skill:

```bash
python scripts/validate_virtual_team.py --pretty
```

## Runtime Routing

Runtime routing rules (primary routes, stage council overlays, score model, thresholds, and fallback rules) and workflow bundle definitions (12 bundles with use-when / sequence / resume anchor / confidence levels) live in dedicated reference files:

- [references/runtime-routing-rules.md](references/runtime-routing-rules.md) — Primary Routes, Stage Council Overlays, Routing Score Model, Thresholds, Fallback Rules
- [references/workflow-bundles.md](references/workflow-bundles.md) — 12 workflow bundle definitions and Bundle Confidence Levels (each bundle has a stable `bundle_id` anchor for external reference; pseudo-bundles like `decline-and-reroute` are documented separately)

## Release Notes

完整版本历史、字段迁移指南和 Memory Keeper 计划见 [docs/release-notes.md](docs/release-notes.md)。

### v6.0.19 (2026-07-26)

- 路由生成 worktree 与迭代命令时直接复用已经解析的主仓 `state-root`，避免再次通过 shell 猜测路径。

### v6.0.18 (2026-07-26)

- 将 decision log 和 durable iteration state 统一写入主仓 state-root，修复 linked worktree、含空格路径和持久状态分裂。
- worktree 路由新增显式否定与纯规划抑制；change-localization 排除产品定位和只读审计。
- validator/test fixture 改用自动清理的系统临时目录，避免 `.tmp-validation` 泄漏污染仓库门禁。

### v6.0.17 (2026-07-25)

收窄 worktree 关键词初筛表（移除高频误触发的泛词，保留语义明确的并行隔离信号），
补负向 eval 锁定项目管理语境不应触发 worktree。v6.0.11–v6.0.16 依次引入了定位与
迭代约束强化、改动点定位与目标项目知识库协议、worktree 状态目录归属、`.vidt/`
状态目录收拢、worktree 两层判断、eval 断言与激活条件修复。详见 docs/release-notes.md。

### v6.0.10 (2026-07-23)

Pages artifact action 升级到 v4，并删除 custom Actions 静态部署链不使用的
`.nojekyll`；发布门禁与回归覆盖改为校验真实 artifact 边界。
