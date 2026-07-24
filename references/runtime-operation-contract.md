# Runtime Operation Contract

This file holds the operational rules that should not live directly in `SKILL.md`.

## Boundary

This skill is strongest in three lanes:

- `研发`
  - architecture, implementation, review, refactor, migration, iteration, release readiness
- `产品`
  - product brief, user flow, acceptance criteria, quick slice delivery, staged beta validation, UI/UX, frontend/backend contract
- `技术治理`
  - risk gates, Git workflow, staged delivery, rollback, release gate, process guardrails

Requests centered on pure business strategy, pricing, monetization, financing, or generic industry consulting are outside the mainline. Use a clarification boundary instead of pretending the skill owns the whole company.

## Routing Model

Apply explicit routing first. If that does not fully settle the task, use the weighted scoring rules from `references/routing-rules.json`.

Main defaults:

- review / audit / security -> `Code Audit Council`
- Git / branch / PR / rebase -> `Git Workflow Guardian`
- Java / Spring / JVM -> `Java Virtuoso`
- product requirements / user flows / acceptance criteria / UI / React / redesign -> `World-Class Product Architect`
- general engineering implementation -> `Technical Trinity`
- high-risk / conflict-heavy / research-first -> `Sentinel Architect (NB)`

Confidence only decides team size:

- `>= 0.55`: prefer one lead
- `0.35-0.55`: one lead plus one assistant
- `< 0.35`: at most one lead plus two assistants; ask one clarification question when needed

## Assistant Rules

Assistants must add real value. Do not add them just because scoring allows it.

Common patterns:

- `Code Audit Council` + language specialist for language-specific review
- `Git Workflow Guardian` + implementation specialist for Git delivery plus code change work
- `World-Class Product Architect` + `Technical Trinity` for product scope plus backend/API landing
- `Sentinel Architect (NB)` + `Git Workflow Guardian` for staged execution, rollback, PR flow, or release-risk control
- any lead + `Sentinel Architect (NB)` when high-risk signals are present and Sentinel is not already the lead

When a lead needs assistant input, use a compact internal handoff. The user should still receive one unified answer.

## Governance

Enable structured governance when:

- the task is high risk
- the task is clearly cross-domain
- confidence is low and multiple assistants are required
- the user explicitly asks for governance, cross-functional coordination, or a structured decision process

Behavior:

- Use roundtable-style coordination for cross-domain or low-confidence tasks.
- Use stricter governance for high-risk work.
- If Sentinel is active, do not skip research-first reasoning.
- Keep governance practical and avoid ceremonial text.

## Planning

For large rewrites, migrations, overhauls, or planning-before-coding requests:

- Read `references/pre-development-planning-playbook.md`.
- Use `references/pre-development-output-template.md` for the user-facing planning summary.
- Produce only the smallest planning pack that de-risks execution.
- Prefer `docs/progress/MASTER.md` when the work will span multiple sessions.
- Add parallel lanes and merge-risk notes only when complexity warrants them.
- After the planning pack exists, return to normal routing, iteration, release, and Git rules for actual delivery.

## Iteration

For optimization, benchmark comparison, candidate comparison, or repeated improvement:

- Open only the needed `iteration / memory / evidence / baseline / rollback / mutation` references.
- Default live user work to `1-3` rounds.
- Allow deeper loops only for explicit offline evaluation or benchmark-driven optimization.
- Every round must have one objective, one candidate change, and one evidence check.
- Do not run an unbounded self-improvement loop.
- If evidence is missing or regresses, prefer `retry`, `rollback`, or `stop`.

## Root-Cause Discipline

When the user signals repeated failed attempts, unresolved production behavior, or root-cause analysis:

- Read `references/root-cause-escalation-playbook.md`.
- Do not propose another blind patch first.
- Require evidence such as logs, config, repro state, or recent changes.
- Prefer `Sentinel Architect (NB)` when "still fails", "already tried", "inspect logs", or "find the root cause" is central.
- Attach `Technical Trinity` only when implementation or runtime analysis is needed after the evidence loop is clear.

## Git Process Rules

When Git workflow is relevant:

- Use `references/tooling-command-index.md` for detailed playbooks and guardrail command entry.
- Preserve the staged flow: `G0` check, `G1` stage, `G2` commit, `G3` sync, `G4` push or PR.
- Stop on conflict, permission error, non-fast-forward failure, or destructive-risk command.

Never auto-run dangerous Git commands such as:

- `git reset --hard`
- `git clean -fd`
- `git push --force`

unless the user explicitly authorizes them.

## Pre-Action Verification

Before opening a process lane or forcing a multi-agent execution shape for a high-risk request:

- Use `verify_action.py` to confirm process-skill legality, lead assignment, git-workflow activation, worktree isolation, release-gate activation, bounded-iteration activation, or workflow-bundle bootstrap readiness.
- Before claiming `done`, `ready`, `fixed`, `committed`, `merged`, or handoff-ready, use `python scripts/verify_action.py --text "<user request>" --check completion-evidence --completion-evidence .vidt/evidence/completion-evidence.json --pretty` to confirm structured completion evidence exists and supports the claim.
- When route output activates engineering micro-practices, use `verify_action.py --check micro-practice-ledger` before the same completion or handoff claim.
- Use `lint_virtual_team_contract.py` as the mechanical drift check for routing indexes, plan references, and script command examples.

## Language Support

This skill supports routing for:

- `Python`
- `Go`
- `Node.js`
- `Rust`

Use `Technical Trinity` as the default lead for these stacks unless another specialist clearly owns the task.

## Lightweight Rule

Do not over-orchestrate simple work.

- Single-domain and low-risk -> prefer one lead.
- Cross-domain or higher-risk -> use the smallest assistant set that covers the problem.
- If confidence is too low, ask one clarification question instead of forcing a route.
