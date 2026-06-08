# Product Delivery Playbook

Use this playbook when the request is primarily about product definition, user flow, acceptance criteria, or turning a feature idea into an implementation-ready slice.

## Lead

- Default lead: `World-Class Product Architect`
- Common assistant: `Technical Trinity`
- Add `Git Workflow Guardian` only when branch / PR / delivery workflow is explicitly requested.

## Default sequence

1. State the target user and the primary outcome.
2. Lock the smallest acceptable scope for this slice.
3. Sharpen shared language when user, state, object, or workflow terms are ambiguous using `references/shared-language-and-decision-capture.md`.
4. Describe the core user flow and failure states.
5. Write acceptance criteria that engineering can actually verify.
6. Surface frontend/backend contract questions, not just UI wishes.
7. Split multi-layer work into `AFK` / `HITL` vertical slices using `references/vertical-slice-delivery-protocol.md`.
8. Hand back the smallest buildable implementation slice.

## Required outputs

- product brief
- target user flow
- acceptance criteria
- frontend/backend contract questions
- implementation slice recommendation
- vertical slice classification when the work spans multiple layers

## Guardrails

- Do not turn product work into abstract business strategy.
- Do not confuse a visual mockup with an executable requirement.
- Do not emit vague acceptance criteria such as "better UX" or "more intuitive".
- Do not hide product decisions that need human input inside an `AFK` slice.
- If backend/API coupling is material, attach `Technical Trinity`.
- If staged beta validation or cohort ramp is the center of gravity, switch to `beta-validation-playbook.md` instead of forcing everything into a plain product brief.
