---
name: virtual-intelligent-dev-team
archetype: router
description: Bounded work-loop router for complex software tasks. Routes to the smallest defensible workflow with one semantic lead from 8 specialists (Java Virtuoso, Sentinel Architect, Technical Trinity, Code Audit Council, Git Workflow Guardian, World-Class Product Architect, Data Pipeline Guardian, API Contract Sentinel), attaches copilots only when useful, asks intent-confirmation for fuzzy ideas, and closes with verifiable evidence.
---

# Virtual Intelligent Dev Team

Route complex software work into the smallest defensible delivery workflow, keep one semantic lead, and close the task with verifiable evidence and a resume anchor.

## Positioning

This skill is not only an expert router. It is a bounded work-loop skill for complex tasks.

It has seven core closure layers plus one optional stage-council overlay:

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
   - Code-facing delivery uses Worker / Verifier separation, max-cycle retry, remediation patch, controlled real subagent runtime eligibility, external-agent soft orchestration fallback, and a DeliveryCycleReport before Lead acceptance.
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
3. Keep Direct Answer advice-only. If the user asks for code edits, refactors, bug fixes, verification, commits, release readiness, or repeated iteration, route to the smallest delivery bundle instead.
3.5. Use Multi-Expert Execution only when multiple specialist perspectives materially change the result. Spawn real experts only when runtime evidence exists; otherwise label the result as soft expert orchestration.
4. If the request is a narrow implementation or bug fix, use quick slice delivery instead of a full product or planning workflow.
5. Choose one lead agent.
6. Add one or two assistant agents only when they add clear value.
7. Enable governance or process guardrails only when needed.
8. Use a compact handoff when lead and assistants need structured coordination.
9. If the request is primarily about building AI-readable project context, route execution to `skill-forge` and its project knowledge capture protocol after the software-risk lanes are identified.
10. If the request is a fuzzy idea or low-information route-changing ask, ask one intent-confirmation question before treating the provisional route as final.
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

Read indexes first; do not flatten the whole skill into this file.

- Playbook and protocol index:
  [references/playbook-index.md](references/playbook-index.md)
- Execution-quality guardrails:
  [references/execution-quality-guardrails.md](references/execution-quality-guardrails.md)
- Output mode selection:
  [references/mode-selection-protocol.md](references/mode-selection-protocol.md)
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
- Team catalog:
  [references/agent-catalog.md](references/agent-catalog.md)
- Maintainer-facing project docs:
  [README.md](README.md) and [docs/README.md](docs/README.md)

## Governance & Observability (v5.0+)

The skill exposes a governance layer alongside the routing layer:

- **Decision log**: every route decision appends one JSON line to
  `.skill-metrics/decision-log.jsonl`. Schema: `references/decision-log.schema.json`.
  Legacy `governance_events.jsonl` entries can be migrated with
  `scripts/migrate_governance_events.py` (one-shot, idempotent).
- **Agent manifest**: each lead agent in `references/agent-catalog.md` and
  `references/routing-rules.json` declares `Constraints` (hard
  guardrails the LLM must enforce) and `Evidence Requirements` (what the
  agent must produce before claiming done/ready/ship).
- **Health check**: `scripts/check_harness_health.py` validates Agent
  Identity, Agent Manifest, Routing Rules, Workflow Bundles, Decision Log
  readability, and Language Profiles presence.
- **Dashboard**: `scripts/inspect_decision_log.py` summarizes the decision
  log as JSON / Markdown / self-contained HTML.

Typical invocations:

```bash
# Health snapshot
python scripts/check_harness_health.py --pretty

# Decision log summary (stdout JSON)
python scripts/inspect_decision_log.py --pretty

# Markdown + HTML report (paths are required)
python scripts/inspect_decision_log.py \
  --markdown-output .skill-metrics/decision-log-report.md \
  --html-output .skill-metrics/decision-log-report.html

# One-shot legacy migration (run once after upgrading)
python scripts/migrate_governance_events.py --pretty
```

## Language Profile Loading (v5.0+)

Language support is split into three orthogonal layers:

1. **Routing** — `references/routing-rules.json → language_profiles`
   decides which lead agent handles the request (13 profiles: python / go
   / nodejs / rust / java / kotlin / swift / cpp / csharp / php / ruby /
   elixir / scala).
2. **Context** — `references/language-profiles.yaml → profiles.<lang>`
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

### Primary Routes

| Trigger family | Selected route | Default lead | Fallback |
| --- | --- | --- | --- |
| review / audit / security | audit-fix-deliver | Code Audit Council | Technical Trinity when implementation follow-up dominates |
| git / branch / pr / push | govern-change-safely | Git Workflow Guardian | Technical Trinity when git is incidental |
| rewrite / migration / plan-first | plan-first-build | Technical Trinity | Sentinel Architect (NB) when risk or research-first signals dominate |
| iteration / retry / optimize | bounded-iteration | Technical Trinity | Sentinel Architect (NB) when repeated failures require root-cause discipline |
| release / ship / hold | ship-hold-remediate | Technical Trinity | Git Workflow Guardian when delivery governance overtakes release evidence |
| beta / staged validation / rollout feedback | beta-feedback-ramp | World-Class Product Architect | Technical Trinity when product signals are weak and implementation dominates |
| data pipeline / ETL / stream processing | data-pipeline-govern | Data Pipeline Guardian | Technical Trinity when infrastructure-only |
| API design / contract / versioning | api-contract-govern | API Contract Sentinel | Technical Trinity when implementation-only |

