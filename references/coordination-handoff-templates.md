# Coordination Handoff Templates

Use these templates when a lead agent needs structured input from one or more assistants. Keep them short and concrete. They are coordination aids, not user-facing ceremony.

## 1. Standard Lead-to-Assistant Handoff

```markdown
## Handoff
- From: [Lead agent]
- To: [Assistant agent]
- Task slice: [Specific subproblem]
- Why this agent: [Why this agent is needed]
- Current context:
  - Goal: [Primary user outcome]
  - Constraints: [Technical, timeline, risk, policy]
  - Relevant files or systems: [Paths or components]
- Deliverable requested:
  - Needed output: [Decision, findings, design delta, Git step, etc.]
  - Acceptance criteria:
    - [Criterion 1]
    - [Criterion 2]
- Return format:
  - Summary:
  - Claim:
  - Evidence:
  - Risks:
  - Decision:
  - Recommendation:
```

## 2. Audit Feedback Loop

Use when `Code Audit Council` reviews work owned by another lead.

```markdown
## Audit Feedback
- Reviewer: Code Audit Council
- Owner: [Lead or implementation specialist]
- Verdict: [PASS / FAIL / PASS WITH RISKS]
- Highest-severity finding: [One-line summary]
- Findings:
  - [Severity] [Issue]
  - [Severity] [Issue]
- Required fixes before ship:
  - [Fix 1]
  - [Fix 2]
- Evidence needed for closure:
  - [Test, diff, benchmark, screenshot, proof]
- Return delta:
  - Claim:
  - Evidence:
  - Decision:
```

## 3. Git Execution Handoff

Use when `Git Workflow Guardian` needs to control sequencing while another agent owns the code change.

```markdown
## Git Handoff
- Lead owner: [Feature/review agent]
- Git owner: Git Workflow Guardian
- Current stage: [G0 / G1 / G2 / G3 / G4]
- Target branch strategy: [branch/worktree/pr plan]
- Preconditions:
  - [State check]
  - [Tests or review state]
- Safe next step:
  - [Exact minimal action]
- Stop conditions:
  - [Conflict]
  - [Permission issue]
  - [Non-fast-forward]
- Return delta:
  - Claim:
  - Evidence:
  - Next action:
```

## 4. Product-to-Execution Handoff

Use when `World-Class Product Architect` needs `Technical Trinity` to land a product slice.

```markdown
## Product to Execution
- Product owner: [World-Class Product Architect]
- Execution owner: Technical Trinity
- Product decision:
  - [Chosen scope, flow, or acceptance criteria]
- Technical landing requested:
  - [Architecture or implementation slice]
- Non-negotiable constraints:
  - [Delivery, contract, performance, UX, policy]
- Expected output:
  - System shape
  - Implementation slice
  - Main risks
  - Claim
  - Evidence
  - Decision
```

## 5. Escalation Snapshot

Use only when risk, ambiguity, or disagreement is high enough to justify stronger governance.

```markdown
## Escalation Snapshot
- Trigger: [Why normal routing is insufficient]
- Lead agent: [Current lead]
- Assistants involved: [List]
- Open conflict or uncertainty:
  - [Decision or risk]
- Options considered:
  - [Option A]
  - [Option B]
- Decision needed:
  - [What must be decided now]
- Recommended governance mode:
  - [Roundtable / Sentinel-led staged execution]
- Return delta:
  - Claim:
  - Evidence:
  - Decision:
```

## 6. Root-Cause Escalation Handoff

Use when `Sentinel Architect (NB)` takes over after repeated failed attempts or when the user explicitly asks for root-cause analysis.

```markdown
## Root-Cause Handoff
- Lead: Sentinel Architect (NB)
- Assistant: [Technical Trinity / Code Audit Council / other]
- Symptom:
  - [Observed failure]
- Attempts already made:
  - [Attempt 1]
  - [Attempt 2]
- Evidence available:
  - [Logs / config / repro / recent diff]
- Evidence missing:
  - [What must be inspected next]
- Root-cause hypotheses:
  - [Hypothesis A]
  - [Hypothesis B]
- Smallest validating step:
  - [Exact next action]
- Guardrail:
  - Do not propose a production fix before validation unless the user asks for containment only.
- Return delta:
  - Claim:
  - Evidence:
  - Decision:
  - Next action:
```

## 7. Iteration Review Handoff

Use when a lead is running a bounded optimization loop and needs one assistant to review the next round.

```markdown
## Iteration Review
- Lead owner: [Lead agent]
- Review owner: [Assistant agent]
- Objective:
  - [What is being optimized]
- Baseline:
  - [Current accepted result]
- Candidate change:
  - [One change for this round]
- Evidence required:
  - [Validator / benchmark / regression / test]
- Hard constraints:
  - [What must not regress]
- Allowed decisions:
  - keep
  - retry
  - rollback
  - stop
- Expected return:
  - Decision
  - Claim
  - Evidence summary
  - Main risk
```
