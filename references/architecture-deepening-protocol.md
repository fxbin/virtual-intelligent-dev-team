# Architecture Deepening Protocol

Use this micro-practice when the work is about architecture improvement,
testability, AI navigability, module ownership, adapters, seams, or entropy
reduction.

## Goal

Find changes that make modules deeper: more useful behavior behind simpler,
clearer interfaces. This gives maintainers locality and gives agents a smaller
surface to reason about.

## Vocabulary

Use these terms consistently:

- `module`
  - Anything with an interface and implementation.
- `interface`
  - Everything callers must know: types, invariants, ordering, errors, config,
    and behavior.
- `implementation`
  - The code behind the interface.
- `seam`
  - The place behavior can change without editing every caller.
- `adapter`
  - A concrete implementation behind a seam.
- `depth`
  - The leverage of the interface. Deep modules hide useful complexity behind a
    smaller interface.
- `locality`
  - The degree to which bugs, changes, and knowledge stay concentrated.
- `leverage`
  - The useful behavior callers get without learning internal complexity.

## Evaluation Tests

Use these before proposing a refactor:

- `deletion test`
  - If deleting a module removes complexity entirely, it may be shallow. If the
    complexity reappears across many callers, the module may be earning its keep.
- `adapter reality test`
  - One adapter can be a hypothetical seam. Two or more adapters prove a real
    seam.
- `test surface test`
  - The interface should be the stable test surface; tests should not need
    private implementation knowledge.
- `locality test`
  - A change should concentrate behavior rather than spread edits across many
    callers.

## Candidate Shape

```markdown
## Deepening Candidate

- Modules:
- Current shallow interface:
- Proposed deeper interface:
- Locality gain:
- Leverage gain:
- Test surface:
- Entropy retired:
- Recommendation: Strong | Worth exploring | Speculative
```

## Relationship To Anti-Entropy

Use `references/anti-entropy-governance.md` when the candidate retires duplicate
owners, old paths, fallbacks, adapters, or source-of-truth behavior.

Do not preserve a shallow path only because it already exists. Keep compatibility
only when active external dependency evidence exists.

## Completion Evidence

When active, completion should name:

- candidates considered
- top recommendation
- deletion / adapter / locality evidence
- tests that would become simpler or more reliable
- entropy retired or deliberately preserved
