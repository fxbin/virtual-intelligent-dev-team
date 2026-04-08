# Technical Governance Playbook

Use this playbook when the request is about release control, staged execution, branch policy, rollback, refactor governance, or other engineering safety rails.

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
6. Only then move into commit / push / PR / release actions.

## Required outputs

- execution mode
- risk checkpoint list
- verification plan
- rollback conditions
- branch / PR / release sequence

## Guardrails

- Do not treat Git commands as the governance plan.
- Do not skip rollback thinking on production-sensitive work.
- Do not open a release gate without explicit evidence criteria.
- When the request is still ambiguous, clarify the governance boundary before execution.
