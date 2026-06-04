# Goal Framing Protocol

Use this protocol when the user gives a broad goal, repeated-failure task,
release decision, optimization loop, migration, or any request where success
evidence and stop conditions may drift during execution.

Goal framing is a start protocol. It should not become a separate planning
ceremony unless the user explicitly asks to stop after framing.

## When To Use

Use when any of these are true:

- the user explicitly asks to define the goal, non-goals, or stop condition
- the task is broad enough that implementation could drift
- the task is failure-prone or has already retried several times
- release, beta, or post-release decisions depend on evidence boundaries
- multi-agent or external backend work needs a compact task packet

Do not use for:

- tiny wording edits
- simple factual Q&A
- one-command status checks
- route-only answers

## Goal Frame

Keep the frame compact:

```yaml
goal_frame:
  requested_outcome:
  success_evidence:
  stop_condition:
  non_goals:
  constraints:
  route:
  next_action:
```

Allowed stop states:

- `done`
- `blocked`
- `needs-verification`
- `scope-exceeded`

Rules:

- `done` requires success evidence.
- `blocked` requires a missing dependency, permission, or required fact.
- `needs-verification` means work may exist but evidence is insufficient.
- `scope-exceeded` means continuing would violate the goal or non-goals.

## Route Integration

After the frame, continue into the selected bundle unless the user asked to
frame only.

Map common signals:

- clear narrow fix -> `quick-slice-deliver`
- ambiguous product or contract -> `product-spec-deliver`
- rewrite, migration, or plan-first work -> `plan-first-build`
- repeated failure -> `root-cause-remediate`
- release readiness -> `ship-hold-remediate`
- beta ramp -> `beta-feedback-ramp`
- shipped feedback loop -> `post-release-close-loop`

## Subagent Context Packet

When dispatching subagents or external Agent backends, send a compact context
packet instead of the full conversation:

```yaml
subagent_context_packet:
  task:
  goal:
  stop_condition:
  relevant_baseline_refs:
  relevant_files:
  known_facts:
  unknowns:
  non_goals:
  expected_output:
  verification_expected:
  must_read_excerpts:
  unsafe_assumptions:
```

The packet is a handoff aid, not evidence replacement. Critical facts still
need bounded raw file, log, test, or command evidence.

## Drift Rule

If the user's goal changes during execution:

1. state old goal and new goal
2. identify scope delta and new risk
3. decide whether to continue, re-route, pause, or create a new work order
4. update the resume anchor when a durable workspace exists

