# Output Contract

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
2. `Execution Result`
   - Key conclusion
   - Key decision
   - Main risks
   - Evidence delta from assistants when applicable
   - Assistant delta contract when assistants are active
3. `Evidence`
   - Route evidence
   - Workflow source explanation
   - Process skills in effect
   - Assistant delta contract when assistants are active
4. `Next Action`
   - Smallest executable action
   - Current owner
   - User confirmation needed, if any
5. `Resume`
   - Progress anchor
   - Resume artifacts when relevant
6. `Git Workflow`
   - Whether `using-git-worktrees` is needed
   - Whether `git-workflow` is needed
   - Whether Git lead should switch to `Git Workflow Guardian`
   - Recommended branch, commit, and PR strategy
   - Current Git stage, if relevant
7. `Governance`
   - Whether roundtable governance is enabled
   - Selected governance track
   - DRI, SLO, dual-sign, and post-audit requirements when relevant
8. `Team Engine Lite` when role-separated delivery is active
   - Whether Worker / Verifier separation is required
   - Worker and Verifier roles
   - Max cycles and acceptance gates
   - Whether Worker can self-pass
   - Runtime claim and closure verdict
9. `External Agent Backend` when soft backend orchestration is active
   - Orchestration mode
   - Runtime claim
   - Backend orchestration verdict
   - Required output contracts
10. `Real Subagent Runtime` when the route is eligible for controlled real subagent execution
   - Eligibility and activation reason
   - Current runtime claim and candidate runtime claim
   - Whether runtime evidence is still required
   - Max subagents, spawn policy, merge policy, and fallback
11. `Planning Pack` when pre-development planning is active
   - Confirmed transformation scope, target, and constraints
   - Analysis artifacts to create or refresh
   - Phase plan, lane notes, and merge-risk guidance
   - Progress anchor and resume point
12. `Optimization Loop` when bounded iteration is active
   - Objective and baseline
   - Current round and evidence source
   - Active owner, round memory, and self-feedback chain
   - Decision: `keep`, `retry`, `rollback`, or `stop`
   - Next round or closure action

## Response Pack

When a fast user-facing draft is needed from the router result, prefer the response-pack generator from `references/tooling-command-index.md`.

The response pack should expose workflow source explanation when it helps justify why the route is process-led, lead-led, or only a fallback.

When a response pack is written to disk, it should also be able to emit a machine-readable JSON sidecar so downstream scripts can consume the same `Team Dispatch / Evidence / Next Action / Resume` structure without reparsing Markdown.

The sidecar schema is documented in `references/response-pack-sidecar-schema.md`.
