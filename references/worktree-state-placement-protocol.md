# Worktree State Placement Protocol

Use this protocol when a task executes inside a git worktree and any `.vidt/`
state directory is involved. The goal is an unambiguous tie-breaker for where
each piece of state lives, so that worktree creation, cleanup, and parallel
worktrees never strand or split state.

This protocol governs the **placement** of state directories. It does not change
what each directory stores; that stays with each directory's own protocol.

## When To Activate

Activate when any of these appear:

- `needs_worktree` is true (the request routed the `using-git-worktrees` process
  skill)
- parallel worktrees are in use (two or more tasks each in their own worktree)
- a bounded-iteration candidate lives in its own worktree
- multiple agents each occupy a separate worktree for one task
- any step is about to write a `.vidt/` artifact while `cwd` is a worktree and
  not the main repository

Do not activate when the task runs entirely in the main repository and no
worktree is involved — then state-root and execution-root coincide and the
default `--root .` behavior is already correct.

## Core Rule

Define two roots and keep them straight:

- **state-root** — the main repository root (the directory that holds the
  primary `.git`). All durable, shared, cross-task, and cross-agent state lives
  here.
- **execution-root** — the current worktree directory (or the main repository
  itself when no worktree is used). Code changes and one-shot execution
  artifacts live here.

When execution-root and state-root differ, state goes to state-root and only
execution products go to execution-root. This is the implicit default the skill
already follows; this protocol makes it explicit and checkable.

## Placement Table

| Directory | Placement | Why |
|---|---|---|
| `.vidt/harness` | state-root | constraints and breaker state are shared across tasks and worktrees |
| `.vidt/context` | state-root | global project context is reused across worktrees |
| `.vidt/evidence` | state-root | release evidence aggregates across worktrees before a ship decision |
| `.vidt/handoff` | state-root | role handoffs must be readable by agents in any worktree; `artifact_path` is relative to state-root |
| `.vidt/practices` | state-root | micro-practice ledger accumulates across all work |
| `.vidt/metrics` | state-root | decision log and telemetry are global |
| `.vidt/governance` | state-root | governance plans span the whole project |
| `.vidt/product` | state-root | product delivery state is shared across phases |
| `.vidt/delivery` | state-root | quick-slice status is task-level but reusable across sessions |
| `.vidt/beta` | state-root | beta programs span releases |
| `.vidt/post-release` | state-root | post-release signals are global |
| `.vidt/auto` | state-root | auto-run state and snapshots persist across runs |
| `.vidt/architecture` | state-root | architecture notes are project-wide |
| `.vidt/iterations` | state-root (workspace) | iteration workspace, round memory, and distilled patterns persist; the controller reads them from state-root |
| iteration candidate outputs (`.tmp-iteration-round-XX/`, `patches/*.patch`, materialize targets) | execution-root | one-shot candidate products live with the candidate worktree and are disposable |
| `.vidt/performance` | state-root | performance baselines are project-wide |

If a directory is not listed, default to state-root. Only artifacts that are
inherently one-shot and tied to a specific worktree's working tree belong in
execution-root.

## Worktree Path Convention

A worktree shares Git metadata but has its own working tree. Resolve state-root
from the first `worktree` record in Git's porcelain output; this is the main
worktree and remains correct when paths contain spaces or Git metadata is kept
outside the checkout:

```bash
STATE_ROOT="$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)"
```

When a script accepts `--root`, pass state-root explicitly from inside a
worktree rather than relying on the `--root .` default:

```bash
STATE_ROOT="$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -n 1)"
python scripts/init_harness_constraints.py --root "$STATE_ROOT" --summary "<task>" --pretty
```

Python runtimes should use an argv-based subprocess and parse porcelain records
directly, as `scripts/route_request.py:resolve_repository_roots()` does. Do not
pipe `git-common-dir` through `xargs`: whitespace splitting corrupts valid paths,
and the parent of an external git-dir is not necessarily the main worktree.

The `--root .` default is correct only when `cwd` is already the main
repository. Inside a worktree it points at the worktree, which is the wrong
place for shared state.

## Relationship To Other Protocols

- **harness-engineering-constraint** — `.vidt/harness/engineering-constraints.md`
  lives in state-root. From a worktree, call `init_harness_constraints.py` with
  `--root "$STATE_ROOT"` so the constraint file is shared and survives worktree
  cleanup.
- **file-handoff** — `.vidt/handoff/` lives in state-root. Because every agent
  reads and writes the same state-root directory regardless of which worktree
  it runs in, cross-worktree handoffs work without changing the handoff schema;
  `artifact_path` stays relative to state-root, and the "path resolves to the
  file itself" check holds as long as the verifier also resolves against
  state-root.
- **project-knowledge-pyramid** — the pyramid and its SHA baseline live in
  state-root. When worktrees share one `.git` but differ in working tree, the
  baseline records the main repository's HEAD so drift detection compares
  against a stable reference, not a per-worktree snapshot.
- **change-localization** — localization steps run against execution-root (the
  worktree being edited), but the L1 overview and any pyramid tiers are read
  from state-root. Do not re-derive the project map inside each worktree.
- **iteration-protocol** — the iteration workspace (`.vidt/iterations`) stays
  in state-root; only the candidate worktree's own outputs (patches, materialize
  targets, `.tmp-iteration-round-XX/`) live in execution-root. Benchmark the
  candidate in its worktree, as the iteration protocol already requires.

## Completion Evidence

When this protocol is active, completion must name:

- whether state-root and execution-root were separated for this task
- the resolved state-root path the task used
- any state directory written to execution-root by mistake, and its correction
- whether any worktree cleanup stranded state, and how it was recovered
