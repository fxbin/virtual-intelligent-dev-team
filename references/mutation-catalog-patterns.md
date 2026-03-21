# Mutation Catalog Patterns

Use this reference when `virtual-intelligent-dev-team` needs to optimize its own skill files through deterministic mutations instead of ad hoc shell edits.

## Why This Exists

The bounded loop is strongest when self-feedback can become one replayable `mutation_plan`.

Prefer a mutation catalog when the loop needs to repeatedly modify files such as:

- `references/routing-rules.json`
- `references/regression-cases.json`
- `evals/evals.json`
- `SKILL.md`
- `agents/openai.yaml`

## Built-In Operation Families

### Text operations

Use these for Markdown, YAML, or prompt files:

- `replace_text`
- `insert_after`
- `insert_before`
- `append_text`
- `prepend_text`
- `write_file`
- `delete_file`

### JSON operations

Use these for deterministic control files:

- `json_set`
  - Set or create one JSON pointer target.
- `json_merge`
  - Deep-merge one object into another object target.
- `json_delete`
  - Remove one JSON pointer target.
- `json_append`
  - Append one value to an array target.
- `json_append_unique`
  - Append only when the array does not already contain the same item.
  - Use `match_keys` for array-of-object files such as eval registries.

JSON operations use RFC 6901 style pointers such as:

- `/weights/git_workflow`
- `/evals`
- `/routing/frontend/negative_keywords`

## Recommended Self-Optimization Targets

### 1. Rebalance routing rules

Use JSON operations against `references/routing-rules.json`.

Typical edits:

- lower a false-positive keyword weight with `json_set`
- add a new exclusion block with `json_merge`
- remove a stale override with `json_delete`

### 2. Add regression coverage

Use `json_append_unique` against:

- `references/regression-cases.json`
- `evals/evals.json`

Prefer `match_keys` such as:

- `["name"]` for regression case registries
- `["id"]` for eval arrays

### 3. Refine skill instructions

Use text operations against:

- `SKILL.md`
- `references/*.md`
- `agents/openai.yaml`

Good uses:

- insert one new guardrail after an existing heading
- replace one trigger rule sentence
- append one benchmark reminder without rewriting the whole file

## Example Catalog Entry

```json
{
  "id": "checkout-false-positive-self-fix",
  "priority": 10,
  "when_any_keywords": ["checkout false positive", "routing regression", "eval coverage"],
  "mutation_plan": {
    "mode": "patch",
    "operations": [
      {
        "op": "json_set",
        "path": "references/routing-rules.json",
        "pointer": "/weights/git_workflow",
        "value": 1
      },
      {
        "op": "json_append_unique",
        "path": "evals/evals.json",
        "pointer": "/evals",
        "match_keys": ["id"],
        "value": {
          "id": 101,
          "prompt": "Audit this checkout UX for accessibility and mobile responsiveness."
        }
      }
    ]
  }
}
```

## Guardrails

- Keep one bottleneck per rule.
- Prefer JSON operations for JSON files instead of large `write_file` rewrites.
- Use text insertion or replacement only around stable anchors.
- Make duplicate prevention explicit with `match_keys` when appending regression or eval entries.
- Treat the mutation catalog as replayable infrastructure, not as a one-off scratchpad.
