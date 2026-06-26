# Decision Log Schema (decision-log/v1)

> This file documents the append-only governance decision log introduced in v5.0.
> The canonical machine-readable schema is `decision-log.schema.json` (sibling file). This document is the prose companion.

## Why a separate log

Before v5.0, the routing layer appended one JSON line per route decision to
`.skill-metrics/governance_events.jsonl`. That file grew organically and only
carried the four fields needed for fast-track quota enforcement. v5.0 makes
the file a real **decision ledger**:

- Same append-only semantics.
- Same on-disk path concept (relative to the working directory), but renamed
  to `.skill-metrics/decision-log.jsonl` to signal that it now serves the
  broader governance triangle (Identity × Routing × Constraints), not only
  the fast-track counter.
- Schema is explicit (`references/decision-log.schema.json`).
- New optional fields describe the **decision** and **evidence**, not just the
  routing outcome.

## File location

The path is configurable via `routing-rules.json → fast_track_control.metrics_file`,
default `.skill-metrics/decision-log.jsonl`. The path is resolved relative to
the current working directory at write time (typically the repo root).

## Producer surface

Only one writer in v5.0:

- `scripts/route_request.py → append_governance_event()`

This is the **single canonical writer** for routing-layer decisions. It is
also invoked from `run_release_gate.py`, `run_team_engine_drill.py`, and
the iteration harness, all of which funnel through the same helper.

Read-side consumers:

- `route_request.py → load_governance_events()` (fast-track quota and cooldown)
- `scripts/inspect_decision_log.py` (this skill's dashboard reader; introduced in v5.0)

## Field reference

| Field | Required | Type | Description |
|---|---|---|---|
| `timestamp` | yes | ISO 8601 string | When the decision was made. Seconds precision. |
| `decision` | yes | enum | Semantic decision kind (see below). |
| `lead_agent` | yes | string | Display name of the lead agent that owns the decision. |
| `verifier` | yes | enum | Independent verification outcome. `n_a` means no verifier ran. |
| `risk_level` | yes | enum | Risk tier: `low` / `medium` / `high`. |
| `selected_track` | yes | enum | `regular track` (full dual-sign flow) or `fast track` (quota-gated). |
| `reason` | yes | string | Short human-readable rationale. Empty string allowed. |
| `evidence` | no | string | Optional pointer to evidence (test IDs, gate statuses, fragments joined by `||`). |
| `mode_hint` | yes | string | Producer tag (e.g. `route_request`, `release_gate`). |

### `decision` enum

| Value | When emitted |
|---|---|
| `route_selected` | A lead agent was selected for a request (default for the routing layer). |
| `delivery_accepted` | A DeliveryCycleReport was accepted by the Lead after Worker/Verifier cycle. |
| `delivery_held` | A DeliveryCycleReport was held by the Lead (verifier failed or evidence missing). |
| `release_ship` | Release gate answered `ship`. |
| `release_hold` | Release gate answered `hold`. |
| `fast_track_engaged` | Routing engaged the fast-track (quota-gated) path. |
| `fallback_engaged` | A fallback route was engaged (assistant took over, fallback used, etc.). |
| `intent_confirmation_requested` | Skill asked the user a targeted intent-confirmation question before finalizing the route. |

### `verifier` enum

| Value | When emitted |
|---|---|
| `n_a` | No verifier ran (typical for routing-only entries — legacy entries also default here). |
| `pass` | Independent verifier passed. |
| `fail` | Independent verifier failed. |
| `hold` | Independent verifier held pending human input. |

## Migration from `governance_events.jsonl`

`scripts/migrate_governance_events.py` performs a one-shot migration:

1. Reads every line from `.skill-metrics/governance_events.jsonl`.
2. Parses it as JSON.
3. Adds the four new v5.0 fields with these defaults if missing:
   - `decision`: `"route_selected"`
   - `verifier`: `"n_a"`
   - `reason`: `""`
   - `evidence`: `""` (note: evidence is optional, but legacy entries get an empty value for symmetry)
4. Validates each line against `decision-log.schema.json` (basic shape check).
5. Writes valid lines to `.skill-metrics/decision-log.jsonl`.
6. Emits a migration summary (counts, skipped lines, errors).

After migration, the original `governance_events.jsonl` file is **left in
place** but is no longer written to. Operators can delete it manually after
they are confident the new log is intact.

## Compatibility notes

- The schema sets `additionalProperties: false`. Producers must not emit
  unknown keys; if you need a new field, add it to the schema first.
- `evidence` is the only field that is not in `required`. Producers may
  omit it; readers should treat missing `evidence` as `""`.
- `verifier` was *implicit* before v5.0 (never read). It is now `required`,
  so any legacy producer that bypasses the helper must be updated.
- The fast-track counter (`get_fast_track_stats`) still reads only
  `timestamp` and `selected_track`, so the additional fields are pure
  additive payload — they do not change behavior.

## How to read the log

```bash
# Pretty JSON summary
python scripts/inspect_decision_log.py --pretty

# Markdown report
python scripts/inspect_decision_log.py --markdown-output /tmp/decision-log.md

# Self-contained HTML dashboard
python scripts/inspect_decision_log.py --html-output /tmp/decision-log.html
```