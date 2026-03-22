---
name: virtual-intelligent-dev-team
description: Intelligent expert-team router and bounded-iteration orchestrator for complex requests. Dispatch the best lead agent from Java Virtuoso, Sentinel Architect (NB), Technical Trinity, Code Audit Council, Git Workflow Guardian, Omni-Architect, Executive Trinity, and World-Class Product Architect, attach the right copilot agents when work crosses code, architecture, security, git workflow, domain strategy, business decisions, or frontend UX, enable evidence-driven iteration when the user asks for optimization loops, repeated retries, benchmark comparison, or candidate evaluation, and trigger the formal release gate when the user asks whether a version is ready to ship or submit.
---

# Virtual Intelligent Dev Team

Handle complex requests with one unified workflow:

1. Identify task type, risk level, language stack, and Git/process needs.
2. Choose one lead agent.
3. Add one or two assistant agents only when they add clear value.
4. Enable governance or process guardrails only when needed.
5. Use a compact handoff when lead and assistants need structured coordination.
6. If the user asks for optimization, repeated improvement, benchmark comparison, or another round, enter bounded iteration instead of open-ended self-looping.
7. If the user asks whether the current version can ship, submit, or pass formal acceptance, run the release gate instead of answering from a benchmark summary alone.
8. Produce one unified response instead of disconnected role fragments.

## Positioning

This skill is not only an expert router. It is a bounded work-loop skill for complex tasks.

Its current operating model has four practical closure layers:

1. `Routing closure`
   - Route work across lead, assistant, governance, and process tracks based on task shape, risk, stack, and workflow signals.
2. `Iteration closure`
   - Support baseline registration, round memory, self-feedback, `keep / retry / rollback / stop`, `pivot`, and `resume`.
3. `Release closure`
   - Use a formal release gate to decide `ship` or `hold`, and bootstrap the next remediation loop when the outcome is `hold`.
4. `Drill closure`
   - Verify the workflow through offline drills that cover rollback, resume, and release-gate bootstrap paths.

The goal is evidence-driven execution with boundaries, not open-ended autonomous looping.

## Quick examples

- `评估当前项目里的版本，看看能不能继续优化`
  - Route into bounded iteration with evidence, baseline comparison, and next-round decisions.
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

For the project-facing explanation, common scenarios, and Chinese terminology notes, read `references/skill-positioning.md`.

## When to use

Use this skill when:

- The user does not know which specialist should own the task.
- The task spans two or more domains such as code, architecture, security, audit, Git, frontend UX, product, or business strategy.
- The user needs a cross-domain decision such as:
  - audit plus implementation
  - strategy plus technical landing
  - unfamiliar industry architecture plus compliance plus delivery
- The task needs structured coordination, governance, or workflow guardrails.

If the task is simple and clearly single-domain, still use this skill if it triggers naturally, but keep routing lightweight.

Use bounded iteration only when the request benefits from it:

- explicit optimization loops
- benchmark or regression comparison
- repeated retries with evidence required
- candidate comparison before committing to a direction

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
- `Omni-Architect`
  - Unfamiliar industries, cross-industry systems, domain constraints, and compliance-heavy architecture.
- `Executive Trinity`
  - Business strategy, growth, pricing, monetization, competitive decisions, and operating model.
- `World-Class Product Architect`
  - Frontend UX, visual redesign, interaction design, React UI, and implementation guidance.

## Routing model

Apply explicit routing first. If that does not fully settle the task, apply weighted scoring from `references/routing-rules.json`.

### Priority routing

- Route to `Code Audit Council`
  - For review, audit, security review, PR review, vulnerability review, or refactor assessment.
  - Do not let this override UI or UX review requests.
- Route to `Git Workflow Guardian`
  - For commit, push, pull, rebase, merge, branch strategy, or PR process tasks.
  - If the user only mentions a PR but the true ask is review or audit, keep `Code Audit Council` as lead.
- Route to `Java Virtuoso`
  - For Java, Spring, JVM, GC, Java migration, or Java concurrency work.
- Route to `World-Class Product Architect`
  - For page redesign, React UI, interaction design, visual polish, or frontend UX optimization.
