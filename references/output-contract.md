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
   - Active engineering micro-practices and their ledger anchor when any micro-practice is active
   - Assistant delta contract when assistants are active
   - Completion evidence slots before any `done`, `fixed`, `ready`, `ship`, `commit`, `merge`, or handoff claim:
     - evidence action / check performed
     - result / exit status
     - covered scope
     - uncovered scope
     - residual risk
     - confidence grade: `A | B | C`
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
   - DeliveryCycleReport evidence before Lead acceptance
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
13. `Goal Frame` when `references/goal-framing-protocol.md` is active
   - Requested outcome
   - Success evidence
   - Stop condition
   - Non-goals
   - Current stop state: `done | blocked | needs-verification | scope-exceeded`
14. `Anti-Entropy` when `references/anti-entropy-governance.md` is active
   - Deletion class
   - Old path or object
   - New canonical owner
   - Decision: `delete-first | compat-exception | confirmation-first`
   - Retired behavior and preserved behavior
   - Remaining entropy or retirement follow-up

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
