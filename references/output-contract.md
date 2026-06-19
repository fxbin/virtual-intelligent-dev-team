# Output Contract

## Primary Goal

**Answer the user's question directly and completely.**

Process structure is a tool, not the product. When a simple technical question has a simple technical answer, give that answer without wrapping it in team-dispatch ceremony.

---

## Output Modes

Choose the output mode based on question complexity and user needs:

### Mode 1: Direct Answer (Default)

**Use for:**
- Single-domain technical questions
- Bug fixes and debugging
- Performance optimization
- Code review requests
- "How do I..." questions

**Output structure:**
```markdown
## [直接回答标题]

[技术分析]

## 解决方案

[具体的、可操作的方案，包含代码示例或配置]

## 实施步骤

1. [步骤 1 - 具体命令或操作]
2. [步骤 2]
3. [步骤 3]

## 预期效果

[量化的预期结果]
```

**Skip these sections:**
- Team Dispatch
- Evidence
- Resume
- Git Workflow (unless explicitly needed)
- Governance

**Example questions:**
- "前端性能慢，怎么优化？"
- "这个 bug 怎么修？"
- "如何提升打包速度？"

---

### Mode 2: Multi-Expert Execution

**Use when:**
- Multi-domain problems requiring multiple perspectives
- Complex technical decisions (architecture + data + ops + security)
- Questions where diverse expert views add material value
- Examples: "微服务拆分", "React性能优化", "系统重构方案"

**Key difference from other modes:**
- Spawns multiple experts only when the host exposes real Agent spawn / wait / merge runtime evidence.
- Collects real expert outputs only when those experts were actually spawned.
- Falls back to soft expert orchestration when runtime evidence is unavailable, and labels that fallback explicitly instead of implying true parallel execution.
- Synthesizes the available perspectives into one comprehensive answer.

**Execution process:**
1. Identify 2-4 relevant experts based on problem domains.
2. Check whether the host exposes spawn / wait / merge runtime evidence.
3. If real runtime exists, spawn each expert in parallel or sequence when dependencies exist.
4. If real runtime is unavailable, keep one response, use clearly labeled specialist lenses, and mark the runtime claim as soft orchestration.
5. Synthesize all perspectives into a unified solution.

**Output structure:**
```markdown
## 多专家协作分析

### 专家团队
- **[Expert 1]**: [领域] - [分析角度]
- **[Expert 2]**: [领域] - [分析角度]
- **[Expert 3]**: [领域] - [分析角度]

---

### [Expert 1] 的分析

[实际执行后的专家输出；若未真实 spawn，则标注为 soft expert lens]

### [Expert 2] 的分析

[实际执行后的专家输出；若未真实 spawn，则标注为 soft expert lens]

### [Expert 3] 的分析

[实际执行后的专家输出；若未真实 spawn，则标注为 soft expert lens]

---

## 综合方案

[基于多个专家输出的整合方案，包含：]
- 共识点（所有专家一致认同的）
- 权衡建议（专家意见分歧时的取舍）
- 实施路径（综合各方建议的最优路径）
- 预期效果

## 实施步骤

1. [综合后的第一步]
2. [综合后的第二步]
3. [综合后的第三步]
```

**Examples:**

*Question: "微服务架构拆分规划"*
- Spawn: Sentinel Architect + Database Expert + DevOps Specialist
- Collect: 架构拆分方案 + 数据迁移策略 + 部署运维方案
- Synthesize: 综合的分阶段迁移路线图

*Question: "React 应用性能全面优化"*
- Spawn: Frontend Performance Expert + Build Tool Specialist + Code Review Expert
- Collect: 运行时优化 + 构建优化 + 代码质量改进
- Synthesize: 三阶段优化方案（立即见效 + 中期改进 + 长期重构）

---

### Mode 3: Expert Routing

**Use when:**
- Question needs specific expertise
- But doesn't require multiple experts
- Single specialist perspective sufficient

**Output structure:**
```markdown
## 路由决策

**专家：** [专家名称]  
**原因：** [一句话说明为什么需要这个专家]

## [专家视角的技术分析]

[深入的技术分析]

## 解决方案

[具体方案]

## 实施步骤

[详细步骤]
```

**Include minimal process info:**
- Lead agent (one line)
- Why selected (one line)

**Skip:**
- Full Team Dispatch structure
- Evidence sections
- Resume anchors

---