- Route to `Executive Trinity`
  - For business strategy, growth, pricing, monetization, market choices, or competitive positioning.
- Route to `Omni-Architect`
  - For unfamiliar industry systems, compliance-heavy domain architecture, or cross-industry solution design.
- Route to `Technical Trinity`
  - For general system design or engineering implementation not clearly owned by a narrower specialist.
- Elevate to `Sentinel Architect (NB)`
  - For high-risk, critical, research-first, production-impacting, or conflict-heavy tasks.

### Confidence routing

- `confidence >= 0.55`
  - Prefer one lead unless an assistant override rule should attach a copilot.
- `0.35 <= confidence < 0.55`
  - Use one lead plus one assistant.
- `confidence < 0.35`
  - Use one lead plus up to two assistants and prefer a clarifying question.

Always apply negative keywords to reduce false positives.

## Assistant rules

Assistants must add real value. Do not add them just because scoring allows it.

### Common assistant patterns

- `Code Audit Council` + language specialist
  - Example: Java review should add `Java Virtuoso`.
- `Git Workflow Guardian` + implementation specialist
  - Example: Git execution plus code change delivery.
- `Executive Trinity` + `Technical Trinity`
  - Use when the user asks for both business strategy and technical landing.
- `Omni-Architect` + `Technical Trinity`
  - Use when the user asks for domain/compliance architecture and implementation delivery together.
- Any lead + `Sentinel Architect (NB)`
  - Add Sentinel when high-risk signals are present and Sentinel is not already the lead.

### Coordination rule

When a lead needs assistant input, use a compact internal handoff instead of loose role switching.

- Read `references/coordination-handoff-templates.md` when the task needs review feedback loops, strategy-to-execution transfer, Git sequencing, or escalation.
- Read `references/dispatch-activation-cards.md` when you need a crisp prompt for what the assistant must deliver.
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

If the task matches a common multi-role pattern, load the closest runbook from `references/scenario-runbooks.md`.

- Startup MVP
- Audit and fix
- Strategy with technical landing
- Regulated or unfamiliar domain build
- Frontend UX with backend coupling
- High-risk production change
- Repeated-failure or root-cause debugging
- Evidence-driven iteration

Use runbooks to speed coordination shape, not to force a rigid ceremony.

## Bounded iteration

When the user asks to iterate, optimize, benchmark, compare candidates, or keep improving until stable:

- Read `references/self-optimization-architecture.md` for the operating model.
- Read `references/agency-inspired-loop-patterns.md` for semantic-owner preservation, Dev↔QA loop design, and checkpointed memory.
- Read `references/iteration-protocol.md` before running the loop.
- Read `references/iteration-state-machine.md` to keep the round lifecycle deterministic.
- Read `references/loop-orchestration.md` when the user wants capped multi-round optimization.
- Read `references/memory-model.md` to keep only useful short-term and distilled memory.
- Read `references/evidence-ledger-schema.md` to structure each round.
- Read `references/baseline-registry.md` before registering or reusing a benchmark baseline.
- Read `references/rollback-and-stop-rules.md` before deciding to keep, retry, rollback, or stop.
- Read `references/mutation-catalog-patterns.md` when the loop needs to turn repeated feedback into deterministic self-mutations across JSON, Markdown, or YAML control files.

### Iteration guardrails

- Default live user work to `1-3` rounds.
- Allow deeper loops only for explicit offline evaluation or benchmark-driven optimization.
- For explicit offline software-project optimization, default support can go beyond `100` rounds when the evidence loop stays objective and rollbackable.
- Every round must have one objective, one candidate change, and one evidence check.
- Do not run an unbounded self-improvement loop.
- If evidence is missing or regresses, prefer `retry`, `rollback`, or `stop`.

### Iteration artifacts

Use these templates when the loop is active:

- `assets/iteration-ledger-template.md`
- `assets/round-reflection-template.md`
- `assets/round-memory-template.md`
- `assets/self-feedback-template.md`
- `assets/distilled-patterns-template.md`

## Root-cause discipline

When the user signals repeated failed attempts, unresolved production behavior, or explicitly asks for root-cause analysis:

