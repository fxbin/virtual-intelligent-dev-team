# Runtime Routing Rules

This document defines the primary routes, stage council overlays, score model, thresholds, and fallback rules used by the routing engine. The machine-readable source of truth lives in `routing-rules.json` and is exercised by `scripts/route_request.py`.

## Primary Routes

| Trigger family | Selected route | Default lead | Fallback |
| --- | --- | --- | --- |
| review / audit / security | audit-fix-deliver | Code Audit Council | Technical Trinity when implementation follow-up dominates |
| git / branch / pr / push | govern-change-safely | Git Workflow Guardian | Technical Trinity when git is incidental |
| rewrite / migration / plan-first | plan-first-build | Technical Trinity | Sentinel Architect (NB) when risk or research-first signals dominate |
| iteration / retry / optimize | bounded-iteration | Technical Trinity | Sentinel Architect (NB) when repeated failures require root-cause discipline |
| release / ship / hold | ship-hold-remediate | Technical Trinity | Git Workflow Guardian when delivery governance overtakes release evidence |
| beta / staged validation / rollout feedback | beta-feedback-ramp | World-Class Product Architect | Technical Trinity when product signals are weak and implementation dominates |
| data pipeline / ETL / stream processing | data-pipeline-govern | Data Pipeline Guardian | Technical Trinity when infrastructure-only |
| API design / contract / versioning | api-contract-govern | API Contract Sentinel | Technical Trinity when implementation-only |

## Stage Council Overlays

These overlays sit under `product-spec-deliver`; they do not replace the selected lead or workflow bundle.

| Trigger family | Overlay | Lead remains |
| --- | --- | --- |
| PRD / product strategy / user research / competitor / metrics / roadmap / stakeholder | product-discovery-council | World-Class Product Architect |
| high-fidelity prototype / runnable HTML prototype / design system / visual design / accessibility | prototype-design-council | World-Class Product Architect |

## Routing Score Model

1. **Explicit priority routing** — `priority_routing_rules` handle hard priority scenarios like "audit before language stack", "explicit Git workflow before general engineering".
2. **Positive keyword scoring** — accumulate by weight when `positive` keywords match.
3. **Negative keyword penalty** — subtract penalty to reduce false triggers and cross-domain leakage.
4. **Score clamping** — `final_score = clamp(positive_score - negative_score, 0, max_agent_score)`.
5. **Confidence** — `confidence = top1_score / max(top3_total_score, 1)`.
6. **Language detection** — `language_profiles` identify `python/go/nodejs/rust/java/kotlin/swift/cpp/csharp/php/ruby/elixir/scala` and map to lead agents.
7. **Matching boundaries** — Chinese: substring match; English: word boundary match (short words like `pr`, `ui`, `go` require technical context).

## Thresholds

- `high_confidence` (0.55): single lead
- `medium_confidence` (0.35): lead + 1 assistant
- Below `medium_confidence`: lead + 2 assistants, suggest clarification
- `sentinel_overlay_threshold` (6): trigger governance overlay

## Fallback Rules

- If explicit process skill detection is stronger than specialist routing, prefer the process route.
- If the request is low-information and no route clears confidence, ask one clarification question.
- If the task is single-domain and low-risk, keep one lead and suppress ceremony.
- Always return the smallest executable next step plus the correct resume anchor.
