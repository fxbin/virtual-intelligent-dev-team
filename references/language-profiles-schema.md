# Language Profiles Schema (language-profiles/v1)

> Prose companion to `references/language-profiles.yaml`. The YAML file is the
> source of truth for the per-language context that the LLM injects into an
> agent's working memory after a profile is matched. The router itself still
> uses `references/routing-rules.json → language_profiles` for the routing
> decision.

## Why two files (JSON + YAML)

v5.0 splits language support into three orthogonal layers, each with its
own responsibility:

| Layer | File | Responsibility |
|---|---|---|
| Routing | `routing-rules.json → language_profiles` | Decide **which lead agent** handles a request whose prompt mentions this language. |
| Context | `language-profiles.yaml → profiles.<lang>` | Feed the matched lead agent the language's **ecosystem defaults, idioms, verification commands, and guardrails**. |
| Constraints | `language-profiles.yaml → profiles.<lang>.harness_constraints` | Inject language-specific guardrails that the LLM must honor (cross-reference with `agent_rules[*].constraints`). |

The router's JSON shape (`{ lead_agent, profile, keywords }`) is small and
deterministic — easy to lint and easy for `route_request.detect_languages` to
consume. The YAML shape is rich prose — meant for the LLM, not for the
router.

## File conventions

- **YAML only**, not JSON. Follows the codebase's existing YAML style: 2
  space indent, `snake_case` keys, plain unquoted strings, no `|` / `>`
  block scalars, no front matter.
- First key is always `schema_version: language-profiles/v1`.
- Second key is `skill_name: virtual-intelligent-dev-team` (matches the
  `const` used in every JSON schema under `references/`).
- `profiles:` is the top-level map, keyed by language id.

## Profile shape

Each `profiles.<lang>` entry has six top-level keys:

| Key | Type | Purpose |
|---|---|---|
| `display_name` | string | Human-readable name shown in dashboards and the LLM context. |
| `routing_keywords` | string array | Mirror of `routing-rules.json → language_profiles[<lang>].keywords`. The router uses the JSON copy; this YAML copy is for human readers and for the consistency check in `scripts/check_language_profiles.py`. |
| `ecosystem` | string map | Framework / build / ORM / async defaults. Each value is a short phrase, e.g. `build: "Gradle / Maven"`. |
| `conventions` | string array | Idiomatic patterns and anti-patterns. Phrased as short rules, not essays. |
| `verification` | string map | Canonical lint / test / coverage / build commands. Keys are free-form (`lint`, `test`, `coverage`, `static_analysis`, `security`, `sanitizers`, …). |
| `harness_constraints` | string array | Hard guardrails the LLM must enforce (e.g. no `!!` non-null assertions in Kotlin). Empty list means "no language-specific constraint beyond the agent's own". |

## Why Java is an exception

Java has a dedicated lead agent (`Java Virtuoso`) because Spring Boot, JVM
tuning, and concurrency review cannot be expressed as a simple conventions
list. The Java profile in this YAML is **still useful** — it injects
baseline toolchain commands (Gradle / Maven, Spring Boot 3.x, JVM 21+) that
`Java Virtuoso` already knows but that round out the dashboard view and let
other agents reason about Java code when it appears incidentally.

## Adding a new profile

1. Add a `profiles.<lang>` entry to `language-profiles.yaml`. The profile
   must have all six top-level keys (use `harness_constraints: []` for none).
2. Add a matching `language_profiles[<lang>]` entry to
   `routing-rules.json` with `{ lead_agent, profile, keywords }`. The
   `profile` value must equal the YAML key.
3. Run `python scripts/check_language_profiles.py --pretty` to verify the
   two files stay in sync.
4. Add at least one `language_routing.<lang> is <Lead Agent>` case to
   `evals/evals.json` so the regression harness covers the new entry.

## Validity checking

`scripts/check_language_profiles.py` enforces these invariants:

1. YAML top-level keys exactly match `routing-rules.json → language_profiles`.
2. Every YAML profile has all six required sub-keys.
3. Every YAML `routing_keywords` entry is also present in
   `routing-rules.json → language_profiles[<lang>].keywords`. Mismatches are
   surfaced as warnings, not errors, so you can iterate quickly.
4. `harness_constraints` lines do not duplicate items already in the
   matched agent's `agent_rules[<agent>].constraints` (best-effort string
   overlap; warnings only).

The linter `lint_virtual_team_contract.py` does **not** read YAML files
(see `lint_virtual_team_contract.py` is YAML-blind), so
`check_language_profiles.py` is the canonical validator for this file.

## Why this is in `references/` and not `assets/`

`assets/` holds templates the skill writes out (e.g. brief scaffolds,
project-context stubs). `references/` holds authoritative data the skill
reads at runtime. Language profiles are read-only input data consumed by
the LLM, so they belong in `references/` alongside `routing-rules.json`.