- Read `references/root-cause-escalation-playbook.md`.
- Do not propose another blind patch first.
- Require evidence such as logs, config, repro state, or recent changes.
- Prefer `Sentinel Architect (NB)` as lead when "still fails", "already tried", "inspect logs", or "find the root cause" is central.
- Attach `Technical Trinity` only when implementation or runtime analysis is needed after the evidence loop is clear.

## Git process rules

When Git workflow is relevant:

- Read `references/git-workflow-playbook.md` for branch policy, commit convention, PR gate, or release cadence.
- Read `references/using-git-worktrees-playbook.md` for parallel branches or isolated task execution.
- Run `scripts/git_workflow_guardrail.py` when deterministic Git stage checks are needed.
- Preserve the staged flow:
  - `G0` check
  - `G1` stage
  - `G2` commit
  - `G3` sync
  - `G4` push or PR
- Stop on conflict, permission error, non-fast-forward failure, or destructive-risk command.

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
2. `Execution Result`
   - Key conclusion
   - Key decision
   - Main risks
3. `Next Step`
   - Smallest executable action
   - User confirmation needed, if any
4. `Git Workflow`
   - Whether `using-git-worktrees` is needed
   - Whether `git-workflow` is needed
   - Whether Git lead should switch to `Git Workflow Guardian`
   - Recommended branch, commit, and PR strategy
   - Current Git stage, if relevant
5. `Governance`
   - Whether roundtable governance is enabled
   - Selected governance track
   - DRI, SLO, dual-sign, and post-audit requirements when relevant
6. `Optimization Loop` when bounded iteration is active
   - Objective and baseline
   - Current round and evidence source
   - Active owner, round memory, and self-feedback chain
   - Decision: `keep`, `retry`, `rollback`, or `stop`
   - Next round or closure action

The lead agent owns the response structure. Assistants should only add the delta that matters.

## Built-in references and checks

- Read `references/agent-catalog.md` for detailed triggers and anti-patterns.
- Read `references/coordination-handoff-templates.md` for compact lead/assistant handoffs.
- Read `references/dispatch-activation-cards.md` for assistant activation patterns.
- Read `references/agency-inspired-loop-patterns.md` for self-iteration patterns adapted from `agency-agents-main`.
- Read `references/scenario-runbooks.md` for common multi-role execution shapes.
- Read `references/root-cause-escalation-playbook.md` for repeated-failure and root-cause debugging.
- Read `references/routing-score-matrix.md` for routing weights and confidence interpretation.
- Read `references/routing-rules.json` as the source of truth for scoring and exclusions.
- Read `references/self-optimization-architecture.md` for bounded self-optimization design.
- Read `references/iteration-protocol.md` for the round contract.
- Read `references/iteration-state-machine.md` for the round state machine.
- Read `references/loop-orchestration.md` for capped multi-round execution.
- Read `references/memory-model.md` for short-term versus distilled memory.
- Read `references/evidence-ledger-schema.md` for per-round evidence shape.
- Read `references/baseline-registry.md` for baseline registration and reuse.
- Read `references/rollback-and-stop-rules.md` for closure decisions.
- Read `references/mutation-catalog-patterns.md` for replayable self-optimization mutation patterns.
- Read `references/offline-loop-drill-playbook.md` when you need a real multi-round offline drill that proves rollback, keep, pivot, and resume behavior end to end.
- Read `references/release-gate-playbook.md` when you need a release-candidate decision instead of only a fast benchmark pass.
- Use `assets/iteration-ledger-template.md`, `assets/round-reflection-template.md`, and `assets/distilled-patterns-template.md` when recording bounded iteration.
- Use `assets/iteration-plan-template.json` when the user wants a multi-round loop.
- Run `scripts/register_benchmark_baseline.py` to register a reusable local baseline.
- Run `scripts/init_iteration_round.py` to scaffold one bounded-iteration round.
- Run `scripts/run_iteration_cycle.py` to advance one round through initialization, benchmarking, evaluation, and closure, including benchmarking a candidate repo or worktree when needed.
- Run `scripts/run_iteration_loop.py` to execute a capped multi-round optimization plan and auto-synthesize the next candidate from round memory, self-feedback, open loops, and distilled patterns when autonomous mode is enabled.
- Run `scripts/run_offline_loop_drill.py` when you need a real offline acceptance drill for rollback, keep, pivot, resume, and release-gate hold bootstrap.
- Run `scripts/run_release_gate.py` when you need a formal ship-or-hold gate that includes the real offline loop drill; on `hold` it should emit the next iteration brief, seed a blocker-specific mutation catalog plus `repo-copy` workspace for the next bounded loop, and on `ship` it should close the loop into release archive artifacts.
- Run `scripts/promote_iteration_baseline.py` to promote a kept round into the next reusable baseline.
- Run `scripts/sync_distilled_patterns.py` to rebuild distilled patterns from accepted rounds.
- Run `scripts/compare_benchmark_results.py` to decide `keep`, `retry`, `rollback`, or `stop` from benchmark evidence.

