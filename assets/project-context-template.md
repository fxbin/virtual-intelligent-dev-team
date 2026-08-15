# Project Context

Use this file for durable project rules that should survive across delivery slices.

## Stack

- Runtime:
- Frameworks:
- Package manager:
- Test runner:

## Commands

- Install:
- Test:
- Lint:
- Build:
- Run locally:

## Architecture Rules

- Entry points:
- Data boundaries:
- Shared modules:
- Integration contracts:
- Stable semantic keys / enums / data attributes:
- Presentation/localization boundaries:

## External Systems

Record only durable non-secret identifiers and boundaries.

- Provider / service:
- Human-readable resource name:
- Canonical project/resource ID:
- How resource identity is verified:
- Required remote capabilities:
- Auth/scope boundary:
- Secret boundary:
- Safe read/dry-run command:
- Remote mutation command/path:
- Production verification path:
- CLI/manual fallback:

## Delivery Rules

- Default branch:
- Commit style:
- Review expectation:
- Release constraints:
- Release-train branch (if used):
- Child Issue closing policy on non-default branch:
- Final release PR ownership:
- Required code-plane gates:
- Required control-plane gates:
- Required production data-plane gates:
- Rollback anchor:

## Canonical Project Truth

- Master / roadmap source:
- Product/spec source:
- Release/status source:
- Migration/schema history source:
- Current phase / gate:
- Explicitly paused/gated work:

## Forbidden Changes

- Do not modify:
- Do not introduce:
- Ask first before:

## Verification Evidence

- Required before completion:
- Useful targeted checks:
- Known flaky or expensive checks:
- Required remote read-back:
- Required production smoke:

## Operator Handoff

When an operator must execute a remote command:

- Working directory / target:
- Dry-run/read-only command first:
- Expected safe output:
- STOP conditions:
- Secret handling note:
- Mutation command:
- Non-secret result to return:
- Resume anchor:
