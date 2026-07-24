# Trigger Health Baseline

Use this baseline when the virtual team fails to activate, activates too often,
or selects the wrong lane.

Do not fix trigger problems by making `SKILL.md` longer by default. Diagnose the
layer that owns the failure.

## Trigger Layers

### L0 Availability

Question:

- Is `virtual-intelligent-dev-team` installed and visible to the host?

Evidence:

- the skill appears in the host's skill list
- `SKILL.md`, `VERSION`, and `agents/openai.yaml` are readable
- repo metadata points to the same version

Failure owner:

- install, sync, or host discovery path

### L1 Entry Cue

Question:

- Did the user explicitly name the skill or provide a task shape that clearly
  needs it?

Evidence:

- explicit `$virtual-intelligent-dev-team`
- complex software delivery, product scope, governance, release, Git,
  iteration, beta, root-cause, multi-agent, or project-knowledge cue

Failure owner:

- trigger wording or host skill matcher

### L2 Route Selection

Question:

- Given the prompt, does routing choose the correct lead and smallest workflow
  bundle?

Evidence:

- `python scripts/route_request.py --text "<request>" --config references/routing-rules.json`
- `references/regression-cases.json`

Failure owner:

- `routing-rules.json`, `SKILL.md` Workflow Bundles, `playbook-index.md`, or
  route examples

### L3 Execution Depth

Question:

- Once selected, did the skill execute deeply enough for the task risk?

Evidence:

- required bundle artifacts exist when needed
- `.vidt/harness/engineering-constraints.md` exists before code-facing edits
- Team Engine Lite evidence exists when active
- completion evidence slots are present before final claims

Failure owner:

- workflow reference, output contract, tooling command, or implementation
  discipline

### L4 Context Pressure And Re-Entry

Question:

- After compaction, resume, long tool output, or user redirection, did the
  route re-check still match the current task?

Evidence:

- resume anchor readback
- current workflow state
- changed user request or changed risk profile

Failure owner:

- resume decision matrix, automation state inspection, or missing route
  re-entry check

### L5 False Positive Control

Question:

- Is the skill activating full workflow ceremony on simple work?

Evidence:

- prompt is single-domain, low-risk, read-only, or tiny edit
- no release, Git, governance, iteration, product, or multi-agent cue exists

Failure owner:

- overbroad trigger wording, over-eager bundle selection, or missing fast-path
  negative tests

## Minimum Trigger Matrix

Maintain examples for:

- quick implementation slice -> `quick-slice-deliver`
- rewrite or migration planning -> `plan-first-build`
- release readiness -> `ship-hold-remediate`
- repeated regression -> `root-cause-remediate`
- staged beta -> `beta-feedback-ramp`
- post-release signal loop -> `post-release-close-loop`
- Git or branch flow -> Git workflow lane
- simple Q&A -> no heavy bundle
- tiny edit -> no durable workspace

## Repair Rule

Fix trigger failures in this order:

1. add or clarify regression sample
2. inspect route result
3. update the narrow owner file
4. run validation
5. only then adjust `SKILL.md` if the runtime contract itself was incomplete