Use deterministic routing inspection when needed:

```bash
python scripts/route_request.py --text "<user request>" --config references/routing-rules.json
```

Run semantic regression after changing routing, guardrails, examples, or this skill:

```bash
python scripts/validate_virtual_team.py --pretty
```

Bootstrap one iteration round when bounded iteration is active:

```bash
python scripts/init_iteration_round.py --workspace .skill-iterations --round-id round-01 --objective "<goal>" --baseline "<baseline>" --pretty
```

Register a reusable baseline before running a stateful iteration cycle:

```bash
python scripts/register_benchmark_baseline.py --workspace .skill-iterations --label stable --report <baseline-report> --pretty
```

Run one stateful iteration cycle:

```bash
python scripts/run_iteration_cycle.py --workspace .skill-iterations --round-id round-01 --objective "<goal>" --baseline-label stable --candidate "<candidate-change>" --candidate-worktree ../wt-round-01 --candidate-output-dir .tmp-iteration-round-01 --promote-label accepted-round-01 --sync-distilled-patterns --pretty
```

Run one stateful iteration cycle from a deterministic patch artifact:

```bash
python scripts/run_iteration_cycle.py --workspace .skill-iterations --round-id round-01 --objective "<goal>" --baseline-label stable --candidate "<candidate-change>" --candidate-worktree ../wt-round-01 --candidate-patch .skill-iterations/patches/round-01.patch --patch-strip 1 --benchmark-command "python scripts/run_benchmarks.py --output-dir {output_dir} --pretty" --auto-apply-rollback --pretty
```

Run a capped multi-round loop from a plan file:

```bash
python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.json --pretty
```

Run the benchmark gate with the real offline drill included:

```bash
python scripts/run_benchmarks.py --output-dir evals/benchmark-results --include-offline-drill --pretty
```

Resume an interrupted offline loop from persisted state:

```bash
python scripts/run_iteration_loop.py --workspace .skill-iterations --plan .skill-iterations/iteration-plan.json --resume --pretty
```

Run the real offline drill suite for rollback, keep, pivot, and resume:

```bash
python scripts/run_offline_loop_drill.py --workspace .tmp-offline-loop-drill --pretty
```

Run the formal release gate:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --pretty
```

Run the formal release gate and close the loop into the iteration workspace:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --release-label release-ready --pretty
```

Run the formal release gate and, on `hold`, immediately bootstrap the next bounded iteration loop:

```bash
python scripts/run_release_gate.py --output-dir evals/release-gate --iteration-workspace .skill-iterations --auto-run-next-iteration-on-hold --hold-loop-max-rounds 3 --pretty
```

When this `hold` bootstrap path is active, the release gate should create a git-detached `repo-copy`, a blocker-specific mutation catalog, and remediation artifacts under `artifacts/release-gate-hold/` so the next loop starts from runnable self-mutation scaffolding instead of an empty retry.

Materialize a structured candidate brief into a patch artifact with the built-in materializer:

```bash
python scripts/materialize_candidate_patch.py --brief .skill-iterations/candidate-briefs/round-01.json --candidate-root ../wt-round-01 --patch-output .skill-iterations/patches/round-01.patch --pretty
```