### Mode 4: Full Workflow

**Use when:**
- Large refactors or migrations
- Cross-domain coordination needed
- Release readiness checks
- Governance-sensitive changes
- Multi-phase delivery

**Output structure:**
[Use all 16 sections as defined below]

---

## Mode Selection Rule

**Default to Direct Answer Mode.**

Only escalate to Expert Routing or Full Workflow when:
- User explicitly asks for team coordination
- Task genuinely requires cross-domain work
- Governance or release gates are needed
- Risk level demands formal verification

**When in doubt, answer directly.** Users prefer actionable solutions over process ceremony.

---

## Full Workflow Output Structure

After routing, answer with one unified structure. The lead agent owns the response. Assistants should only add the delta that matters.

## User-Facing Sections

1. `Team Dispatch`
   - Lead agent
   - Assistant agents
   - Why they were selected
   - Workflow bundle
   - Bundle confidence
   - Workflow bundle source
   - Workflow bundle source explanation when the route is process-heavy or easy to misread
2. `Intent Confirmation` when the user gives a fuzzy idea or low-information route-changing request
   - Confirmation question before treating the provisional route as final
   - Stable option ids such as `product-opportunity`, `prototype-exploration`, `technical-feasibility`, `architecture-risk`, and `delivery-plan`
   - Target lead, workflow bundle, and stage council for each option
   - Provisional route retained only as a fallback, not as confirmed intent
3. `Execution Result`
   - Key conclusion
   - Key decision
   - Main risks
   - Evidence delta from assistants when applicable
   - Assistant delta contract when assistants are active
4. `Evidence`
   - Route evidence
   - Workflow source explanation
   - Process skills in effect
   - Active engineering micro-practices and their ledger anchor when any micro-practice is active
   - Active stage councils when product or prototype work needs phase-level specialists
   - Assistant delta contract when assistants are active
   - Completion evidence slots before any `done`, `fixed`, `ready`, `ship`, `commit`, `merge`, or handoff claim:
     - evidence action / check performed
     - result / exit status
     - covered scope
     - uncovered scope
     - residual risk
     - confidence grade: `A | B | C`
5. `Next Action`
   - Smallest executable action
   - Current owner
   - User confirmation needed, if any
6. `Resume`
   - Progress anchor
   - Resume artifacts when relevant
7. `Git Workflow`
   - Whether `using-git-worktrees` is needed
   - Whether `git-workflow` is needed
   - Whether Git lead should switch to `Git Workflow Guardian`
   - Recommended branch, commit, and PR strategy
   - Current Git stage, if relevant
   - For audit batch remediation, one commit record per accepted P0/P1/P2 batch:
     - batch id and severity
     - findings covered
     - files touched
     - verification evidence
     - commit message and hash after commit
     - remaining or deferred findings
8. `Governance`
   - Whether roundtable governance is enabled
   - Selected governance track
   - DRI, SLO, dual-sign, and post-audit requirements when relevant
9. `Team Engine Lite` when role-separated delivery is active
   - Whether Worker / Verifier separation is required
   - Worker and Verifier roles
   - Max cycles and acceptance gates
   - Whether Worker can self-pass
   - Runtime claim and closure verdict
   - DeliveryCycleReport evidence before Lead acceptance
10. `External Agent Backend` when soft backend orchestration is active
   - Orchestration mode
   - Runtime claim
   - Backend orchestration verdict
   - Required output contracts
11. `Real Subagent Runtime` when the route is eligible for controlled real subagent execution
   - Eligibility and activation reason
   - Current runtime claim and candidate runtime claim
   - Whether runtime evidence is still required
   - Max subagents, spawn policy, merge policy, and fallback
12. `Planning Pack` when pre-development planning is active
   - Confirmed transformation scope, target, and constraints
   - Analysis artifacts to create or refresh
   - Phase plan, lane notes, and merge-risk guidance
   - Progress anchor and resume point
13. `Optimization Loop` when bounded iteration is active
   - Objective and baseline
   - Current round and evidence source
   - Active owner, round memory, and self-feedback chain
   - Decision: `keep`, `retry`, `rollback`, or `stop`
   - Next round or closure action
14. `Goal Frame` when `references/goal-framing-protocol.md` is active
   - Requested outcome
   - Success evidence
   - Stop condition
   - Non-goals
   - Current stop state: `done | blocked | needs-verification | scope-exceeded`
