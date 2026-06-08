# Shared Language And Decision Capture

Use this micro-practice when a software task depends on domain terms, ambiguous
product language, or hard-to-reverse technical decisions.

## Goal

Keep the team aligned with a small project vocabulary and decision trail without
turning project context into a full spec.

## When To Activate

Activate when any of these appear:

- fuzzy or overloaded domain terms
- product scope, user flow, acceptance criteria, or API contract work
- architecture planning that names business concepts or module responsibilities
- repeated confusion caused by different names for the same thing
- a decision is hard to reverse, surprising without context, and chosen from real
  alternatives

Do not activate for tiny edits, read-only Q&A, or implementation details that do
not change shared language.

## Vocabulary Anchor

Preferred project anchor:

- `.skill-context/project-context.md`

If the host project already has a dedicated glossary such as `CONTEXT.md`, use it
as the vocabulary source and keep `.skill-context/project-context.md` focused on
commands, constraints, and verification defaults.

Record only stable terms:

```markdown
## Language

- `<Term>`
  - Means:
  - Avoid:
  - Notes:
```

Do not store implementation plans, scratch notes, or one-off task constraints as
language.

## Decision Anchor

Use a decision note only when all three are true:

- hard to reverse
- surprising without context
- selected from real trade-offs

Preferred lightweight location:

- `docs/decisions/`

Suggested shape:

```markdown
# <Decision Title>

- Status:
- Context:
- Decision:
- Alternatives considered:
- Consequences:
```

## Runtime Rules

1. If the user uses a fuzzy term, propose the precise term before building on it.
2. If project language contradicts the request, surface the conflict and ask or
   infer only when code evidence is strong.
3. Update the vocabulary when a term becomes stable.
4. Offer a decision note sparingly; never make every preference an ADR.
5. Link acceptance criteria, slice names, tests, and module maps back to the
   accepted vocabulary.

## Completion Evidence

When this micro-practice was active, completion should name:

- language terms added or confirmed
- unresolved terminology conflicts
- decision notes created or intentionally skipped
- downstream artifacts that now use the accepted vocabulary
