# Stage Council Protocol

Stage councils add phase-level specialists under the existing
`World-Class Product Architect` route.

They are overlays, not new top-level leads. The current lead still owns the
user-visible answer, scope boundary, and final acceptance. Team Engine Lite still
owns Worker / Verifier separation when delivery begins.

## Activation Boundary

Activate a stage council only when the request would be materially worse if a
single product generalist handled the whole phase.

Use a council when the request explicitly involves:

- product strategy, PRD, requirements, user research, competitor analysis,
  metrics, roadmap, sprint planning, stakeholder updates, or product
  brainstorming
- prototype design, high-fidelity UI, runnable HTML prototypes, design systems,
  visual design, page design, brand tone, or accessibility review
- explicit "expert team", "council", "专家团", "多角色", or "团队协作" phrasing
  together with one of the product or prototype surfaces above

Do not activate a council for:

- small fixes that only need `quick-slice-deliver`
- backend-only architecture
- pure Git workflow
- release gates
- code audit findings
- generic "make it better" requests without product or prototype evidence

## Council Types

### `product-discovery-council`

Use for product discovery, strategy, PRD, requirements, user research,
competitor analysis, metrics, roadmap, sprint, and stakeholder work.

Role cards:

- `requirement-analyst`
  - Owns scope, P0/P1/P2 requirements, acceptance criteria, and non-goals.
- `user-researcher`
  - Owns target user, jobs-to-be-done, research synthesis, and user risk.
- `competitive-analyst`
  - Owns competitor patterns, differentiation, and market proof.
- `data-analyst`
  - Owns success metrics, funnel or retention signals, and decision evidence.
- `roadmap-planner`
  - Owns sequencing, milestones, stakeholder updates, and delivery tradeoffs.

Default sequence:

1. Collect current user, market, data, and constraint evidence.
2. Synthesize P0/P1/P2 scope and non-goals.
3. Turn the product decision into acceptance criteria and slice boundaries.
4. Hand the accepted product slice back to `product-spec-deliver`.

Quality gates:

- `scope_gate`
- `user_evidence_gate`
- `competitive_or_market_evidence_gate`
- `metric_gate`
- `roadmap_sequence_gate`

Default output artifacts:

- `.vidt/product/current-slice.md`
- `.vidt/product/acceptance-criteria.md`
- `.vidt/product/stage-council-plan.json`

### `prototype-design-council`

Use for design prototype, high-fidelity UI, design system, visual direction,
runnable prototype, and accessibility-sensitive interaction work.

Role cards:

- `ux-discovery`
  - Owns surface, audience, task flow, content scale, and interaction
    constraints.
- `design-system-curator`
  - Owns design system choice, tokens, component conventions, and brand fit.
- `prototype-builder`
  - Owns runnable prototype, responsive states, and component composition.
- `visual-critic`
  - Owns visual hierarchy, specificity, restraint, and anti-generic review.
- `accessibility-reviewer`
  - Owns keyboard path, contrast, focus states, and mobile readability.

Default sequence:

1. Lock design brief and surface constraints.
2. Select or derive design tokens before prototype work.
3. Build the smallest runnable high-fidelity prototype.
4. Review visual quality and accessibility before implementation handoff.

Quality gates:

- `design_brief_gate`
- `design_token_gate`
- `prototype_runnable_gate`
- `visual_quality_gate`
- `accessibility_gate`

Default output artifacts:

- `.vidt/product/prototype-design-brief.md`
- `.vidt/product/stage-council-plan.json`

## Operating Rules

- Keep one semantic lead: `World-Class Product Architect`.
- Keep one workflow bundle: normally `product-spec-deliver`.
- Councils may change the artifact sequence, but not the top-level route.
- Council roles produce deltas. The lead synthesizes one unified response.
- If real subagent runtime is unavailable, represent councils as soft
  orchestration roles and do not claim independent runtime execution.
- If product and prototype councils both activate, run product discovery before
  prototype design unless the user already supplied a locked PRD.

## Machine-Readable Plan

When a persistent plan is useful, write it from
`assets/stage-council-plan-template.json` to:

```bash
.vidt/product/stage-council-plan.json
```

Minimum fields:

- `enabled`
- `active_councils`
- `workflow_bundle`
- `lead_agent`
- `councils[].roles`
- `councils[].quality_gates`
- `councils[].output_artifacts`
- `resume_anchor`

## Closure

Stage council work is complete only when:

- each active council has named the evidence it used
- required gates are checked or explicitly marked unavailable
- output artifacts or their planned paths are named
- the lead has translated council outputs into the current workflow bundle
- Team Engine Lite verification is still applied before delivery acceptance
