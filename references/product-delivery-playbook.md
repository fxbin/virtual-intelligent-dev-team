# Product Delivery Playbook

Use this playbook when the request is primarily about product definition, user flow, acceptance criteria, or turning a feature idea into an implementation-ready slice.

## Lead

- Default lead: `World-Class Product Architect`
- Common assistant: `Technical Trinity`
- Add `Git Workflow Guardian` only when branch / PR / delivery workflow is explicitly requested.

## Default sequence

1. State the target user and the primary outcome.
2. Lock the smallest acceptable scope for this slice.
3. Describe the core user flow and failure states.
4. Write acceptance criteria that engineering can actually verify.
5. Surface frontend/backend contract questions, not just UI wishes.
6. Hand back the smallest buildable implementation slice.

## Required outputs

- product brief
- target user flow
- acceptance criteria
- frontend/backend contract questions
- implementation slice recommendation

## Guardrails

- Do not turn product work into abstract business strategy.
- Do not confuse a visual mockup with an executable requirement.
- Do not emit vague acceptance criteria such as "better UX" or "more intuitive".
- If backend/API coupling is material, attach `Technical Trinity`.
