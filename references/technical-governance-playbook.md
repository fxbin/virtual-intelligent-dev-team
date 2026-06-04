# Technical Governance Playbook

Use this playbook when the request is about release control, staged execution, branch policy, rollback, refactor governance, or other engineering safety rails.

For repository AI onboarding, `AGENTS.md`, or project-local `.agents/skills/` work, use this playbook only to define analysis lanes, risk boundaries, and verification evidence. Hand the actual context-writing rules to `skill-forge` and its project knowledge capture protocol.

When governance work touches duplicate owners, fallback growth, old paths,
adapters, guards, schema, persistence, or source-of-truth behavior, compose
`references/anti-entropy-governance.md` before destructive or compatibility
decisions.

## Leads

- Default lead: `Git Workflow Guardian` for workflow-first tasks
- Escalate to `Sentinel Architect (NB)` when the change is high-risk, production-sensitive, or research-first
- Common assistants: `Code Audit Council`, `Technical Trinity`

## Default sequence

1. Define the execution mode and owner.
2. State the risk boundary and stop conditions.
3. Lock the smallest safe next action.
4. Define verification evidence before and after the change.
5. State rollback or hold conditions explicitly.
6. Classify anti-entropy risk when old paths, fallbacks, duplicate owners, or
   source-of-truth surfaces are involved.
7. Only then move into commit / push / PR / release actions.

## Required outputs

- execution mode
- risk checkpoint list
- verification plan
- rollback conditions
- anti-entropy decision when relevant
- branch / PR / release sequence

## Guardrails

- Do not treat Git commands as the governance plan.
- Do not skip rollback thinking on production-sensitive work.
- Do not open a release gate without explicit evidence criteria.
- Do not add another fallback, guard, or adapter when evidence points to a
  wrong owner that should be retired or corrected.
- Do not execute irreversible persistent-state deletion without explicit scoped
  user confirmation.
- When the request is still ambiguous, clarify the governance boundary before execution.
