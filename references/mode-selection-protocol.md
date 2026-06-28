# Mode Selection Protocol

Use this protocol after the request's task type, risk level, language stack,
and process signals are identified.

The goal is to keep the response mode as small as the task allows while still
preserving verification, runtime honesty, and resume anchors for delivery work.

## Decision Tree

1. **Is it a simple, single-domain explanation or advice question?**
   - Yes -> **Direct Answer Mode**
   - Typical signals: "how do I...", conceptual debugging advice, single-domain
     optimization guidance.
   - Boundary: the user is not asking the agent to edit, refactor, implement,
     verify, commit, release, or iterate.
   - Output: Analysis -> Solution -> Steps -> Expected Results.

2. **Does it need multiple expert perspectives?**
   - Yes -> **Multi-Expert Execution Mode**
   - Typical signals: multi-domain problems such as architecture + data + ops,
     or complex technical decisions that benefit from diverse specialist views.
   - Runtime rule: spawn 2-4 experts only when the host exposes real spawn /
     wait / merge runtime evidence. Otherwise, use soft expert orchestration and
     label it honestly.
   - Examples: "微服务拆分规划", "React性能全面优化", "系统重构方案".

3. **Does it need full workflow orchestration?**
   - Yes -> **Full Workflow Mode**
   - Typical signals: large refactor, migration, multi-phase delivery, release
     readiness, or governance gates.
   - Output: selected route, fallback, next executable step, required artifact,
     and resume anchor.

4. **Otherwise use Expert Routing Mode.**
   - Typical signals: a focused specialist question that is not merely a simple
     explanation and does not need full workflow orchestration.
   - Output: expert selection, specialist analysis, solution, implementation
     steps.

## Hard Boundaries

- Multi-domain problems route to Multi-Expert Execution, not Direct Answer.
- Direct Answer is advice-only. If the user asks for code edits, refactors, bug
  fixes, verification, commits, release readiness, or repeated iteration, route
  to the smallest delivery bundle instead.
- Narrow implementation or bug-fix work should use quick-slice delivery rather
  than a full product or planning workflow.
- Large rewrites, migrations, overhauls, or planning-before-coding requests
  enter pre-development planning before implementation.
- Release readiness, formal acceptance, or ship/pass/submit questions run the
  release gate rather than answering from benchmark summaries alone.

## Mode Outputs

### Direct Answer Mode

- Technical Analysis
- Solution, with code or config examples when helpful
- Implementation Steps
- Expected Results

### Multi-Expert Execution Mode

- Expert Team Roster: 2-4 experts
- Individual Expert Analyses: actual execution outputs only when real runtime
  exists; otherwise clearly labeled expert-lens analysis
- Synthesized Solution
- Unified Implementation Steps

### Expert Routing Mode

- Expert Selection: one line naming who and why
- Expert's Technical Analysis
- Solution
- Implementation Steps

### Full Workflow Mode

- `Selected route`: lead, assistants, workflow bundle, and why this route won
- `Fallback`: clarification path or downgraded route when confidence or evidence
  is weak
- `Next step`: smallest executable action, required artifact, and resume anchor