### Stage Council Overlays

These overlays sit under `product-spec-deliver`; they do not replace the selected lead or workflow bundle.

| Trigger family | Overlay | Lead remains |
| --- | --- | --- |
| PRD / product strategy / user research / competitor / metrics / roadmap / stakeholder | product-discovery-council | World-Class Product Architect |
| high-fidelity prototype / runnable HTML prototype / design system / visual design / accessibility | prototype-design-council | World-Class Product Architect |

### Routing Score Model

1. **Explicit priority routing** — `priority_routing_rules` handle hard priority scenarios like "audit before language stack", "explicit Git workflow before general engineering".
2. **Positive keyword scoring** — accumulate by weight when `positive` keywords match.
3. **Negative keyword penalty** — subtract penalty to reduce false triggers and cross-domain leakage.
4. **Score clamping** — `final_score = clamp(positive_score - negative_score, 0, max_agent_score)`.
5. **Confidence** — `confidence = top1_score / max(top3_total_score, 1)`.
6. **Language detection** — `language_profiles` identify `python/go/nodejs/rust/java/kotlin/swift/cpp/csharp/php/ruby/elixir/scala` and map to lead agents.
7. **Matching boundaries** — Chinese: substring match; English: word boundary match (short words like `pr`, `ui`, `go` require technical context).

### Thresholds

- `high_confidence` (0.55): single lead
- `medium_confidence` (0.35): lead + 1 assistant
- Below `medium_confidence`: lead + 2 assistants, suggest clarification
- `sentinel_overlay_threshold` (6): trigger governance overlay

### Fallback Rules

- If explicit process skill detection is stronger than specialist routing, prefer the process route.
- If the request is low-information and no route clears confidence, ask one clarification question.
- If the task is single-domain and low-risk, keep one lead and suppress ceremony.
- Always return the smallest executable next step plus the correct resume anchor.

## Workflow Bundles

Use workflow bundles when routing should return more than a lead agent. A bundle is the smallest reusable delivery journey for a recurring request shape.

### 1. `plan-first-build`

- **Use when**: rewrite, migration, architecture overhaul, or "plan first" requests
- **Sequence**:
  1. Lock scope, target, and constraints
  2. Create compact system map when target area is unfamiliar
  3. Create planning pack
  4. Split execution into vertical slices with AFK/HITL classifications
  5. Create progress anchor and durable `.skill-context/project-context.md`
  6. Hand back to normal implementation routing
- **Resume anchor**: `docs/progress/MASTER.md`

### 2. `product-spec-deliver`

- **Use when**: product scope, user flow, acceptance criteria, or frontend/backend contract alignment
- **Sequence**:
  1. Define target user and primary outcome
  2. Lock smallest acceptable scope
  3. Sharpen shared language when product terms are ambiguous
  4. Write user flow and acceptance criteria
  5. Split build work into vertical slices when feature spans layers
  6. Surface frontend/backend contract questions before implementation
- **Resume anchors**: `.skill-product/current-slice.md`, `.skill-product/acceptance-criteria.md`

### 3. `audit-fix-deliver`

- **Use when**: review findings and remediation path in one motion
- **Sequence**:
  1. Findings first
  2. Separate blockers from follow-up improvements
  3. If P0/P1/P2 batch fixes requested: freeze findings, build batch order, fix one batch, verify, commit
  4. Resume anchor: last verified batch

### 4. `govern-change-safely`

- **Use when**: Git workflow, branch strategy, PR sequencing, or merge safety
- **Sequence**:
  1. Assess current branch state and work-in-progress
  2. Determine safest change path (worktree, branch, or patch)
  3. Execute with rollback plan
  4. Verify clean state before proceeding

### 5. `ship-hold-remediate`

- **Use when**: release readiness decisions
- **Sequence**:
  1. Run release gate checks
  2. Produce `ship` / `hold` decision with evidence
  3. If `hold`: generate remediation plan with priority order
  4. Resume anchor: release-gate report

### 6. `bounded-iteration`

- **Use when**: optimization loops, benchmark comparison, repeated retries
- **Sequence**:
  1. Lock objective: target outcome, baseline, metric, constraints, max rounds
  2. Each round: define candidate → state hypothesis → validate → record evidence → decide (`keep`/`retry`/`rollback`/`stop`)
  3. Closure: finalize ledger, write reflection, preserve patterns
- **Caps**: live requests ≤3 rounds, offline ≤120 rounds, same hypothesis ≤2 retries

### 7. `beta-feedback-ramp`

- **Use when**: staged validation or rollout risk control
- **Sequence**:
  1. Define cohort and success criteria
  2. Run staged rollout with feedback capture
  3. Analyze signals and decide ramp/hold/rollback
  4. Resume anchor: beta status report

### Bundle Confidence Levels

| Bundle | Confidence | Source |
|--------|-----------|--------|
| `ship-hold-remediate` | 0.98 | process-skill (explicit release gate) |
| `plan-first-build` | 0.96 | process-skill (explicit planning request) |
| `root-cause-remediate` | 0.93 | process-skill (explicit iteration) |
| `audit-fix-deliver` | 0.88 | keyword+lead |
| `govern-change-safely` | 0.85 | keyword+lead |
| `direct-execution` | 0.35 | fallback (no strong bundle match) |

Use bundle as explicit execution journey when `bundle_confidence >= 0.6`. Keep execution lightweight when `bundle_confidence < 0.6`.