15. `Anti-Entropy` when `references/anti-entropy-governance.md` is active
   - Deletion class
   - Old path or object
   - New canonical owner
   - Decision: `delete-first | compat-exception | confirmation-first`
   - Retired behavior and preserved behavior
   - Remaining entropy or retirement follow-up
16. `Stage Councils` when `references/stage-council-protocol.md` is active
   - Active council names
   - Lead owner
   - Role cards
   - Required gates
   - Output artifacts
   - Resume anchor

## Engineering Micro-Practices

When route output activates `micro_practices`, preserve them as a small local
ledger instead of treating them as another workflow bundle.

The user-facing response should expose:

- active practice names
- the reference for each practice
- the evidence the practice expects
- the ledger resume anchor, usually `.skill-practices/micro-practice-ledger.json`

The ledger can be initialized with:

```bash
python scripts/init_micro_practices.py --root . --text "<user request>" --pretty
```

Update one practice when evidence is captured or a blocker is found:

```bash
python scripts/update_micro_practices.py --ledger .skill-practices/micro-practice-ledger.json --name <practice-name> --status satisfied --evidence "<evidence>" --pretty
```

Before a completion claim, evaluate the ledger:

```bash
python scripts/evaluate_micro_practices.py --ledger .skill-practices/micro-practice-ledger.json --pretty
```

The evaluation decision is a small gate:

- `complete`: all practices are `satisfied`
- `continue`: one or more practices are still `active`
- `blocked`: one or more practices are `blocked`

## Stage Councils

Stage councils are optional overlays under the existing `product-spec-deliver`
bundle. They do not replace the lead agent or create a new top-level skill.

Expose them only when `stage_council_plan.enabled` is true:

- active councils, for example `product-discovery-council` or `prototype-design-council`
- `references/stage-council-protocol.md`
- `assets/stage-council-plan-template.json`
- the role cards and quality gates that changed the artifact sequence
- the council-specific resume anchor

## Intent Confirmation

When the request is a fuzzy idea, low-information ask, or asks the system to
decide between route-changing directions, ask one targeted confirmation question
before presenting the provisional route as final.

Use stable option ids so both humans and evals can reason about the choice:

- `product-opportunity`
- `prototype-exploration`
- `technical-feasibility`
- `architecture-risk`
- `delivery-plan`

Each option should name the target lead, workflow bundle, and stage council when
one would be activated. Keep the provisional route visible, but mark it as
provisional until the user confirms the intent.

## Completion Evidence Rule

Do not claim a task is complete from routing output, worker self-report, stale
logs, or partial checks.

For non-trivial work, completion output must preserve these semantic slots even
when written in natural prose:

```yaml
completion_evidence:
  evidence_action:
  result:
  covered_scope:
  uncovered_scope:
  residual_risk:
  confidence_grade: "A | B | C"
  evidence_refs:
```

Confidence grades:

- `A`: direct check plus relevant regression evidence, no known unresolved
  scope.
- `B`: direct check with bounded residual risk.
- `C`: partial evidence only; do not present as closed.

When Team Engine Lite is active, `A` or `B` also requires Verifier evidence and
Lead acceptance through a DeliveryCycleReport.

Machine-readable completion evidence should use:

```bash
mkdir -p .skill-evidence && cp assets/completion-evidence-template.json .skill-evidence/completion-evidence.json
python scripts/verify_completion_evidence.py --evidence .skill-evidence/completion-evidence.json --pretty
```

The action preflight equivalent is:

```bash
python scripts/verify_action.py --text "<user request>" --check completion-evidence --completion-evidence .skill-evidence/completion-evidence.json --pretty
```

Contract:

- `references/completion-evidence.schema.json`
- `assets/completion-evidence-template.json`
- `evidence_refs` must include at least one verifiable command or an existing
  local artifact path; purely descriptive notes do not support completion.

## Response Pack

When a fast user-facing draft is needed from the router result, prefer the response-pack generator from `references/tooling-command-index.md`.

The response pack should expose workflow source explanation when it helps justify why the route is process-led, lead-led, or only a fallback.

When a response pack is written to disk, it should also be able to emit a machine-readable JSON sidecar so downstream scripts can consume the same `Team Dispatch / Evidence / Next Action / Resume` structure without reparsing Markdown.

The sidecar schema is documented in `references/response-pack-sidecar-schema.md`.