When `autonomous_candidate_generation` is enabled in the plan, the loop keeps generating the next bounded hypothesis from `round-memory.md`, `self-feedback.md`, `open-loops.md`, and `distilled-patterns.md` until it hits `stop` or the round cap.
Use `hypothesis_key` plus `loop_policy.max_same_hypothesis_retries` to prevent the loop from retrying the same idea indefinitely.
Use `loop_policy.max_consecutive_non_keep_rounds` when a long offline loop should stop after too many consecutive `retry` / `rollback` decisions without a new `keep`; set it to `0` or omit it to disable that guardrail.
Use `loop_policy.auto_pivot_on_stagnation` when autonomous rounds should block an exhausted hypothesis and pivot to the next actionable bottleneck instead of hard-stopping on the first stagnation trigger.
Use `benchmark_command_template` or per-round `benchmark_command` when the candidate repo does not expose `scripts/run_benchmarks.py`.
Use `apply_command` / `rollback_command` plus candidate worktrees when the loop should actually mutate code, capture workspace snapshots, and restore the previous state on measured regression.
Use `candidate_patch_template` or per-round `candidate_patch` plus `patch_strip` when each round should apply a reproducible patch artifact instead of an imperative mutation command.
Use `candidate_brief_template` plus `materialize_command_template` when the loop should transform a synthesized candidate into a concrete patch artifact or workspace mutation before benchmarking.
Use `mutation_plan` inside the candidate brief when you want the built-in materializer to turn structured text or JSON file operations into a patch without relying on an external command.
Use top-level `mutation_catalog` when feedback, open loops, and distilled context should deterministically synthesize the next round's `mutation_plan`; the loop records `mutation_plan_source` and `mutation_focus` in the candidate brief and round result.
For JSON control files, prefer `json_set`, `json_merge`, `json_delete`, `json_append`, and `json_append_unique` so the loop can safely optimize routing rules, regression registries, and eval inventories.
Treat `apply_command` and `candidate_patch` as mutually exclusive within one round.
If `auto_apply_rollback` is enabled and no explicit `rollback_command` is provided, a rollback decision will reverse the applied patch automatically.
`run_iteration_loop.py` now persists `loops/<plan>-state.json` after each completed round and writes `loops/<plan>-summary.json` on completion, so long offline runs can resume safely after interruption.
Use `--resume` only with the same plan content; the loop will reject drifted plan files instead of resuming into a different objective.
Loop state and summary now expose `decision_counts` plus `consecutive_non_keep_rounds`, so deep offline runs can inspect stagnation and resume with the same non-progress budget intact.
When auto-pivot is enabled, loop state also persists `blocked_hypothesis_keys`, `pivot_history`, `pivot_count`, and `pending_generation_reason` so a crash between rounds does not erase the next pivot decision.
When materialization is enabled, the loop writes one candidate brief JSON per round and can invoke a materializer command before `run_iteration_cycle.py`, which closes the gap between “next candidate idea” and “next executable change”.
If no external `materialize_command` is provided but the candidate brief contains `mutation_plan.operations`, the built-in materializer can generate the patch artifact automatically.
If a synthesized or explicit `mutation_plan` exists and the round has a candidate repo but no explicit `candidate_patch`, the loop can default the patch artifact path automatically.
When the loop controller itself changes, prefer a real offline drill before calling the self-optimization loop “closed enough”.
When the user asks whether the current version is ready to ship, prefer `run_release_gate.py` over a benchmark-only answer.

Promote a kept round into a new baseline:

```bash
python scripts/promote_iteration_baseline.py --workspace .skill-iterations --round-id round-01 --label accepted-round-01 --pretty
```

Rebuild distilled patterns from accepted rounds:

```bash
python scripts/sync_distilled_patterns.py --workspace .skill-iterations --pretty
```

Compare candidate and baseline benchmark results:

```bash
python scripts/compare_benchmark_results.py --baseline <baseline-report> --candidate <candidate-report> --pretty
```

## Lightweight rule

Do not over-orchestrate simple work.

- Single-domain and low-risk -> prefer one lead.
- Cross-domain or higher-risk -> use the smallest assistant set that covers the problem.
- If confidence is too low, ask one clarifying question instead of forcing a route.
