# Project Memory Lite

> **Journal 模式**(P1-10):本协议已升级为 workspace journal 模式。
> 详见 `references/workspace-journal-protocol.md`。
> journal 是 event sourcing(事件流),能复盘"上一次为什么走 Sentinel 而不是 Trinity"。
> compaction 后状态不丢失(对应 Karpathy 的"pod 重启内存清空"问题)。

Use this protocol when the request benefits from resuming work across sessions,
rounds, or delivery gates, but a full persistent memory system would be too heavy.

## Goal

Keep just enough durable context to:

- resume safely after a pause
- continue an iteration without replaying every artifact
- preserve accepted patterns without turning guesses into policy

## Default Anchors

## 1. Planning Anchor

- File:
  - `docs/progress/MASTER.md`
- Use when:
  - pre-development planning is active
  - the task will span multiple sessions
- Stores:
  - current phase
  - active constraints
  - lane status
  - next resume point

## 2. Iteration Snapshot

- File:
  - `.vidt/iterations/current-round-memory.md`
- Use when:
  - bounded iteration or evidence-backed remediation is active
- Stores:
  - current round
  - candidate change
  - evidence summary
  - carry-forward loops

## 3. Accepted Pattern Anchor

- File:
  - `.vidt/iterations/distilled-patterns.md`
- Use when:
  - a reusable pattern survived evidence
- Stores:
  - stable signals
  - reuse rule
  - evidence note

## 4. Project Context Anchor

- File:
  - `.vidt/context/project-context.md`
- Use when:
  - durable project rules, commands, stack assumptions, or forbidden changes should carry across slices
  - a quick delivery slice needs project-specific constraints before implementation
- Stores:
  - stack and command defaults
  - architecture and style rules
  - delivery expectations
  - forbidden changes and required verification evidence

## Lightweight Resume Contract

When recommending resume artifacts, prefer:

1. one primary anchor
2. up to two supporting artifacts
3. the smallest next action

Do not ask the next session to replay every round file by default.

## Recommended Materialization

- One-step initialization:

```bash
python scripts/init_project_memory.py --root . --mode all --pretty
```

- Project context:

```bash
python scripts/init_project_context.py --root . --pretty
```

- Planning anchor:

```bash
mkdir -p docs/progress
cp assets/pre-development-progress-master-template.md docs/progress/MASTER.md
```

- Iteration snapshot:

```bash
mkdir -p .vidt/iterations
cp assets/round-memory-template.md .vidt/iterations/current-round-memory.md
```

- Accepted pattern anchor:

```bash
mkdir -p .vidt/iterations
cp assets/distilled-patterns-template.md .vidt/iterations/distilled-patterns.md
```

## What Not To Do

- Do not pretend this is long-term institutional memory.
- Do not store speculative notes as accepted patterns.
- Do not return five or six anchors when one would unblock the next step.
- Do not put one-off task constraints in project context; use the Harness constraint artifact for per-task implementation boundaries.
