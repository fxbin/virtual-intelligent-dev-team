# Execution Quality Guardrails

This reference adapts the strongest lesson from small behavioral guideline
skills: keep the runtime contract short, observable, and hard to over-expand.

Use these guardrails after routing selects a lead and workflow bundle.

## 1. Surface Assumptions

- State the key assumption behind the selected route.
- If two materially different interpretations exist, name both before choosing.
- Ask only when the missing fact would change the route, risk level, or artifact.
- For low-information requests, prefer a clarification route over forced ceremony.

## 2. Smallest Defensible Bundle

- Pick the smallest workflow bundle that can close the request safely.
- Do not attach assistants because a score allows it; attach them only for a
  concrete delta the lead cannot provide alone.
- Do not open governance, Git, release, beta, or iteration lanes unless the user
  request or evidence makes that lane useful.

## 3. Surgical Execution

- Touch only the lane, artifact, or file family implied by the selected route.
- Match the existing repo and skill structure before adding new abstractions.
- Clean up artifacts created by the current route; report unrelated drift instead
  of silently rewriting it.
- When editing a skill, keep `SKILL.md` as the runtime contract and move long
  rules into `references/`, `assets/`, `evals/`, or `scripts/`.

## 4. Verifiable Closure

- Convert the request into success criteria before executing substantial work.
- Name the verification command, artifact, or observable result for the route.
- For iteration, compare against a baseline and decide `keep`, `retry`,
  `rollback`, or `stop`.
- For release, answer with `ship` or `hold` and preserve the follow-up anchor.

## Output Check

Every substantial route should be able to answer:

- `assumption_check`: What assumption would change this route?
- `minimality_check`: Why is this the smallest defensible bundle?
- `surgical_scope`: Which files, artifacts, or workflow lanes are in scope?
- `verification_check`: What evidence closes the loop?
