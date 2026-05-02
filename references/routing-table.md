# Routing Table

This note keeps the router contract compact and explicit.

## Primary routes

| Trigger family | Selected route | Default lead | Fallback |
| --- | --- | --- | --- |
| review / audit / security | audit-fix-deliver | Code Audit Council | Technical Trinity when implementation follow-up dominates |
| git / branch / pr / push | govern-change-safely | Git Workflow Guardian | Technical Trinity when git is incidental |
| rewrite / migration / plan-first | plan-first-build | Technical Trinity | Sentinel Architect (NB) when risk or research-first signals dominate |
| iteration / retry / optimize | bounded-iteration | Technical Trinity | Sentinel Architect (NB) when repeated failures require root-cause discipline |
| release / ship / hold | ship-hold-remediate | Technical Trinity | Git Workflow Guardian when delivery governance overtakes release evidence |
| beta / staged validation / rollout feedback | beta-feedback-ramp | World-Class Product Architect | Technical Trinity when product signals are weak and implementation dominates |

## Fallback rules

- If explicit process skill detection is stronger than specialist routing, prefer the process route.
- If the request is low-information and no route clears confidence, ask one clarification question.
- If the task is single-domain and low-risk, keep one lead and suppress ceremony.

## Next step rule

- Always return the smallest executable next step plus the correct resume anchor.
