# System Map Protocol

Use this micro-practice when the team is unfamiliar with a code area, the request
touches multiple modules, or the user asks to "zoom out" before changing code.

## Goal

Create a compact map of relevant modules, callers, data flow, and seams before
the team proposes changes. The map should reduce accidental local fixes that
ignore the larger system.

## When To Activate

Activate when any of these appear:

- "zoom out", "map the code", "how does this fit", or "module map"
- rewrite, migration, architecture overhaul, or project-wide refactor
- unfamiliar area with multiple likely owners
- repeated bug where call-chain context may be the real issue
- interface, adapter, or ownership changes

## Map Shape

```markdown
## System Map

- Domain terms:
- Entry points:
- Modules:
- Callers:
- Data or event flow:
- Seams:
- Existing tests or feedback loops:
- Unknowns:
```

Use accepted project vocabulary from
`references/shared-language-and-decision-capture.md` when naming concepts.

## Rules

1. Read the smallest relevant code surface first.
2. Name callers and callees at the level where decisions are made.
3. Prefer a map that explains behavior over a full file inventory.
4. Mark unknowns instead of inventing relationships.
5. For architecture work, pass the map into
   `references/architecture-deepening-protocol.md`.

## Completion Evidence

When active, completion should name:

- modules and callers mapped
- seams identified
- tests or feedback loops found
- unknowns that could change the route
- whether the map changed the selected workflow bundle
